import argparse
import logging

from app_arguments import AppArguments
from models.processor import BaseProcessor
from models.reader import BaseReader
from models.validator import BaseValidator, ValidationResult
from processors import DataProcessor
from readers import CSVReader
from validators import DataValidator


def parse_args() -> AppArguments:
    """Parse & return command line args"""
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Parse & Display customer, order datasets from given sources",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add the arguments
    parser.add_argument(
        "barcodes_file", type=str, help="Name of the barcodes csv file."
    )
    parser.add_argument("orders_file", type=str, help="Name of the orders csv file.")
    parser.add_argument(
        "-p", "--file_path", type=str, default="data", help="Path of the dataset files"
    )
    parser.add_argument(
        "-t", "--top_n", type=int, default=5, help="Number of top customers to display."
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enables debugging mode."
    )

    cli_args, _ = parser.parse_known_args()
    return AppArguments(**vars(cli_args))


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
    logger.debug(
        f"Barcodes file {args.barcodes_file_path.name} loaded. {barcodes_df.shape[0]} rows found."
    )

    orders_df = reader.read(args.orders_file_path)
    if orders_df.shape[0] == 0:
        logger.warning(f"No data row in orders file: {args.orders_file}")
        return
    logger.debug(
        f"Orders file {args.orders_file_path.name} loaded. {orders_df.shape[0]} rows found."
    )

    # Validate data
    barcode_validation: ValidationResult = validator.validate_barcodes(
        barcodes_df, "barcode"
    )
    if not barcode_validation["is_valid"]:
        for error_pair in barcode_validation["errors"]:
            logger.warning(f"{error_pair!s}")

    processor.set_dataframes(barcodes_df, orders_df)

    order_validation = validator.validate_orders(processor.merged_df, "barcode")
    if not order_validation["is_valid"]:
        for error_pair in order_validation["errors"]:
            logger.warning(f"{error_pair!s}")

        processor.merged_df = order_validation["data"]

    # Process data
    aggregated_df = processor.get_aggregated_data()

    # Generate the processed output dataset
    aggregated_df.write_csv(args.output_file_path, separator=",")
    logger.info(f"Processed data file is generated {args.output_file_path.name!s}.")

    # Get top N customers & output
    top_customers = processor.get_top_n_customers(args.top_n)
    output = [
                 f"Top {args.top_n} customers:",
                 f"{'Customer ID': ^15}, {'Total Barcodes': ^15}",
             ] + [
                 f"{row['customer_id']: ^15}, {row['total_barcodes']: ^15}"
                 for row in top_customers.rows(named=True)
             ]
    logger.info("\n".join(output))

    # Output number of unused barcodes
    logger.info(
        f"Number of unused barcodes: {processor.get_unused_barcodes_count()!s}."
    )


# App entry point
if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Configure logging, set log level according to debug
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    logger = logging.getLogger("MainApp")

    logger.debug(f"Starting process with args: {args}")
    main(args, logger)
    logger.debug("Process finished.")
