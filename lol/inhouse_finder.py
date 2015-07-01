import sys
import argparse
import riotwatcher
import json
from pprint import pprint
import os
import os.path


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


class Model(object):
	def __init__(self, args):
		self.api = None
		self.key = None
		self.homies_by_id = {}
		self.homie_names = set()
		self.custom_only = False
		self.classic_only = True
		self.threshold = 4
		self.gen_config = False
		self.monitor = args.monitor
		self.output_dir = args.output_dir
		if args.config:
			self.read_config(args.config)
		if args.key:
			self.key = args.key
		if args.summoner_list:
			self.read_summoners(args.summoner_list)
		if args.gen_config:
			self.gen_config = args.gen_config
		if not args.custom_only is None:
			self.custom_only = args.custom_only
		if not args.classic_only is None:
			self.classic_only = args.classic_only 
		if not args.threshold is None:
			self.threshold = args.threshold
		if self.key:
			self.api = riotwatcher.RiotWatcher(self.key, enforce_limits=True)
	
	def __str__(self):
		l = []
		homies_lines = ["\t\t" + line for line in pprint_to_string(self.homies(), True).split("\n")]
		names_lines = ["\t\t" + line for line in pprint_to_string(list(self.homie_names), True).split("\n")]
		l.append("Model(")
		l.append("\tkey:")
		l.append("\t\t{}".format(self.key))
		l.append("\tthreshold:")
		l.append("\t\t{}".format(self.threshold))
		l.append("\tcustom_only:")
		l.append("\t\t{}".format(self.custom_only))
		l.append("\tclassic_only:")
		l.append("\t\t{}".format(self.classic_only))
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
		if u"threshold" in obj:
			self.threshold = obj[u"threshold"]
		if u"custom_only" in obj:
			self.custom_only = obj[u"custom_only"]
		if u"classic_only" in obj:
			self.classic_only = obj[u"classic_only"]
	
	def read_summoners(self, file):
		for line in file:
			line = line.strip()
			if line:
				self.homie_names.add(line)
	
	def write_config(self, file):
		d = {}
		d[u"version"] = "0.2"
		d[u"threshold"] = self.threshold
		d[u"custom_only"] = self.custom_only
		d[u"classic_only"] = self.classic_only
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
	
	def resolve_homie_names(self):
		#Try to resolve names to IDs
		if self.homie_names:
			json = self.api.get_summoners(self.homie_names)
			if json:
				lower_homie_names = {name.lower(): name for name in self.homie_names}
				for key in json:
					homie_id = json[key][u"id"]
					homie_name = json[key][u"name"]
					homie = Homie(homie_name, homie_id)
					self.homies_by_id[homie_id] = homie
					if homie_name.lower() in lower_homie_names:
						self.homie_names.remove(lower_homie_names[homie_name.lower()])
	
	def update_homie_games(self):
		for homie in self.homies():
			response = self.api.get_recent_games(homie.id)
			if response:
				homie.recent_games = response[u"games"]
	
	def identify_inhouses(self):
		inhouses = set()
		homie_id_set = frozenset(self.homie_ids())
		for homie in self.homies():
			for game in homie.recent_games:
				is_classic = (game[u"gameMode"] == u"CLASSIC")
				is_custom = (game[u"gameType"] == u"CUSTOM_GAME")
				game_player_ids = set()
				game_player_ids.add(homie.id)
				game_id = game[u"gameId"]
				for player in game[u"fellowPlayers"]:
					game_player_ids.add(player[u'summonerId'])
				if len(game_player_ids & homie_id_set) >= self.threshold:
					if self.custom_only and not is_custom:
						continue
					if self.classic_only and not is_classic:
						continue
					inhouses.add(game[u"gameId"])
		return inhouses
		

def make_output_dir(path):
	# technically a race here.
	if os.path.exists(path):
		return os.path.isdir(path) and os.access(path, os.W_OK)
	else:
		try:
			os.mkdir(path)
		except:
			return False
		return True


def main(model):
	#set up the output directory
	if model.output_dir:
		if not make_output_dir(model.output_dir):
			print "Could not create/access output directory"
			sys.exit(1)

	#if asked, generate config and exit
	if model.gen_config:
		model.write_config(sys.stdout)
		sys.exit(0)
	
	model.resolve_homie_names()
	model.update_homie_games()
	inhouses = model.identify_inhouses()
	
	print "Games played with bros"
	pprint(inhouses)



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--gen-config", action="store_true", help="Generate a config file for later use with --config. The file is written to stdout. This file contains your key, so keep it safe.")
	parser.add_argument("--monitor", action="store_true", help="Periodically check for games and emit output as new games are detected.")
	parser.add_argument("--output-dir", help="Directory to save game data into.")
	config_group = parser.add_argument_group("Configuration options", description="Arguments can be written to a configuration file using --gen-config and reused later with --config. Options supplied on the command line take precedence over those supplied in the config file.")
	game_modes_group = config_group.add_mutually_exclusive_group()
	game_modes_group.add_argument("--all-game-modes", dest="classic_only", action="store_false", help="Include games from all game modes")
	game_modes_group.add_argument("--classic-only", action="store_true", default=None, help="Include games from the classic mode only (default)")
	config_group.add_argument("--config", "-c",  type=argparse.FileType('r'), help="The config file to use. Arguments provided on the command line override options in the config file.")
	custom_group = config_group.add_mutually_exclusive_group()
	custom_group.add_argument("--custom-games-only", dest="custom_only", action="store_true", default=None, help="Only include custom games")
	custom_group.add_argument("--all-games", dest="custom_only", action="store_false", help="Include data from all games (default)")
	config_group.add_argument("--key", "-k", help="The Riot API key to use.")
	config_group.add_argument("--summoner-list", '-l', type=argparse.FileType('r'), help="A file containing the summoner names, one per line.")
	config_group.add_argument("--threshold", "-t", type=int, default=None, help="Threshold for how many games it takes to be an inhouse game")
	args = parser.parse_args()
	model = Model(args)
	if not model.key:
		parser.error("A key is required")
	if model.threshold < 0 or model.threshold > 10:
		parser.error("Threshold must be 0 <= threshold <= 10")
	main(model) 

