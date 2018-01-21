from os import makedirs
from os.path import isfile, isdir, abspath
from shutil import rmtree
from time import time
from sys import executable
from math import ceil

from .auth import auth
from .term_input import autocomplete_match, yes_or_no, int_input

from click import command, group, pass_context

from meh import Config, Option, ExceptionInConfigError

from appdirs import user_config_dir

import spotipy

import dateutil.parser as dp
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

# Library constants
# click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# spotify-graveyard constants
CONFIG_DIR = user_config_dir("spotify-graveyard")
CONFIG_LOCATION = CONFIG_DIR + "/config.cfg"

PLAYLIST_MAX_LIMIT = 50
PLAYLIST_TRACKS_MAX_LIMIT = 100

def is_int(obj):
	return type(obj) is int

def is_float(obj):
	return type(obj) is float

config = Config()
config.add(Option("access_token", None))
config.add(Option("valid_until", 0.0, validator=is_float))
config.add(Option("inbox_playlist_id", None))
config.add(Option("graveyard_playlist_id", None))
config.add(Option("livespan", 7, validator=is_int))


def can_edit_playlist(playlist, owner):
	return playlist["owner"]["id"] == owner


def load_config():
	global config

	cfg = None

	try:
		cfg = config.load(CONFIG_LOCATION)
	except (IOError, ExceptionInConfigError):
		pass

	return cfg


@group(context_settings=CONTEXT_SETTINGS)
def cli():
	"""
	spotify-graveyard:

	Bury the undead tracks in your Inbox playlist once and for all!
	"""
	pass


@command()
def wizard():
	"""🎩"""
	global config
	cfg = load_config()

	if cfg != None and cfg.valid_until > time():
		print("📥  Valid Spotify token cached!")

		access_token = cfg.access_token
		valid_until = cfg.valid_until

	else:
		print("%s📤%s  Requesting token from Spotify..." % (
			Fore.BLUE, Style.RESET_ALL))		

		access_token, expires_in = auth()
		valid_until = (time() + expires_in) - 5

		print("%s📥%s  Token acquired!" % (Fore.GREEN, 
			Style.RESET_ALL))

	sp = spotipy.Spotify(auth=access_token)

	username = sp.me()["id"]

	print("👤  Spotify username: %s%s%s" % (
		Fore.GREEN, username, Style.RESET_ALL))

	playlists = []
	playlists_count = sp.user_playlists(username, limit=0)["total"]


	offset = 0
	for _ in range(ceil(playlists_count / PLAYLIST_MAX_LIMIT)):
		playlists += sp.user_playlists(username, 
			limit=PLAYLIST_MAX_LIMIT, offset=offset)["items"]

		offset += PLAYLIST_MAX_LIMIT


	indexed_playlists = {}

	index = 0
	for playlist in playlists:
		indexed_playlists["%s [%s]" % (
			playlist["name"], playlist["id"])] = index
		index += 1

	inbox_playlist = None
	graveyard_playlist = None

	def choose_playlist(type_):
		playlist_usable = False
		while not playlist_usable:
			playlist_index = autocomplete_match("%s➡%s  %s playlist:" % (
					Fore.BLUE, Style.RESET_ALL, type_), indexed_playlists)

			playlist = playlists[playlist_index]

			if can_edit_playlist(playlist, username):
				playlist_usable = True
			else:
				print("%s⚠%s  Playlist can not be edited, please choose a "
					"different one." % (Fore.YELLOW, Style.RESET_ALL))

		return playlist

	while inbox_playlist == graveyard_playlist:
		inbox_playlist = choose_playlist("Inbox")
		graveyard_playlist = choose_playlist("Graveyard")

		if inbox_playlist == graveyard_playlist:
			print("%s⚠%s  Two different playlists are required." % (
				Fore.YELLOW, Style.RESET_ALL))

	if not isdir(CONFIG_DIR):
		makedirs(CONFIG_DIR)

	

	config.dump(CONFIG_LOCATION)
	cfg = config.load(CONFIG_LOCATION)

	cfg.access_token = access_token
	cfg.valid_until = valid_until
	cfg.inbox_playlist_id = inbox_playlist["id"]
	cfg.graveyard_playlist_id = graveyard_playlist["id"]
	cfg.livespan = int_input("%s➡%s  For how many days should songs "
		"stay the inbox playlist?" % (
			Fore.BLUE, Style.RESET_ALL))



