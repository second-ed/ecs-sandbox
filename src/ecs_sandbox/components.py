from enum import StrEnum, auto, unique


@unique
class Components(StrEnum):
    SCHEDULE = auto()
    FILE_FORMAT = auto()
    COMPRESSION = auto()
    DATA_SOURCE = auto()
    ENVIRONMENT = auto()
