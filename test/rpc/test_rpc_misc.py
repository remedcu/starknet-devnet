"""
Tests RPC miscellaneous
"""

from __future__ import annotations

import pytest
from starkware.starknet.public.abi import get_storage_var_address
from starkware.starknet.core.os.class_hash import compute_class_hash

from starknet_devnet.blueprints.rpc.structures.types import BlockHashDict
from starknet_devnet.blueprints.rpc.utils import rpc_root
from starknet_devnet.general_config import DEFAULT_GENERAL_CONFIG

from .rpc_utils import rpc_call, gateway_call, get_block_with_transaction, pad_zero


# pylint: disable=too-many-locals
@pytest.mark.usefixtures("run_devnet_in_background")
def test_get_state_update(deploy_info, invoke_info, contract_class):
    """
    Get state update for the block
    """
    block_with_deploy = get_block_with_transaction(deploy_info["transaction_hash"])
    block_with_invoke = get_block_with_transaction(invoke_info["transaction_hash"])

    contract_address: str = deploy_info["address"]
    block_with_deploy_hash: str = pad_zero(block_with_deploy["block_hash"])
    block_with_invoke_hash: str = pad_zero(block_with_invoke["block_hash"])
    block_id_deploy = BlockHashDict(block_hash=block_with_deploy_hash)
    block_id_invoke = BlockHashDict(block_hash=block_with_invoke_hash)
    class_hash = pad_zero(hex(compute_class_hash(contract_class)))

    storage = gateway_call(
        "get_storage_at",
        contractAddress=contract_address,
        key=get_storage_var_address("balance"),
    )

    new_root_deploy = rpc_root(
        gateway_call("get_state_update", blockHash=block_with_deploy_hash)["new_root"]
    )
    new_root_invoke = rpc_root(
        gateway_call("get_state_update", blockHash=block_with_invoke_hash)["new_root"]
    )

    resp = rpc_call("starknet_getStateUpdate", params={"block_id": block_id_deploy})
    state_update = resp["result"]

    assert state_update["block_hash"] == block_with_deploy_hash
    assert state_update["new_root"] == new_root_deploy
    assert "old_root" in state_update
    assert isinstance(state_update["old_root"], str)
    assert state_update["state_diff"] == {
        "storage_diffs": [],
        "deployed_contracts": [
            {
                "address": pad_zero(contract_address),
                "class_hash": class_hash,
            }
        ],
        "declared_contracts": [
            {
                "class_hash": class_hash,
            }
        ],
        "nonces": [],
    }

    resp = rpc_call("starknet_getStateUpdate", params={"block_id": block_id_invoke})
    state_update = resp["result"]

    assert state_update["block_hash"] == block_with_invoke_hash
    assert state_update["new_root"] == new_root_invoke
    assert "old_root" in state_update
    assert isinstance(state_update["old_root"], str)
    assert state_update["state_diff"] == {
        "storage_diffs": [
            {
                "address": contract_address,
                "key": pad_zero(hex(get_storage_var_address("balance"))),
                "value": pad_zero(storage),
            }
        ],
        "deployed_contracts": [],
        "declared_contracts": [],
        "nonces": [],
    }


@pytest.mark.parametrize("params", [{}, None])
@pytest.mark.usefixtures("run_devnet_in_background")
def test_chain_id(params):
    """
    Test chain id
    """
    chain_id = DEFAULT_GENERAL_CONFIG.chain_id.value

    resp = rpc_call("starknet_chainId", params=params)
    rpc_chain_id = resp["result"]

    assert rpc_chain_id == hex(chain_id)


@pytest.mark.parametrize("params", [{}, None])
@pytest.mark.usefixtures("run_devnet_in_background")
def test_syncing(params):
    """
    Test syncing
    """
    resp = rpc_call("starknet_syncing", params=params)
    assert "result" in resp, f"Unexpected response: {resp}"
    assert resp["result"] is False


@pytest.mark.parametrize("params", [2, "random string", True])
@pytest.mark.usefixtures("run_devnet_in_background")
def test_call_with_invalid_params(params):
    """Call with invalid params"""

    # could be any legal method, just passing something to get params to fail
    ex = rpc_call(method="starknet_getClass", params=params)
    assert ex["error"] == {"code": -32602, "message": "Invalid params"}


@pytest.mark.usefixtures("run_devnet_in_background")
def test_get_events_empty_with_no_events():
    """
    Test
    """
    resp = rpc_call("starknet_getEvents", params={
            "from_block": "0",
            "to_block": "latest",
            "address": "",
            "keys": []
        })
    print("resp", resp)

    assert resp["result"] == []
