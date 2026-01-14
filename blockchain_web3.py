"""
Blockchain & Web3 Integration - Week 8 Elite Tier
NFT minting, crypto payments, smart contracts, IPFS storage, token gating
"""

import hashlib
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NFTMetadata:
    """NFT metadata structure."""
    name: str
    description: str
    image_url: str
    content_type: str
    attributes: List[Dict]
    creator: str
    royalty_percentage: float = 5.0
    
    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "image": self.image_url,
            "content_type": self.content_type,
            "attributes": self.attributes,
            "creator": self.creator,
            "royalty_info": {
                "royalty_percentage": self.royalty_percentage,
                "royalty_address": self.creator
            }
        })


class NFTMinter:
    """NFT minting service for AI-generated content."""
    
    def __init__(self, network: str = "polygon"):
        self.network = network  # ethereum, polygon, solana
        self.minted_nfts: Dict[str, Dict] = {}
        self.contract_address = "0x..." if network == "ethereum" else "0x..."
        
    def mint_content_nft(self, content: str, metadata: NFTMetadata, creator_wallet: str) -> Dict:
        """Mint AI-generated content as NFT."""
        nft_id = str(uuid.uuid4())
        
        # Upload to IPFS
        ipfs_hash = self._upload_to_ipfs(content)
        metadata.image_url = f"ipfs://{ipfs_hash}"
        
        # Upload metadata to IPFS
        metadata_hash = self._upload_metadata_to_ipfs(metadata.to_json())
        
        # Create NFT record
        nft = {
            "nft_id": nft_id,
            "token_id": len(self.minted_nfts) + 1,
            "contract_address": self.contract_address,
            "network": self.network,
            "creator": creator_wallet,
            "content_hash": ipfs_hash,
            "metadata_uri": f"ipfs://{metadata_hash}",
            "royalty_percentage": metadata.royalty_percentage,
            "minted_at": time.time(),
            "status": "minted"
        }
        
        self.minted_nfts[nft_id] = nft
        
        # Simulate blockchain transaction
        tx_hash = self._create_mint_transaction(nft)
        nft["transaction_hash"] = tx_hash
        
        return nft
    
    def _upload_to_ipfs(self, content: str) -> str:
        """Upload content to IPFS."""
        # In production: use actual IPFS client (ipfshttpclient, Pinata API)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        ipfs_hash = f"Qm{content_hash[:44]}"  # Mock IPFS hash
        
        return ipfs_hash
    
    def _upload_metadata_to_ipfs(self, metadata_json: str) -> str:
        """Upload metadata JSON to IPFS."""
        metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        return f"Qm{metadata_hash[:44]}"
    
    def _create_mint_transaction(self, nft: Dict) -> str:
        """Create blockchain mint transaction."""
        # In production: use web3.py or ethers.js
        tx_data = {
            "to": nft["contract_address"],
            "function": "mintNFT",
            "args": [nft["creator"], nft["metadata_uri"]],
            "network": self.network
        }
        
        tx_hash = hashlib.sha256(json.dumps(tx_data).encode()).hexdigest()
        return f"0x{tx_hash}"
    
    def get_nft_details(self, nft_id: str) -> Optional[Dict]:
        """Get NFT details by ID."""
        return self.minted_nfts.get(nft_id)
    
    def transfer_nft(self, nft_id: str, from_wallet: str, to_wallet: str) -> Dict:
        """Transfer NFT to another wallet."""
        nft = self.minted_nfts.get(nft_id)
        if not nft:
            return {"error": "NFT not found"}
        
        # Create transfer transaction
        tx_hash = hashlib.sha256(f"{nft_id}{from_wallet}{to_wallet}{time.time()}".encode()).hexdigest()
        
        return {
            "nft_id": nft_id,
            "from": from_wallet,
            "to": to_wallet,
            "transaction_hash": f"0x{tx_hash}",
            "status": "transferred"
        }


