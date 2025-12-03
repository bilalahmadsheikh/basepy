from .contracts import Contract
from .abis import ERC20_ABI

class ERC20(Contract):
    def __init__(self, client, address):
        super().__init__(client, address, ERC20_ABI)

    def balance_of(self, address):
        """Returns the token balance of the address."""
        return self.call("balanceOf", address)

    def transfer(self, wallet, to_address, amount):
        """Transfers tokens to a specified address."""
        # Note: Amount should be in raw units (Wei equivalent).
        # Use utils.to_wei if you have a decimal amount and know the decimals.
        return self.transact(wallet, "transfer", to_address, amount)

    def approve(self, wallet, spender_address, amount):
        """Approves a spender to spend a specific amount of tokens."""
        return self.transact(wallet, "approve", spender_address, amount)

    def get_decimals(self):
        """Returns the token decimals."""
        return self.call("decimals")

    def get_symbol(self):
        """Returns the token symbol."""
        return self.call("symbol")
    
    def get_name(self):
        try:
            return self.call("name")
        except Exception:
            return None

    def get_total_supply(self):
        try:
            return self.call("totalSupply")
        except Exception:
            return None

