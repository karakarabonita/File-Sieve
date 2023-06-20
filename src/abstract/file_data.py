from abc import ABC, abstractmethod
import os


class FileData(ABC):
    def __init__(self, out_dir, make_new=True):
        self.out_dir = out_dir
        self.make_new = make_new

        os.makedirs(out_dir, exist_ok=make_new)
    
    @abstractmethod
    def find_file(self, fp, sector, idx, chunk_path) -> bool:
        raise NotImplementedError