from abc import ABC, abstractmethod
from itertools import count
import os


class FileFinder(ABC):
    def __init__(self, out_dir, ext, make_new=True):
        self.out_dir = out_dir
        self.make_new = make_new
        self.ext = ext
        self.id_counter = count()

        os.makedirs(out_dir, exist_ok=make_new)
    
    def find_file(self, f, sector) -> bool:
        return self._find_file(f, sector)
    
    @abstractmethod
    def _find_file(self, f, sector) -> bool:
        raise NotImplementedError