import os
from collections import namedtuple

from abstract.file_finder import FileFinder
from util.file_data_util import check_cross_sector_footer, write_to_file


HFTypeInfo = namedtuple(
    'HFTypeInfo',
    ['name', 'extension', 'header', 'footer'])

JPEG_INFO = HFTypeInfo('JPEG', 'jpg',  b'\xff\xd8\xff', b'\xff\xd9')
PNG_INFO = HFTypeInfo('PNG', 'png', b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a',
                      b'\x49\x45\x4E\x44\xAE\x42\x60\x82')
GM81_INFO = HFTypeInfo('GM81', 'gm81', b'\x91\xD5\x12\x00\x2A\x03\x00\x00',
                       b'Extension Packages\x00\x00\x00\x00')
GIF_INFO = HFTypeInfo('GIF', 'gif', b'GIF8', b';')
PDF_INFO = HFTypeInfo('PDF', 'pdf', b'%PDF', b'%%EOF')

HF_INFO = [JPEG_INFO, PNG_INFO, GM81_INFO, GIF_INFO, PNG_INFO]


def create_hf_finders(output_path, types):
    info_filtered = filter(lambda info: info.extension in types, HF_INFO)
    hf_types = [
        HFFinder(info.header, info.footer, info.extension, 
               os.path.join(output_path, info.name))
        for info in info_filtered
    ]
    return hf_types


class HFFinder(FileFinder):
    def __init__(self, header, footer, ext, out_dir, make_new=True):
        super().__init__(out_dir, ext, make_new=make_new)

        self.header = header
        self.footer = footer

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
    def _find_file(self, f, sector):
        if sector[:len(self.header)] == self.header:
            start_position = f.tell() - 512
            found, byte_count = self.check_file_end(f, sector)

            if not found:
                print('ran out of data before finding end of image')
                return False
            
            id = next(self.id_counter)
            file_path = os.path.join(self.out_dir, f'file{id}.{self.ext}')
            write_to_file(f, start_position, byte_count, file_path)
            f.seek(start_position + 512)
            return True
        return False