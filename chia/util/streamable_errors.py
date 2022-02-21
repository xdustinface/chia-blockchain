from enum import IntEnum
from typing import Any, List


class ErrorCodes(IntEnum):
    Unknown = 0
    ParameterMissing = 1
    InvalidType = 2
    InvalidSize = 3
    ConversionFailed = 4


class StreamableError(Exception):
    trace: List[str]
    error_code: ErrorCodes

    def __init__(self, message: str, error_code: ErrorCodes, field_trace: List[str]):
        super().__init__(message)
        self.error_code = error_code
        self.trace = field_trace


class ParameterMissingError(StreamableError):
    def __init__(self, trace: List[str]):
        super().__init__(f"Parameter missing: " + ".".join(trace), ErrorCodes.ParameterMissing, trace)


class InvalidTypeError(StreamableError):
    def __init__(self, value: Any, expected_type: type, actual_type: type, trace: List[str]):
        super().__init__(
            f"Invalid type for {value}: Expected {expected_type.__name__}, Actual: {type(actual_type).__name__}",
            ErrorCodes.InvalidType,
            trace,
        )


class InvalidSizeError(StreamableError):
    def __init__(self, value: Any, expected_size: int, actual_size: int, trace: List[str]):
        super().__init__(
            f"Invalid size for {value}: Expected {expected_size}, Actual: {actual_size}",
            ErrorCodes.InvalidSize,
            trace,
        )


class ConversionError(StreamableError):
    def __init__(self, value: Any, to_type: type, trace: List[str]):
        name: str = ".".join(trace)
        super().__init__(
            f"Failed to convert {name} from type {type(value).__name__} to {to_type.__name__}. Value: {value}",
            ErrorCodes.ConversionFailed,
            trace,
        )
