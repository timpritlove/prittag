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
import mutagen.id3 as id3


COVER_TAG_PIC = os.path.join(os.path.dirname(__file__), 'Radiotux_ID3Tag.jpg')

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger = logging.getLogger("tagtool")
logger.addHandler(NullHandler())

def transfer_tags_of_file(mp3, destination):
    if source_mp3_is_ok(mp3):
        logger.info('reading tags from %s' % mp3)
        tags = read_tags_from_mp3(mp3)
        logger.info('writing tags to %s' % destination)
        file_type = get_file_type(destination)
        if file_type == 'ogg':
            write_tags_to_ogg(destination, tags)
        elif file_type == 'mp3':
            write_tags_to_mp3(destination, tags)
        else:
            raise TypeError("%s is neither a mp3 nor an ogg file" % path)


def source_mp3_is_ok(path):
    if not os.path.exists(path):
        raise TypeError("%s dosen't exist" % path)
    elif not os.path.isfile(path):
        raise TypeError("%s isn't a file" % path)
    elif os.path.splitext(path)[1] not in ['.mp3', '.MP3']:
        raise TypeError("%s isn't a mp3 file" % path)
    else:
        return True


def read_tags_from_mp3(path):
    tags = get_default_tags()
    audio = MP3(path)
    filename = os.path.split(path)[1]
    filename_tags = get_tags_from_filename(filename)
    tags.update(filename_tags)
    for tag in ['TIT2', 'TPE1', 'TALB', 'TDRC', 'TCOP', 'WXXX:']:
        if audio.has_key(tag):
            tags[tag] = unicode(audio[tag])
        else:
            if not tags.has_key(tag):
                tags[tag] = ''
    return tags

def get_default_tags():
    tags = {'TPE1' : 'RadioTux Team',
            'TALB' : 'RadioTux',
            'TCOP' : 'cc by-nc-sa de',
            'WXXX:' : 'http://radiotux.de'}
    return tags

filename_reg = re.compile('(\d{4})-\d{2}-\d{2}\.RadioTux\.(.+?)\.(.+?)(\.mp3|\.ogg)')
num_only_reg = re.compile('\d+')
def get_tags_from_filename(filename):
    tags = {}
    result = re.search(filename_reg,filename)
    if result:
        date, format, title = result.groups()
        if re.match(num_only_reg,title):
            num = title
            title = 'RadioTux %s #%s' % (format, num)
        else:
            title = 'Radiotux %s %s' % (format, title)
        tags['TIT2'] = unicode(title)
        tags['TDRC'] = unicode(date)
    else:
        logger.warn('Parsing filename "%s" failed' % (str(filename)))
    return tags


def get_file_type(path):
    ext = os.path.splitext(path)[1]
    ext = string.replace(ext, '.', '')
    ext = ext.lower()
    return ext


def write_tags_to_ogg(path, tags):
    audio = OggVorbis(path)
    for dest, source in [['TITLE', 'TIT2'], ['ARTIST', 'TPE1'],
                         ['ALBUM', 'TALB'], ['DATE', 'TDRC'],
                         ['COPYRIGHT', 'TCOP'], ['LICENSE', 'WXXX:']]:
        audio[dest] = tags[source]
    audio['coverartmime'] = 'image/jpeg'
    audio['coverartdescription'] = 'Radiotux_ID3Tag.jpg'
    audio['coverart'] = get_ogg_coverart()
    audio.save()


def get_ogg_coverart():
    f = open(COVER_TAG_PIC, 'rb')
    data = f.read()
    f.close()
    data = base64.b64encode(data)
    return data


def write_tags_to_mp3(path, tags):
    audio = MP3(path)
    audio['TIT2'] = id3.TIT2(encoding=3, text=tags['TIT2'])
    audio['TPE1'] = id3.TPE1(encoding=3, text=tags['TPE1'])
    audio['TALB'] = id3.TALB(encoding=3, text=tags['TALB'])
    audio['TDRC'] = id3.TDRC(encoding=3, text=tags['TDRC'])
    audio['TCOP'] = id3.TCOP(encoding=3, text=tags['TCOP'])
    audio['WXXX'] = id3.WXXX(encoding=3, url=tags['WXXX:'])
    image = get_mp3_coverart()
    image = id3.APIC(3, 'image/jpeg', 0, 'Radiotux_ID3Tag.jpg', image)
    audio[image.HashKey] = image
    audio.save()


def get_mp3_coverart():
    f = open(COVER_TAG_PIC, 'rb')
    data = f.read()
    f.close()
    return str(data)


if __name__ == "__main__":
    print 'Tagtool (c) Copyright 2010 Nils Mehrtens (for details see gpl.txt)'
    if len(sys.argv) != 3:
        print 'usage: %s <mp3 to read from> <ogg/mp3 to write to>' % sys.argv[0]
        sys.exit(1)
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s:%(module)s %(message)s')

        transfer_tags_of_file(sys.argv[1], sys.argv[2])
