from models.processor import BaseProcessor
from models.reader import BaseReader
from models.validator import BaseValidator
from processors import DataProcessor
from readers import CSVReader
from tiqets_app import TiqetsApp
from utils import get_logger, parse_args
from validators import DataValidator


# Main function
def main():
    """Execute the main logic of the application."""
    # Parse command-line arguments
    args = parse_args()
    logger = get_logger("MainApp", args.debug)

    logger.debug(f"Starting process with args: {args}")

    # Create instances of dependencies
    reader: BaseReader = CSVReader()
    validator: BaseValidator = DataValidator()
    processor: BaseProcessor = DataProcessor()

    app = TiqetsApp(args, logger, reader, validator, processor)

    is_ok = app.read_data()
    if not is_ok:
        logger.debug("Process terminated because of errors on reading data")
        return

    is_ok = app.validate_data()
    if not is_ok:
        logger.debug("Process terminated because of errors on validating data")
        return

    is_ok = app.process_data()
    if not is_ok:
        logger.debug("Process terminated because of errors on processing data")
        return

    logger.debug("Process finished successfully.")


# App entry point
if __name__ == "__main__":
    main()
