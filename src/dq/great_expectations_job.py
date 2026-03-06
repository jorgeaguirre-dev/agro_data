"""
Job de Glue para ejecutar validaciones de Great Expectations
Con sincronización forzada del catálogo
"""
import sys
import json
import time
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Inicialización
args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "suite_name", "database_name", "table_name", "results_bucket"],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


def force_catalog_sync(spark, database, table, max_attempts=10, delay=5):
    """Fuerza la sincronización del catálogo y reintenta hasta que la tabla esté disponible"""

    print("🔄 Forzando sincronización del catálogo...")

    # Opción 1: Refrescar la tabla si existe
    try:
        spark.sql(f"REFRESH TABLE `{database}`.`{table}`")
        print(f"✅ Tabla {database}.{table} refrescada")
    except Exception:
        print("⚠️ No se pudo refrescar (la tabla puede no existir aún)")

    # Opción 2: Listar tablas disponibles en Spark
    for attempt in range(max_attempts):
        try:
            print(
                f"🔍 Intento {attempt + 1}/{max_attempts} - Verificando tablas en Spark..."
            )

            # Listar bases de datos en Spark
            spark.sql("SHOW DATABASES").show(truncate=False)

            # Intentar usar la base de datos
            spark.sql(f"USE `{database}`")

            # Listar tablas en esta base de datos
            tables_df = spark.sql("SHOW TABLES")
            print("📋 Tablas disponibles en Spark:")
            tables_df.show(truncate=False)

            # Verificar si nuestra tabla está en la lista
            tables_list = [row["tableName"] for row in tables_df.collect()]

            if table in tables_list:
                print(f"✅ Tabla {table} encontrada en Spark!")

                # Intentar contar registros
                count_df = spark.sql(f"SELECT COUNT(*) FROM `{database}`.`{table}`")
                count = count_df.collect()[0][0]
                print(f"📊 Registros encontrados: {count}")
                return True
            else:
                print(
                    f"⏳ Tabla {table} NO encontrada en Spark. Tablas disponibles: {tables_list}"
                )

        except Exception as e:
            print(f"⏳ Error en intento {attempt + 1}: {str(e)[:100]}")

        if attempt < max_attempts - 1:
            print(f"   Esperando {delay} segundos...")
            time.sleep(delay)

    return False


