from unittest import TestCase

#from src.full_node.mempool_check_conditions import build_block_program_args
#from src.consensus.blockchain_interface import BlockchainInterface
from src.consensus.block_store_interface import BlockStoreInterface
from src.consensus.build_block_program_args import build_block_program_args
from src.types.blockchain_format.program import NilSerializedProgram, Program, SerializedProgram
from src.types.full_block import FullBlock
from src.wallet.puzzles.load_clvm import load_clvm


CLVM_DESERIALIZE_MOD = load_clvm("chialisp_deserialisation.clvm", package_or_requirement="src.wallet.puzzles")

# full_block_list : List[FullBlock] = await block_store.get_full_blocks_at(gen_refs)

# database maybe
class ProbablyDefinitelyARealBlockchain(BlockStoreInterface):
    async def get_full_blocks_at(self, heights: List[uint32]) -> List[FullBlock]:
        return None


class TestGeneratorReferences(TestCase):
    def test_build_block_program_args(self):
        deserializer = CLVM_DESERIALIZE_MOD
        nil = NilSerializedProgram
        one_arg_list = SerializedProgram.from_bytes(bytes.fromhex("ff4180"))
        two_arg_list = SerializedProgram.from_bytes(bytes.fromhex("ff41ff4280"))
        blocks = ProbablyDefinitelyARealBlockchain()

        # Tests begin
        block_args = build_block_program_args(nil, nil, blocks, 100)
        self.assertEqual(block_args, nil)

        block_args = build_block_program_args(deserializer, nil, blocks, 100)
        self.assertEqual(block_args, nil)

        block_args = build_block_program_args(nil, one_arg_list, blocks, 100)
        self.assertEqual(block_args, nil)

        #block_args = build_block_program_args(deserializer, one_arg_list)
        #self.assertEqual(block_args, nil)

        #block_args = build_block_program_args(deserializer, two_arg_list)
        #self.assertEqual(block_args, nil)

