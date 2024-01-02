import polars as pl

from models.processor import ProcessResult


class DataProcessor:
    def __init__(self):
        """Initializes a DataProcessor object with the given barcodes and orders dataframe."""

        self.barcodes_df: pl.DataFrame | None = None
        self.orders_df: pl.DataFrame | None = None
        self.merged_df: pl.DataFrame | None = None

    def set_dataframes(self, barcodes_df: pl.DataFrame, orders_df: pl.DataFrame) -> ProcessResult:
        try:
            self.barcodes_df = barcodes_df
            self.orders_df = orders_df
            # Merge orders and barcodes dataframes.
            self.merged_df = self.orders_df.join(barcodes_df, on="order_id", how="left")
            return {"is_ok": True}
        except Exception as exc:
            return {"is_ok": False, "error": f"Unable to set dataframes: {exc!s}"}

    def get_aggregated_data(self) -> ProcessResult:
        """
        Group the merged dataframe by customer_id and order_id and aggregate the grouped dataframe.

        Returns:
            pl.DataFrame: Aggregated DataFrame.
        """
        err_prefix = "Unable to aggregate data:"
        if self.merged_df is None:
            return {
                "is_ok": False,
                "error": f"{err_prefix} Merged dataset is empty.",
            }

        try:
            grouped = self.merged_df.groupby(["customer_id", "order_id"])

            # Aggregate the grouped dataframe to get the list of barcodes for each order
            aggregated_df = grouped.agg(pl.col("barcode").alias("barcodes").apply(lambda col: str(col.to_list())))
            return {"is_ok": True, "data": aggregated_df}
        except Exception as exc:
            return {"is_ok": False, "error": f"{err_prefix} {exc!s}"}

    def get_top_n_customers(self, top_n: int = 5) -> ProcessResult:
        """
        Get top N customers who bought the most barcodes.

        Args:
            top_n (int): Number of top customers to retrieve.

        Returns:
            pl.DataFrame: DataFrame with top N customers.
        """
        err_prefix = "Unable to calculate top N customers:"

        if self.merged_df is None:
            return {
                "is_ok": False,
                "error": f"{err_prefix} Merged dataset is empty.",
            }

        try:
            customers_df = (
                self.merged_df.groupby("customer_id")
                .agg(pl.count("barcode").alias("total_barcodes"))
                .sort("total_barcodes", descending=True)
                .limit(top_n)
            )
            return {"is_ok": True, "data": customers_df}

        except Exception as exc:
            return {
                "is_ok": False,
                "error": f"{err_prefix} {exc!s}",
            }

    def get_unused_barcodes_count(self) -> ProcessResult:
        """
        Returns the count of unused barcodes.

        Returns:
            int: The count of unused barcodes.
        """
        err_prefix = "Unable to calculate unused barcodes:"

        if self.barcodes_df is None:
            return {
                "is_ok": False,
                "error": f"{err_prefix} Barcodes dataset is empty.",
            }

        try:
            unused_barcodes = int(self.barcodes_df["order_id"].is_null().sum())
            return {"is_ok": True, "data": unused_barcodes}

        except Exception as exc:
            return {
                "is_ok": False,
                "error": f"{err_prefix} {exc!s}",
            }
