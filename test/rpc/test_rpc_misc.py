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

from ..account import (
    invoke,
)
from ..util import (
    deploy,
)
from ..shared import (
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    EVENTS_CONTRACT_PATH,
)


@pytest.fixture(name="input_data")
def fixture_input_data(request):
    """
    Fixture to input data
    """
    return request.param


@pytest.fixture(name="expected_data")
def fixture_expected_data(request):
    """
    Fixture to return expected data
    """
    return request.param


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
@pytest.mark.parametrize(
    "run_devnet_in_background, input_data, expected_data",
    [
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {"from_block": "0", "to_block": "latest", "address": "", "keys": []},
            4,
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {"from_block": "0", "to_block": "3", "address": "", "keys": []},
            2,
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {"from_block": "3", "to_block": "4", "address": "", "keys": []},
            2,
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {
                "from_block": "0",
                "to_block": "latest",
                "address": "0x62230eA046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488",
                "keys": [],
            },
            2,
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {
                "from_block": "0",
                "to_block": "latest",
                "address": "",
                "keys": [
                    "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
                ],
            },
            2,
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            {
                "from_block": "0",
                "to_block": "latest",
                "address": "",
                "keys": [
                    "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9",
                    "0x3db3da4221c078e78bd987e54e1cc24570d89a7002cefa33e548d6c72c73f9d",
                ],
            },
            4,
        ),
    ],
    indirect=True,
)
def test_get_events_empty_with_no_events(input_data, expected_data):
    """
    Test RPC get_events.
    """
    deploy_info = deploy(EVENTS_CONTRACT_PATH)
    for i in range(0, 2):
        invoke(
            calls=[(deploy_info["address"], "increase_balance", [i])],
            account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
            private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        )
    resp = rpc_call("starknet_getEvents", params=input_data)
    assert len(resp["result"]) == expected_data
