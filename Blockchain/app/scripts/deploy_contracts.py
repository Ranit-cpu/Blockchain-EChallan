"""
Deploy TrafficChallanSystem smart contract.
Usage: python scripts/deploy_contract.py
"""
import asyncio, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from web3 import AsyncWeb3
from web3.middleware import ExtraDataToPOAMiddleware
from app.config import settings

CONTRACT_SOL  = Path(__file__).parent.parent / "contracts" / "TrafficChallanSystem.sol"
CONTRACT_JSON = Path(__file__).parent.parent / "contracts" / "TrafficChallanSystem.json"


async def compile_and_deploy() -> str:
    try:
        from solcx import compile_source, install_solc, get_installed_solc_versions
        installed = [str(v) for v in get_installed_solc_versions()]
        if "0.8.20" not in installed:
            print("Installing solc 0.8.20 ...")
            install_solc("0.8.20")

        compiled = compile_source(
            CONTRACT_SOL.read_text(),
            output_values=["abi", "bin"],
            solc_version="0.8.20",
        )
        iface = compiled["<stdin>:TrafficChallanSystem"]
        CONTRACT_JSON.write_text(json.dumps({"abi": iface["abi"], "bytecode": iface["bin"]}, indent=2))
        print("Contract compiled.")
        return await deploy(iface["abi"], iface["bin"])
    except Exception as e:
        print(f"Compilation error: {e}")
        if CONTRACT_JSON.exists():
            print("Using cached ABI/bytecode ...")
            d = json.loads(CONTRACT_JSON.read_text())
            return await deploy(d["abi"], d["bytecode"])
        raise


async def deploy(abi: list, bytecode: str) -> str:
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.BLOCKCHAIN_RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    assert await w3.is_connected(), f"Cannot connect to {settings.BLOCKCHAIN_RPC_URL}"

    acct = w3.eth.account.from_key(settings.DEPLOYER_PRIVATE_KEY)
    print(f"Deploying from : {acct.address}")
    print(f"Chain ID       : {settings.BLOCKCHAIN_CHAIN_ID}")
    print(f"Balance        : {w3.from_wei(await w3.eth.get_balance(acct.address), 'ether')} ETH")

    contract  = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce     = await w3.eth.get_transaction_count(acct.address)
    gas_price = await w3.eth.gas_price

    tx     = await contract.constructor().build_transaction({
        "from": acct.address, "nonce": nonce,
        "gas": settings.GAS_LIMIT, "gasPrice": gas_price,
        "chainId": settings.BLOCKCHAIN_CHAIN_ID,
    })
    signed  = w3.eth.account.sign_transaction(tx, settings.DEPLOYER_PRIVATE_KEY)
    tx_hash = await w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Tx hash        : {tx_hash.hex()} — waiting ...")

    receipt  = await w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    addr     = receipt["contractAddress"]
    print(f"\n✅ TrafficChallanSystem deployed at: {addr}")
    print(f"   Block: {receipt['blockNumber']}  Gas used: {receipt['gasUsed']}")
    print(f"\nAdd to .env:\nCONTRACT_ADDRESS={addr}")
    return addr


if __name__ == "__main__":
    asyncio.run(compile_and_deploy())