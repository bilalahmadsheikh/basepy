"""
Transaction examples showcasing READ operations.

This demonstrates how to:
- Query transaction details
- Check transaction status
- Wait for confirmations
- Monitor transaction history

NOTE: This example uses READ operations only (no wallet needed).
For SENDING transactions, see send_transaction_example.py
"""

from basepy.client import BaseClient
from basepy.transactions import Transaction
import time


def demo_query_transaction(tx_handler, tx_hash):
    """Demonstrate querying transaction details."""
    print("\n" + "="*60)
    print("QUERY TRANSACTION DETAILS")
    print("="*60)
    print(f"Transaction Hash: {tx_hash}")
    
    try:
        # Get transaction details
        tx = tx_handler.get(tx_hash)
        
        print("\nTransaction Details:")
        print(f"  From: {tx['from']}")
        print(f"  To: {tx['to']}")
        print(f"  Value: {tx['value'] / 10**18:.6f} ETH")
        print(f"  Gas Limit: {tx['gas']:,}")
        print(f"  Gas Price: {tx['gasPrice'] / 10**9:.2f} Gwei")
        print(f"  Nonce: {tx['nonce']}")
        
        if tx['blockNumber']:
            print(f"  Block Number: {tx['blockNumber']:,}")
            print(f"  Status: Mined ✅")
        else:
            print(f"  Status: Pending ⏳")
            
        # Check if it's a contract interaction
        if tx['input'] != '0x':
            print(f"  Contract Interaction: Yes")
            print(f"  Data Length: {len(tx['input'])} characters")
        else:
            print(f"  Type: Simple ETH Transfer")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_get_receipt(tx_handler, tx_hash):
    """Demonstrate getting transaction receipt."""
    print("\n" + "="*60)
    print("GET TRANSACTION RECEIPT")
    print("="*60)
    
    try:
        receipt = tx_handler.get_receipt(tx_hash)
        
        print(f"Transaction: {tx_hash}")
        print(f"\nReceipt Details:")
        print(f"  Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")
        print(f"  Block Number: {receipt['blockNumber']:,}")
        print(f"  Gas Used: {receipt['gasUsed']:,}")
        print(f"  Effective Gas Price: {receipt['effectiveGasPrice'] / 10**9:.2f} Gwei")
        
        # Calculate total cost
        total_cost = receipt['gasUsed'] * receipt['effectiveGasPrice']
        print(f"  Total Cost: {total_cost / 10**18:.8f} ETH")
        
        # Check for contract deployment
        if receipt.get('contractAddress'):
            print(f"  Contract Deployed: {receipt['contractAddress']}")
        
        # Check for logs/events
        if receipt['logs']:
            print(f"  Events Emitted: {len(receipt['logs'])} events")
        else:
            print(f"  Events Emitted: None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   (Receipt only available after transaction is mined)")


def demo_check_status(tx_handler, tx_hash):
    """Demonstrate checking transaction status."""
    print("\n" + "="*60)
    print("CHECK TRANSACTION STATUS")
    print("="*60)
    print(f"Transaction: {tx_hash}")
    
    status = tx_handler.get_status(tx_hash)
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'failed': '❌',
        'not_found': '🔍'
    }
    
    status_messages = {
        'pending': 'Transaction is in the mempool, waiting to be mined',
        'confirmed': 'Transaction was successfully mined and executed',
        'failed': 'Transaction was mined but execution failed (reverted)',
        'not_found': 'Transaction not found on the blockchain'
    }
    
    print(f"\nStatus: {status_emoji.get(status, '❓')} {status.upper()}")
    print(f"Description: {status_messages.get(status, 'Unknown status')}")


