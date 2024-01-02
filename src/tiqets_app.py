import logging

import polars as pl

from app_arguments import AppArguments
from models.processor import BaseProcessor
from models.reader import BaseReader
from models.validator import BaseValidator, ValidationResult


class TiqetsApp:
    def __init__(
        self,
        args: AppArguments,
        logger: logging.Logger,
        reader: BaseReader,
        validator: BaseValidator,
        processor: BaseProcessor,
    ):
        self.args = args
        self.logger = logger
        self.reader = reader
        self.validator = validator
        self.processor = processor
        self.barcodes_df: pl.DataFrame
        self.orders_df: pl.DataFrame

    def read_data(self) -> bool:
        # Read CSV files
        self.barcodes_df = self.reader.read(self.args.barcodes_file_path)
        if self.barcodes_df.shape[0] == 0:
            self.logger.warning(f"No data row in barcodes file: {self.args.barcodes_file}")
            return False

        self.logger.debug(
            f"Barcodes file {self.args.barcodes_file_path.name} loaded. {self.barcodes_df.shape[0]} rows found."
        )

        self.orders_df = self.reader.read(self.args.orders_file_path)
        if self.orders_df.shape[0] == 0:
            self.logger.warning(f"No data row in orders file: {self.args.orders_file}")
            return False

        self.logger.debug(
            f"Orders file {self.args.orders_file_path.name} loaded. {self.orders_df.shape[0]} rows found."
        )

        return True

    def validate_data(self) -> bool:
        # Validate data
        barcode_validation: ValidationResult = self.validator.validate_barcodes(self.barcodes_df, "barcode")
        if not barcode_validation["is_valid"]:
            for error_pair in barcode_validation["errors"]:
                self.logger.warning(f"{error_pair!s}")

        set_df_proc = self.processor.set_dataframes(self.barcodes_df, self.orders_df)
        if not set_df_proc["is_ok"]:
            self.logger.error(set_df_proc["error"])
            return False

        order_validation = self.validator.validate_orders(self.processor.merged_df, "barcode")
        if not order_validation["is_valid"]:
            for error_pair in order_validation["errors"]:
                self.logger.warning(f"{error_pair!s}")

            self.processor.merged_df = order_validation["data"]

        return True

    def process_data(self) -> bool:
        # Process data
        aggregate_proc = self.processor.get_aggregated_data()
        if not aggregate_proc["is_ok"]:
            self.logger.error(aggregate_proc["error"])
            return False

        # Generate the processed output dataset
        aggregate_proc["data"].write_csv(self.args.output_file_path, separator=",")
        self.logger.info(f"Processed data file is generated {self.args.output_file_path.name!s}.")

        # Get top N customers & output
        top_customers_proc = self.processor.get_top_n_customers(self.args.top_n)
        if not top_customers_proc["is_ok"]:
            self.logger.warning(aggregate_proc["error"])
        else:
            output = [
                f"Top {self.args.top_n} customers:",
                f"{'Customer ID': ^15}, {'Total Barcodes': ^15}",
            ] + [
                f"{row['customer_id']: ^15}, {row['total_barcodes']: ^15}"
                for row in top_customers_proc["data"].rows(named=True)
            ]
            self.logger.info("\n".join(output))

        # Output number of unused barcodes
        unused_barcodes_proc = self.processor.get_unused_barcodes_count()
        if not unused_barcodes_proc["is_ok"]:
            self.logger.warning(unused_barcodes_proc["error"])
        else:
            self.logger.info(f"Number of unused barcodes: {unused_barcodes_proc['data']!s}.")

        return True
