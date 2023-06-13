import os

from file_data_util import write_to_file


class QuickTimeData:
    known_ftyp_subtypes = set()
    signatures = set([
        b'ftyp', b'mdat', b'moov', b'pnot', b'udta', b'uuid', b'moof',
        b'free', b'skip', b'jP2 ', b'wide', b'load', b'ctab', b'imap',
        b'matt', b'kmat', b'clip', b'crgn', b'sync', b'chap', b'tmcd',
        b'scpt', b'ssrc', b'PICT', b'mdat',
    ])

    def __init__(self, subtypes, ext, out_dir, make_new=True):
        self.subtypes = subtypes
        self.ext = ext
        self.out_dir = out_dir

        QuickTimeData.known_ftyp_subtypes |= set(subtypes)
        os.makedirs(out_dir, exist_ok=make_new)
    
    def find_file(self, f, sector, idx, chunk_path):
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
            
            file_path = os.path.join(self.out_dir, f'file{idx}.{self.ext}')
            write_to_file(f, start_position, total_bytes, file_path)
            f.seek(start_position + 512)
            return True
        elif sector[4:8] == b'ftyp' and \
             sector[8:12] not in QuickTimeData.known_ftyp_subtypes:
            print(f'found unknown quicktime subtype {sector[8:12]}' + \
                  f' at {hex(start_position)}')
        return False