try:
    print("=" * 50)
    print("🚀 INICIANDO JOB DE DATA QUALITY")
    print("=" * 50)
    print("📋 Configuración:")
    print(f"   - Database: {args['database_name']}")
    print(f"   - Table: {args['table_name']}")
    print(f"   - Suite: {args['suite_name']}")
    print(f"   - Results bucket: {args['results_bucket']}")

    # Opción 3: Usar Glue Client directamente para debug
    glue_client = boto3.client("glue", region_name="us-east-1")
    try:
        tables_response = glue_client.get_tables(DatabaseName=args["database_name"])
        print(
            f"📋 Tablas en Glue Catalog: {[t['Name'] for t in tables_response['TableList']]}"
        )
    except Exception as e:
        print(f"⚠️ Error obteniendo tablas de Glue: {e}")

    # ESPERAR hasta que la tabla esté disponible en Spark
    if not force_catalog_sync(spark, args["database_name"], args["table_name"]):
        # Último recurso: intentar con la ruta S3 directamente
        print("⚠️ Intentando acceder por ruta S3 como fallback...")
        s3_path = f"s3://{args['results_bucket'].replace('-curated', '')}/{args['table_name']}"

        # Determinar la ruta correcta
        if "rinde" in args["table_name"]:
            s3_path = "s3://agro-data-pipeline-dev-curated/rinde_lotes"
        else:
            s3_path = "s3://agro-data-pipeline-dev-curated/clima_diario"

        print(f"📂 Leyendo directamente de: {s3_path}")

        try:
            df = spark.read.parquet(s3_path)
            total_rows = df.count()
            print(f"✅ Lectura directa exitosa! {total_rows} registros")

            # Crear vista temporal para poder usar SQL
            df.createOrReplaceTempView(args["table_name"])

        except Exception as e2:
            raise Exception(
                f"No se pudo acceder a los datos ni por catalog ni por S3: {e2}"
            )
    else:
        # Leer la tabla normalmente
        df = spark.sql(
            f"SELECT * FROM `{args['database_name']}`.`{args['table_name']}`"
        )
        total_rows = df.count()

    print(f"📊 Total de registros: {total_rows}")

    if total_rows == 0:
        print("⚠️ Tabla vacía - no se pueden realizar validaciones")
        results = {
            "suite_name": args["suite_name"],
            "table": args["table_name"],
            "database": args["database_name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows": 0,
            "status": "EMPTY_TABLE",
            "validations": [],
        }
    else:
        # Mostrar schema y datos
        print("📋 Schema:")
        df.printSchema()
        print("📋 Primeras 3 filas:")
        df.show(3, truncate=False)

        # Validaciones
        results = {
            "suite_name": args["suite_name"],
            "table": args["table_name"],
            "database": args["database_name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows": total_rows,
            "validations": [],
        }

        # Columnas disponibles
        columns = df.columns
        print(f"📋 Columnas disponibles: {columns}")

        # Validación 1: Sin nulos en lote_id (si existe)
        if "lote_id" in columns:
            null_count = df.filter("`lote_id` IS NULL").count()
            results["validations"].append(
                {
                    "expectation": "not_null_lote_id",
                    "column": "lote_id",
                    "success": null_count == 0,
                    "null_count": null_count,
                    "null_percentage": round(null_count / total_rows * 100, 2),
                }
            )
            print(f"   lote_id nulos: {null_count}")

        # Validaciones específicas por tabla
        if "rinde" in args["table_name"]:
            if "rinde" in columns:
                out_of_range = df.filter(
                    "CAST(`rinde` AS double) < 0 OR CAST(`rinde` AS double) > 20000"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_rinde_0_20000",
                        "column": "rinde",
                        "success": out_of_range == 0,
                        "out_of_range": out_of_range,
                    }
                )
                print(f"   rinde fuera de rango: {out_of_range}")

            if "campana" in columns:
                null_campana = df.filter("`campana` IS NULL").count()
                results["validations"].append(
                    {
                        "expectation": "not_null_campana",
                        "column": "campana",
                        "success": null_campana == 0,
                        "null_count": null_campana,
                    }
                )

        elif "clima" in args["table_name"]:
            if "temperatura" in columns:
                temp_out = df.filter(
                    "CAST(`temperatura` AS double) < -20 OR CAST(`temperatura` AS double) > 50"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_temperatura_-20_50",
                        "column": "temperatura",
                        "success": temp_out == 0,
                        "out_of_range": temp_out,
                    }
                )
                print(f"   temperatura fuera de rango: {temp_out}")

            if "precipitacion" in columns:
                precip_out = df.filter(
                    "CAST(`precipitacion` AS double) < 0 OR CAST(`precipitacion` AS double) > 500"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_precipitacion_0_500",
                        "column": "precipitacion",
                        "success": precip_out == 0,
                        "out_of_range": precip_out,
                    }
                )
                print(f"   precipitación fuera de rango: {precip_out}")

    # Guardar resultados
    s3 = boto3.client("s3")
    key = f"dq_results/{args['table_name']}_{args['suite_name']}_{time.strftime('%Y%m%d_%H%M%S')}.json"

    s3.put_object(
        Bucket=args["results_bucket"],
        Key=key,
        Body=json.dumps(results, indent=2, default=str),
    )

    print(f"📈 Resultados guardados en s3://{args['results_bucket']}/{key}")

    if total_rows > 0:
        all_success = all(v.get("success", False) for v in results["validations"])
        print(f"✅ Validaciones exitosas: {all_success}")

        if not all_success:
            print("⚠️ Algunas validaciones fallaron - revisar resultados")
    else:
        print("⚠️ Tabla vacía - validaciones no aplicadas")

    print("=" * 50)
    print("✅ JOB COMPLETADO")
    print("=" * 50)

except Exception as e:
    print(f"❌ Error fatal: {str(e)}")
    import traceback

    traceback.print_exc()
    raise
finally:
    job.commit()
