from dataclasses import dataclass
from typing import Optional

from chia.streamable import Streamable, streamable
from chia.types.blockchain_format.vdf import VDFInfo, VDFProof


@dataclass(frozen=True)
@streamable
class SignagePoint(Streamable):
    cc_vdf: Optional[VDFInfo]
    cc_proof: Optional[VDFProof]
    rc_vdf: Optional[VDFInfo]
    rc_proof: Optional[VDFProof]
