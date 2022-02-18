import logging
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, List
from enum import IntEnum

from blspy import G1Element

import aiohttp

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash
from chia.util.ints import uint16, uint32, uint64
from chia.util.json_util import obj_to_response
from chia.util.byte_types import hexstr_to_bytes
from chia.util.streamable import Streamable

log = logging.getLogger(__name__)


def _validate_list(entries: List[Any], entry_type: type) -> None:
    for entry in entries:
        if type(entry) != entry_type:
            raise InvalidTypeError(entry, entry_type, type(entry))

class RPCErrorCodes(IntEnum):
    Unknown = 0
    ParameterMissing = 1
    InvalidType = 2
    InvalidSize = 3
    OutOfRange = 4
    ConversionFailed = 5


class RPCError(Exception):
    error_message: str
    error_code: int

    def __init__(self, error_message: str, error_code: int):
        super().__init__(error_message)
        self.error_message = error_message
        self.error_code = error_code


class ParameterMissingError(RPCError):
    def __init__(self, name: str):
        super().__init__(f"Parameter missing: {name}", RPCErrorCodes.ParameterMissing)


class InvalidTypeError(RPCError):
    def __init__(self, value: Any, expected_type: type, actual_type: type):
        super().__init__(
            f"Invalid type for {value}: Expected {expected_type}, Actual: {type(actual_type)}",
            RPCErrorCodes.InvalidType,
        )


class InvalidSizeError(RPCError):
    def __init__(self, value: Any, expected_size: int, actual_size: int):
        super().__init__(
            f"Invalid size for {value}: Expected {expected_size}, Actual: {actual_size}", RPCErrorCodes.InvalidSize
        )


class OutOfRangeError(RPCError):
    def __init__(self, value: Any, expected_type: type):
        super().__init__(f"Value {value} out of range for {expected_type}", RPCErrorCodes.InvalidSize)


class ConversionError(RPCError):
    def __init__(self, value: Any, to_type: type):
        super().__init__(f"Failed to convert {value} to {to_type}", RPCErrorCodes.ConversionFailed)


