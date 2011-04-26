#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#  prittag - a tool for tagging mp3, ogg and aac files                      #
#                                                                           #
#  Copyright (c) 2010 Nils Mehrtens                                         #
#                                                                           #
#  prittag is free software; you can redistribute it and/or modify it       #
#  under the terms of the GNU General Public License                        #
#  as published by the Free Software Foundation;                            #
#  either version 3 of the License, or (at your option) any later version.  #
#  prittag is distributed in the hope that it will be useful, but           #
#  WITHOUT ANY WARRANTY; without even the implied warranty of               #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                     #
#  See the GNU General Public License for more details.                     #
#                                                                           #
#  You should have received a copy of the GNU General Public License        #
#  along with this program; if not, see <http://www.gnu.org/licenses/>.     #
#############################################################################

import sys
import os
import base64
import string
import re
from xml.etree import ElementTree

from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover
import mutagen.id3 as id3

def parse_xml(path):
    tags = {}
    with open(path, 'r') as f:
        xml = ElementTree.XML(f.read())
    for child in xml.getchildren():
        key = str(child.tag)
        value = unicode(child.text)
        tags[key] = value
    return tags

def tag_file(path, tags):
    file_type = get_file_type(path)
    if file_type in ['ogg', 'oga']:
        write_tags_to_ogg(path, tags)
    elif file_type == 'mp3':
        write_tags_to_mp3(path, tags)
    elif file_type in ['mp4', 'm4a', 'aac']:
        write_tags_to_mp4(path, tags)
    else:
        raise TypeError("%s is neither a mp3 nor an ogg nor a mp4 file" % path)

def get_file_type(path):
    ext = os.path.splitext(path)[1]
    ext = string.replace(ext, '.', '')
    ext = ext.lower()
    return ext

def write_tags_to_ogg(path, tags):
    audio = OggVorbis(path)
    for dest, source in [['TITLE', 'title'], ['COMPOSER', 'compser'],
                         ['ALBUM', 'ambum'], ['DATE', 'date'],
                         ['ARTIST', 'artist'], ['GENRE', 'genre']]:
        if source in tags:
            audio[dest] = tags[source]
    if 'COVER' in tags:
        audio['coverartmime'] = 'image/jpeg'
        audio['coverartdescription'] = 'Cover'
        audio['coverart'] = get_ogg_coverart(tags['COVER'])
        audio.save()


def get_ogg_coverart(path):
    with open(path, 'rb') as f:
        data = f.read()
    data = base64.b64encode(data)
    return data


def write_tags_to_mp3(path, tags):
    audio = MP3(path)
    for i, tag in [['title', 'TIT2'], ['artist', 'TPE1'], ['album', 'TALB'],
                   ['date', 'TDRC'], ['composer', 'TCOM'], ['genre', 'TCON'],
                   ['lyrics', 'USLT']]:
        if i in tags:
            if tag == 'USLT':
                tag = id3.Frames[tag](encoding=3, text=tags[i], desc='', lang='eng')
                audio[tag.HashKey] = tag
            else:
                audio[tag] = id3.Frames[tag](encoding=3, text=tags[i])
    if 'cover' in tags:
        image = get_mp3_coverart(tags['cover'])
        image = id3.APIC(3, 'image/jpeg', 0, 'Cover', image)
        audio[image.HashKey] = image
    audio.save()


def get_mp3_coverart(path):
    with open(path, 'rb') as f:
        data = f.read()
    return str(data)

def write_tags_to_mp4(path, tags):
    audio = MP4(path)
    for dest, source in [['\xa9nam', 'title'], ['\xa9wrt', 'composer'],
                         ['\xa9alb', 'album'], ['\xa9day','date'],
                         ['\xa9ART', 'artist'], ['\xa9gen', 'genre'],
                         ['\xa9lyr', 'lyrics']]:
        if source in tags:
            audio[dest] = [tags[source]]
    if 'cover' in tags:
        audio['covr'] = [get_mp4_coverart(tags['cover'])]
    audio.save()

def get_mp4_coverart(path):
    with open(path, 'rb') as f:
        data = f.read()
    cover = MP4Cover(data)
    return cover

if __name__ == "__main__":
    print '''prittag  Copyright (C) 2011 Nils Mehrtens
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; see http://www.gnu.org/licenses/gpl.html for details.
'''
    if len(sys.argv) < 3:
        print 'usage: %s <xml file with tags> <file to tag> [<file to tag> ...]' % sys.argv[0]
        sys.exit(1)
    else:
        args = sys.argv[1:]
        for path in args:
            if not os.path.exists(path):
                print "%s doesn't exist." % path
                sys.exit(1)
            elif not os.path.isfile(path):
                print "%s is not a file." % path
                sys.exit(1)
        config = args[0]
        files = args[1:]
        tags = parse_xml(config)
        for file in files:
            print "Tagging %s ..." % file
            tag_file(file, tags)
