import os

from util.file_data_util import check_cross_sector_footer, write_to_file


class HFData:
    def __init__(self, header, footer, ext, out_dir, make_new=True):
        self.header = header
        self.footer = footer
        self.ext = ext
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=make_new)

    def check_file_end(self, f, sector):
        byte_count = 0
        while len(sector) > 0:
            if self.footer in sector:
                byte_count += sector.index(self.footer) + len(self.footer)
                return True, byte_count

            next_sector = f.read(512)
            additional_bytes = check_cross_sector_footer(
                sector, next_sector, self.footer)
            if additional_bytes > 0:
                byte_count += additional_bytes
                return True, byte_count
            
            sector = next_sector
            byte_count += 512
        return False, 0

    """
    Invariant: File pointer f is at the same position on return as when
    passed in (i.e., a call to f.read() will not miss or double-read any
    bytes after a call to this function).
    """
    def find_file(self, f, sector, idx, chunk_path):
        if sector[:len(self.header)] == self.header:
            start_position = f.tell() - 512
            found, byte_count = self.check_file_end(f, sector)

            if not found:
                print('ran out of data before finding end of image')
                return False
            
            file_path = os.path.join(self.out_dir, f'file{idx}.{self.ext}')
            write_to_file(f, start_position, byte_count, file_path)
            f.seek(start_position + 512)
            return True
        return False