#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#  tagtool - a tool for tagging mp3, ogg and aac files                      #
#                                                                           #
#  Copyright (c) 2010 Nils Mehrtens                                         #
#                                                                           #
#  tagtool is free software; you can redistribute it and/or modify it       #
#  under the terms of the GNU General Public License                        #
#  as published by the Free Software Foundation;                            #
#  either version 3 of the License, or (at your option) any later version.  #
#  tagtool is distributed in the hope that it will be useful, but           #
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
import logging
import argparse

from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover
import mutagen.id3 as id3

CMD_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger = logging.getLogger("tagtool")
logger.addHandler(NullHandler())

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
    for dest, source in [['TITLE', 'TIT2'], ['COMPOSER', 'TCOM'],
                         ['ALBUM', 'TALB'], ['DATE', 'TDRC'],
                         ['ARTIST', 'TPE1'], ['GENRE', 'TCON']]:
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
    for i, tag in [['TIT2', id3.TIT2], ['TPE1', id3.TPE1], ['TALB', id3.TALB],
                   ['TDRC', id3.TDRC], ['TCOM', id3.TCOM], ['TCON', id3.TCON]]:
        if i in tags:

            audio[i] = tag(encoding=3, text=tags[i])
    if 'COVER' in tags:
        image = get_mp3_coverart(tags['COVER'])
        image = id3.APIC(3, 'image/jpeg', 0, 'Cover', image)
        audio[image.HashKey] = image
    audio.save()


def get_mp3_coverart(path):
    with open(path, 'rb') as f:
        data = f.read()
    return str(data)


if __name__ == "__main__":
    print '''Tagtool  Copyright (C) 2011 Nils Mehrtens
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; see http://www.gnu.org/licenses/gpl.html for details.
'''
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(module)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs = '+', help = 'A file that shall be tagged (one of mp3, ogg, mp4)',
                       metavar = 'file')
    parser.add_argument('-t', '--title')
    parser.add_argument('-al', '--album')
    parser.add_argument('-ar', '--artist')
    parser.add_argument('-co', '--composer')
    parser.add_argument('-d', '--date')
    parser.add_argument('-g', '--genre')
    parser.add_argument('-cv', '--cover', help = 'JPG file containing the cover')
    args =  parser.parse_args()

    tags = {}
    for arg, dest in [[args.title, 'TIT2'], [args.album, 'TALB'], [args.artist,'TPE1'],
             [args.composer, 'TCOM'], [args.date, 'TDRC'], [args.genre, 'TCON'],
             [args.cover, 'COVER']]:
        if arg != None:
            tags[dest] = arg.decode(CMD_ENCODING)
    for file in args.files:
        logging.info('Tagging %s' % file)
        tag_file(file, tags)
