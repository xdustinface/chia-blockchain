from __future__ import annotations

from typing import Any, Dict, List, Tuple

from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint64
from chia.wallet.puzzles.load_clvm import load_clvm_maybe_recompile
from chia.wallet.util.merkle_utils import build_merkle_tree

P2_1_OF_N = load_clvm_maybe_recompile("p2_1_of_n.clvm")
P2_CURRIED_PUZZLE_HASH = load_clvm_maybe_recompile("p2_puzzle_hash.clvm")
AUGMENTED_CONDITION = load_clvm_maybe_recompile("augmented_condition.clvm")


def create_augmented_cond_puzzle(condition: List[Any], puzzle: Program) -> Program:
    return AUGMENTED_CONDITION.curry(condition, puzzle)


def create_augmented_cond_puzzle_hash(condition: List[Any], puzzle_hash: bytes32) -> bytes32:
    return AUGMENTED_CONDITION.curry(condition, puzzle_hash).get_tree_hash_precalc(puzzle_hash)


def create_augmented_cond_solution(inner_solution: Program) -> Any:
    return Program.to([inner_solution])


def create_p2_puzzle_hash_puzzle(puzzle_hash: bytes32) -> Program:
    return P2_CURRIED_PUZZLE_HASH.curry(puzzle_hash)


def create_p2_puzzle_hash_solution(inner_puzzle: Program, inner_solution: Program) -> Any:
    return Program.to([inner_puzzle, inner_solution])


def create_clawback_merkle_tree(
    timelock: uint64, sender_ph: bytes32, recipient_ph: bytes32
) -> Tuple[bytes32, Dict[bytes32, Tuple[int, List[bytes32]]]]:
    timelock_condition = [80, timelock]
    augmented_cond_puz_hash = create_augmented_cond_puzzle_hash(timelock_condition, recipient_ph)
    p2_puzzle_hash_puz = create_p2_puzzle_hash_puzzle(sender_ph)
    merkle_tree = build_merkle_tree([augmented_cond_puz_hash, p2_puzzle_hash_puz.get_tree_hash()])
    return merkle_tree


def create_merkle_proof(
    merkle_tree: Tuple[bytes32, Dict[bytes32, Tuple[int, List[bytes32]]]], puzzle_hash: bytes32
) -> Any:
    return Program.to(merkle_tree[1][puzzle_hash])


def create_merkle_puzzle(timelock: uint64, sender_ph: bytes32, recipient_ph: bytes32) -> Program:
    merkle_tree = create_clawback_merkle_tree(timelock, sender_ph, recipient_ph)
    return P2_1_OF_N.curry(merkle_tree[0])
