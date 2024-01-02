import argparse
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from app_arguments import AppArguments


def parse_args() -> AppArguments:
    """Parse & return command line args"""
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Parse & Display customer, order datasets from given sources",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add the arguments
    parser.add_argument("barcodes_file", type=str, help="Name of the barcodes csv file.")
    parser.add_argument("orders_file", type=str, help="Name of the orders csv file.")
    parser.add_argument("-p", "--file_path", type=str, default="data", help="Path of the dataset files")
    parser.add_argument("-t", "--top_n", type=int, default=5, help="Number of top customers to display.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enables debugging mode.")

    cli_args, _ = parser.parse_known_args()
    return AppArguments(**vars(cli_args))


def get_logger(name: str, is_debug: bool) -> logging.Logger:
    """Generate logger, set log level according to debug and return it"""
    logging.basicConfig(
        level=logging.DEBUG if is_debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    logger = logging.getLogger(name)

    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setLevel(logging.DEBUG if is_debug else logging.INFO)
    handler_stream.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    handler_file_rotating_error = TimedRotatingFileHandler(
        filename="out/logs/errors", when="D", interval=1, backupCount=5
    )
    handler_file_rotating_error.suffix = "%Y-%m-%d.log"
    handler_file_rotating_error.setLevel(logging.WARNING)
    handler_file_rotating_error.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
    )

    logger.addHandler(handler_stream)
    logger.addHandler(handler_file_rotating_error)
    logger.propagate = False
    return logger
