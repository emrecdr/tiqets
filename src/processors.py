import polars as pl


class DataProcessor:
    def __init__(self):
        """Initializes a DataProcessor object with the given barcodes and orders dataframe."""

        self.barcodes_df: pl.DataFrame | None = None
        self.orders_df: pl.DataFrame | None = None
        self.merged_df: pl.DataFrame | None = None

    def set_dataframes(self, barcodes_df: pl.DataFrame, orders_df: pl.DataFrame):
        self.barcodes_df = barcodes_df
        self.orders_df = orders_df
        self.merged_df = self.merge_dataframes()

    def merge_dataframes(self) -> pl.DataFrame | None:
        """
        Merge orders and barcodes dataframes.

        Returns:
            pl.DataFrame: Merged DataFrame.
        """
        return (
            self.orders_df.join(self.barcodes_df, on="order_id", how="left")
            if self.orders_df is not None and self.barcodes_df is not None
            else None
        )

    def get_aggregated_data(self) -> pl.DataFrame | None:
        """
        Group the merged dataframe by customer_id and order_id and aggregate the grouped dataframe.

        Returns:
            pl.DataFrame: Aggregated DataFrame.
        """
        if self.merged_df is None:
            return None

        grouped = self.merged_df.groupby(["customer_id", "order_id"])

        # Aggregate the grouped dataframe to get the list of barcodes for each order
        return grouped.agg(pl.col("barcode").alias("barcodes").apply(lambda col: str(col.to_list())))

    def get_top_n_customers(self, top_n: int = 5) -> pl.DataFrame | None:
        """
        Get top N customers who bought the most barcodes.

        Args:
            top_n (int): Number of top customers to retrieve.

        Returns:
            pl.DataFrame: DataFrame with top N customers.
        """
        return (
            (
                self.merged_df.groupby("customer_id")
                .agg(pl.count("barcode").alias("total_barcodes"))
                .sort("total_barcodes", descending=True)
                .limit(top_n)
            )
            if self.merged_df is not None
            else None
        )

    def get_unused_barcodes_count(self) -> int | None:
        """
        Returns the count of unused barcodes.

        Returns:
            int: The count of unused barcodes.
        """
        return int(self.barcodes_df["order_id"].is_null().sum()) if self.barcodes_df is not None else None
