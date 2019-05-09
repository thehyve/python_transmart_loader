import csv
from collections import Iterable
from typing import List


class DsvReader:
    """
    Semicolon-separated values reader.
    """

    def close(self) -> None:
        if self.file:
            self.file.close()

    def __init__(self, path: str):
        self.file = open(path, 'r')
        self.reader: Iterable[List[str]] = csv.reader(self.file, delimiter=';')

    def __del__(self):
        self.close()
