import os
from collections import namedtuple

from abstract.file_data import FileData
from util.file_data_util import write_to_file


RIFFTypeInfo = namedtuple('RIFFTypeInfo', ['name', 'extension', 'riff_code'])

AVI_INFO = RIFFTypeInfo('AVI', 'avi', b'AVI ')
WAV_INFO = RIFFTypeInfo('WAV', 'wav', b'WAVE')

RIFF_INFO = [AVI_INFO, WAV_INFO]


def create_riff_types(output_path, chunk_name, types):
    info_filtered = filter(lambda info: info.extension in types, RIFF_INFO)
    riff_types = [
        RIFFData(info.riff_code, info.extension,
                 os.path.join(output_path, info.name, chunk_name))
        for info in info_filtered
    ]
    return riff_types


class RIFFData(FileData):
    known_riff_types = [b'AVI ', b'WAVE']

    def __init__(self, file_type, ext, out_dir, make_new=True, data_max=5e10):
        super().__init__(out_dir, ext, make_new=make_new)

        self.file_type = file_type
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
                id = next(self.id_counter)
                file_path = os.path.join(self.out_dir, f'file{id}.{self.ext}')
                write_to_file(f, start_position, file_size, file_path)
            else:
                print(f'maximum data exceeded, skipping file at {hex(start_position)}...')
            f.seek(start_position + 512)
            return True
        elif sector[:4] == b'RIFF' and sector[8:12] not in RIFFData.known_riff_types:
            print(f'unknown RIFF type {sector[8:12]} found at {hex(start_position)}')
        return False