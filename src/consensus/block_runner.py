from typing import List, Tuple

from src.full_node.block_store import BlockStore
from src.full_node.mempool_check_conditions import get_name_puzzle_conditions, get_puzzle_and_solution_for_coin
from src.types.blockchain_format.coin import Coin
from src.types.blockchain_format.program import Program, SerializedProgram
from src.types.blockchain_format.sized_bytes import bytes32
from src.types.full_block import FullBlock, additions_for_npc


class BlockRunner:
    def __init__(self, cache_size: int):
        self.cache_size = cache_size

    def get_name_puzzle_conditions(
        self, program: SerializedProgram, generators: List[SerializedProgram], mode: bool = True
    ):
        return get_name_puzzle_conditions(program, generators, mode)

    async def get_removals_and_additions(
        self, store: BlockStore, block: FullBlock, mode: bool = True
    ) -> Tuple[List[bytes32], List[Coin]]:
        removals: List[bytes32] = []
        additions: List[Coin] = []
        ref_list = block.transactions_generator_ref_list
        blocks = await store.get_full_blocks_at(ref_list)
        generators = []
        for block in blocks:
            generators.append(block.transactions_generator)
        # This should never throw here, block must be valid if it comes to here
        err, npc_list, cost = self.get_name_puzzle_conditions(block.transactions_generator, generators, mode)
        # build removals list
        if npc_list is None:
            return [], []
        for npc in npc_list:
            removals.append(npc.coin_name)

        additions.extend(additions_for_npc(npc_list))

        return removals, additions

    async def get_puzzle_solution_for_single_coin(self, store: BlockStore, block: FullBlock, coin_name: bytes32):
        ref_list = block.transactions_generator_ref_list
        blocks = await store.get_full_blocks_at(ref_list)
        generators = []
        for block in blocks:
            generators.append(block.transactions_generator)

        error, puzzle, solution = get_puzzle_and_solution_for_coin(block.transactions_generator, generators, coin_name)

        return error, puzzle, solution
