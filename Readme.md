prittag
=======

Prittag is a modified version of a tool I build for [Radio Tux](http://blog.radiotux.de/).
I created this version to serve the request made by Tim Pritlove in the [episode 01](http://tim.geekheim.de/2011/03/26/ls001-audio-dateiformate-feeds-und-itunes/) of the podcast "Der Lautsprecher" for a tool which could help him with automating his podcasts generation, so he easily could offer multiple audio formats without more work.

It writes the following tags to multiple Ogg, MP3 or MP4 files:

- album
- artist
- composer
- date
- genre
- title

Additionally it can add a albumart (cover) to them.

The name was chosen according to the amazing tool [prittorrent](https://github.com/astro/prittorrent).

Dependencies
============

- [Python 2.7](http://python.org) or [Python 2.6](http://python.org) with [argparse](http://code.google.com/p/argparse/) module
- [Mutagen](http://code.google.com/p/mutagen/)

Installation
============
- Download it to a place of your choice
- Call it from the command line (try ./prittag.py --help for a overview)
