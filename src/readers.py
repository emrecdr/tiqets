from pathlib import Path

import polars as pl

from models.errors import AppReaderError


class CSVReader:
    @staticmethod
    def read(file_path: Path | str) -> pl.DataFrame:
        """Reads a CSV file and returns a Polars DataFrame."""
        try:
            return pl.read_csv(file_path)
        except Exception as exc:
            raise AppReaderError(
                f"Unable to read file {file_path.name if isinstance(file_path, Path) else str(file_path)}: {exc!s}"
            ) from exc
