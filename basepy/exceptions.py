class BasePyError(Exception):
    """Base exception for BasePy SDK."""
    pass

class ConnectionError(BasePyError):
    """Raised when connection to Base RPC fails."""
    pass

class WalletError(BasePyError):
    """Raised when there is an issue with wallet operations."""
    pass

class TransactionError(BasePyError):
    """Raised when a transaction fails."""
    pass

class ContractError(BasePyError):
    """Raised when a smart contract interaction fails."""
    pass
