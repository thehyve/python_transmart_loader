from abc import abstractmethod
from typing import Sequence, Any


class CsvWriter:
    """
    This is an abstract version of the return of csv.writer().
    """

    @abstractmethod
    def writerow(self, row: Sequence[Any]) -> None:
        pass

    @abstractmethod
    def writerows(self, rows: Sequence[Sequence[Any]]) -> None:
        pass
