from dataclasses import dataclass

from chia.streamable import Streamable, streamable
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint32


@dataclass(frozen=True)
@streamable
class PoolTarget(Streamable):
    puzzle_hash: bytes32
    max_height: uint32  # A max height of 0 means it is valid forever
