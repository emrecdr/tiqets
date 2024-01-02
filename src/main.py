import logging

from app_arguments import AppArguments
from models.processor import BaseProcessor
from models.reader import BaseReader
from models.validator import BaseValidator, ValidationResult
from processors import DataProcessor
from readers import CSVReader
from utils import get_logger, parse_args
from validators import DataValidator


# Main function
def main(args: AppArguments, logger: logging.Logger):
    """Execute the main logic of the application."""

    # Create instances of dependencies
    reader: BaseReader = CSVReader()
    validator: BaseValidator = DataValidator()
    processor: BaseProcessor = DataProcessor()

    # Read CSV files
    barcodes_df = reader.read(args.barcodes_file_path)
    if barcodes_df.shape[0] == 0:
        logger.warning(f"No data row in barcodes file: {args.barcodes_file}")
        return
    logger.debug(f"Barcodes file {args.barcodes_file_path.name} loaded. {barcodes_df.shape[0]} rows found.")

    orders_df = reader.read(args.orders_file_path)
    if orders_df.shape[0] == 0:
        logger.warning(f"No data row in orders file: {args.orders_file}")
        return
    logger.debug(f"Orders file {args.orders_file_path.name} loaded. {orders_df.shape[0]} rows found.")

    # Validate data
    barcode_validation: ValidationResult = validator.validate_barcodes(barcodes_df, "barcode")
    if not barcode_validation["is_valid"]:
        for error_pair in barcode_validation["errors"]:
            logger.warning(f"{error_pair!s}")

    set_df_proc = processor.set_dataframes(barcodes_df, orders_df)
    if not set_df_proc["is_ok"]:
        logger.error(set_df_proc["error"])
        return

    order_validation = validator.validate_orders(processor.merged_df, "barcode")
    if not order_validation["is_valid"]:
        for error_pair in order_validation["errors"]:
            logger.warning(f"{error_pair!s}")

        processor.merged_df = order_validation["data"]

    # Process data
    aggregate_proc = processor.get_aggregated_data()
    if not aggregate_proc["is_ok"]:
        logger.error(aggregate_proc["error"])
        return

    # Generate the processed output dataset
    aggregate_proc["data"].write_csv(args.output_file_path, separator=",")
    logger.info(f"Processed data file is generated {args.output_file_path.name!s}.")

    # Get top N customers & output
    top_customers_proc = processor.get_top_n_customers(args.top_n)
    if not top_customers_proc["is_ok"]:
        logger.warning(aggregate_proc["error"])
    else:
        output = [
            f"Top {args.top_n} customers:",
            f"{'Customer ID': ^15}, {'Total Barcodes': ^15}",
        ] + [
            f"{row['customer_id']: ^15}, {row['total_barcodes']: ^15}"
            for row in top_customers_proc["data"].rows(named=True)
        ]
        logger.info("\n".join(output))

    # Output number of unused barcodes
    unused_barcodes_proc = processor.get_unused_barcodes_count()
    if not unused_barcodes_proc["is_ok"]:
        logger.warning(unused_barcodes_proc["error"])
    else:
        logger.info(f"Number of unused barcodes: {unused_barcodes_proc['data']!s}.")


# App entry point
if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()
    logger = get_logger("MainApp", args.debug)

    logger.debug(f"Starting process with args: {args}")
    main(args, logger)
    logger.debug("Process finished.")
