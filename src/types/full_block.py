from dataclasses import dataclass
from typing import List, Optional, Set

from chiabip158 import PyBIP158

from src.types.announcement import Announcement
from src.types.blockchain_format.coin import Coin
from src.types.blockchain_format.foliage import Foliage, FoliageTransactionBlock, TransactionsInfo
from src.types.blockchain_format.program import SerializedProgram
from src.types.blockchain_format.reward_chain_block import RewardChainBlock
from src.types.blockchain_format.sized_bytes import bytes32
from src.types.blockchain_format.vdf import VDFProof
from src.types.end_of_slot_bundle import EndOfSubSlotBundle
from src.types.header_block import HeaderBlock
from src.types.name_puzzle_condition import NPC
from src.util.condition_tools import created_announcements_for_conditions_dict, created_outputs_for_conditions_dict
from src.util.ints import uint32
from src.util.streamable import Streamable, streamable


@dataclass(frozen=True)
@streamable
class FullBlock(Streamable):
    # All the information required to validate a block
    finished_sub_slots: List[EndOfSubSlotBundle]  # If first sb
    reward_chain_block: RewardChainBlock  # Reward chain trunk data
    challenge_chain_sp_proof: Optional[VDFProof]  # If not first sp in sub-slot
    challenge_chain_ip_proof: VDFProof
    reward_chain_sp_proof: Optional[VDFProof]  # If not first sp in sub-slot
    reward_chain_ip_proof: VDFProof
    infused_challenge_chain_ip_proof: Optional[VDFProof]  # Iff deficit < 4
    foliage: Foliage  # Reward chain foliage data
    foliage_transaction_block: Optional[FoliageTransactionBlock]  # Reward chain foliage data (tx block)
    transactions_info: Optional[TransactionsInfo]  # Reward chain foliage data (tx block additional)
    transactions_generator: Optional[SerializedProgram]  # Program that generates transactions
    transactions_generator_ref_list: List[
        uint32
    ]  # List of block heights of previous generators referenced in this block

    @property
    def prev_header_hash(self):
        return self.foliage.prev_block_hash

    @property
    def height(self):
        return self.reward_chain_block.height

    @property
    def weight(self):
        return self.reward_chain_block.weight

    @property
    def total_iters(self):
        return self.reward_chain_block.total_iters

    @property
    def header_hash(self):
        return self.foliage.get_hash()

    def is_transaction_block(self):
        return self.foliage_transaction_block is not None

    def get_block_header(self, addition_coins, removals_names) -> HeaderBlock:
        # Create filter
        byte_array_tx: List[bytes32] = []
        if self.is_transaction_block():
            assert removals_names is not None
            assert addition_coins is not None
            for coin in addition_coins:
                byte_array_tx.append(bytearray(coin.puzzle_hash))
            for name in removals_names:
                byte_array_tx.append(bytearray(name))

            for coin in self.get_included_reward_coins():
                byte_array_tx.append(bytearray(coin.puzzle_hash))

        bip158: PyBIP158 = PyBIP158(byte_array_tx)
        encoded_filter: bytes = bytes(bip158.GetEncoded())

        return HeaderBlock(
            self.finished_sub_slots,
            self.reward_chain_block,
            self.challenge_chain_sp_proof,
            self.challenge_chain_ip_proof,
            self.reward_chain_sp_proof,
            self.reward_chain_ip_proof,
            self.infused_challenge_chain_ip_proof,
            self.foliage,
            self.foliage_transaction_block,
            encoded_filter,
            self.transactions_info,
        )

    def get_included_reward_coins(self) -> Set[Coin]:
        if not self.is_transaction_block():
            return set()
        assert self.transactions_info is not None
        return set(self.transactions_info.reward_claims_incorporated)

    def is_fully_compactified(self) -> bool:
        for sub_slot in self.finished_sub_slots:
            if (
                sub_slot.proofs.challenge_chain_slot_proof.witness_type != 0
                or not sub_slot.proofs.challenge_chain_slot_proof.normalized_to_identity
            ):
                return False
            if sub_slot.proofs.infused_challenge_chain_slot_proof is not None and (
                sub_slot.proofs.infused_challenge_chain_slot_proof.witness_type != 0
                or not sub_slot.proofs.infused_challenge_chain_slot_proof.normalized_to_identity
            ):
                return False
        if self.challenge_chain_sp_proof is not None and (
            self.challenge_chain_sp_proof.witness_type != 0 or not self.challenge_chain_sp_proof.normalized_to_identity
        ):
            return False
        if self.challenge_chain_ip_proof.witness_type != 0 or not self.challenge_chain_ip_proof.normalized_to_identity:
            return False
        return True


def additions_for_npc(npc_list: List[NPC]) -> List[Coin]:
    additions: List[Coin] = []

    for npc in npc_list:
        for coin in created_outputs_for_conditions_dict(npc.condition_dict, npc.coin_name):
            additions.append(coin)

    return additions


def announcements_for_npc(npc_list: List[NPC]) -> List[Announcement]:
    announcements: List[Announcement] = []

    for npc in npc_list:
        announcements.extend(created_announcements_for_conditions_dict(npc.condition_dict, npc.coin_name))

    return announcements
