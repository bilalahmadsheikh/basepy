"""
Basic connection example showcasing all BaseClient read features.

This example demonstrates:
- Network connection
- Account data queries
- Block information
- Gas price checks
- Base-specific L1 fee estimation
"""

from basepy.client import BaseClient


def demo_network_info(client):
    """Demonstrate network information queries."""
    print("\n" + "="*60)
    print("NETWORK INFORMATION")
    print("="*60)
    
    chain_id = client.get_chain_id()
    is_mainnet = chain_id == 8453
    network_name = "Base Mainnet" if is_mainnet else f"Base Sepolia (testnet)" if chain_id == 84532 else f"Unknown (Chain ID: {chain_id})"
    
    print(f"Network: {network_name}")
    print(f"Chain ID: {chain_id}")
    print(f"Connected: {client.is_connected()}")


def demo_block_info(client):
    """Demonstrate block information queries."""
    print("\n" + "="*60)
    print("BLOCK INFORMATION")
    print("="*60)
    
    # Get current block number
    block_number = client.get_block_number()
    print(f"Current Block Number: {block_number:,}")
    
    # Get latest block details
    block = client.get_block('latest')
    print(f"\nLatest Block Details:")
    print(f"  Hash: {block['hash'].hex()}")
    print(f"  Timestamp: {block['timestamp']}")
    print(f"  Gas Used: {block['gasUsed']:,} / {block['gasLimit']:,}")
    print(f"  Transactions: {len(block['transactions'])}")
    
    # Get base fee (EIP-1559)
    if 'baseFeePerGas' in block:
        base_fee_gwei = block['baseFeePerGas'] / 10**9
        print(f"  Base Fee: {base_fee_gwei:.2f} Gwei")


def demo_account_info(client, address):
    """Demonstrate account data queries."""
    print("\n" + "="*60)
    print("ACCOUNT INFORMATION")
    print("="*60)
    
    print(f"Address: {address}")
    
    # Get balance
    balance_wei = client.get_balance(address)
    balance_eth = balance_wei / 10**18
    print(f"Balance: {balance_eth:.6f} ETH ({balance_wei:,} Wei)")
    
    # Get transaction count (nonce)
    tx_count = client.get_transaction_count(address)
    print(f"Transactions Sent: {tx_count}")
    
    # Check if contract
    is_contract = client.is_contract(address)
    account_type = "Smart Contract" if is_contract else "Externally Owned Account (EOA)"
    print(f"Account Type: {account_type}")
    
    if is_contract:
        code = client.get_code(address)
        print(f"Contract Code Size: {len(code)} bytes")


def demo_gas_prices(client):
    """Demonstrate gas price queries."""
    print("\n" + "="*60)
    print("GAS PRICES")
    print("="*60)
    
    # Get current gas price
    gas_price = client.get_gas_price()
    gas_price_gwei = gas_price / 10**9
    print(f"Current Gas Price: {gas_price_gwei:.2f} Gwei")
    
    # Get base fee (EIP-1559)
    base_fee = client.get_base_fee()
    base_fee_gwei = base_fee / 10**9
    print(f"Base Fee (EIP-1559): {base_fee_gwei:.2f} Gwei")
    
    # Estimate cost for simple ETH transfer (21,000 gas)
    simple_transfer_cost = 21000 * gas_price
    simple_transfer_eth = simple_transfer_cost / 10**18
    print(f"\nSimple ETH Transfer Cost:")
    print(f"  Gas Needed: 21,000")
    print(f"  L2 Cost: ~{simple_transfer_eth:.6f} ETH")


def demo_l1_fee(client):
    """Demonstrate Base-specific L1 fee estimation."""
    print("\n" + "="*60)
    print("BASE L1 FEE ESTIMATION (OP Stack Feature)")
    print("="*60)
    
    # Example: Simple transfer has minimal calldata
    simple_transfer_data = b''  # No calldata for simple ETH transfer
    
    try:
        l1_fee = client.get_l1_fee(simple_transfer_data)
        l1_fee_eth = l1_fee / 10**18
        
        print(f"L1 Data Fee (empty calldata): {l1_fee_eth:.8f} ETH")
        print(f"\nNote: Base transactions have TWO costs:")
        print(f"  1. L2 Execution Fee (normal gas)")
        print(f"  2. L1 Data Fee (posting to Ethereum mainnet)")
        print(f"\nTotal Cost = L2 Fee + L1 Fee")
    except Exception as e:
        print(f"Could not estimate L1 fee: {e}")


def demo_testnet_connection():
    """Demonstrate connecting to Base Sepolia testnet."""
    print("\n" + "="*60)
    print("TESTNET CONNECTION EXAMPLE")
    print("="*60)
    
    try:
        testnet_client = BaseClient(chain_id=84532)
        print(f"Connected to Base Sepolia (Testnet)")
        print(f"Chain ID: {testnet_client.get_chain_id()}")
        print(f"Block Number: {testnet_client.get_block_number():,}")
    except Exception as e:
        print(f"Failed to connect to testnet: {e}")


def main():
    """Main example showcasing all BaseClient features."""
    print("="*60)
    print("BASE PYTHON SDK - BASIC CONNECTION EXAMPLE")
    print("="*60)
    
    try:
        # Connect to Base Mainnet
        client = BaseClient()
        print("✅ Successfully connected to Base Mainnet!")
        
        # Demo 1: Network Information
        demo_network_info(client)
        
        # Demo 2: Block Information
        demo_block_info(client)
        
        # Demo 3: Account Information
        # Using a well-known Base address as an example
        example_address = "0x835678a611B28684005a5e2233695fB6cbbB0007"  # WETH on Base
        demo_account_info(client, example_address)
        
        # Demo 4: Gas Prices
        demo_gas_prices(client)
        
        # Demo 5: Base-specific L1 Fee
        demo_l1_fee(client)
        
        # Demo 6: Testnet Connection
        demo_testnet_connection()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()