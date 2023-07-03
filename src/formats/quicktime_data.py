import os
from collections import namedtuple

from abstract.file_data import FileData
from util.file_data_util import write_to_file


QuickTimeTypeInfo = namedtuple('QuickTimeTypeInfo', ['name', 'extension', 'subtypes'])

MP4_INFO = QuickTimeTypeInfo('MP4', 'mp4', [
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41', b'mp42', b'mp71', b'msnv',
    b'ndas', b'ndsc', b'ndsh', b'ndsm', b'ndsp', b'ndss', b'ndxc', b'ndxh',
    b'ndxm', b'ndxp', b'ndxs',
])
M4A_INFO = QuickTimeTypeInfo('M4A', 'm4a', [b'M4A '])
MOV_INFO = QuickTimeTypeInfo('MOV', 'mov', [b'qt  '])
M4V_INFO = QuickTimeTypeInfo('M4V', 'm4v', [b'M4V '])

QUICKTIME_INFO = [MP4_INFO, M4A_INFO, MOV_INFO, M4V_INFO]


def create_quicktime_finders(output_path, chunk_name, types):
    info_filtered = filter(lambda info: info.extension in types,
                           QUICKTIME_INFO)
    quicktime_types = [
        QuickTimeData(info.subtypes, info.extension,
               os.path.join(output_path, info.name, chunk_name)) 
        for info in info_filtered
    ]
    return quicktime_types


class QuickTimeData(FileData):
    known_ftyp_subtypes = set()
    signatures = set([
        b'ftyp', b'mdat', b'moov', b'pnot', b'udta', b'uuid', b'moof',
        b'free', b'skip', b'jP2 ', b'wide', b'load', b'ctab', b'imap',
        b'matt', b'kmat', b'clip', b'crgn', b'sync', b'chap', b'tmcd',
        b'scpt', b'ssrc', b'PICT', b'mdat',
    ])

    def __init__(self, subtypes, ext, out_dir, make_new=True):
        super().__init__(out_dir, ext, make_new=make_new)

        self.subtypes = subtypes
        

        QuickTimeData.known_ftyp_subtypes |= set(subtypes)
    
    def find_file(self, f, sector):
        start_position = f.tell() - 512
        if sector[4:8] == b'ftyp' and sector[8:12] in self.subtypes:
            total_bytes = 0
            first_size = int.from_bytes(sector[:4], byteorder='big')
            if first_size > 50_000:
                print(f'large ftyp block ({first_size}) ' + \
                      f'at {hex(start_position)}, skipping...')
                return False
            
            total_bytes += first_size
            f.seek(start_position + first_size)
            chunk_header = f.read(8)
            while chunk_header[4:] in QuickTimeData.signatures:
                chunk_size = int.from_bytes(chunk_header[:4], byteorder='big')
                total_bytes += chunk_size
                f.seek(chunk_size - 8, 1)
                chunk_header = f.read(8)
            
            id = next(self.id_counter)
            file_path = os.path.join(self.out_dir, f'file{id}.{self.ext}')
            write_to_file(f, start_position, total_bytes, file_path)
            f.seek(start_position + 512)
            return True
        elif sector[4:8] == b'ftyp' and \
             sector[8:12] not in QuickTimeData.known_ftyp_subtypes:
            print(f'found unknown quicktime subtype {sector[8:12]}' + \
                  f' at {hex(start_position)}')
        return False