from brownie import accounts, config, network, accounts
import eth_utils

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development", "ganache-local", "mainnet-fork"]


def get_account(
    index=None, id=None
):  # para hacerlo mas generico y poder obtener cualquier cuenta por el metodo que sea
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def encode_function_data(initializer=None, *args):
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account_from,
    proxy_contract,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    if proxy_admin_contract:
        if initializer:
            # encode args
            data = encode_function_data(initializer, *args)
            # como tenemos admin contract y detectamos un initializer, tenemos que llamar a esa funcion
            tx = proxy_admin_contract.upgradeAndCall(
                proxy_contract,
                new_implementation_address,
                data,
                {"from": account_from, "gas_limit": 1000000},
            )
        else:
            tx = proxy_admin_contract.upgrade(
                proxy_contract, new_implementation_address, {"from": account_from}
            )
    else:  # no tiene admin contract, el admin puede ser un tipo cualquiera
        if initializer:
            data = encode_function_data(initializer, *args)
            tx = proxy_contract.upgradeToAndCall(
                new_implementation_address,
                data,
                {"from": account_from},
            )
        else:
            tx = proxy_contract.upgradeTo(
                new_implementation_address, {"from": account_from}
            )
    return tx  # hacer el wait afuera