class CryptoPaymentGateway:
    """Accept crypto payments (BTC, ETH, USDC)."""
    
    def __init__(self):
        self.supported_currencies = ["BTC", "ETH", "USDC", "MATIC"]
        self.payment_addresses: Dict[str, str] = {}
        self.payments: Dict[str, Dict] = {}
    
    def create_payment_request(self, amount: float, currency: str, order_id: str) -> Dict:
        """Create crypto payment request."""
        if currency not in self.supported_currencies:
            return {"error": f"Currency {currency} not supported"}
        
        payment_id = str(uuid.uuid4())
        
        # Generate deposit address (in production: use HD wallet)
        deposit_address = self._generate_deposit_address(currency)
        
        payment = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "deposit_address": deposit_address,
            "status": "pending",
            "created_at": time.time(),
            "expires_at": time.time() + 3600,  # 1 hour expiry
            "confirmations_required": 3 if currency == "BTC" else 12,
            "current_confirmations": 0
        }
        
        self.payments[payment_id] = payment
        return payment
    
    def _generate_deposit_address(self, currency: str) -> str:
        """Generate deposit address for currency."""
        addresses = {
            "BTC": "bc1q" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:40],
            "ETH": "0x" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:40],
            "USDC": "0x" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:40],
            "MATIC": "0x" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:40]
        }
        return addresses.get(currency, "")
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """Check payment status on blockchain."""
        payment = self.payments.get(payment_id)
        if not payment:
            return {"error": "Payment not found"}
        
        # In production: check blockchain for transactions to deposit address
        # Simulate confirmation progress
        if payment["status"] == "pending":
            payment["current_confirmations"] = min(
                payment["confirmations_required"],
                payment.get("current_confirmations", 0) + 1
            )
            
            if payment["current_confirmations"] >= payment["confirmations_required"]:
                payment["status"] = "confirmed"
                payment["confirmed_at"] = time.time()
        
        return payment
    
    def process_lightning_payment(self, invoice: str) -> Dict:
        """Process Bitcoin Lightning Network payment."""
        payment_id = str(uuid.uuid4())
        
        payment = {
            "payment_id": payment_id,
            "type": "lightning",
            "invoice": invoice,
            "status": "paid",  # Lightning is instant
            "paid_at": time.time()
        }
        
        return payment


class SmartContractManager:
    """Manage smart contracts for content licensing and royalties."""
    
    def __init__(self, network: str = "polygon"):
        self.network = network
        self.contracts: Dict[str, Dict] = {}
    
    def deploy_licensing_contract(self, content_id: str, license_terms: Dict) -> Dict:
        """Deploy smart contract for content licensing."""
        contract_id = str(uuid.uuid4())
        
        contract = {
            "contract_id": contract_id,
            "type": "licensing",
            "content_id": content_id,
            "network": self.network,
            "terms": license_terms,
            "creator": license_terms.get("creator_address"),
            "royalty_percentage": license_terms.get("royalty_percentage", 10),
            "license_price": license_terms.get("price", 0),
            "deployed_at": time.time(),
            "contract_address": f"0x{hashlib.sha256(contract_id.encode()).hexdigest()[:40]}",
            "active": True
        }
        
        self.contracts[contract_id] = contract
        return contract
    
    def execute_license_purchase(self, contract_id: str, buyer_address: str, payment_amount: float) -> Dict:
        """Execute license purchase via smart contract."""
        contract = self.contracts.get(contract_id)
        if not contract:
            return {"error": "Contract not found"}
        
        if payment_amount < contract["license_price"]:
            return {"error": "Insufficient payment"}
        
        # Calculate royalty distribution
        royalty_amount = payment_amount * (contract["royalty_percentage"] / 100)
        creator_payment = payment_amount - royalty_amount
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "contract_id": contract_id,
            "buyer": buyer_address,
            "amount_paid": payment_amount,
            "creator_receives": creator_payment,
            "royalty_amount": royalty_amount,
            "timestamp": time.time(),
            "license_granted": True
        }
        
        return transaction
    
    def get_royalty_earnings(self, creator_address: str) -> Dict:
        """Get accumulated royalty earnings for creator."""
        total_royalties = 0
        transactions = []
        
        for contract in self.contracts.values():
            if contract.get("creator") == creator_address:
                # Calculate earnings from this contract
                # In production: query blockchain events
                pass
        
        return {
            "creator_address": creator_address,
            "total_royalties": total_royalties,
            "pending_withdrawal": total_royalties,
            "transactions": transactions
        }


