import os

from abstract.file_data import FileData
from util.file_data_util import write_to_file


MP4_SUB_TYPES = [
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41', b'mp42', b'mp71', b'msnv',
    b'ndas', b'ndsc', b'ndsh', b'ndsm', b'ndsp', b'ndss', b'ndxc', b'ndxh',
    b'ndxm', b'ndxp', b'ndxs',
]
M4A_SUB_TYPES = [b'M4A ']
MOV_SUB_TYPES = [b'qt  ']
M4V_SUB_TYPES = [b'M4V ']


def create_quicktime_types(output_path, chunk_name, types):
    quicktime_types = [
        QuickTimeData(MP4_SUB_TYPES, 'mp4',
                      os.path.join(output_path, 'MP4s', chunk_name)),
        QuickTimeData(M4A_SUB_TYPES, 'm4a',
                      os.path.join(output_path, 'M4As', chunk_name)),
        QuickTimeData(MOV_SUB_TYPES, 'mov',
                      os.path.join(output_path, 'MOVs', chunk_name)),
        QuickTimeData(M4V_SUB_TYPES, 'm4v',
                      os.path.join(output_path, 'M4Vs', chunk_name)),
    ]
    return list(filter(
        lambda quicktime_type: quicktime_type.ext in types, quicktime_types))


class QuickTimeData(FileData):
    known_ftyp_subtypes = set()
    signatures = set([
        b'ftyp', b'mdat', b'moov', b'pnot', b'udta', b'uuid', b'moof',
        b'free', b'skip', b'jP2 ', b'wide', b'load', b'ctab', b'imap',
        b'matt', b'kmat', b'clip', b'crgn', b'sync', b'chap', b'tmcd',
        b'scpt', b'ssrc', b'PICT', b'mdat',
    ])

    def __init__(self, subtypes, ext, out_dir, make_new=True):
        super().__init__(out_dir, make_new=make_new)

        self.subtypes = subtypes
        self.ext = ext

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
            
            file_path = os.path.join(self.out_dir, f'file{self.id_counter}.{self.ext}')
            write_to_file(f, start_position, total_bytes, file_path)
            f.seek(start_position + 512)
            return True
        elif sector[4:8] == b'ftyp' and \
             sector[8:12] not in QuickTimeData.known_ftyp_subtypes:
            print(f'found unknown quicktime subtype {sector[8:12]}' + \
                  f' at {hex(start_position)}')
        return False