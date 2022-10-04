"""
RPC miscellaneous endpoints
"""

from __future__ import annotations

from typing import Union, List
import collections
from starknet_devnet.blueprints.rpc.structures.types import (
    BlockId,
    Felt,
    Address,
)
from starknet_devnet.state import state


def is_empty(value):
    """
    Return true if empty.
    """
    return not value and isinstance(value, collections.Iterable)


def is_not_empty(value):
    """
    Return true if not empty.
    """
    return not is_empty(value)


def filter_address(address, event):
    """
    Filter by address.
    """
    return bool(address == "" or event.from_address == int(address, 0))


def filter_keys(keys, event):
    """
    Filter by keys.
    """
    return bool(
        (is_empty(keys)) or (is_not_empty(keys) and bool(set(event.keys) & set(keys)))
    )


def get_events_from_block(block, address, keys):
    """
    Return filtered events.
    """
    events = []
    for event in block.transaction_receipts[0].events:
        if filter_keys(keys, event) and filter_address(address, event):
            events.append(event)

    return events


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
async def get_events(
    from_block: BlockId, to_block: BlockId, address: Address, keys: List[Address]
) -> str:
    """
    Returns all events matching the given filter
    """

    events = []
    keys = [int(k, 0) for k in keys]
    to_block = (
        state.starknet_wrapper.blocks.get_number_of_blocks()
        if to_block == "latest"
        else to_block
    )

    for block_number in range(int(from_block), int(to_block)):
        block = state.starknet_wrapper.blocks.get_by_number(block_number)
        if block.transaction_receipts != ():
            events.extend(get_events_from_block(block, address, keys))

    return events


async def get_nonce(contract_address: Address) -> Felt:
    """
    Get the latest nonce associated with the given address
    """
    raise NotImplementedError()
