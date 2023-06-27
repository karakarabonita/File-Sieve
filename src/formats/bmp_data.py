from itertools import count
import os

from util.file_data_util import write_to_file


BMP_START = b'BM'

_id_counter = count()


def find_bmp_file(f, sector, ext, output_path):
    sig_length = len(BMP_START)
    if sector[:sig_length] == BMP_START:
        start_position = f.tell() - 512
        file_size = int.from_bytes(
            sector[sig_length:sig_length + 4], byteorder='little')
        if file_size > 20_000_000:
            return False
        id = next(_id_counter)
        file_path = os.path.join(output_path, f'file{id}.{ext}')
        write_to_file(f, start_position, file_size, file_path)
        f.seek(start_position + 512)
        return True
    return False