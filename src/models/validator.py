from dataclasses import dataclass
from typing import Any, List, NotRequired, Protocol, TypedDict

from polars import DataFrame


# Data class for error with a string message and a list of failed rows
@dataclass
class ValidationError:
    error_message: str
    failed_rows: List[Any] | None = None

    def __str__(self) -> str:
        error_output_rows = (
            ""
            if self.failed_rows is None
            else ("\n".join([", ".join([f'"{key}": {value}' for key, value in d.items()]) for d in self.failed_rows]))
        )
        return f"{self.error_message} \n{error_output_rows}"


# Interface for the return object type
class ValidationResult(TypedDict):
    is_valid: bool
    errors: NotRequired[List[ValidationError] | None]
    data: NotRequired[Any]


# Base interface for all validator classes
class BaseValidator(Protocol):
    def validate_barcodes(self, dataframe: DataFrame, column: str) -> ValidationResult:
        ...

    def validate_orders(self, dataframe: DataFrame, column: str) -> ValidationResult:
        ...
