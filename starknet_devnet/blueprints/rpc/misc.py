"""
RPC miscellaneous endpoints
"""

from __future__ import annotations

from typing import Union

from starknet_devnet.blueprints.rpc.structures.payloads import Felt, Address
from starknet_devnet.blueprints.rpc.structures.types import BlockId
from starknet_devnet.blueprints.rpc.utils import get_block_by_block_id
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
async def get_events(block_id: BlockId) -> int:
    """
    Returns all events matching the given filter
    """
    # TODO: move to the new file?
    # TODO: get events and filter them -> EVENT_FILTER & RESULT_PAGE_REQUEST
    block = get_block_by_block_id(block_id)
    return 42


async def get_nonce(contract_address: Address) -> Felt:
    """
    Get the latest nonce associated with the given address
    """
    raise NotImplementedError()
