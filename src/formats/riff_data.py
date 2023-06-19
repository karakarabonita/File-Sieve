import os

from util.file_data_util import write_to_file


class RIFFData:
    known_riff_types = [b'AVI ', b'WAVE']

    def __init__(self, file_type, ext, out_dir, make_new=True, data_max=5e10):
        self.file_type = file_type
        self.ext = ext
        self.out_dir = out_dir
        self.data_max = int(data_max)
        self.total_bytes = 0
        os.makedirs(out_dir, exist_ok=make_new)
    
    def find_file(self, f, sector, idx, chunk_path):
        start_position = f.tell() - 512
        if sector[:4] == b'RIFF' and sector[8:12] == self.file_type:
            # Add 8 to accommodate size of 'RIFF' and file_size
            file_size = int.from_bytes(sector[4:8], byteorder='little') + 8

            if file_size > self.data_max:
                print(f'file over {self.data_max} bytes found at {hex(start_position)}.')
            self.total_bytes += file_size
            
            if self.total_bytes <= self.data_max:
                file_path = os.path.join(self.out_dir, f'file{idx}.{self.ext}')
                write_to_file(f, start_position, file_size, file_path)
            else:
                print(f'maximum data exceeded, skipping file at {hex(start_position)}...')
            f.seek(start_position + 512)
            return True
        elif sector[:4] == b'RIFF' and sector[8:12] not in RIFFData.known_riff_types:
            print(f'unknown RIFF type {sector[8:12]} found at {hex(start_position)}')
        return False