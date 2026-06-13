"""
Data Quality Validator - Implementación nativa en PySpark
"""
import sys
import json
import time
import boto3
from pyspark import SparkConf, SparkContext
from pyspark.context import SparkContext as OriginalSparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

CLOUD_REGION = 'us-east-1'

class DataQualityValidator:
    """Validador de calidad de datos para tablas agrícolas"""

    def __init__(self, spark, database_name, table_name, results_bucket, suite_name):
        self.spark = spark
        self.database_name = database_name
        self.table_name = table_name
        self.results_bucket = results_bucket
        self.suite_name = suite_name
        self.glue_client = boto3.client('glue', region_name=CLOUD_REGION)

    def wait_for_table(self, max_attempts=12, delay=10):
        """Espera a que la tabla esté disponible en Glue Catalog"""
        for attempt in range(max_attempts):
            try:
                tables = self.glue_client.get_tables(DatabaseName=self.database_name)
                table_names = [t['Name'] for t in tables['TableList']]

                if self.table_name in table_names:
                    print(f"✅ Tabla {self.table_name} encontrada en Glue Catalog")
                    return True

                print(f"⏳ Intento {attempt + 1}/{max_attempts}: tabla no disponible")

            except Exception as e:
                print(f"⚠️ Error verificando: {str(e)[:100]}")

            if attempt < max_attempts - 1:
                time.sleep(delay)

        raise Exception(f"Tabla {self.database_name}.{self.table_name} no disponible")

    def load_data(self):
        """Carga los datos desde Glue Catalog"""
        print("=" * 50)
        print("🔍 CARGANDO DATOS")
        print("=" * 50)

        # Verificar que el catalog está configurado
        catalog_impl = self.spark.conf.get("spark.sql.catalogImplementation", "no configurado")
        print(f"🔍 Catalog implementation: {catalog_impl}")

        # Listar bases de datos disponibles
        try:
            dbs = self.spark.sql("SHOW DATABASES").collect()
            print(f"📋 Bases de datos: {[row.namespace for row in dbs]}")
        except Exception as e:
            print(f"⚠️ Error listando databases: {e}")

        # Intentar usar la base de datos
        try:
            self.spark.sql(f"USE {self.database_name}")
            print(f"✅ Base de datos seleccionada: {self.database_name}")
        except Exception as e:
            print(f"⚠️ Error usando base de datos: {e}")

        # Consultar la tabla
        query = f"SELECT * FROM `{self.database_name}`.`{self.table_name}`"
        print(f"📊 Ejecutando: {query}")

        df = self.spark.sql(query)
        print(f"✅ Datos cargados correctamente")
        return df

    def validate_not_null(self, df, columns):
        """Valida que las columnas críticas no tengan nulos"""
        results = []
        for column in columns:
            if column in df.columns:
                null_count = df.filter(f"`{column}` IS NULL").count()
                total_rows = df.count()
                success = null_count == 0
                results.append({
                    "expectation": f"not_null_{column}",
                    "column": column,
                    "success": success,
                    "null_count": null_count,
                    "null_percentage": round(null_count / total_rows * 100, 2) if total_rows > 0 else 0
                })
                print(f"   {column}: {null_count} nulos")
        return results

    def validate_ranges(self, df):
        """Valida rangos según el tipo de tabla"""
        results = []

        if 'rinde' in self.table_name:
            if 'rinde' in df.columns:
                out_of_range = df.filter("CAST(`rinde` AS double) < 0 OR CAST(`rinde` AS double) > 20000").count()
                results.append({
                    "expectation": "range_rinde_0_20000",
                    "column": "rinde",
                    "success": out_of_range == 0,
                    "out_of_range": out_of_range
                })
                print(f"   rinde fuera de rango: {out_of_range}")
        else:
            if 'temperatura' in df.columns:
                temp_out = df.filter("CAST(`temperatura` AS double) < -20 OR CAST(`temperatura` AS double) > 50").count()
                results.append({
                    "expectation": "range_temperatura_-20_50",
                    "column": "temperatura",
                    "success": temp_out == 0,
                    "out_of_range": temp_out
                })
                print(f"   temperatura fuera de rango: {temp_out}")

            if 'precipitacion' in df.columns:
                precip_out = df.filter("CAST(`precipitacion` AS double) < 0 OR CAST(`precipitacion` AS double) > 500").count()
                results.append({
                    "expectation": "range_precipitacion_0_500",
                    "column": "precipitacion",
                    "success": precip_out == 0,
                    "out_of_range": precip_out
                })
                print(f"   precipitación fuera de rango: {precip_out}")

        return results

    def save_results(self, results, total_rows):
        """Guarda los resultados en S3"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        key = f"dq_results/{self.table_name}_{self.suite_name}_{timestamp}.json"

        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=self.results_bucket,
            Key=key,
            Body=json.dumps({
                "suite_name": self.suite_name,
                "table": self.table_name,
                "database": self.database_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_rows": total_rows,
                "validations": results
            }, indent=2, default=str)
        )

        print(f"📈 Resultados guardados en s3://{self.results_bucket}/{key}")
        return key

    def run(self):
        """Ejecuta todas las validaciones"""
        print("=" * 50)
        print("🚀 INICIANDO DATA QUALITY JOB")
        print("=" * 50)

        # 1. Esperar tabla
        self.wait_for_table()

        # 2. Cargar datos
        df = self.load_data()
        total_rows = df.count()
        print(f"📊 Registros a validar: {total_rows}")

        if total_rows == 0:
            print("⚠️ Tabla vacía")
            self.save_results([], 0)
            return

        # 3. Ejecutar validaciones
        print("🔍 Ejecutando validaciones...")

        # Validaciones de nulos
        critical_columns = ['lote_id', 'campana'] if 'rinde' in self.table_name else ['lote_id', 'fecha']
        validation_results = self.validate_not_null(df, critical_columns)

        # Validaciones de rangos
        validation_results.extend(self.validate_ranges(df))

        # 4. Guardar resultados
        self.save_results(validation_results, total_rows)

        # 5. Evaluar éxito
        all_passed = all(v.get('success', False) for v in validation_results)
        print(f"✅ Todas las validaciones exitosas: {all_passed}")

        if not all_passed:
            raise Exception("Algunas validaciones de calidad fallaron")


def main():
    """Función principal del job"""
    args = getResolvedOptions(sys.argv, [
        'JOB_NAME', 'suite_name', 'database_name', 'table_name', 'results_bucket'
    ])

    # Configuración completa para Glue Catalog
    conf = SparkConf()
    
    # Configuración del catálogo de Spark
    conf.set("spark.sql.catalogImplementation", "hive")
    conf.set("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
    
    # Configuración del metastore de Hive para usar Glue
    conf.set("hive.metastore.warehouse.dir", "/tmp/spark-warehouse")
    conf.set("hive.metastore.client.factory.class", "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory")
    
    # Configuración adicional de Glue
    conf.set("spark.hadoop.hive.metastore.client.factory.class", "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory")
    
    # Configuración de S3
    conf.set("spark.hadoop.fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.InstanceProfileCredentialsProvider")
    
    sc = SparkContext(conf=conf)
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    
    # Verificar la configuración
    print("=" * 50)
    print("🔍 CONFIGURACIÓN DE SPARK")
    print("=" * 50)
    print(f"Catalog implementation: {spark.conf.get('spark.sql.catalogImplementation')}")
    print(f"Metastore factory: {spark.conf.get('hive.metastore.client.factory.class', 'not set')}")
    
    # Listar bases de datos para verificar conexión
    print("📋 Listando bases de datos...")
    try:
        dbs = spark.sql("SHOW DATABASES").collect()
        print(f"   Bases de datos encontradas: {[row.namespace for row in dbs]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    
    try:
        validator = DataQualityValidator(
            spark=spark,
            database_name=args['database_name'],
            table_name=args['table_name'],
            results_bucket=args['results_bucket'],
            suite_name=args['suite_name']
        )
        
        validator.run()
        job.commit()
        
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        raise