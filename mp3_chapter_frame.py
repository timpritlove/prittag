# -*- coding: utf-8 -*-
"""
This module offers an additional ID3 Frame not implementet in mutagen,
which is called CHAP and provides the possibility to embed chapter marks in a mp3
"""
from struct import unpack, pack

from mutagen.id3 import IntegerSpec, Frame, BitPaddedInt, ID3

class CHAP(Frame):
    """
    The chapter frame specified in http://www.id3.org/id3v2-chapters-1.0
    """
    def __init__(self, start, stop, start_offset, stop_offset, embeded_frames):
        super(CHAP, self).__init__()
        self.embeded_frames = embeded_frames
        self.start = start
        self.stop = stop
        self.start_offset = start_offset
        self.stop_offset = stop_offset
    def _writeData(self):
        def save_frame(frame):
            #Copied from mutagen.id3.ID3
            flags = 0
            framedata = frame._writeData()
            datasize = BitPaddedInt.to_str(len(framedata), width=4)
            header = pack('>4s4sH', type(frame).__name__, datasize, flags)
            return header + framedata

        data = []
        for i in (self.start, self.stop, self.start_offset, self.stop_offset):
            i = BitPaddedInt.to_str(i, width=4)
            data.append(i)
        for frame in self.embeded_frames:
            frame = save_frame(frame)
            data.append(frame)
        return ''.join(data)

    def _readData(self, data):
        # I don't need it and it's damn hard -> too lazy
        print 'not implmented'
        return None

class CTOC(Frame):
    """
    The table of contents frame specified in http://www.id3.org/id3v2-chapters-1.0
    """
    def __init__(self, has_parent, ordered, child_element_ids, embeded_frames):
        self.has_parent = has_parent
        self.ordered = ordered
        self.child_element_ids = child_element_ids
        self.embeded_frames = embeded_frames

    def _writeData(self):
        def save_frame(frame):
            #Copied from mutagen.id3.ID3
            flags = 0
            framedata = frame._writeData()
            datasize = BitPaddedInt.to_str(len(framedata), width=4)
            header = pack('>4s4sH', type(frame).__name__, datasize, flags)
            return header + framedata
        def bin(s):
            return str(s) if s<=1 else bin(s>>1) + str(s&1)
        data = []
        flags = []
        for i in (self.has_parent, self.ordered):
            if i:
                flags.append('1')
            else:
                flags.append('0')
        flags = int(''.join(flags))
        flags =  bin(flags)
        flags = ''.join(('\x00\x00\x00', flags))
        data.append(flags)

        entry_count = BitPaddedInt.to_str(len(self.child_element_ids), width=8)
        data.append(entry_count)

        for i in self.child_element_ids:
            data.append(''.join((str(i), '\x00')))

        for i in self.embeded_frames:
            data.append(save_frame(i))

        return ''.join(data)



from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TIT3

mp3 = MP3('test.mp3')
chap = CHAP(embeded_frames=[TIT3(encoding=3, text="Hallo")], start=1, stop=50,
            start_offset = 5, stop_offset = 5)
chap2 = CHAP(embeded_frames=[TIT3(encoding=3, text="Hallo")], start=20, stop=50,
                         start_offset = 5, stop_offset = 5)
print chap.HashKey
print chap2.HashKey
ctoc = CTOC(False, True, [1], [TIT2(encoding=3, text="LOL")])
print repr(ctoc._writeData())
