from brownie import Box, Contract, ProxyAdmin, TransparentUpgradeableProxy, BoxV2
from scripts.utils import get_account, encode_function_data, upgrade


def main():
    deploy()


def deploy():
    account = get_account()
    contract = Box[-1] if Box else Box.deploy({"from": account})

    proxy_admin = ProxyAdmin[-1] if ProxyAdmin else ProxyAdmin.deploy({"from": account})

    # initializer = contract.store, 1 siendo contract.store la funcion initializer, y 1 el parametro que esta recibe. Convertir en un stream esto, ya que es lo que recibe como parametro el upgradeAndCall
    initializer = contract.store, 1

    encoded_initializer = encode_function_data(initializer)
    # el primer parametro seria el contrato Implementacion, con la logica de negocio
    # El segundo contrato es el admin, podria poner mi address, pero estamos usando el contrato ProxyAdmin
    # La ventaja es que los upgrades se disparan desde el ProxyAdmin. Tiene esas funciones ya definidas.
    # El tercer parametro es un stream de bytes representando el initializer
    proxy = (
        TransparentUpgradeableProxy[-1]
        if TransparentUpgradeableProxy
        else TransparentUpgradeableProxy.deploy(
            contract.address,
            proxy_admin.address,
            encoded_initializer,
            {"from": account},
        )
    )  # a veces hay problemas calculando el gas limit asi que si pasa algo, agregarle un gas_limit: 1000000

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    # Normalmente, romperia esto con cualquier contrato, pero con el proxy no. Le estamos asignando al proxy
    # una Abi que claramente no tiene, pero como va a delegar todas las llamadas, va a funcionar
    # Esto es para poder hacer las llamadas aca.
    print(proxy_box.retrieve())

    # ---- UPGRADE from Box to BoxV2

    # deployamos BoxV2
    print("Deploying new Box...")
    boxv2 = BoxV2[-1] if BoxV2 else BoxV2.deploy({"from": account})
    print(f"New Box deployed at {boxv2.address}")

    print("Upgrading Proxy...")
    tx = upgrade(account, proxy_box, boxv2.address, proxy_admin, boxv2.store, 100)
    tx.wait(1)
    print("New Implementation. Proxy upgraded!")

    new_proxy_boxv2 = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    print("Retrieve: ", new_proxy_boxv2.retrieve())
    tx = new_proxy_boxv2.store(20, {"from": account})
    tx.wait(1)
    print("After store: ", new_proxy_boxv2.retrieve())
    tx = new_proxy_boxv2.increment({"from": account})
    tx.wait(1)
    print("After increment: ", new_proxy_boxv2.retrieve())
