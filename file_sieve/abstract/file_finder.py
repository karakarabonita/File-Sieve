from abc import ABC, abstractmethod
from itertools import count
import os


class FileFinder(ABC):
    def __init__(self, out_dir, ext, make_new=True):
        self.out_dir = out_dir
        self.make_new = make_new
        self.ext = ext
        self.directory_exists = False
        self.id_counter = count()
    
    def find_file(self, f, sector) -> bool:
        if self._check_signature(sector):
            self.ensure_directory()
            return self._find_file(f, sector)
        return False
    
    @abstractmethod
    def _check_signature(self, sector) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _find_file(self, f, sector) -> bool:
        raise NotImplementedError
    
    def ensure_directory(self):
        if not self.directory_exists:
            os.makedirs(self.out_dir, exist_ok=self.make_new)
            self.directory_exists = True
        