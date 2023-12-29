# Application error classes
class AppError(Exception):
    pass


class AppReaderError(AppError):
    pass


class AppConfigError(AppError):
    pass
