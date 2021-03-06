import csv
import uuid
import psutil
from datetime import datetime, timedelta
from random import gauss, seed, randint, uniform, choice, random

GAME_NAMES_PATH = "./data/vgsales.csv"

class DataGenerator():
	def __init__(self, num_users=6000000):
		self.supported_platform = {
			"PC": self.generate_pc_stats(),
			"PS4": self.generate_ps4_stats()
		}
		self.uids = self.generate_uids(num_users)
		self.games = self.read_games(GAME_NAMES_PATH)

	def generate_pc_stats(self):
		return {
			"CPU": psutil.cpu_percent(interval=1) * 8 * random(),
			"RAM": psutil.virtual_memory()[2] * random()
		}

	def generate_ps4_stats(self):
		return {
			"CPU": psutil.cpu_percent(interval=1) * 10 * random(),
			"RAM": psutil.virtual_memory()[2] * random()
		}

	def get_users(self):
		return self.uids

	def read_games(self, fname):
		games = []
		with open(fname) as csv_file:
			reader = csv.reader(csv_file)
			for row in reader:
				if row[2] in self.supported_platform:
					games.append({"game":row[1], "platform":row[2]})
		return games

	def generate_uids(self, num_users):
		users = [{
			"UID": str(uuid.uuid4()),
			"Age": self.generate_age(),
			"StartedPlaying": None
		} for i in range(num_users)]

		return users

	def get_game(self):
		return choice(self.games)

	def get_uid(self):
		user = choice(self.uids)
		if user["StartedPlaying"]:
			delta = datetime.now() - user["StartedPlaying"]
			r = gauss(0.5, 0.4)
			if (delta.seconds * delta.days > 30 * 60 and r < 0.8) or r < 0.2:
				user["StartedPlaying"] = None
		else:
			user["StartedPlaying"] = datetime.now()
		return user["UID"]

	def generate_age(self):
		return int(gauss(0.75, 0.15) * uniform(22, 70))

	def generate_platform_stats(self, platform):
		return str(self.supported_platform[platform])

	def create_purchase_event(self):
		game = self.get_game()
		platform = game["platform"]
		platform_stats = self.generate_platform_stats(platform)

		return {
			"Game": game["game"],
			"Platform": platform,
			"Item": "none",
			"Price": uniform(0.5, 60.0)
		}

	def create_gameplay_event(self):
		game = self.get_game()
		platform = game["platform"]
		platform_stats = self.generate_platform_stats(platform)

		return {
			"Game": game["game"],
			"Platform": platform,
			"PlatformStats": platform_stats,
		}

	def create_event(self):
		if random() < 0.15:
			return "purchase_event", self.create_purchase_event()
		return "gameplay_event", self.create_gameplay_event()

	def generate_data(self):
		event_type, event = self.create_event()
		uid = self.get_uid()
		time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

		return {
			"event_type": event_type,
			"UID": uid,
			"Time": time,
			"event_body": event
		}

if __name__=="__main__":
	seed()
	import json
	from pprint import pprint
	generator = DataGenerator(100)
	while True:
		data = generator.generate_data()
		enc = json.dumps(data).encode('utf-8')
		pprint(enc)
		pprint(json.loads(enc.decode('utf-8')))