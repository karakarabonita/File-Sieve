"""
Checks for a cross sector footer, returning the number of additional
bytes if found, and 0 otherwise.

Upholds the still file pointer invariant.
"""
def check_cross_sector_footer(sector, next_sector, footer):
    length = len(footer)
    for i in range(length - 1, 0, -1):
        if sector[512 - i:512] == footer[0:i] and \
           next_sector[0:length - i] == footer[i:]:
            return length - i
    return 0


def write_to_file(f, start_position, byte_count, file_path):
    f.seek(start_position)
    file_data = f.read(byte_count)
    if len(file_data) != byte_count:
        print('data goes beyond end of chunk, skipping...')
        return
    with open(file_path, mode='wb') as nf:
        nf.write(file_data)