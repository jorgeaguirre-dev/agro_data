"""
AWS Glue Job para procesar datos climáticos
"""
import sys
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Inicialización
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

try:
    print(f"📥 Leyendo clima desde: {args['input_path']}")
    
    # 1. Leer CSV
    df = spark.read.option("header", "true").csv(args['input_path'])
    total_inicial = df.count()
    print(f"📊 Registros climáticos: {total_inicial}")
    print(f"📋 Columnas: {df.columns}")
    
    # 2. Validaciones inline
    print("🔍 Validando datos climáticos...")
    
    # 2.1 Convertir a numérico
    df = df.withColumn("temp_num", F.col("temperatura").cast("double"))
    df = df.withColumn("precip_num", F.col("precipitacion").cast("double"))
    
    # 2.2 Validar rangos
    df = df.filter(F.col("temp_num").between(-20, 50))
    df = df.filter(F.col("precip_num").between(0, 500))
    
    # 2.3 Eliminar nulos en columnas clave
    df = df.dropna(subset=["lote_id", "fecha"])
    
    # 2.4 Validar formato de fecha
    df = df.withColumn("fecha_valida", 
                       F.when(F.col("fecha").rlike("^\\d{4}-\\d{2}-\\d{2}$"), True)
                       .otherwise(False))
    df = df.filter(F.col("fecha_valida") == True)
    
    # 3. Transformaciones
    print("🔄 Aplicando transformaciones...")
    
    # 3.1 Estandarizar nombres
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower().strip().replace(" ", "_"))
    
    # 3.2 EXTRAER campaña de la fecha (asumiendo formato YYYY-MM-DD)
    df = df.withColumn("campana", F.substring(F.col("fecha"), 1, 4))
    
    # 3.3 CREAR columna lote a partir de lote_id
    df = df.withColumn("lote", F.col("lote_id"))
    
    # 3.4 Limpiar particiones
    df = df.withColumn("campana", F.regexp_replace(F.col("campana"), "[^a-zA-Z0-9]", "_"))
    df = df.withColumn("lote", F.regexp_replace(F.col("lote"), "[^a-zA-Z0-9]", "_"))
    
    # 3.5 Limpiar columnas temporales
    df = df.drop("temp_num", "precip_num", "fecha_valida")
    
    total_final = df.count()
    print(f"📊 Registros después de validaciones: {total_final}")
    print(f"   Filtrados: {total_inicial - total_final}")
    print(f"📋 Columnas finales: {df.columns}")
    
    # 4. Escribir
    print(f"📤 Escribiendo a: {args['output_path']}")
    print(f"📂 Particionando por: campana, lote")
    df.write \
        .mode("overwrite") \
        .partitionBy("campana", "lote") \
        .parquet(args['output_path'])
    
    print("✅ Job climático completado")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise
finally:
    job.commit()