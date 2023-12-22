from datetime import datetime
import logging
import os
import pathlib
from dataclasses import dataclass, field
from typing import Optional

from errors import ConfigError


@dataclass(frozen=False)
class AppArguments:
    """Represents the arguments for the application.

    This class stores the following arguments:
    - orders_file: The name of the orders csv file.
    - barcodes_file: The name of the barcodes csv file.
    - file_path: The directory where the input files are located. Default is "data".
    - top_n: The number of top customers to consider. Default is 5.
    - debug: Whether to enable debug mode. Default is False.
    - output_folder_path: The directory where the output file will be saved. Default is "out".
    - log_level: The log level based on the debug mode.
    - orders_file_path: The resolved path to the orders file.
    - barcodes_file_path: The resolved path to the barcodes file.
    - output_file_path: The resolved path to the output file.
    """

    orders_file: str
    barcodes_file: str
    file_path: str = "data"
    top_n: Optional[int] = 5
    debug: bool = False
    output_folder_path: str = "out"
    log_level: str = field(init=False)
    orders_file_path: pathlib.Path = field(init=False)
    barcodes_file_path: pathlib.Path = field(init=False)
    output_file_path: pathlib.Path = field(init=False)

    def __post_init__(self):
        """Perform post-initialization tasks.

        This method sets the log level based on the debug mode and converts string directories into path objects.
        It also resolves the paths for the orders and barcodes files, and raises an error if the files do not exist.
        Finally, it sets the output file path based on the resolved paths and the current timestamp.

        Raises:
            ConfigError: If the orders or barcodes file does not exist.
        """
        # Set log level according to debug
        self.log_level = logging.INFO if self.debug else logging.WARNING
        # Turn string directories into path objs
        app_path = pathlib.Path(__file__).resolve().parent.parent
        input_file_path = app_path / self.file_path
        for name in ["orders_file", "barcodes_file"]:
            file_name = self.__dict__[name]
            self.__dict__[f"{name}_path"]: pathlib.Path = (
                pathlib.Path(file_name)
                if file_name.startswith(os.path.sep)
                else input_file_path / file_name
            )
            if not self.__dict__[f"{name}_path"].exists():
                raise ConfigError(f"Unable to find given {name!r} file {file_name!s}.")

        self.output_file_path = (
            app_path
            / self.output_folder_path
            / f"{self.orders_file_path.stem}_{self.barcodes_file_path.stem}_{datetime.now():%Y%m%d%H%M%S}.csv"
        )
