import sys
from unittest.mock import MagicMock

# Mock awsglue modules so they can be imported locally without a Glue environment
for module in [
    "awsglue",
    "awsglue.context",
    "awsglue.job",
    "awsglue.utils",
    "pyspark",
    "pyspark.context",
    "pyspark.sql",
    "pyspark.sql.functions",
]:
    sys.modules[module] = MagicMock()
