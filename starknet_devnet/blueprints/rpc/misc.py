"""
RPC miscellaneous endpoints
"""

from __future__ import annotations
from queue import Empty

from typing import Union, List

from starknet_devnet.blueprints.rpc.structures.types import BlockId, BlockNumber, Felt, Address
from starknet_devnet.state import state
import collections

def is_empty(a):
    return not a and isinstance(a, collections.Iterable)

def is_not_empty(a):
    return not is_empty(a)

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
async def get_events(from_block: BlockId, to_block: BlockId, address: Address, keys: List[Address]) -> str:
    """
    Returns all events matching the given filter
    """
    # TODO: move to the new file?
    # TODO: what about RESULT_PAGE_REQUEST and paging?
    # TODO: add tests (test case with address 0x not 0x0)

    devnet_state = state.starknet_wrapper.get_state()
    print("devnet_state", devnet_state.events)

    number_of_blocks_start = from_block
    if to_block == "latest":
        number_of_blocks_end = state.starknet_wrapper.blocks.get_number_of_blocks()
    else:
        number_of_blocks_end = to_block

    # TODO: Refactor this to avoid for if for if and is_not_empty/is_empty/else case with keys
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
                    event_to_add = "" # Get rid of this clear

                if address == "":
                    events.append(event_to_add)
                elif address != "" and event.from_address == int(address, 0):
                    events.append(event_to_add)
                    print('adress filtering at ', i, ': ', event_to_add) 

    print("events: ", events)
    return events


async def get_nonce(contract_address: Address) -> Felt:
    """
    Get the latest nonce associated with the given address
    """
    raise NotImplementedError()
