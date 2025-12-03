from .exceptions import ContractError

class Contract:
    def __init__(self, client, address, abi):
        self.client = client
        self.address = address
        self.abi = abi
        self.contract = self.client.w3.eth.contract(address=address, abi=abi)

    def call(self, function_name, *args):
        """Calls a read-only function of the contract."""
        try:
            func = getattr(self.contract.functions, function_name)
            return func(*args).call()
        except Exception as e:
            raise ContractError(f"Failed to call function {function_name}: {e}")

    def transact(self, wallet, function_name, *args, gas=None, value=0):
        """Sends a transaction to a contract function."""
        try:
            func = getattr(self.contract.functions, function_name)
            nonce = self.client.w3.eth.get_transaction_count(wallet.address)
            
            tx_params = {
                'chainId': self.client.get_chain_id(),
                'gasPrice': self.client.w3.eth.gas_price,
                'nonce': nonce,
                'value': value
            }
            
            if gas:
                tx_params['gas'] = gas
            else:
                 # Estimate gas
                tx_params['gas'] = func(*args).estimate_gas({'from': wallet.address, 'value': value})

            tx = func(*args).build_transaction(tx_params)
            
            signed_tx = wallet.sign_transaction(tx)
            tx_hash = self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return self.client.w3.to_hex(tx_hash)
        except Exception as e:
            raise ContractError(f"Failed to transact with function {function_name}: {e}")
