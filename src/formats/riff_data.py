import os

from abstract.file_data import FileData
from util.file_data_util import write_to_file


AVI_TYPE = b'AVI '
WAV_TYPE = b'WAVE'


def create_riff_types(output_path, chunk_name, types):
    riff_types = [
        RIFFData(AVI_TYPE, 'avi',
                 os.path.join(output_path, 'AVIs', chunk_name)),
        RIFFData(WAV_TYPE, 'wav',
                 os.path.join(output_path, 'WAVs', chunk_name)),
    ]
    return list(filter(lambda riff_type: riff_type.ext in types, riff_types))


class RIFFData(FileData):
    known_riff_types = [b'AVI ', b'WAVE']

    def __init__(self, file_type, ext, out_dir, make_new=True, data_max=5e10):
        super().__init__(out_dir, make_new=make_new)

        self.file_type = file_type
        self.ext = ext
        self.data_max = int(data_max)
        self.total_bytes = 0
    
    def find_file(self, f, sector):
        start_position = f.tell() - 512
        if sector[:4] == b'RIFF' and sector[8:12] == self.file_type:
            # Add 8 to accommodate size of 'RIFF' and file_size
            file_size = int.from_bytes(sector[4:8], byteorder='little') + 8

            if file_size > self.data_max:
                print(f'file over {self.data_max} bytes found at {hex(start_position)}.')
            self.total_bytes += file_size
            
            if self.total_bytes <= self.data_max:
                file_path = os.path.join(self.out_dir, f'file{self.id_counter}.{self.ext}')
                write_to_file(f, start_position, file_size, file_path)
            else:
                print(f'maximum data exceeded, skipping file at {hex(start_position)}...')
            f.seek(start_position + 512)
            return True
        elif sector[:4] == b'RIFF' and sector[8:12] not in RIFFData.known_riff_types:
            print(f'unknown RIFF type {sector[8:12]} found at {hex(start_position)}')
        return False