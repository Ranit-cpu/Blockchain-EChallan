"""
Web3.py integration for TrafficChallanSystem smart contract.
Matches app/blockchain/TrafficChallanSystem.sol
"""
from typing import Any
from web3 import AsyncWeb3, Web3
from web3.middleware import geth_poa_middleware
from app.config import settings
from app.core.exceptions import BlockchainError
from app.core.logging import get_logger

logger = get_logger(__name__)

TRAFFIC_CHALLAN_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"name": "addOfficer", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_officer", "type": "address"}], "outputs": []},
    {"name": "removeOfficer", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_officer", "type": "address"}], "outputs": []},
    {"name": "addCamera", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_camera", "type": "address"}], "outputs": []},
    {"name": "revokeCamera", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_camera", "type": "address"}], "outputs": []},
    {"name": "createChallan", "type": "function", "stateMutability": "nonpayable",
     "inputs": [
         {"name": "_vehicleNumber", "type": "string"},
         {"name": "_violationType", "type": "string"},
         {"name": "_fineAmount", "type": "uint256"},
         {"name": "_violationTimestamp", "type": "uint256"},
         {"name": "_ipfsCid", "type": "string"},
         {"name": "_evidenceHash", "type": "bytes32"},
     ],
     "outputs": [{"name": "challanId", "type": "uint256"}]},
    {"name": "createChallanByCamera", "type": "function", "stateMutability": "nonpayable",
     "inputs": [
         {"name": "_vehicleNumber", "type": "string"},
         {"name": "_violationType", "type": "string"},
         {"name": "_fineAmount", "type": "uint256"},
         {"name": "_violationTimestamp", "type": "uint256"},
         {"name": "_ipfsCid", "type": "string"},
         {"name": "_evidenceHash", "type": "bytes32"},
     ],
     "outputs": [{"name": "challanId", "type": "uint256"}]},
    {"name": "recordPayment", "type": "function", "stateMutability": "nonpayable",
     "inputs": [
         {"name": "_challanId", "type": "uint256"},
         {"name": "_paymentTxRef", "type": "bytes32"},
     ],
     "outputs": []},
    {"name": "verifyChallan", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_challanId", "type": "uint256"}], "outputs": []},
    {"name": "disputeChallan", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_challanId", "type": "uint256"}], "outputs": []},
    {"name": "resolveDispute", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_challanId", "type": "uint256"}], "outputs": []},
    {"name": "cancelChallan", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_challanId", "type": "uint256"}], "outputs": []},
    {"name": "closeChallan", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "_challanId", "type": "uint256"}], "outputs": []},
    {"name": "getChallan", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "_challanId", "type": "uint256"}],
     "outputs": [{"name": "", "type": "tuple", "components": [
         {"name": "challanId", "type": "uint256"},
         {"name": "vehicleNumber", "type": "string"},
         {"name": "violationType", "type": "string"},
         {"name": "fineAmount", "type": "uint256"},
         {"name": "violationTimestamp", "type": "uint256"},
         {"name": "blockchainTimestamp", "type": "uint256"},
         {"name": "ipfsCid", "type": "string"},
         {"name": "evidenceHash", "type": "bytes32"},
         {"name": "status", "type": "uint8"},
         {"name": "createdBy", "type": "address"},
         {"name": "verifiedBy", "type": "address"},
         {"name": "disputeResolvedBy", "type": "address"},
         {"name": "paymentTxRef", "type": "bytes32"},
         {"name": "paidAt", "type": "uint256"},
     ]}]},
    {"name": "getAuditLog", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "_logId", "type": "uint256"}],
     "outputs": [{"name": "", "type": "tuple", "components": [
         {"name": "logId", "type": "uint256"},
         {"name": "challanId", "type": "uint256"},
         {"name": "actor", "type": "address"},
         {"name": "action", "type": "uint8"},
         {"name": "timestamp", "type": "uint256"},
     ]}]},
    {"name": "getChallanAuditLogIds", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "_challanId", "type": "uint256"}],
     "outputs": [{"name": "", "type": "uint256[]"}]},
    {"name": "violationKey", "type": "function", "stateMutability": "pure",
     "inputs": [
         {"name": "_vehicleNumber", "type": "string"},
         {"name": "_violationType", "type": "string"},
         {"name": "_violationTimestamp", "type": "uint256"},
         {"name": "_evidenceHash", "type": "bytes32"},
     ],
     "outputs": [{"name": "", "type": "bytes32"}]},
    {"name": "isOfficer", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "_addr", "type": "address"}],
     "outputs": [{"name": "", "type": "bool"}]},
    {"name": "isCamera", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "_addr", "type": "address"}],
     "outputs": [{"name": "", "type": "bool"}]},
    {"name": "challanCounter", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "admin", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "address"}]},
    {"name": "ChallanCreated", "type": "event", "anonymous": False,
     "inputs": [
         {"indexed": True, "name": "challanId", "type": "uint256"},
         {"indexed": False, "name": "vehicleNumber", "type": "string"},
         {"indexed": False, "name": "violationType", "type": "string"},
         {"indexed": False, "name": "fineAmount", "type": "uint256"},
         {"indexed": False, "name": "violationTimestamp", "type": "uint256"},
         {"indexed": False, "name": "ipfsCid", "type": "string"},
         {"indexed": False, "name": "evidenceHash", "type": "bytes32"},
         {"indexed": True, "name": "createdBy", "type": "address"},
     ]},
    {"name": "ChallanPaid", "type": "event", "anonymous": False,
     "inputs": [
         {"indexed": True, "name": "challanId", "type": "uint256"},
         {"indexed": False, "name": "paymentTxRef", "type": "bytes32"},
         {"indexed": True, "name": "recordedBy", "type": "address"},
         {"indexed": False, "name": "amount", "type": "uint256"},
     ]},
    {"name": "ChallanDisputed", "type": "event", "anonymous": False,
     "inputs": [
         {"indexed": True, "name": "challanId", "type": "uint256"},
         {"indexed": True, "name": "actor", "type": "address"},
     ]},
    {"name": "OfficerActionPerformed", "type": "event", "anonymous": False,
     "inputs": [
         {"indexed": True, "name": "challanId", "type": "uint256"},
         {"indexed": True, "name": "officer", "type": "address"},
         {"indexed": False, "name": "action", "type": "uint8"},
         {"indexed": False, "name": "timestamp", "type": "uint256"},
     ]},
]

