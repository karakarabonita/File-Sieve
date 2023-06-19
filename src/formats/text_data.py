import os

from util.file_data_util import write_to_file


NULL_SECTOR = b'\x00' * 512
VALID_CHARS = b'\x00\t\n\r !"%&\'(),./0123456789?' + \
              b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
HEX_CHARS = b'\00\t\n\r ABCDEFabcdef0123456789'


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


def find_text_file(f, sector, idx, ext, chunk_path, output_path):
    start_position = f.tell() - 512
    byte_count = 0
    while passes_checks(sector):
        if sector == NULL_SECTOR:
            break
        byte_count += 512
        sector = f.read(512)

    if 0 < byte_count <= 100_000:
        file_path = os.path.join(output_path, f'file{idx}.{ext}')
        write_to_file(f, start_position, byte_count, file_path)
        return True
    elif byte_count > 100_000:
        print(f'text file over 100kb found ' + \
              f'at {hex(start_position)}, skipping...')
    return False