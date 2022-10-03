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
    # TODO: Move to the new file?
    # TODO: What about RESULT_PAGE_REQUEST and paging?
    # TODO: Refactor this in declarative way to avoid for if for if

    devnet_state = state.starknet_wrapper.get_state()
    print("devnet_state.events", devnet_state.events)

    number_of_blocks_start = from_block
    if to_block == "latest":
        number_of_blocks_end = state.starknet_wrapper.blocks.get_number_of_blocks()
    else:
        number_of_blocks_end = to_block

    print("all blocks", state.starknet_wrapper.blocks.get_number_of_blocks())

    new_keys = []
    for k in keys:
        new_keys.append(int(k, 0))

    keys = new_keys
    print("keys", keys)

    events = []
    for i in range(int(number_of_blocks_start), int(number_of_blocks_end)):
        block = state.starknet_wrapper.blocks.get_by_number(i)
        if block.transaction_receipts != ():
            for event in block.transaction_receipts[0].events:
                event_to_add = event

                if is_not_empty(keys) and bool(set(event.keys) & set(keys)):
                    event_to_add = event
                elif is_empty(keys):
                    event_to_add = event
                else:
                    continue

                if address == "":
                    events.append(event_to_add)
                elif address != "" and event.from_address == int(address, 0):
                    events.append(event_to_add)
                    print("adress filtering at ", i, ": ", event_to_add)

    print("events: ", events)
    return events


async def get_nonce(contract_address: Address) -> Felt:
    """
    Get the latest nonce associated with the given address
    """
    raise NotImplementedError()
