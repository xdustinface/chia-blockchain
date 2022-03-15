from typing import Dict

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.wallet.cat_wallet.cat_utils import CATDescription

DEFAULT_CATS: Dict[bytes32, CATDescription] = {
    bytes32.from_hexstr("78ad32a8c9ea70f27d73e9306fc467bab2a6b15b30289791e37ab6e8612212b1"): CATDescription(
        name="Spacebucks", symbol="SBX"
    ),
    bytes32.from_hexstr("8ebf855de6eb146db5602f0456d2f0cbe750d57f821b6f91a8592ee9f1d4cf31"): CATDescription(
        name="Marmot", symbol="MRMT"
    ),
    bytes32.from_hexstr("6d95dae356e32a71db5ddcb42224754a02524c615c5fc35f568c2af04774e589"): CATDescription(
        name="Stably USD", symbol="USDS"
    ),
    bytes32.from_hexstr("509deafe3cd8bbfbb9ccce1d930e3d7b57b40c964fa33379b18d628175eb7a8f"): CATDescription(
        name="Chia Holiday 2021 Token", symbol="CH21"
    ),
}
