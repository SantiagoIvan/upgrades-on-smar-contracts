from brownie import (
    Contract,
    TransparentUpgradeableProxy,
    Box,
    BoxV2,
    network,
    ProxyAdmin,
    exceptions,
)
from scripts.utils import get_account, encode_function_data, upgrade
import pytest


def test_delegate_calls():
    if network.show_active() != "rinkeby":
        pytest.skip()
    account = get_account()
    box = Box[-1]
    proxy_admin = ProxyAdmin[-1]
    empty_init = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, empty_init, {"from": account}
    )

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    assert proxy_box.retrieve() == 0
    tx = proxy_box.store(1, {"from": account})
    tx.wait(1)
    assert proxy_box.retrieve() == 1


def test_can_upgrade_and_delegate():
    if network.show_active() != "rinkeby":
        pytest.skip()
    account = get_account()
    proxy_admin = ProxyAdmin[-1]
    box = Box.deploy({"from": account})
    empty_init = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        empty_init,
        {"from": account, "gas_limit": 1000000},
    )
    boxv2 = BoxV2.deploy({"from": account})

    tx = upgrade(account, proxy, boxv2.address, proxy_admin)
    tx.wait(1)

    new_proxy_interface = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    # new interface works
    assert new_proxy_interface.retrieve() == 0
    tx = new_proxy_interface.store(1, {"from": account})
    tx.wait(1)
    assert new_proxy_interface.retrieve() == 1
    tx = new_proxy_interface.increment({"from": account})
    tx.wait(1)
    assert new_proxy_interface.retrieve() == 2
