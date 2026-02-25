"""
AWS Glue Job para procesar datos climáticos diarios
"""
import sys
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

sys.path.append('/tmp')
from utils.validators import validate_not_null, validate_date_consistency
from utils.transformers import standardize_schema, add_partition_columns

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Leer datos
df = spark.read.option("header", "true").csv(args['input_path'])

# Validaciones específicas para clima
df = validate_not_null(df, ["lote_id", "fecha", "temperatura", "precipitacion"])
df = validate_date_consistency(df, "fecha", "yyyy-MM-dd")
df = df.filter("temperatura BETWEEN -20 AND 50")
df = df.filter("precipitacion BETWEEN 0 AND 500")

# Transformaciones
df = standardize_schema(df)
df = add_partition_columns(df, "campana", "lote")

# Escribir
df.write \
    .mode("overwrite") \
    .partitionBy("campana", "lote") \
    .parquet(args['output_path'])

job.commit()
