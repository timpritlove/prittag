prittag
=======

Prittag is a modified version of a tool I build for [Radio Tux](http://blog.radiotux.de/).
I created this version to serve the request made by Tim Pritlove in the [episode 01](http://tim.geekheim.de/2011/03/26/ls001-audio-dateiformate-feeds-und-itunes/) of the podcast "Der Lautsprecher" for a tool which could help him with automating his podcasts generation, so he easily could offer multiple audio formats without more work.

It writes the following tags to multiple Ogg, MP3 or MP4 files:

- album
- album artist
- artist
- comment
- composer
- date
- disk
- genre
- lyrics
- number of disks
- number of tracks
- title
- track

Additionally it can add a albumart (cover) to them.

The name was chosen according to the amazing tool [prittorrent](https://github.com/astro/prittorrent).

Dependencies
============

- [Python 2.6](http://python.org) or higher (Not Python 3.x)
- [Mutagen](http://code.google.com/p/mutagen/)

Installation
============
Download it to a place of your choice
Install all dependencies

Usage
=====
Prittag expects a XML file and at least one audio file as arguments.
The XML file tells prittag which tags it should write into the files and is expected to look like example.xml.
By default prittag will perform a  white space stripping on every tag and every line of multi line tags.
You can enable and disable this as well globally as for every single tag by adding the option "strip-space" and setting it either to "yes" or "no".
For example:

```xml
    <?xml version="1.0" encoding="UTF-8" ?>
    <tags strip-space="no">
	<title>FooBar</title>
	<lyrics strip-space="yes">
	Foo
	Bar
	</lyrics>
    </tags>
```

Call it from the command line like this: "./prittag.py foo.xml bar.mp3 bar.oga bar.m4a"
