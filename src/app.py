from __future__ import annotations

import argparse
import logging

from app_arguments import AppArguments
from tiqets_processor import TiqetsProcessor


def get_args() -> AppArguments:
    """Parse & return command line args"""
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Parse & Display customer, order datasets from given sources",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add the arguments
    parser.add_argument("orders_file", type=str, help="Name of the orders csv file.")
    parser.add_argument("barcodes_file", type=str, help="Name of the books csv file.")
    parser.add_argument(
        "-t", "--top_n", type=int, default=5, help="Display top N customers."
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enables debugging mode."
    )
    parser.add_argument(
        "-p", "--file_path", type=str, default="data", help="Path of the dataset files"
    )

    cli_args, _ = parser.parse_known_args()
    return AppArguments(**vars(cli_args))


# Main function
def main():
    """Execute the main logic of the application."""
    args = get_args()
    # Configure logging, set log level according to debug
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger()

    processor = TiqetsProcessor(args)
    processor.read_data()
    processor.validate_data()
    processor.process_data()

    # Output the results
    if processor.out_duplicate_barcodes is None:
        logger.info("Duplicate barcodes not found.")
    else:
        logger.warning(f"Duplicate barcodes found:\n{processor.out_duplicate_barcodes}")
        for row in processor.out_duplicate_barcodes.rows(named=True):
            print(f"{row['barcode']}, {row['order_id']}")

    # Generate the processed output dataset
    processor.out_processed_data.write_csv(args.output_file_path, separator=",")
    logger.info(f"Processed data file generated {args.output_file_path.name!s}.")

    # Output top N customers
    logger.info(f"Top {args.top_n} customers:")
    for row in processor.out_top_customers.rows(named=True):
        print(f"{row['customer_id']}, {row['total_barcodes']}")

    logger.info(f"Number of unused barcodes: {processor.out_unused_barcode_count!s}.")


# App entry point
if __name__ == "__main__":
    main()
