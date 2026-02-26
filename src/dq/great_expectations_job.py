"""
Job de Glue para ejecutar validaciones de Great Expectations
"""
import sys
import json
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Inicialización
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'suite_name', 'database_name', 'table_name'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

try:
    print(f"🔍 Ejecutando validaciones para {args['table_name']}")
    
    # Leer tabla desde Glue Catalog
    df = spark.sql(f"SELECT * FROM {args['database_name']}.{args['table_name']}")
    total_rows = df.count()
    print(f"📊 Registros a validar: {total_rows}")
    
    # Validaciones inline (simulando Great Expectations)
    results = {
        "suite_name": args['suite_name'],
        "table": args['table_name'],
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "total_rows": total_rows,
        "validations": []
    }
    
    # Validación 1: Sin nulos en columnas críticas
    for col in ['lote_id'] if 'rinde' in args['table_name'] else ['lote_id', 'fecha']:
        null_count = df.filter(f"{col} IS NULL").count()
        success = null_count == 0
        results['validations'].append({
            "expectation": f"column_values_not_null_{col}",
            "column": col,
            "success": success,
            "null_count": null_count,
            "null_percentage": round(null_count/total_rows*100, 2) if total_rows > 0 else 0
        })
    
    # Validación 2: Rangos
    if 'rinde' in args['table_name']:
        out_of_range = df.filter("rinde < 0 OR rinde > 20000").count()
        results['validations'].append({
            "expectation": "column_values_between_rinde_0_20000",
            "column": "rinde",
            "success": out_of_range == 0,
            "out_of_range": out_of_range,
            "min_expected": 0,
            "max_expected": 20000
        })
    else:
        # Validaciones clima
        temp_out = df.filter("temperatura < -20 OR temperatura > 50").count()
        precip_out = df.filter("precipitacion < 0 OR precipitacion > 500").count()
        results['validations'].extend([
            {
                "expectation": "column_values_between_temp_-20_50",
                "column": "temperatura",
                "success": temp_out == 0,
                "out_of_range": temp_out
            },
            {
                "expectation": "column_values_between_precip_0_500",
                "column": "precipitacion",
                "success": precip_out == 0,
                "out_of_range": precip_out
            }
        ])
    
    # Validación 3: Formato fecha
    if 'clima' in args['table_name']:
        import re
        fecha_invalida = df.rdd.filter(
            lambda r: not re.match(r'^\d{4}-\d{2}-\d{2}$', r.fecha) if r.fecha else False
        ).count()
        results['validations'].append({
            "expectation": "column_values_match_regex_fecha",
            "column": "fecha",
            "success": fecha_invalida == 0,
            "invalid_format": fecha_invalida
        })
    
    # Guardar resultados en S3
    s3 = boto3.client('s3')
    bucket = args.get('results_bucket', 'agro-data-pipeline-dev-curated')
    key = f"dq_results/{args['table_name']}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(results, indent=2)
    )
    
    # Determinar éxito global
    all_success = all(v['success'] for v in results['validations'])
    
    print(f"📈 Resultados guardados en s3://{bucket}/{key}")
    print(f"✅ Todas las validaciones exitosas: {all_success}")
    
    if not all_success:
        raise Exception("Algunas validaciones de calidad fallaron")
    
except Exception as e:
    print(f"❌ Error en validaciones: {str(e)}")
    raise
finally:
    job.commit()