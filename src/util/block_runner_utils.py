from typing import List

from src.full_node.block_store import BlockStore
from src.types.full_block import FullBlock
from src.util.ints import uint32


def get_list_of_generators(block: FullBlock, store: BlockStore):
    ref_list = block.transactions_generator_ref_list
    blocks = await store.get_full_blocks_at(ref_list)
    generators = []
    for block in blocks:
        generators.append(block.transactions_generator)
    return generators


def get_list_of_generators_ref(ref_list: List[uint32], store: BlockStore):
    blocks = await store.get_full_blocks_at(ref_list)
    generators = []
    for block in blocks:
        generators.append(block.transactions_generator)
    return generators