CHALLAN_STATUS = {
    0: "Created",
    1: "Paid",
    2: "Disputed",
    3: "Cancelled",
    4: "Closed",
}
CHALLAN_STATUS_INT = {v: k for k, v in CHALLAN_STATUS.items()}

OFFICER_ACTION = {
    0: "CreatedChallan",
    1: "VerifiedChallan",
    2: "RecordedPayment",
    3: "MarkedDisputed",
    4: "ResolvedDispute",
    5: "CancelledChallan",
    6: "ClosedChallan",
}


def to_evidence_hash(value: str) -> bytes:
    """Map an off-chain evidence/challan hash string to bytes32 for the contract."""
    if value.startswith("0x") and len(value) == 66:
        return bytes.fromhex(value[2:])
    return Web3.keccak(text=value)


def to_payment_tx_ref(reference: str) -> bytes:
    if reference.startswith("0x") and len(reference) == 66:
        return bytes.fromhex(reference[2:])
    return Web3.keccak(text=reference)


class BlockchainService:
    _instance: "BlockchainService | None" = None
    _w3: AsyncWeb3 | None = None
    _contract: Any = None

    @classmethod
    async def get_instance(cls) -> "BlockchainService":
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        try:
            self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            if not await self._w3.is_connected():
                raise BlockchainError("Cannot connect to blockchain node")
            if settings.CONTRACT_ADDRESS:
                self._contract = self._w3.eth.contract(
                    address=AsyncWeb3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=TRAFFIC_CHALLAN_ABI,
                )
                logger.info("TrafficChallanSystem contract loaded", address=settings.CONTRACT_ADDRESS)
            else:
                logger.warning("CONTRACT_ADDRESS not set — blockchain calls will fail")
            logger.info("Blockchain service ready", rpc=settings.BLOCKCHAIN_RPC_URL)
        except BlockchainError:
            raise
        except Exception as e:
            raise BlockchainError(f"Blockchain init failed: {e}")

    @property
    def w3(self) -> AsyncWeb3:
        if not self._w3:
            raise BlockchainError("Web3 not initialized")
        return self._w3

    @property
    def contract(self) -> Any:
        if not self._contract:
            raise BlockchainError("Contract not loaded — check CONTRACT_ADDRESS in .env")
        return self._contract

    async def _send_tx(self, fn: Any) -> dict[str, Any]:
        account = self.w3.eth.account.from_key(settings.DEPLOYER_PRIVATE_KEY)
        nonce = await self.w3.eth.get_transaction_count(account.address)
        gas_price = await self.w3.eth.gas_price
        tx = await fn.build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": settings.GAS_LIMIT,
            "gasPrice": gas_price,
            "chainId": settings.BLOCKCHAIN_CHAIN_ID,
        })
        signed = self.w3.eth.account.sign_transaction(tx, settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = await self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "gas_used": receipt["gasUsed"],
            "status": "confirmed" if receipt["status"] == 1 else "failed",
            "receipt": receipt,
        }

    def _parse_challan_created_id(self, receipt: dict) -> int | None:
        try:
            logs = self.contract.events.ChallanCreated().process_receipt(receipt)
            if logs:
                return int(logs[0]["args"]["challanId"])
        except Exception:
            pass
        return None

    # ── Officer / camera ──────────────────────────────────────────────────────

    async def add_officer(self, officer_address: str) -> dict[str, Any]:
        try:
            fn = self.contract.functions.addOfficer(
                AsyncWeb3.to_checksum_address(officer_address)
            )
            return await self._send_tx(fn)
        except Exception as e:
            raise BlockchainError(f"add_officer: {e}")

    async def add_camera(self, camera_address: str) -> dict[str, Any]:
        try:
            fn = self.contract.functions.addCamera(
                AsyncWeb3.to_checksum_address(camera_address)
            )
            return await self._send_tx(fn)
        except Exception as e:
            raise BlockchainError(f"add_camera: {e}")

    # ── Challan creation ──────────────────────────────────────────────────────

    async def create_challan(
        self,
        vehicle_number: str,
        violation_type: str,
        fine_amount_paise: int,
        violation_timestamp: int,
        ipfs_cid: str,
        evidence_hash: str,
    ) -> dict[str, Any]:
        try:
            fn = self.contract.functions.createChallan(
                vehicle_number,
                violation_type,
                fine_amount_paise,
                violation_timestamp,
                ipfs_cid or "",
                to_evidence_hash(evidence_hash),
            )
            result = await self._send_tx(fn)
            result["on_chain_challan_id"] = self._parse_challan_created_id(result.pop("receipt"))
            logger.info(
                "Challan created on-chain",
                vehicle=vehicle_number,
                on_chain_id=result.get("on_chain_challan_id"),
                tx=result["tx_hash"],
            )
            return result
        except BlockchainError:
            raise
        except Exception as e:
            raise BlockchainError(f"create_challan: {e}")

    async def create_challan_by_camera(
        self,
        vehicle_number: str,
        violation_type: str,
        fine_amount_paise: int,
        violation_timestamp: int,
        ipfs_cid: str,
        evidence_hash: str,
    ) -> dict[str, Any]:
        try:
            fn = self.contract.functions.createChallanByCamera(
                vehicle_number,
                violation_type,
                fine_amount_paise,
                violation_timestamp,
                ipfs_cid or "",
                to_evidence_hash(evidence_hash),
            )
            result = await self._send_tx(fn)
            result["on_chain_challan_id"] = self._parse_challan_created_id(result.pop("receipt"))
            return result
        except BlockchainError:
            raise
        except Exception as e:
            raise BlockchainError(f"create_challan_by_camera: {e}")

    # ── Payment & status ──────────────────────────────────────────────────────

    async def record_payment_on_chain(
        self, on_chain_challan_id: int, payment_reference: str
    ) -> dict[str, Any]:
        try:
            fn = self.contract.functions.recordPayment(
                on_chain_challan_id,
                to_payment_tx_ref(payment_reference),
            )
            result = await self._send_tx(fn)
            result.pop("receipt", None)
            return result
        except Exception as e:
            raise BlockchainError(f"record_payment_on_chain: {e}")

    async def verify_challan_on_chain(self, on_chain_challan_id: int) -> dict[str, Any]:
        try:
            fn = self.contract.functions.verifyChallan(on_chain_challan_id)
            result = await self._send_tx(fn)
            result.pop("receipt", None)
            return result
        except Exception as e:
            raise BlockchainError(f"verify_challan_on_chain: {e}")

    async def dispute_challan_on_chain(self, on_chain_challan_id: int) -> dict[str, Any]:
        try:
            fn = self.contract.functions.disputeChallan(on_chain_challan_id)
            result = await self._send_tx(fn)
            result.pop("receipt", None)
            return result
        except Exception as e:
            raise BlockchainError(f"dispute_challan_on_chain: {e}")

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_challan_from_chain(self, challan_id: int) -> dict[str, Any]:
        try:
            c = await self.contract.functions.getChallan(challan_id).call()
            return {
                "challan_id": c[0],
                "vehicle_number": c[1],
                "violation_type": c[2],
                "fine_amount": c[3],
                "violation_timestamp": c[4],
                "blockchain_timestamp": c[5],
                "ipfs_cid": c[6],
                "evidence_hash": c[7].hex(),
                "status": CHALLAN_STATUS.get(c[8], "Unknown"),
                "created_by": c[9],
                "verified_by": c[10],
                "dispute_resolved_by": c[11],
                "payment_tx_ref": c[12].hex() if c[12] != b"\x00" * 32 else None,
                "paid_at": c[13],
            }
        except Exception as e:
            raise BlockchainError(f"get_challan_from_chain: {e}")

    async def get_challan_counter(self) -> int:
        try:
            return int(await self.contract.functions.challanCounter().call())
        except Exception as e:
            raise BlockchainError(f"get_challan_counter: {e}")

    async def get_transaction_receipt(self, tx_hash: str) -> dict[str, Any] | None:
        try:
            r = await self.w3.eth.get_transaction_receipt(tx_hash)
            if r:
                return {
                    "block_number": r["blockNumber"],
                    "gas_used": r["gasUsed"],
                    "status": "confirmed" if r["status"] == 1 else "failed",
                }
            return None
        except Exception:
            return None

    async def is_connected(self) -> bool:
        try:
            return await self.w3.is_connected()
        except Exception:
            return False


async def get_blockchain_service() -> BlockchainService:
    return await BlockchainService.get_instance()
