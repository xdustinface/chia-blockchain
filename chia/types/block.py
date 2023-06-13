from __future__ import annotations

from dataclasses import dataclass

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint32
from chia.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class BlockIdentifier(Streamable):
    hash: bytes32
    height: uint32
