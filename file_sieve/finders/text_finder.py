import os
from itertools import count

from abstract.file_finder import FileFinder
from util.file_data_util import write_to_file


NULL_SECTOR = b'\x00' * 512
VALID_CHARS = b'\x00\t\n\r !"%&\'(),./0123456789?' + \
              b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
HEX_CHARS = b'\00\t\n\r ABCDEFabcdef0123456789'

_id_counter = count()


def is_valid(sector):
    return len(bytearray(filter(
        lambda byte: byte in VALID_CHARS, sector))) == len(sector)


def is_null(sector):
    return len(bytearray(filter(
        lambda byte: byte in b'\x00\t\n\r ', sector))) == len(sector)


def is_hex(sector):
    return len(bytearray(filter(
        lambda byte: byte in HEX_CHARS, sector))) == len(sector)


def passes_checks(sector):
    return not is_hex(sector) and is_valid(sector)


def create_text_finder(output_path, chunk_name):
    out_dir = os.path.join(output_path, 'TXT', chunk_name)
    return TextData(out_dir, 'bmp')


class TextData(FileFinder):
    def __init__(self, out_dir, ext, make_new=True):
        super().__init__(out_dir, ext, make_new)

    def _find_file(self, f, sector):
        start_position = f.tell() - 512
        byte_count = 0
        while passes_checks(sector):
            if sector == NULL_SECTOR:
                break
            byte_count += 512
            sector = f.read(512)

        if 0 < byte_count <= 100_000:
            id = next(_id_counter)
            file_path = os.path.join(self.out_dir, f'file{id}.{self.ext}')
            write_to_file(f, start_position, byte_count, file_path)
            return True
        elif byte_count > 100_000:
            print(f'text file over 100kb found ' + \
                f'at {hex(start_position)}, skipping...')
        return False