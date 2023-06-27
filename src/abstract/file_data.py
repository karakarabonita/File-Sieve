from abc import ABC, abstractmethod
from itertools import count
import os


class FileData(ABC):
    def __init__(self, out_dir, ext, make_new=True):
        self.out_dir = out_dir
        self.make_new = make_new
        self.ext = ext
        self.id_counter = count()

        os.makedirs(out_dir, exist_ok=make_new)
    
    @abstractmethod
    def find_file(self, fp, sector) -> bool:
        raise NotImplementedError