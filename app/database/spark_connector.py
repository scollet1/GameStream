import os
import findspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, asc
from pyspark import SparkContext, SparkConf, SQLContext


class SparkConnector:
	def __init__(self):
		findspark.init("/home/ubuntu/server/spark-2.4.5-bin-hadoop2.7")
		conf = SparkConf() \
			.setMaster("local[*]") \
			.setAppName('SparkCassandraAnalytics') \
			.set('spark.jars.packages', 'com.datastax.spark:spark-cassandra-connector_2.11:2.3.0') \
			.set('spark.cassandra.connection.host', os.environ['DB_ADDR']) \
			.set('spark.cassandra.auth.username', os.environ['DB_USER']) \
			.set('spark.cassandra.auth.password', os.environ['DB_PASS']) \
			.set('spark.executor.memory', '9g') \
			.set('spark.driver.memory','3g')
		sc = SparkContext(conf=conf)
		self.sqlContext = SQLContext(sc)

	def submit_sql(self, query):
		return self.sqlContext.sql(query).collect()

	def load_and_get_table_df(self, keys_space_name, table_name):
		table_df = self.sqlContext.read \
			.format("org.apache.spark.sql.cassandra") \
			.options(table=table_name, keyspace=keys_space_name) \
			.load()
		return table_df

if __name__=="__main__":
	sdb = SparkConnector()
	users = sdb.load_and_get_table_df("v1", "users")
	gevents = sdb.load_and_get_table_df("v1", "gameplay_events")
	pevents = sdb.load_and_get_table_df("v1", "purchase_events")

	df = gevents.crossJoin(pevents)

	df.show()

	data = {
		'game_name': 'Fallout Trilogy',
		'system_pc': True,
#		'age_bracket_from': 5
	}

	df.show()

	# join dates
	if 'datetime_from' in data:
		df = gevents.where(df.event_time > datetime(data['datetime_from']))
	if 'datetime_to' in data:
		df = gevents.where(df.event_time < datetime(data['datetime_to']))
	if 'game_name' in data:
		df = gevents.where(col('game').like(data['game_name']))

	df.show()

	# join system
	if 'system_pc' in data and 'system_ps4' in data:
		df.where(df.platform == 'PC' | df.platform == 'PS4')
	elif 'system_ps4' in data:
		df.where(df.platform == 'PC')
	elif 'system_pc' in data:
		df.where(df.platform == 'PS4')

	df.show()

	# if 'age_bracket_from' not in data:
	# 	data['age_bracket_from'] = 13
	# if 'age_bracket_to' not in data:
	# 	data['age_bracket_to'] = 75
	# df = df.join(users, (users.age > data['age_bracket_from']) & (users.age < data['age_bracket_to']) & (users.id == df.user_id))

	df.show()
