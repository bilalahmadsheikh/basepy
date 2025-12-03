from web3 import Web3

# Constants
BASE_MAINNET_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532

BASE_MAINNET_RPC_URLS = [
    "https://mainnet.base.org",
    "https://base.gateway.tenderly.co",
    "https://base.publicnode.com",
]

BASE_SEPOLIA_RPC_URLS = [
    "https://sepolia.base.org",
    "https://base-sepolia.gateway.tenderly.co",
    "https://base-sepolia.publicnode.com",
]

def to_wei(amount, unit="ether"):
    """Converts a value to Wei."""
    return Web3.to_wei(amount, unit)

def from_wei(amount, unit="ether"):
    """Converts a value from Wei."""
    return Web3.from_wei(amount, unit)

def is_address(address):
    """Checks if the address is valid."""
    return Web3.is_address(address)

def to_checksum_address(address):
    """Returns the checksummed address."""
    return Web3.to_checksum_address(address)
