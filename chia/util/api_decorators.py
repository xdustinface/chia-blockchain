from __future__ import annotations

import functools
import logging
from dataclasses import dataclass, field
from inspect import signature
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Optional, Union, get_type_hints

from chia.protocols.protocol_message_types import ProtocolMessageTypes
from chia.server.outbound_message import Message
from chia.util.streamable import Streamable, _T_Streamable

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from chia.server.ws_connection import WSChiaConnection

    converted_api_f_type = Union[
        Callable[[Union[bytes, _T_Streamable]], Coroutine[Any, Any, Optional[Message]]],
        Callable[[Union[bytes, _T_Streamable], WSChiaConnection], Coroutine[Any, Any, Optional[Message]]],
    ]

    initial_api_f_type = Union[
        Callable[[Any, _T_Streamable], Coroutine[Any, Any, Optional[Message]]],
        Callable[[Any, _T_Streamable, WSChiaConnection], Coroutine[Any, Any, Optional[Message]]],
    ]

metadata_attribute_name = "_chia_api_metadata"


@dataclass
class ApiMetadata:
    api_function: bool = False
    peer_required: bool = False
    bytes_required: bool = False
    execute_task: bool = False
    reply_type: List[ProtocolMessageTypes] = field(default_factory=list)
    message_class: Optional[Any] = None


def get_metadata(function: Callable[..., Any]) -> ApiMetadata:
    maybe_metadata: Optional[ApiMetadata] = getattr(function, metadata_attribute_name, None)
    if maybe_metadata is None:
        raise TypeError("not an api method")

    return maybe_metadata


def maybe_get_metadata(function: Callable[..., Any]) -> Optional[ApiMetadata]:
    return getattr(function, metadata_attribute_name, None)


def default_and_get_metadata(function: Callable[..., Any]) -> ApiMetadata:
    maybe_metadata: Optional[ApiMetadata] = maybe_get_metadata(function=function)

    if maybe_metadata is None:
        metadata = ApiMetadata()
        setattr(function, metadata_attribute_name, metadata)
    else:
        metadata = maybe_metadata

    return metadata


def api_request(f: initial_api_f_type) -> converted_api_f_type:  # type: ignore
    annotations = get_type_hints(f)
    sig = signature(f)

    @functools.wraps(f)
    def f_substitute(*args, **kwargs) -> Any:  # type: ignore
        binding = sig.bind(*args, **kwargs)
        binding.apply_defaults()
        inter = dict(binding.arguments)

        # Converts each parameter from a Python dictionary, into an instance of the object
        # specified by the type annotation (signature) of the function that is being called (f)
        # The method can also be called with the target type instead of a dictionary.
        for param_name, param_class in annotations.items():
            if param_name != "return" and isinstance(inter[param_name], Streamable):
                if param_class.__name__ == "bytes":
                    continue
                if metadata.bytes_required:
                    inter[f"{param_name}_bytes"] = bytes(inter[param_name])
                    continue
            if param_name != "return" and isinstance(inter[param_name], bytes):
                if param_class.__name__ == "bytes":
                    continue
                if metadata.bytes_required:
                    inter[f"{param_name}_bytes"] = inter[param_name]
                inter[param_name] = param_class.from_bytes(inter[param_name])
        return f(**inter)  # type: ignore

    metadata = default_and_get_metadata(function=f)
    setattr(f_substitute, metadata_attribute_name, metadata)
    metadata.api_function = True

    # It would be good to better identify the single parameter of interest.
    metadata.message_class = [
        hint for name, hint in get_type_hints(f).items() if name not in {"self", "peer", "return"}
    ][-1]

    return f_substitute


def peer_required(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner() -> Callable[..., Any]:
        metadata = default_and_get_metadata(function=func)
        metadata.peer_required = True
        return func

    return inner()


def bytes_required(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner() -> Callable[..., Any]:
        metadata = default_and_get_metadata(function=func)
        metadata.bytes_required = True
        return func

    return inner()


def execute_task(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner() -> Callable[..., Any]:
        metadata = default_and_get_metadata(function=func)
        metadata.execute_task = True
        return func

    return inner()


def reply_type(prot_type: List[ProtocolMessageTypes]) -> Callable[..., Any]:
    def wrap(func: Callable[..., Any]) -> Callable[..., Any]:
        def inner() -> Callable[..., Any]:
            metadata = default_and_get_metadata(function=func)
            metadata.reply_type.extend(prot_type)
            return func

        return inner()

    return wrap