@dataclass
class RequestParams:
    _request: Dict = field(default_factory=dict)

    def __contains__(self, item) -> bool:
        return item in self._request

    def _get(self, name: str, data_type: type, *, optional: bool = False) -> Any:
        if name not in self._request or self._request[name] is None:
            if optional:
                return None
            raise ParameterMissingError(name)
        param = self._request[name]
        # If some types there are special ways to parse them
        if data_type == bytes:
            return RequestParams.parse_bytes(param)
        if data_type == bytes32:
            return RequestParams.parse_bytes32(param)
        if data_type == G1Element:
            return RequestParams.parse_pubkey(param)
        # For all other type requests we just check if its the correct one
        if type(param) != data_type:
            # If it isn't we try to parse it to the expected type
            try:
                return data_type(param)
            except Exception:
                raise InvalidTypeError(param, data_type, type(param))
        return param

    def get_nested_params(self, name) -> "RequestParams":
        return RequestParams(self._get(name, dict, optional=False))

    def get_nested_params_optional(self, name) -> Optional["RequestParams"]:
        ret = self._get(name, dict, optional=True)
        if ret is None:
            return None
        return RequestParams(ret)

    def get_str(self, name: str) -> str:
        return self._get(name, str)

    def get_str_list(self, name: str) -> List[str]:
        raw_list = self._get(name, list)
        _validate_list(raw_list, str)
        return raw_list

    def get_nested_params_list(self, name: str, allow_empty: bool = False) -> List["RequestParams"]:
        raw_list: List[Dict] = self._get(name, list)
        if len(raw_list) == 0 and not allow_empty:
            raise ParameterMissingError(name)
        for entry in raw_list:
            if type(entry) != dict:
                raise InvalidTypeError(entry, dict, type(entry))
        return [RequestParams(entry) for entry in raw_list]

    def get_str_optional(self, name: str) -> Optional[str]:
        return self._get(name, str, optional=True)

    def get_bool(self, name: str) -> bool:
        return self._get(name, bool)

    def get_bool_optional(self, name: str) -> Optional[bool]:
        return self._get(name, bool, optional=True)

    def get_uint16(self, name: str) -> uint16:
        ret = self.get_uint16_optional(name)
        if ret is None:
            raise ParameterMissingError(name)
        return ret

    def get_uint16_optional(self, name: str) -> Optional[uint16]:
        int_value = self._get(name, int, optional=True)
        if int_value is None:
            return None
        try:
            return uint16(int_value)
        except Exception:
            raise OutOfRangeError(int_value, uint16)

    def get_uint32(self, name: str) -> uint32:
        ret = self.get_uint32_optional(name)
        if ret is None:
            raise ParameterMissingError(name)
        return ret

    def get_uint32_optional(self, name: str) -> Optional[uint32]:
        int_value = self._get(name, int, optional=True)
        if int_value is None:
            return None
        try:
            return uint32(int_value)
        except Exception:
            raise OutOfRangeError(int_value, uint32)

    def get_uint64(self, name: str) -> uint64:
        ret = self.get_uint64_optional(name)
        if ret is None:
            raise ParameterMissingError(name)
        return ret

    def get_uint64_optional(self, name: str) -> Optional[uint64]:
        int_value = self._get(name, int, optional=True)
        if int_value is None:
            return None
        try:
            return uint64(int_value)
        except Exception:
            raise OutOfRangeError(int_value, uint64)

    def get_bytes(self, name: str) -> bytes:
        return self._get(name, bytes)

    def get_bytes_optional(self, name: str) -> Optional[bytes]:
        return self._get(name, bytes, optional=True)

    def get_hash(self, name: str) -> bytes32:
        return self._get(name, bytes32)

    def get_hash_optional(self, name: str) -> Optional[bytes32]:
        return self._get(name, bytes32, optional=True)

    def get_bytes_list(self, name: str) -> List[bytes]:
        return [RequestParams.parse_bytes(x) for x in self._get(name, list)]

    def get_hash_list(self, name: str) -> List[bytes32]:
        return [RequestParams.parse_bytes32(x) for x in self._get(name, list)]

    def get_pubkey(self, name: str) -> G1Element:
        return self._get(name, G1Element)

    def get_pubkey_optional(self, name: str) -> Optional[G1Element]:
        return self._get(name, G1Element, optional=True)

    def get_address_puzzle_hash(self, name: str) -> bytes32:
        raw_address: str = self.get_str(name)
        try:
            return decode_puzzle_hash(raw_address)
        except Exception:
            raise ConversionError(raw_address, bytes32)

    def get_memos_optional(self, name: str) -> Optional[List[bytes]]:
        raw_list: List[str] = self._get(name, list, optional=True)
        if raw_list is None:
            return None
        _validate_list(raw_list, str)
        return [entry.encode("utf-8") for entry in raw_list]

    @staticmethod
    def parse_bytes(hex_str: str) -> bytes:
        if type(hex_str) != str:
            raise InvalidTypeError(hex_str, str, type(hex_str))
        try:
            return hexstr_to_bytes(hex_str)
        except Exception:
            raise InvalidTypeError(hex_str, bytes, str)

    @staticmethod
    def parse_bytes32(hex_str: str) -> bytes32:
        parsed_bytes = RequestParams.parse_bytes(hex_str)
        if len(parsed_bytes) != 32:
            raise InvalidSizeError(hex_str, 32, len(parsed_bytes))
        return bytes32(parsed_bytes)

    @staticmethod
    def parse_pubkey(hex_str: str) -> G1Element:
        parsed_bytes = RequestParams.parse_bytes(hex_str)
        try:
            return G1Element.from_bytes(parsed_bytes)
        except Exception:
            raise ConversionError(parsed_bytes, G1Element)

    @staticmethod
    def convert_from_bytes(raw_bytes: bytes, target_type: type):
        try:
            return target_type.__getattribute__("from_bytes")(raw_bytes)
        except Exception:
            raise ConversionError(raw_bytes, type(target_type))

    @staticmethod
    def convert_from_json_dict(json_dict: Dict[str, Any], target_type: Streamable):
        try:
            return target_type.__getattribute__("from_json_dict")(json_dict)
        except Exception:
            raise ConversionError(json_dict, type(target_type))


def wrap_http_handler(f) -> Callable:
    async def inner(request) -> aiohttp.web.Response:
        request_data = await request.json()
        try:
            res_object = await f(RequestParams(request_data))
            if res_object is None:
                res_object = {}
            if "success" not in res_object:
                res_object["success"] = True
        except RPCError as e:
            res_object = {"success": False, "error_code": e.error_code, "error_message": e.error_message}
        except Exception as e:
            tb = traceback.format_exc()
            log.warning(f"Error while handling message: {tb}")
            res_object = {
                "success": False,
                "error_code": RPCErrorCodes.Unknown,
                "error_message": f"{e.args[0]}" if len(e.args) > 0 else f"{e}",
            }

        return obj_to_response(res_object)

    return inner
