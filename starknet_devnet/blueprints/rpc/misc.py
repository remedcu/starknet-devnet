"""
RPC miscellaneous endpoints
"""

from __future__ import annotations

from typing import Union

from starknet_devnet.blueprints.rpc.structures.types import BlockId, BlockNumber, Felt, Address
from starknet_devnet.state import state


async def chain_id() -> str:
    """
    Return the currently configured StarkNet chain id
    """
    devnet_state = state.starknet_wrapper.get_state()
    config = devnet_state.general_config
    chain: int = config.chain_id.value
    return hex(chain)


async def syncing() -> Union[dict, bool]:
    """
    Returns an object about the sync status, or false if the node is not synching
    """
    return False


# pylint: disable=redefined-builtin
async def get_events(from_block: BlockId, to_block: BlockId, address: Address) -> str:
    """
    Returns all events matching the given filter
    """
    # TODO: move to the new file?
    # TODO: what about RESULT_PAGE_REQUEST?
    devnet_state = state.starknet_wrapper.get_state()
    print("devnet_state", devnet_state.events)
 
    number_of_blocks_start = from_block
    if to_block == "latest":
        number_of_blocks_end = state.starknet_wrapper.blocks.get_number_of_blocks()
    else:
        number_of_blocks_end = to_block
    
    for i in range(int(number_of_blocks_start), int(number_of_blocks_end)):
        block = state.starknet_wrapper.blocks.get_by_number(i)
        if block.transaction_receipts != ():
            print('Events at ', i, ': ', block.transaction_receipts[0].events) 

    # TODO: filters
    # keys as array [a,b,c] = a or b or c

    return devnet_state.events


async def get_nonce(contract_address: Address) -> Felt:
    """
    Get the latest nonce associated with the given address
    """
    raise NotImplementedError()
