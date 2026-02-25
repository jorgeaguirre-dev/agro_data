"""
AWS Glue Job para procesar datos de rinde de lotes
Lee CSV desde landing, valida y escribe Parquet en curated
"""
import sys
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Importar módulos internos
sys.path.append('/tmp')
from utils.validators import validate_yield_range, validate_not_null, validate_date_consistency
from utils.transformers import standardize_schema, add_partition_columns

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Leer datos
df = spark.read.option("header", "true").csv(args['input_path'])

# Validaciones
df = validate_yield_range(df, "rinde", 0, 20000)
df = validate_not_null(df, ["lote_id", "campana"])
df = validate_date_consistency(df, "fecha_cosecha", "yyyy-MM-dd")

# Transformaciones
df = standardize_schema(df)
df = add_partition_columns(df, "campana", "lote")

# Escribir en formato Parquet particionado
df.write \
    .mode("overwrite") \
    .partitionBy("campana", "lote") \
    .parquet(args['output_path'])

job.commit()