class IPFSStorageManager:
    """Decentralized storage using IPFS."""
    
    def __init__(self, pinata_api_key: str = None):
        self.pinata_api_key = pinata_api_key
        self.pinned_files: Dict[str, Dict] = {}
    
    def upload_file(self, content: bytes, filename: str, metadata: Dict = None) -> Dict:
        """Upload file to IPFS and pin it."""
        content_hash = hashlib.sha256(content).hexdigest()
        ipfs_hash = f"Qm{content_hash[:44]}"
        
        file_record = {
            "ipfs_hash": ipfs_hash,
            "filename": filename,
            "size_bytes": len(content),
            "metadata": metadata or {},
            "pinned": True,
            "uploaded_at": time.time(),
            "gateway_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        }
        
        self.pinned_files[ipfs_hash] = file_record
        
        # In production: actually upload to IPFS via Pinata or local node
        # import ipfshttpclient
        # client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
        # res = client.add(content)
        
        return file_record
    
    def retrieve_file(self, ipfs_hash: str) -> Optional[bytes]:
        """Retrieve file from IPFS."""
        # In production: fetch from IPFS
        # client = ipfshttpclient.connect()
        # content = client.cat(ipfs_hash)
        
        return b"File content from IPFS"
    
    def pin_file(self, ipfs_hash: str) -> Dict:
        """Pin existing file to ensure persistence."""
        return {
            "ipfs_hash": ipfs_hash,
            "pinned": True,
            "pin_timestamp": time.time()
        }


class TokenGatingService:
    """Token-gated access to premium features."""
    
    def __init__(self):
        self.gated_features: Dict[str, Dict] = {}
        self.user_tokens: Dict[str, List[str]] = {}
    
    def create_gated_feature(self, feature_id: str, required_tokens: List[str], access_type: str = "any") -> Dict:
        """Create token-gated feature."""
        feature = {
            "feature_id": feature_id,
            "required_tokens": required_tokens,  # NFT contract addresses or token IDs
            "access_type": access_type,  # "any" or "all"
            "active": True,
            "created_at": time.time()
        }
        
        self.gated_features[feature_id] = feature
        return feature
    
    def check_access(self, user_wallet: str, feature_id: str) -> Dict:
        """Check if user has access to gated feature."""
        feature = self.gated_features.get(feature_id)
        if not feature:
            return {"access_granted": False, "error": "Feature not found"}
        
        # Check user's token holdings
        user_tokens = self.user_tokens.get(user_wallet, [])
        required_tokens = feature["required_tokens"]
        
        if feature["access_type"] == "any":
            has_access = any(token in user_tokens for token in required_tokens)
        else:  # "all"
            has_access = all(token in user_tokens for token in required_tokens)
        
        return {
            "access_granted": has_access,
            "feature_id": feature_id,
            "user_wallet": user_wallet,
            "tokens_held": user_tokens,
            "tokens_required": required_tokens
        }
    
    def register_user_tokens(self, user_wallet: str, token_addresses: List[str]):
        """Register user's token holdings."""
        # In production: verify on-chain ownership
        self.user_tokens[user_wallet] = token_addresses


class Web3Analytics:
    """Analytics for Web3 activities."""
    
    def get_nft_stats(self, creator_address: str) -> Dict:
        """Get NFT minting and sales stats."""
        return {
            "creator_address": creator_address,
            "nfts_minted": 47,
            "total_sales": 23,
            "total_volume_eth": 12.5,
            "total_royalties_eth": 1.25,
            "avg_sale_price_eth": 0.54,
            "unique_collectors": 18
        }
    
    def get_payment_analytics(self) -> Dict:
        """Get crypto payment analytics."""
        return {
            "total_payments": 234,
            "total_volume_usd": 45678.90,
            "by_currency": {
                "ETH": {"count": 123, "volume_usd": 23456.78},
                "BTC": {"count": 45, "volume_usd": 12345.67},
                "USDC": {"count": 66, "volume_usd": 9876.45}
            },
            "avg_payment_usd": 195.21
        }
