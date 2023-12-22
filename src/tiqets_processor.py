import sys
from typing import Optional

import polars as pl

from app_arguments import AppArguments

pl.Config.set_tbl_hide_dataframe_shape(True)


class TiqetsProcessor:
    """Process data from orders and barcodes using Polars library.

    Args:
        args: An instance of AppArguments.

    Attributes:
        args: An instance of AppArguments.
        orders: A DataFrame containing orders data.
        barcodes: A DataFrame containing barcodes data.
        out_duplicate_barcodes: A DataFrame containing duplicate barcodes, if any.
        out_processed_data: A DataFrame containing processed data.
        out_top_customers: A DataFrame containing top customers who bought the most barcodes.
        out_unused_barcode_count: An integer representing the count of unused barcodes.

    Methods:
        read_data: Reads orders and barcodes data.
        validate_data: Validates the data and removes duplicate barcodes.
        process_data: Processes the data by merging, grouping, aggregating, and calculating metrics.
    """

    def __init__(self, args: AppArguments):
        self.args = args
        self.orders: pl.DataFrame = None
        self.barcodes: pl.DataFrame = None
        self.out_duplicate_barcodes: Optional[pl.DataFrame] = None
        self.out_processed_data: Optional[pl.DataFrame] = None
        self.out_top_customers: Optional[pl.DataFrame] = None
        self.out_unused_barcode_count: Optional[int] = None

    def read_data(self):
        """Read data from CSV files.
        This method reads the orders and barcodes data from CSV files using the Polars library.
        """
        try:
            # Read orders and barcodes data using Polars
            self.orders = pl.read_csv(self.args.orders_file_path)
            self.barcodes = pl.read_csv(self.args.barcodes_file_path)
        except Exception as e:
            # Log and handle any exceptions during data reading
            self._log_error(f"Error on reading data: {e}")

    def validate_data(self):
        """Validate the data.
        This method checks for duplicate barcodes in the barcodes dataframe.
        If duplicate barcodes are found, it removes them from the dataframe.
        """

        try:
            # Check for duplicate barcodes
            if self.barcodes["barcode"].is_duplicated().any():
                self.out_duplicate_barcodes = self.barcodes.filter(
                    self.barcodes["barcode"].is_duplicated()
                )
                # Removing duplicate barcodes...
                self.barcodes = self.barcodes.unique(
                    subset=["barcode"], keep="none", maintain_order=True
                )

        except Exception as e:
            # Log and handle validation errors
            self._log_error(f"Error on validating data: {e}")

    def process_data(self):
        """Process the data.

        This method merges the orders and barcodes dataframes, groups them by customer_id and order_id,
        aggregates the grouped dataframe to get the list of barcodes for each order,
        gets the top N customers who bought the most barcodes, and calculates the amount of unused book barcodes.
        """

        try:
            # Merge orders and barcodes dataframes
            merged = self.orders.join(self.barcodes, on="order_id")

            # Group the merged dataframe by customer_id and order_id
            grouped = merged.groupby(["customer_id", "order_id"])

            # Aggregate the grouped dataframe to get the list of barcodes for each order
            self.out_processed_data = grouped.agg(
                pl.col("barcode")
                .alias("barcodes")
                .apply(lambda col: str(col.to_list()))
            )

            # Get top N customers who bought the most barcodes
            self.out_top_customers = (
                merged.groupby("customer_id")
                .agg(pl.count("barcode").alias("total_barcodes"))
                .sort("total_barcodes", descending=True)
                .limit(self.args.top_n)
            )

            # Calculate the amount of unused book barcodes
            self.out_unused_barcode_count = self.barcodes["order_id"].is_null().sum()

        except Exception as e:
            # Log and handle any exceptions during data analysis
            self._log_error(f"Error on analyzing data: {e}")

    def _log_error(self, message: str):
        # Log errors to stderr
        print(f"ERROR: {message}", file=sys.stderr)
