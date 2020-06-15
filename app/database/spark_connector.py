import os
from pyspark.sql import SQLContext
from pyspark import SparkContext, SparkConf

os.environ['PYSPARK_SUBMIT_ARGS'] = f"""
	--packages com.datastax.spark:spark-cassandra-connector_2.11:2.3.0
	--conf
		spark.cassandra.connection.host={os.environ['DB_ADDR']}
	pyspark-shell
	"""

class SparkConnector:
	def __init__(self):
		self.sc = SparkContext("local", "spark_analytics")
		self.sqlContext = SQLContext(sc)

	def load_and_get_table_df(self, keys_space_name, table_name):
		table_df = sqlContext.read\
			.format("org.apache.spark.sql.cassandra")\
			.options(table=table_name, keyspace=keys_space_name)\
			.load()
		return table_df