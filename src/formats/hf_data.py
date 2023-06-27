import os

from abstract.file_data import FileData
from util.file_data_util import check_cross_sector_footer, write_to_file


JPEG_START = b'\xff\xd8\xff'
JPEG_END = b'\xff\xd9'
PNG_START = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
PNG_END = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'
GM81_START = b'\x91\xD5\x12\x00\x2A\x03\x00\x00'
GM81_END = b'Extension Packages\x00\x00\x00\x00'
GIF_START = b'GIF8'
GIF_END = b';'
PDF_START = b'%PDF'
PDF_END = b'%%EOF'


def create_hf_types(output_path, chunk_name, types):
    hf_types = [
        HFData(JPEG_START, JPEG_END, 'jpg', 
               os.path.join(output_path, 'JPEGs', chunk_name)),
        HFData(PNG_START, PNG_END, 'png',
               os.path.join(output_path, 'PNGs', chunk_name)),
        HFData(GM81_START, GM81_END, 'gm81',
               os.path.join(output_path, 'GM81s', chunk_name)),
        HFData(GIF_START, GIF_END, 'gif',
               os.path.join(output_path, 'GIFs', chunk_name)),
        HFData(PDF_START, PDF_END, 'pdf',
               os.path.join(output_path, 'PDFs', chunk_name)),
    ]
    return list(filter(lambda hf_type: hf_type.ext in types, hf_types))


class HFData(FileData):
    def __init__(self, header, footer, ext, out_dir, make_new=True):
        super().__init__(out_dir, make_new=make_new)

        self.header = header
        self.footer = footer
        self.ext = ext

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
    def find_file(self, f, sector):
        if sector[:len(self.header)] == self.header:
            start_position = f.tell() - 512
            found, byte_count = self.check_file_end(f, sector)

            if not found:
                print('ran out of data before finding end of image')
                return False
            
            file_path = os.path.join(self.out_dir, f'file{self.id_counter}.{self.ext}')
            write_to_file(f, start_position, byte_count, file_path)
            f.seek(start_position + 512)
            return True
        return False