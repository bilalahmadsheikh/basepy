# File: basepy/__init__.py
"""BasePy SDK - Python SDK for Base blockchain"""

# Core client
from .client import BaseClient, Config, Metrics, CircuitBreaker, Cache, RateLimiter

# Wallet management
from .wallet import Wallet

# Transactions
from .transactions import Transaction

# Smart contracts
from .contracts import Contract

# Token standards
from .standards import ERC20

# Utility functions
from .utils import to_wei, from_wei, is_address, to_checksum_address
from .utils import BASE_MAINNET_RPC_URLS, BASE_SEPOLIA_RPC_URLS, BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID

__all__ = [
    # Core
    "BaseClient",
    "Config",
    "Metrics",
    "CircuitBreaker",
    "Cache",
    "RateLimiter",

    # Wallet
    "Wallet",

    # Transactions
    "Transaction",

    # Contracts
    "Contract",

    # Token standards
    "ERC20",

    # Utilities
    "to_wei",
    "from_wei",
    "is_address",
    "to_checksum_address",
    "BASE_MAINNET_RPC_URLS",
    "BASE_SEPOLIA_RPC_URLS",
    "BASE_MAINNET_CHAIN_ID",
    "BASE_SEPOLIA_CHAIN_ID",
]