@command()
@pass_context
def run(ctx):
	"""🗡"""
	cfg = load_config()

	if cfg == None:
		if yes_or_no("❓  Config file does not exist, run creation wizard?"):
			ctx.invoke(wizard)

			cfg = load_config()
		else:
			print("%s⚠%s  Config file necessary to continue." % (
				Fore.YELLOW, Style.RESET_ALL))
			exit(1)


	if cfg.valid_until > time():
		print("📥  Valid Spotify token cached!")

		access_token = cfg.access_token
	else:
		print("%s📤%s  Requesting token from Spotify..." % (
			Fore.BLUE, Style.RESET_ALL))			

		access_token, _ = auth()

		print("%s📥%s  Token acquired!" % (Fore.GREEN, 
			Style.RESET_ALL))

	print("🧟‍  Burying undead songs...")

	sp = spotipy.Spotify(auth=access_token)		
	username = sp.me()["id"]

	inbox_track_count = sp.user_playlist_tracks(username, 
		cfg.inbox_playlist_id, fields="total")["total"]

	inbox_tracks = []

	offset = 0
	for _ in range(ceil(inbox_track_count / PLAYLIST_MAX_LIMIT)):
		inbox_tracks += sp.user_playlist_tracks(username, 
			cfg.inbox_playlist_id, limit=PLAYLIST_MAX_LIMIT, 
			offset=offset, 
			fields="items(added_at,track(name,id))")["items"]

		offset += PLAYLIST_TRACKS_MAX_LIMIT	

	now = datetime.now(timezone.utc)

	zombie_tracks = []

	for track in inbox_tracks:
		if relativedelta(now, dp.parse(track["added_at"])).days >= \
			cfg.livespan and track["track"]["id"] != None:

			zombie_tracks.append(track["track"])

	zombie_track_ids = []


	for track in zombie_tracks:
		zombie_track_ids.append(track["id"])

	zombie_track_id_count = len(zombie_track_ids)

	if zombie_track_id_count > 0:

		sp.user_playlist_remove_all_occurrences_of_tracks(username, 
			cfg.inbox_playlist_id, zombie_track_ids)


		sp.user_playlist_add_tracks(username, cfg.graveyard_playlist_id, 
			zombie_track_ids)

	print("✅  Moved %i song%s to graveyard." % (zombie_track_id_count, 
		"" if zombie_track_id_count == 1 else "s"))


@command()
def status():
	"""❓"""
	if not isfile(CONFIG_LOCATION):
		print("%s⚠%s  Config does not exist yet." % (
			Fore.YELLOW, Style.RESET_ALL))
		print("Run %s%sgraveyard wizard%s to create a config file." % (
			Back.WHITE, Fore.BLACK, Style.RESET_ALL))
		exit(1)
	else:
		print("✅  Ready to harvest!")
		exit(0)


@command()
def config_location():
	"""📝"""
	if not isfile(CONFIG_LOCATION):
		print("%s⚠%s  Config does not exist yet." % (
			Fore.YELLOW, Style.RESET_ALL))
		print("Run %s%sgraveyard wizard%s to create a config file." % (
			Back.WHITE, Fore.BLACK, Style.RESET_ALL))
		exit(1)
	else:
		print(CONFIG_LOCATION)
		exit(0)




@command()
def uninstall():
	"""🗑"""
	if yes_or_no("❓  Remove config directory?"):
		if isdir(CONFIG_DIR):
			rmtree(CONFIG_DIR)
			print("❗  Config directory removed.")
		
		print("Run %s%spip3 remove spotify-graveyard%s to uninstall completely." % (
			Back.WHITE, Fore.BLACK, Style.RESET_ALL))



cli.add_command(run)
cli.add_command(status)
cli.add_command(config_location)
cli.add_command(uninstall)
cli.add_command(wizard)


if __name__ == "__main__":
	cli()