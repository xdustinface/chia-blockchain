import io
from typing import Any, BinaryIO


def hexstr_to_bytes(input_str: str) -> bytes:
    """
    Converts a hex string into bytes, removing the 0x if it's present.
    """
    if input_str.startswith("0x") or input_str.startswith("0X"):
        return bytes.fromhex(input_str[2:])
    return bytes.fromhex(input_str)


def make_sized_bytes(size: int):
    """
    Create a streamable type that subclasses "bytes" but requires instances
    to be a certain, fixed size.
    """
    name = "bytes%d" % size

    def __new__(cls, v):
        v = bytes(v)
        if not isinstance(v, bytes) or len(v) != size:
            raise ValueError("bad %s initializer %s" % (name, v))
        return bytes.__new__(cls, v)  # type: ignore

    @classmethod  # type: ignore
    def parse(cls, f: BinaryIO) -> Any:
        b = f.read(size)
        assert len(b) == size
        return cls(b)

    def stream(self, f):
        f.write(self)

    @classmethod  # type: ignore
    def from_bytes(cls: Any, blob: bytes) -> Any:
        # pylint: disable=no-member
        f = io.BytesIO(blob)
        result = cls.parse(f)
        assert f.read() == b""
        return result

    def __bytes__(self: Any) -> bytes:
        f = io.BytesIO()
        self.stream(f)
        return bytes(f.getvalue())

    def __str__(self):
        return self.hex()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, str(self))

    namespace = dict(
        __new__=__new__,
        parse=parse,
        stream=stream,
        from_bytes=from_bytes,
        __bytes__=__bytes__,
        __str__=__str__,
        __repr__=__repr__,
    )

    # The following is a workaround to archive pickle support for `sized_bytes` types (bytes4, bytes8, ...).
    # Obviously `type()` sets `__module__` of those custom types to `chia.util.byte_types` while it must be
    # `chia.types.blockchain_format.sized_bytes` since the class gets created there. This leads to pickle trying to load
    # the sized byte types from the wrong module:
    #
    #    _pickle.PicklingError: Can't pickle <class 'chia.util.byte_types.bytesX'>:
    #                           attribute lookup bytesX on chia.util.byte_types failed
    #
    # Setting `__module__` to `None` seems to force a lookup of the module in pickle. Normally we would just return
    # the result like: `return type(name, (bytes,), namespace)`
    t = type(name, (bytes,), namespace)
    t.__module__ = None
    return t
