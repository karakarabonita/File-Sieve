from util.file_data_util import check_cross_sector_footer
from formats.hf_finder import HFFinder


class ZIPFinder(HFFinder):
    header = b'\x50\x4B\x03\x04'
    footer = b'\x50\x4B\x05\x06'
    remainder_len = 18

    def __init__(self, exclude, out_dir, make_new=True):
        super().__init__(
            ZIPFinder.header, ZIPFinder.footer, 'zip', out_dir, make_new=make_new)
        self.exclude = exclude
        self.out_dir = out_dir

    def check_file_end(self, f, sector):
        if any([item in sector for item in self.exclude]):
            return False, 0

        byte_count = 0
        while len(sector) > 0:
            if self.footer in sector:
                byte_count += sector.index(self.footer) + len(self.footer) + \
                    ZIPFinder.remainder_len
                return True, byte_count

            next_sector = f.read(512)
            additional_bytes = check_cross_sector_footer(
                sector, next_sector, self.footer)
            if additional_bytes > 0:
                byte_count += additional_bytes + ZIPFinder.remainder_len
                return True, byte_count
            
            sector = next_sector
            byte_count += 512
        return False, 0