def demo_wait_for_confirmation(tx_handler, tx_hash):
    """Demonstrate waiting for transaction confirmation."""
    print("\n" + "="*60)
    print("WAIT FOR TRANSACTION CONFIRMATION")
    print("="*60)
    print(f"Transaction: {tx_hash}")
    print("\nWaiting for confirmation (timeout: 120 seconds)...")
    
    try:
        start_time = time.time()
        receipt = tx_handler.wait_for_confirmation(tx_hash, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Transaction confirmed in {elapsed:.1f} seconds!")
        print(f"   Block Number: {receipt['blockNumber']:,}")
        print(f"   Status: {'Success' if receipt['status'] == 1 else 'Failed'}")
        print(f"   Gas Used: {receipt['gasUsed']:,}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_analyze_transaction_cost(tx_handler, tx_hash, client):
    """Demonstrate analyzing full transaction cost on Base."""
    print("\n" + "="*60)
    print("ANALYZE TRANSACTION COST (Base L2)")
    print("="*60)
    
    try:
        receipt = tx_handler.get_receipt(tx_hash)
        tx = tx_handler.get(tx_hash)
        
        print(f"Transaction: {tx_hash}")
        
        # L2 Execution Cost
        l2_cost = receipt['gasUsed'] * receipt['effectiveGasPrice']
        l2_cost_eth = l2_cost / 10**18
        
        print(f"\n💰 Cost Breakdown:")
        print(f"  L2 Execution Fee:")
        print(f"    Gas Used: {receipt['gasUsed']:,}")
        print(f"    Gas Price: {receipt['effectiveGasPrice'] / 10**9:.2f} Gwei")
        print(f"    L2 Cost: {l2_cost_eth:.8f} ETH")
        
        # L1 Data Fee (Base-specific)
        try:
            if tx['input']:
                l1_fee = client.get_l1_fee(tx['input'])
                l1_fee_eth = l1_fee / 10**18
                
                print(f"\n  L1 Data Fee:")
                print(f"    L1 Cost: {l1_fee_eth:.8f} ETH")
                
                # Total
                total_cost_eth = l2_cost_eth + l1_fee_eth
                print(f"\n  📊 Total Cost: {total_cost_eth:.8f} ETH")
                print(f"     L2 portion: {(l2_cost_eth/total_cost_eth)*100:.1f}%")
                print(f"     L1 portion: {(l1_fee_eth/total_cost_eth)*100:.1f}%")
            else:
                print(f"\n  📊 Total Cost: {l2_cost_eth:.8f} ETH")
                print("     (Simple transfer, minimal L1 cost)")
                
        except Exception as e:
            print(f"\n  L1 Data Fee: Could not estimate ({e})")
            print(f"  📊 Total Cost: ~{l2_cost_eth:.8f} ETH (L2 only)")
            
    except Exception as e:
        print(f"❌ Error analyzing cost: {e}")


def demo_monitor_recent_blocks(client, tx_handler):
    """Demonstrate monitoring recent transactions in blocks."""
    print("\n" + "="*60)
    print("MONITOR RECENT BLOCK TRANSACTIONS")
    print("="*60)
    
    try:
        # Get latest block
        block = client.get_block('latest', full_transactions=True)
        
        print(f"Block #{block['number']:,}")
        print(f"Timestamp: {block['timestamp']}")
        print(f"Total Transactions: {len(block['transactions'])}")
        
        # Analyze first 3 transactions
        print(f"\n📋 First 3 Transactions:")
        for i, tx in enumerate(block['transactions'][:3], 1):
            print(f"\n  Transaction {i}:")
            print(f"    Hash: {tx['hash'].hex()}")
            print(f"    From: {tx['from']}")
            print(f"    To: {tx['to'] if tx['to'] else 'Contract Creation'}")
            print(f"    Value: {tx['value'] / 10**18:.6f} ETH")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main example showcasing transaction read operations."""
    print("="*60)
    print("BASE PYTHON SDK - TRANSACTION EXAMPLES")
    print("="*60)
    
    try:
        # Connect to Base Mainnet
        client = BaseClient()
        print("✅ Connected to Base Mainnet")
        
        # Initialize Transaction handler (no wallet needed for reading)
        tx_handler = Transaction(client)
        
        # Example transaction hash (replace with a real one from basescan.org)
        # This is a recent Base mainnet transaction
        example_tx = input("\nEnter a transaction hash to analyze (or press Enter for demo): ").strip()
        
        if not example_tx:
            print("\n💡 No transaction provided. Here's how to use this example:")
            print("   1. Go to https://basescan.org/txs")
            print("   2. Copy any transaction hash")
            print("   3. Run this script again and paste the hash")
            print("\n   For now, showing block monitoring demo...")
            
            # Demo: Monitor recent blocks
            demo_monitor_recent_blocks(client, tx_handler)
            
        else:
            # Ensure proper format
            if not example_tx.startswith('0x'):
                example_tx = '0x' + example_tx
            
            print(f"\n🔍 Analyzing transaction: {example_tx}")
            
            # Demo 1: Query transaction
            demo_query_transaction(tx_handler, example_tx)
            
            # Demo 2: Get receipt
            demo_get_receipt(tx_handler, example_tx)
            
            # Demo 3: Check status
            demo_check_status(tx_handler, example_tx)
            
            # Demo 4: Analyze cost
            demo_analyze_transaction_cost(tx_handler, example_tx, client)
            
            # Demo 5: Wait for confirmation (only for pending transactions)
            status = tx_handler.get_status(example_tx)
            if status == 'pending':
                print("\n⏳ Transaction is pending...")
                response = input("Wait for confirmation? (y/n): ").strip().lower()
                if response == 'y':
                    demo_wait_for_confirmation(tx_handler, example_tx)
        
        print("\n" + "="*60)
        print("✅ TRANSACTION EXAMPLES COMPLETED")
        print("="*60)
        
        print("\n💡 Next Steps:")
        print("   - Try with your own transaction hashes from basescan.org")
        print("   - Monitor transactions in real-time")
        print("   - Integrate into your application for transaction tracking")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()