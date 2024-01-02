from typing import Protocol

import polars as pl


# Base interface for all processor classes
class BaseProcessor(Protocol):
    barcodes_df: pl.DataFrame
    orders_df: pl.DataFrame
    merged_df: pl.DataFrame

    def set_dataframes(self, barcodes_df: pl.DataFrame, orders_df: pl.DataFrame) -> None:
        ...

    def merge_dataframes(self) -> pl.DataFrame:
        ...

    def get_aggregated_data(self) -> pl.DataFrame:
        ...

    def get_top_n_customers(self, top_n: int = 5) -> pl.DataFrame:
        ...

    def get_unused_barcodes_count(self) -> int:
        ...
