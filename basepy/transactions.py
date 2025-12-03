"""
Transaction operations for Base blockchain.

This module handles both:
1. READ operations - Query transaction data (no wallet needed)
2. WRITE operations - Send transactions (requires wallet)

IMPORTANT: All transaction data is automatically converted from HexBytes to
standard Python types (strings, ints) for JSON serialization compatibility.
"""

from typing import Optional, Dict, Any, Union
from .exceptions import TransactionError
from .utils import to_wei
import time
import logging

logger = logging.getLogger(__name__)


def _convert_hex_bytes(obj):
    """
    Recursively convert HexBytes objects to hex strings for JSON serialization.
    
    Args:
        obj: Any object that may contain HexBytes
        
    Returns:
        Object with all HexBytes converted to hex strings
        
    Note:
        This is critical for API endpoints that return transaction data,
        as HexBytes objects cannot be JSON serialized directly.
    """
    if hasattr(obj, 'hex'):
        # Convert HexBytes to hex string
        return obj.hex()
    elif isinstance(obj, dict):
        # Recursively convert dictionary values
        return {k: _convert_hex_bytes(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        # Recursively convert list/tuple items
        return [_convert_hex_bytes(item) for item in obj]
    elif isinstance(obj, bytes):
        # Convert raw bytes to hex string
        return '0x' + obj.hex()
    return obj


class Transaction:
    """
    Unified transaction interface for reading and sending transactions.
    
    PUBLICLY ACCESSIBLE - No authentication required for read operations.
    
    For READ operations (no wallet needed):
        >>> from basepy import BaseClient, Transaction
        >>> client = BaseClient()
        >>> tx = Transaction(client)
        >>> details = tx.get("0x123...")
        >>> tx.wait_for_confirmation("0x123...")
    
    For WRITE operations (wallet required):
        >>> from basepy import BaseClient, Wallet, Transaction
        >>> client = BaseClient()
        >>> wallet = Wallet(private_key="0x...", client=client)
        >>> tx = Transaction(client, wallet)
        >>> tx_hash = tx.send_eth("0xRecipient...", 0.1)
    
    Note:
        All returned data is JSON-serializable. HexBytes objects are
        automatically converted to hex strings.
    """
    
    def __init__(self, client, wallet=None):
        """
        Initialize Transaction handler.
        
        Args:
            client: BaseClient instance (required)
            wallet: Optional Wallet instance (only required for sending transactions)
            
        Note:
            Any user can create a Transaction instance with just a client
            to query transaction data. No private keys or authentication needed.
        """
        self.client = client
        self.wallet = wallet

    # =========================================================================
    # READ OPERATIONS - Query transaction data (PUBLIC ACCESS - no wallet needed)
    # =========================================================================

    def get(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction details by hash.
        
        PUBLIC ACCESS - Anyone can query any transaction on the blockchain.
        
        Args:
            tx_hash: Transaction hash (with or without 0x prefix)
            
        Returns:
            dict: Transaction data containing (all JSON-serializable):
                - hash: Transaction hash (str)
                - from: Sender address (str)
                - to: Recipient address (str)
                - value: Amount in Wei (int)
                - gas: Gas limit (int)
                - gasPrice: Gas price in Wei (int)
                - nonce: Transaction nonce (int)
                - input: Transaction data/calldata (str)
                - blockNumber: Block number or None if pending (int or None)
                - blockHash: Block hash or None if pending (str or None)
                
        Raises:
            TransactionError: If transaction not found
            
        Example:
            >>> tx = transaction.get("0x123...")
            >>> print(f"From: {tx['from']}")
            >>> print(f"To: {tx['to']}")
            >>> print(f"Value: {tx['value'] / 10**18} ETH")
            
        Note:
            All HexBytes objects are automatically converted to hex strings
            for JSON serialization compatibility.
        """
        try:
            # Normalize hash - add 0x prefix if missing
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            
            # Get transaction from blockchain
            tx = self.client.w3.eth.get_transaction(tx_hash)
            
            # Convert to dict and handle HexBytes
            tx_dict = dict(tx)
            
            # Convert all HexBytes to JSON-serializable formats
            return _convert_hex_bytes(tx_dict)
            
        except Exception as e:
            logger.error(f"Failed to get transaction {tx_hash}: {e}")
            raise TransactionError(f"Transaction not found: {tx_hash}") from e

    def get_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction receipt (only available after transaction is mined).
        
        PUBLIC ACCESS - Anyone can query any transaction receipt.
        
        Args:
            tx_hash: Transaction hash (with or without 0x prefix)
            
        Returns:
            dict: Transaction receipt containing (all JSON-serializable):
                - transactionHash: Transaction hash (str)
                - status: 1 if success, 0 if failed (int)
                - blockNumber: Block number (int)
                - gasUsed: Actual gas used (int)
                - effectiveGasPrice: Actual gas price paid (int)
                - logs: Event logs emitted (list)
                - contractAddress: Address of deployed contract or None (str or None)
                - from: Sender address (str)
                - to: Recipient address (str)
                
        Raises:
            TransactionError: If receipt not found (transaction pending or doesn't exist)
            
        Example:
            >>> receipt = transaction.get_receipt("0x123...")
            >>> if receipt['status'] == 1:
            ...     print("Transaction successful!")
            >>> print(f"Gas used: {receipt['gasUsed']}")
            >>> print(f"Block: {receipt['blockNumber']}")
            
        Note:
            Receipts are only available AFTER a transaction has been mined.
            For pending transactions, this will raise TransactionError.
            All HexBytes are converted to hex strings for JSON compatibility.
        """
        try:
            # Normalize hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            
            # Get receipt from blockchain
            receipt = self.client.w3.eth.get_transaction_receipt(tx_hash)
            
            # Convert to dict and handle HexBytes
            receipt_dict = dict(receipt)
            
            # Convert all HexBytes to JSON-serializable formats
            return _convert_hex_bytes(receipt_dict)
            
        except Exception as e:
            logger.error(f"Failed to get receipt for {tx_hash}: {e}")
            raise TransactionError(
                f"Receipt not found (transaction may be pending): {tx_hash}"
            ) from e

    def get_status(self, tx_hash: str) -> str:
        """
        Get human-readable transaction status.
        
        PUBLIC ACCESS - Anyone can check any transaction status.
        
        Args:
            tx_hash: Transaction hash (with or without 0x prefix)
            
        Returns:
            str: One of:
                - "pending": Transaction is in mempool, not yet mined
                - "confirmed": Transaction succeeded (status = 1)
                - "failed": Transaction reverted (status = 0)
                - "not_found": Transaction doesn't exist on the blockchain
                
        Example:
            >>> status = transaction.get_status("0x123...")
            >>> if status == "confirmed":
            ...     print("Transaction was successful!")
            >>> elif status == "failed":
            ...     print("Transaction failed/reverted!")
            >>> elif status == "pending":
            ...     print("Waiting for miners to process...")
            
        Note:
            This method never raises exceptions - it returns "not_found"
            if the transaction doesn't exist.
        """
        try:
            # Try to get receipt first (fastest check if mined)
            receipt = self.get_receipt(tx_hash)
            return "confirmed" if receipt['status'] == 1 else "failed"
        except TransactionError:
            # No receipt - check if transaction exists in mempool
            try:
                tx = self.get(tx_hash)
                # Transaction exists but no receipt = still pending
                return "pending"
            except TransactionError:
                # Transaction doesn't exist at all
                return "not_found"

    def wait_for_confirmation(
        self, 
        tx_hash: str, 
        timeout: int = 120,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        Wait for transaction to be mined and return receipt.
        
        PUBLIC ACCESS - Anyone can wait for any transaction confirmation.
        
        Args:
            tx_hash: Transaction hash (with or without 0x prefix)
            timeout: Maximum seconds to wait (default: 120)
            poll_interval: Seconds between status checks (default: 2.0)
            
        Returns:
            dict: Transaction receipt (JSON-serializable, see get_receipt())
            
        Raises:
            TransactionError: If timeout reached, transaction failed, or not found
            
        Example:
            >>> # After sending a transaction
            >>> tx_hash = wallet.send_eth("0x...", 0.1)
            >>> print("Waiting for confirmation...")
            >>> receipt = transaction.wait_for_confirmation(tx_hash)
            >>> print(f"Confirmed in block {receipt['blockNumber']}")
            
            >>> # Custom timeout for urgent transactions
            >>> receipt = transaction.wait_for_confirmation(tx_hash, timeout=30)
            
        Note:
            This blocks execution until the transaction is mined or timeout.
            On Base, most transactions confirm within 2-5 seconds.
            All returned data is JSON-serializable.
        """
        # Normalize hash
        if not tx_hash.startswith('0x'):
            tx_hash = '0x' + tx_hash
        
        logger.info(f"Waiting for transaction {tx_hash} to be mined...")
        start_time = time.time()
        
        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TransactionError(
                    f"Transaction {tx_hash} not confirmed after {timeout} seconds. "
                    f"It may still be pending - check status manually."
                )
            
            # Check current status
            status = self.get_status(tx_hash)
            
            if status == "confirmed":
                logger.info(f"Transaction {tx_hash} confirmed!")
                return self.get_receipt(tx_hash)
            elif status == "failed":
                receipt = self.get_receipt(tx_hash)
                raise TransactionError(
                    f"Transaction {tx_hash} failed in block {receipt['blockNumber']}"
                )
            elif status == "not_found":
                raise TransactionError(
                    f"Transaction {tx_hash} not found on the blockchain"
                )
            
            # Still pending, wait and retry
            logger.debug(f"Transaction pending... ({elapsed:.1f}s elapsed)")
            time.sleep(poll_interval)

    # =========================================================================
    # WRITE OPERATIONS - Send transactions (REQUIRES WALLET - authentication needed)
    # =========================================================================

    def _require_wallet(self):
        """
        Check if wallet is available for signing transactions.
        
        SECURITY NOTE: Write operations require a wallet with private key.
        Only the wallet owner can send transactions from their address.
        
        Raises:
            TransactionError: If wallet is not initialized
        """
        if self.wallet is None:
            raise TransactionError(
                "Wallet required for sending transactions. "
                "Initialize Transaction with a Wallet instance: "
                "Transaction(client, wallet)"
            )

    def send_eth(
        self, 
        to_address: str, 
        amount: float, 
        unit: str = "ether", 
        gas: int = 21000,
        wait_for_receipt: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Send ETH to a specified address.
        
        REQUIRES WALLET - Only the wallet owner can call this.
        
        Args:
            to_address: Recipient address (must be valid Ethereum address)
            amount: Amount to send (float)
            unit: Unit of amount - "wei", "gwei", or "ether" (default: "ether")
            gas: Gas limit (default: 21000 for simple transfers)
            wait_for_receipt: If True, wait for confirmation (default: False)
            
        Returns:
            str: Transaction hash if wait_for_receipt=False
            dict: Transaction receipt if wait_for_receipt=True (JSON-serializable)
            
        Raises:
            TransactionError: If wallet missing, insufficient balance, or sending fails
            
        Example:
            >>> # Send 0.1 ETH (returns immediately)
            >>> tx_hash = transaction.send_eth("0xRecipient...", 0.1)
            >>> print(f"Transaction sent: {tx_hash}")
            
            >>> # Send and wait for confirmation
            >>> receipt = transaction.send_eth(
            ...     "0xRecipient...", 
            ...     0.1, 
            ...     wait_for_receipt=True
            ... )
            >>> print(f"Confirmed in block {receipt['blockNumber']}")
            
            >>> # Send using different units
            >>> tx_hash = transaction.send_eth("0x...", 1000000, unit="gwei")
            
        Note:
            - Check wallet balance first: client.get_balance(wallet.address)
            - Transaction hash is returned immediately, confirmation takes 2-5s
            - All returned data is JSON-serializable
        """
        self._require_wallet()
        
        try:
            # Convert amount to Wei
            value = to_wei(amount, unit)
            
            # Get current nonce for sender
            nonce = self.client.w3.eth.get_transaction_count(self.wallet.address)
            
            # Build transaction
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': value,
                'gas': gas,
                'gasPrice': self.client.w3.eth.gas_price,
                'chainId': self.client.get_chain_id()
            }
            
            # Sign with wallet private key
            signed_tx = self.wallet.sign_transaction(tx)
            
            # Send to network
            tx_hash = self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = self.client.w3.to_hex(tx_hash)
            
            logger.info(f"Sent {amount} {unit} to {to_address}: {tx_hash_hex}")
            
            # Wait for confirmation if requested
            if wait_for_receipt:
                return self.wait_for_confirmation(tx_hash_hex)
            
            return tx_hash_hex
            
        except Exception as e:
            logger.error(f"Failed to send ETH: {e}")
            raise TransactionError(f"Failed to send ETH: {e}") from e

    def send_erc20(
        self, 
        token_address: str, 
        to_address: str, 
        amount: int, 
        abi: list,
        gas: Optional[int] = None,
        wait_for_receipt: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Send ERC-20 tokens to a specified address.
        
        REQUIRES WALLET - Only the wallet owner can call this.
        
        Args:
            token_address: Token contract address
            to_address: Recipient address
            amount: Amount in token's smallest unit 
                   (e.g., for USDC with 6 decimals: 1000000 = 1 USDC)
            abi: Token contract ABI (standard ERC-20)
            gas: Gas limit (None to estimate automatically)
            wait_for_receipt: If True, wait for confirmation
            
        Returns:
            str: Transaction hash if wait_for_receipt=False
            dict: Transaction receipt if wait_for_receipt=True
            
        Raises:
            TransactionError: If wallet missing, insufficient token balance, or sending fails
            
        Example:
            >>> # Send 100 USDC (6 decimals)
            >>> amount = 100 * 10**6
            >>> tx_hash = transaction.send_erc20(
            ...     token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            ...     to_address="0xRecipient...",
            ...     amount=amount,
            ...     abi=usdc_abi
            ... )
            
            >>> # Send with custom gas limit
            >>> tx_hash = transaction.send_erc20(
            ...     token_address="0x...",
            ...     to_address="0x...",
            ...     amount=amount,
            ...     abi=token_abi,
            ...     gas=150000
            ... )
            
        Note:
            - Check token balance first using ERC20 class
            - Amount must be in smallest unit (consider decimals)
            - Gas is auto-estimated if not provided (with 20% buffer)
            - All returned data is JSON-serializable
        """
        self._require_wallet()
        
        try:
            # Initialize contract
            contract = self.client.w3.eth.contract(address=token_address, abi=abi)
            
            # Get current nonce
            nonce = self.client.w3.eth.get_transaction_count(self.wallet.address)
            
            # Build transaction
            tx = contract.functions.transfer(to_address, amount).build_transaction({
                'chainId': self.client.get_chain_id(),
                'gas': gas or 100000,  # Default gas limit for token transfer
                'gasPrice': self.client.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Estimate gas if not provided
            if gas is None:
                try:
                    estimated_gas = self.client.w3.eth.estimate_gas(tx)
                    tx['gas'] = int(estimated_gas * 1.2)  # Add 20% buffer
                    logger.debug(f"Estimated gas: {estimated_gas}, using: {tx['gas']}")
                except Exception as e:
                    logger.warning(f"Gas estimation failed, using default: {e}")
            
            # Sign transaction
            signed_tx = self.wallet.sign_transaction(tx)
            
            # Send to network
            tx_hash = self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = self.client.w3.to_hex(tx_hash)
            
            logger.info(f"Sent {amount} tokens to {to_address}: {tx_hash_hex}")
            
            # Wait for confirmation if requested
            if wait_for_receipt:
                return self.wait_for_confirmation(tx_hash_hex)
            
            return tx_hash_hex
            
        except Exception as e:
            logger.error(f"Failed to send ERC-20: {e}")
            raise TransactionError(f"Failed to send ERC-20: {e}") from e


# ============================================================================
# SUMMARY & ACCESS CONTROL
# ============================================================================
# 
# This module provides BOTH read and write transaction operations:
#
# READ OPERATIONS (PUBLIC ACCESS - no wallet or authentication needed):
# ✅ get(tx_hash) - Get transaction details (anyone can query any transaction)
# ✅ get_receipt(tx_hash) - Get transaction receipt (public blockchain data)
# ✅ get_status(tx_hash) - Get status: pending/confirmed/failed (public)
# ✅ wait_for_confirmation(tx_hash) - Wait for transaction to be mined (public)
#
# WRITE OPERATIONS (REQUIRES WALLET - authentication via private key):
# 🔐 send_eth(to, amount) - Send ETH (requires wallet with private key)
# 🔐 send_erc20(token, to, amount) - Send ERC-20 tokens (requires wallet)
#
# JSON SERIALIZATION:
# ✅ All HexBytes objects automatically converted to hex strings
# ✅ All returned data is JSON-serializable for API endpoints
# ✅ No manual conversion needed in backend code
#
# All operations include:
# ✅ Type hints for better IDE support
# ✅ Comprehensive documentation with examples
# ✅ Proper error handling with descriptive messages
# ✅ Logging for debugging
# ✅ Input validation
# ============================================================================