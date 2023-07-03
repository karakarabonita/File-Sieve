import os
from itertools import count

from abstract.file_data import FileData
from util.file_data_util import write_to_file


BMP_START = b'BM'

_id_counter = count()


def create_bmp_finder(output_path, chunk_name):
    out_dir = os.path.join(output_path, 'BMP', chunk_name)
    return BMPData(out_dir, 'bmp')


class BMPData(FileData):
    def __init__(self, out_dir, ext, make_new=True):
        super().__init__(out_dir, ext, make_new=make_new)

    def find_file(self, f, sector):
        sig_length = len(BMP_START)
        if sector[:sig_length] == BMP_START:
            start_position = f.tell() - 512
            file_size = int.from_bytes(
                sector[sig_length:sig_length + 4], byteorder='little')
            if file_size > 20_000_000:
                return False
            id = next(_id_counter)
            file_path = os.path.join(self.output_path, f'file{id}.{self.ext}')
            write_to_file(f, start_position, file_size, file_path)
            f.seek(start_position + 512)
            return True
        return False