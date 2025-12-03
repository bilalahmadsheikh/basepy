from eth_account import Account
import secrets
from .exceptions import WalletError

class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = Account.create(secrets.token_hex(32))

    @property
    def address(self):
        """Returns the wallet address."""
        return self.account.address

    @property
    def private_key(self):
        """Returns the private key."""
        return self.account.key.hex()

    @classmethod
    def create(cls):
        """Creates a new random wallet."""
        return cls()

    @classmethod
    def from_private_key(cls, private_key):
        """Imports a wallet from a private key."""
        try:
            return cls(private_key)
        except Exception as e:
            raise WalletError(f"Invalid private key: {e}")

    @classmethod
    def from_mnemonic(cls, mnemonic):
        """Imports a wallet from a mnemonic phrase."""
        try:
            Account.enable_unaudited_hdwallet_features()
            account = Account.from_mnemonic(mnemonic)
            return cls(account.key.hex())
        except Exception as e:
            raise WalletError(f"Invalid mnemonic: {e}")

    def sign_transaction(self, transaction):
        """Signs a transaction dictionary."""
        return self.account.sign_transaction(transaction)
