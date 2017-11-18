from sys import stdout
from shutil import get_terminal_size

from getch import getch, pause

from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

ENTER_ORD = 13
BACKSPACE_ORD = 127
ESC_ORD = 27

def get_terminal_width():
	return get_terminal_size().columns


def startswith(text, lst):
	for item in lst:
		if item.lower().startswith(text):
			return item
	return None


def int_input(term):
	key = " "
	text = ""
	correct_key = False
	needs_redraw = True

	def redraw():
		stdout.write("\r%s" % (" " * get_terminal_width()))
		stdout.flush()

		stdout.write("\r%s %s" % (
			term, text))		

	redraw()

	while ord(key) != ENTER_ORD or not valid_input:
		key = getch()
		ord_key = ord(key)

		if key.isnumeric():
			text += key
			needs_redraw = True

		elif ord_key == BACKSPACE_ORD:
			if len(text) > 0:
				text = text[:-1]
				needs_redraw = True

		elif ord_key == ESC_ORD:
			raise KeyboardInterrupt


		if needs_redraw:
			redraw()

			needs_redraw = False
	
		if len(text) > 0:
			valid_input = True
		else:
			valid_input = False

	print()

	return int(text)

def yes_or_no(term):
	key = " "
	text = ""
	correct_key = False
	needs_redraw = True

	def redraw():
		stdout.write("\r%s" % (" " * get_terminal_width()))
		stdout.flush()

		if text.lower() == "y":
			text_color = Fore.GREEN
		elif text.lower() == "n":
			text_color = Fore.RED
		else:
			text_color = Fore.WHITE

		stdout.write("\r%s [y/n] %s%s%s" % (
			term, text_color, text,
			Style.RESET_ALL))		

	redraw()

	while not correct_key:
		key = getch()
		ord_key = ord(key)

		if key.isalpha() and key.lower() in ("y", "n"):
			text += key
			needs_redraw = True
			correct_key = True

		elif ord_key == ESC_ORD:
			raise KeyboardInterrupt


		if needs_redraw:
			redraw()

			needs_redraw = False
	
	print()

	return True if text.lower() == "y" else False




def autocomplete_match(term, dictionary):
	keys = list(dictionary.keys())	

	key = " "
	text = ""
	autocomplete_match = ""
	match_found = False
	needs_redraw = True

	def redraw():
		stdout.write("\r%s" % (" " * get_terminal_width()))
		stdout.flush()

		stdout.write("\r%s %s%s%s%s" % (
			term, text, Style.DIM, autocomplete_match[len(text):],
			Style.RESET_ALL))		

	redraw()

	while ord(key) != ENTER_ORD or not match_found:
		key = getch()
		ord_key = ord(key)

		if key.isalpha():
			text += key
			needs_redraw = True

		elif ord_key == BACKSPACE_ORD:
			if len(text) > 0:
				text = text[:-1]
				needs_redraw = True

		# Allow some additional characters that are not alpha
		elif 32 <= ord_key <= 64 or 91 <= ord_key <= 96 or \
			123 <= ord_key <= 126:
			
			text += key
			needs_redraw = True

		elif ord_key == ESC_ORD:
			raise KeyboardInterrupt

		if len(text) > 0 and text.strip(" ") != "":
			autocomplete_match = startswith(text, keys)
			if autocomplete_match is None:
				autocomplete_match = text
				match_found = False
			else:
				match_found = True
		else:
			autocomplete_match = text
			match_found = False

		if needs_redraw:
			redraw()

			needs_redraw = False

	stdout.write("\r%s %s" % (term, autocomplete_match))	
	stdout.flush()
	print()

	return dictionary[autocomplete_match]