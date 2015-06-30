import sys
import argparse
import riotwatcher
import json
from pprint import pprint

class Homie(object):
	def __init__(self, name, id):
		self.name  = name
		self.id = id
		self.recent_games = []
	
	def __repr__(self):
		return "Homie(name={name}, id={id})".format(name=self.name, id=self.id)

	def json_dict(self):
		d = {}
		d[u"name"] = self.name
		d[u"id"] = self.id
		return d


def pprint_to_string(obj, strip=False):
	from cStringIO import StringIO
	stringf = StringIO()
	pprint(obj, stream=stringf)
	stringf.seek(0)
	buf = stringf.read()
	stringf.close()
	if strip:
		buf = buf.strip()
	return buf


class Config(object):
	def __init__(self, args):
		self.key = None
		self.homies_by_id = {}
		self.homie_names = set()
		self.gen_config = False
		self.custom_only = False
		self.classic_only = True
		self.threshold = args.threshold
		if args.config:
			self.read_config(args.config)
		if args.key:
			self.key = args.key
		if args.summoner_list:
			self.read_summoners(args.summoner_list)
		if args.gen_config:
			self.gen_config = args.gen_config
		if args.custom_only:
			self.custom_only = args.custom_only
		if args.all_game_modes:
			self.classic_only = False
	
	def __str__(self):
		l = []
		homies_lines = ["\t\t" + line for line in pprint_to_string(self.homies(), True).split("\n")]
		names_lines = ["\t\t" + line for line in pprint_to_string(list(self.homie_names), True).split("\n")]
		l.append("Config(")
		l.append("\tkey:")
		l.append("\t\t{}".format(self.key))
		l.append("\thomies:")
		l.extend(homies_lines)
		l.append("\tnames:")
		l.extend(names_lines)
		l.append(")")
		return "\n".join(l)
	
	def read_config(self, file):
		version = "unknown"
		obj = json.load(file)
		if u"version" in obj:
			version = obj[u"version"]
		if u"key" in obj:
			self.key = obj[u"key"]
		if u"homies" in obj:
			homies = obj[u"homies"]
			for homie_dict in homies:
				name = homie_dict[u"name"]
				id = homie_dict[u"id"]
				homie = Homie(name, id)
				self.homies_by_id[id] = homie
		if u"names" in obj:
			self.homie_names = set(obj[u"names"])
	
	def read_summoners(self, file):
		for line in file:
			line = line.strip()
			if line:
				self.homie_names.add(line)
	
	def write_config(self, file):
		d = {}
		d[u"version"] = "0.1"
		if self.key:
			d[u"key"] = self.key
		if self.homies():
			d[u"homies"] = [homie.json_dict() for homie in self.homies()]
		if self.homie_names:
			d[u"names"] = list(self.homie_names)
		json.dump(d, file, sort_keys=True, indent=4, separators=(',', ': '))
		
	def homies(self):
		return self.homies_by_id.values()
	
	def homie_ids(self):
		return self.homies_by_id.keys()


def main(config):
	riot = riotwatcher.RiotWatcher(config.key, enforce_limits=True)
	if config.homie_names:
		response = riot.get_summoners(config.homie_names)
		if response:
			for key in response:
				homie_id = response[key][u"id"]
				homie_name = response[key][u"name"]
				homie = Homie(homie_name, homie_id)
				config.homies_by_id[homie_id] = homie
			config.homie_names = set()
	if config.gen_config:
		config.write_config(sys.stdout)
		return 0
	for homie in config.homies():
		response = riot.get_recent_games(homie.id)
		if response:
			homie.recent_games = response[u"games"]
	
	inhouses = set()

	homie_id_set = frozenset(config.homie_ids())

	for homie in config.homies():
		for game in homie.recent_games:
			is_classic = (game[u"gameMode"] == u"CLASSIC")
			is_custom = (game[u"gameType"] == u"CUSTOM_GAME")
			fellow_player_ids = set()
			game_id = game[u"gameId"]
			for player in game[u"fellowPlayers"]:
				fellow_player_ids.add(player[u'summonerId'])
			if len(fellow_player_ids & homie_id_set) >= config.threshold:
				if config.custom_only and not is_custom:
					continue
				inhouses.add(game[u"gameId"])
				
	print "Games played with bros"
	pprint(inhouses)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--threshold", "-t", type=int, default=5, help="Threshold for how many games it takes to be an inhouse game")
	parser.add_argument("--custom-only", action="store_true", help="Only include custom games")
	parser.add_argument("--all-game-modes", action="store_true", help="Include games from all game modes (defaults to classic only)")
	config_group = parser.add_argument_group("Configuration options")
	config_group.add_argument("--key", "-k", help="The Riot API key to use.")
	config_group.add_argument("--summoner-list", '-l', type=argparse.FileType('r'), help="A file containing the summoner names, one per line.")
	config_group.add_argument("--config", "-c",  type=argparse.FileType('r'), help="The config file to use.")
	config_group.add_argument("--gen-config", action="store_true", help="Generate a config file for later use with --config and write it to stdout. This file contains your key so keep it safe.")
	args = parser.parse_args()
	config = Config(args)
	if not config.key:
		parser.error("A key is required")
	main(config)

