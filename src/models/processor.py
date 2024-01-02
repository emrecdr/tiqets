from typing import Any, NotRequired, Protocol, TypedDict

import polars as pl


# Interface for the process method return object type
class ProcessResult(TypedDict):
    is_ok: bool
    error: NotRequired[str | None]
    data: NotRequired[Any]


# Base interface for all processor classes
class BaseProcessor(Protocol):
    barcodes_df: pl.DataFrame
    orders_df: pl.DataFrame
    merged_df: pl.DataFrame

    def set_dataframes(self, barcodes_df: pl.DataFrame, orders_df: pl.DataFrame) -> ProcessResult:
        ...

    def get_aggregated_data(self) -> ProcessResult:
        ...

    def get_top_n_customers(self, top_n: int = 5) -> ProcessResult:
        ...

    def get_unused_barcodes_count(self) -> ProcessResult:
        ...
