"""
AWS Glue Job para procesar datos de rinde de lotes
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
    print(f"📥 Leyendo datos desde: {args['input_path']}")
    
    # 1. Leer CSV
    df = spark.read.option("header", "true").csv(args['input_path'])
    total_inicial = df.count()
    print(f"📊 Registros leídos: {total_inicial}")
    print(f"📋 Columnas: {df.columns}")
    
    # 2. Validaciones inline
    print("🔍 Validando datos...")
    
    # 2.1 Filtrar rinde fuera de rango (0-20000)
    df = df.withColumn("rinde_num", F.col("rinde").cast("double"))
    df = df.filter(F.col("rinde_num").between(0, 20000))
    
    # 2.2 Eliminar nulos en columnas críticas
    df = df.dropna(subset=["lote_id", "campana"])
    
    # 2.3 Validar formato de fecha (simple)
    df = df.withColumn("fecha_valida", 
                       F.when(F.col("fecha_cosecha").rlike("^\\d{4}-\\d{2}-\\d{2}$"), True)
                       .otherwise(False))
    df = df.filter(F.col("fecha_valida") == True)
    
    # 3. Transformaciones
    print("🔄 Aplicando transformaciones...")
    
    # 3.1 Estandarizar nombres de columnas
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower().strip().replace(" ", "_"))
    
    # 3.2 CREAR columna lote a partir de lote_id (para particionar)
    df = df.withColumn("lote", F.col("lote_id"))
    
    # 3.3 Limpiar valores de partición
    df = df.withColumn("campana", F.regexp_replace(F.col("campana"), "[^a-zA-Z0-9]", "_"))
    df = df.withColumn("lote", F.regexp_replace(F.col("lote"), "[^a-zA-Z0-9]", "_"))
    
    # 3.4 Eliminar columnas temporales
    df = df.drop("rinde_num", "fecha_valida")
    
    total_final = df.count()
    print(f"📊 Registros después de validaciones: {total_final}")
    print(f"   Filtrados: {total_inicial - total_final}")
    print(f"📋 Columnas finales: {df.columns}")
    
    # 4. Escribir como Parquet particionado
    print(f"📤 Escribiendo a: {args['output_path']}")
    print(f"📂 Particionando por: campana, lote")
    df.write \
        .mode("overwrite") \
        .partitionBy("campana", "lote") \
        .parquet(args['output_path'])
    
    print("✅ Job completado exitosamente")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise
finally:
    job.commit()