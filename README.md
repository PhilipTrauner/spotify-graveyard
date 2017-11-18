<p align="center">
	<img src="https://user-images.githubusercontent.com/9287847/32694654-e3b2321e-c745-11e7-9e27-5eca280eddff.png" height="300">
</p>
<p align="center">
	<strong>spotify-graveyard</strong>
</p>

![Python version support: 3.x \(x > 4\)](https://img.shields.io/badge/python-3.x%20(x%20%3E%204)-brightgreen.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

> Bury the undead tracks in your inbox playlist once and for all!

Do you often add tracks to your inbox playlist that just sit there for months or even years?  
Great, because that's the exact problem that **spotify-graveyard** is trying to solve.

Introducing the **graveyard playlist**:  
A final resting place for songs that have overstayed their welcome in your inbox playlist. If a track stays in your inbox playlist for too long it is moved to this cemetery by **spotify-graveyard**.

**spotify-graveyard** uses the *Implicit Grant* Spotify authentication flow. This way your playlists can be modified locally without ever touching the server of a third party (other than Spotify, of course). Your guilty music pleasures are sure to remain private (yes, even those excessive repeats of [1989 by Taylor Swift](https://open.spotify.com/album/6w36pmMA5bxECalu5rxQAw) 😉)!


### Usage
<img src="https://user-images.githubusercontent.com/9287847/32982750-9c8b80cc-cc89-11e7-92aa-06d3d9768287.gif" width="900px">

```bash
# Recycle the fossilized songs in you inbox playlist
graveyard run
```

### Installation
**pip**  
```bash
pip3 install spotify-graveyard
```

**Manual**  
```bash
git clone https://github.com/PhilipTrauner/spotify-graveyard
cd spotify-graveyard
python3 setup.py install
```

### Requirements
**spotify-graveyard** requires a UNIX-like operating to run properly (`Linux`, `FreeBSD`, `OpenBSD`, `macOS`).  
`Windows` is not supported directly, but the Linux subsystem should work.  

**spotify-graveyard** can not be run headless because it has to open a browser window to receive an authentication token from Spotify.


### FAQ
* Can't I do this in the Spotify client without too much effort anyway?  
	Yes you can.

* Then why should I use this at all?  
	It has a very pretty and ridiculously over-engineered command line interface. Isn't that normally enough to attract GitHub stars?

* Aren't emojis normally necessary to farm stars?  
	Yes they are. That's why **spotify-graveyard** has tons of them. 🎩🗑📝❓🧟‍👤📤📥

* Sign me up!  
	Though so. 😈
