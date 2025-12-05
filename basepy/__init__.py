# File: basepy/__init__.py
"""BasePy SDK - Python SDK for Base blockchain with comprehensive ERC-20 support"""

# Core client
from .client import BaseClient, Config, Metrics, CircuitBreaker, Cache, RateLimiter

# Wallet management
from .wallet import Wallet

# Transactions
from .transactions import Transaction

# Smart contracts
from .contracts import Contract, ERC20Contract  # NEW: ERC20Contract

# Token standards
from .standards import ERC20

# Utility functions - Base utilities
from .utils import to_wei, from_wei, is_address, to_checksum_address
from .utils import BASE_MAINNET_RPC_URLS, BASE_SEPOLIA_RPC_URLS, BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID

# NEW: ERC-20 utilities
from .utils import (
    # Token formatting
    format_token_amount,
    parse_token_amount,
    format_token_balance,
    
    # Address utilities
    normalize_address,
    addresses_equal,
    shorten_address,
    is_zero_address,
    
    # ERC-20 decoding
    decode_erc20_transfer_log,
    decode_all_erc20_transfers,
    is_erc20_transfer_log,
    
    # Transfer analysis
    filter_transfers_by_address,
    filter_transfers_by_token,
    get_transfer_direction,
    calculate_balance_change,
)

# NEW: ABI utilities
from .abis import (
    ERC20_ABI,
    get_common_tokens,
    get_token_addresses,
    is_erc20_transfer_topic,
    ERC20_TRANSFER_TOPIC,
)

__version__ = "1.1.0"  # Updated version for new ERC-20 features

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
    "ERC20Contract",  # NEW

    # Token standards
    "ERC20",

    # Base utilities
    "to_wei",
    "from_wei",
    "is_address",
    "to_checksum_address",
    "BASE_MAINNET_RPC_URLS",
    "BASE_SEPOLIA_RPC_URLS",
    "BASE_MAINNET_CHAIN_ID",
    "BASE_SEPOLIA_CHAIN_ID",
    
    # NEW: Token formatting
    "format_token_amount",
    "parse_token_amount",
    "format_token_balance",
    
    # NEW: Address utilities
    "normalize_address",
    "addresses_equal",
    "shorten_address",
    "is_zero_address",
    
    # NEW: ERC-20 decoding
    "decode_erc20_transfer_log",
    "decode_all_erc20_transfers",
    "is_erc20_transfer_log",
    
    # NEW: Transfer analysis
    "filter_transfers_by_address",
    "filter_transfers_by_token",
    "get_transfer_direction",
    "calculate_balance_change",
    
    # NEW: ABI utilities
    "ERC20_ABI",
    "get_common_tokens",
    "get_token_addresses",
    "is_erc20_transfer_topic",
    "ERC20_TRANSFER_TOPIC",
]