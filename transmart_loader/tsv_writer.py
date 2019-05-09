import csv
from typing import Sequence, Any

from transmart_loader.csv_types import CsvWriter


class TsvWriter(CsvWriter):
    """
    Tab-separated values writer. Creates a new file when initialised
    and fails when the file already exists.
    """
    def writerow(self, row:  Sequence[Any]) -> None:
        self.writer.writerow(row)

    def writerows(self, rows:  Sequence[Sequence[Any]]) -> None:
        self.writer.writerows(rows)

    def close(self) -> None:
        if self.file:
            self.file.close()

    def __init__(self, path: str):
        self.file = open(path, 'x')
        self.writer: CsvWriter = csv.writer(self.file, delimiter='\t')

    def __del__(self):
        self.close()
