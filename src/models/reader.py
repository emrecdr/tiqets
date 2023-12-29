from pathlib import Path
from typing import Protocol

from polars import DataFrame

from models.errors import AppReaderError


# Base interface for all reader classes
class BaseReader(Protocol):
    @staticmethod
    def read(file_path: Path | str) -> DataFrame | AppReaderError:
        ...
