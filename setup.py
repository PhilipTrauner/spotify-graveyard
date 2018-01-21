from setuptools import setup, find_packages

long_description = """.. image:: https://user-images.githubusercontent.com/9287847/32694654-e3b2321e-c745-11e7-9e27-5eca280eddff.png
 :height: 200px

spotify-graveyard
=================

|Python version support: 3.x (x > 4| |License: MIT|

Bury the undead tracks in your inbox playlist once and for all!


.. |Python version support: 3.x (x > 4| image:: https://img.shields.io/badge/python-3.x%20(x%20%3E%204)-brightgreen.svg
.. |License: MIT| image:: https://img.shields.io/badge/license-MIT-blue.svg
"""

setup(
	name="spotify-graveyard",
	version="1.0.1",
	description="Bury the undead tracks in your Inbox playlist once and for all!",
	long_description=long_description,
	url="https://github.com/PhilipTrauner/spotify-graveyard",
	author="Philip Trauner",
	author_email="philip.trauner@arztpraxis.io",
	license="MIT",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3.6",
	],
	keywords="spotify ingest",
	packages=find_packages(),
	install_requires=[
		"spotipy==2.4.4",
		"meh==1.2.1",
		"appdirs==1.4.3",
		"click==6.7",
		"colorama==0.3.9",
		"py-getch==1.0.1",
		"bottle==0.12.13",
		"python-dateutil==2.6.1"
	],
	entry_points={
		"console_scripts": [
			"graveyard=spotify_graveyard:cli",
		],
	},
)
