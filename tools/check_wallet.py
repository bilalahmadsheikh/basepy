"""
Check test wallet status and balance.

This verifies:
1. .env file exists and is valid
2. Wallet can be loaded
3. Connection to Base Sepolia works
4. Balance is sufficient for testing
"""

from basepy import BaseClient, Wallet
import os
from dotenv import load_dotenv
from pathlib import Path


def check_wallet():
    """Check wallet setup and status."""
    
    print("="*70)
    print("🔵 BASE SEPOLIA WALLET CHECKER")
    print("="*70)
    
    # Check .env file
    print("\n1️⃣  Checking .env file...")
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n💡 Run this first:")
        print("   python tools/generate_test_wallet.py")
        return
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check private key
    print("\n2️⃣  Checking environment variables...")
    private_key = os.getenv('TESTNET_PRIVATE_KEY')
    address = os.getenv('TESTNET_ADDRESS')
    
    if not private_key:
        print("❌ TESTNET_PRIVATE_KEY not found in .env")
        return
    
    print("✅ TESTNET_PRIVATE_KEY found")
    
    if address:
        print(f"✅ TESTNET_ADDRESS: {address}")
    
    # Connect to Base Sepolia
    print("\n3️⃣  Connecting to Base Sepolia...")
    try:
        client = BaseClient(chain_id=84532)
        chain_id = client.get_chain_id()
        block_number = client.get_block_number()
        print(f"✅ Connected!")
        print(f"   Chain ID: {chain_id}")
        print(f"   Current Block: {block_number:,}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Load wallet
    print("\n4️⃣  Loading wallet...")
    try:
        wallet = Wallet.from_private_key(private_key, client=client)
        print(f"✅ Wallet loaded!")
        print(f"   Address: {wallet.address}")
        
        # Verify address matches
        if address and wallet.address.lower() != address.lower():
            print(f"⚠️  WARNING: Address mismatch!")
            print(f"   .env has: {address}")
            print(f"   Wallet:   {wallet.address}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {e}")
        return
    
    # Check balance
    print("\n5️⃣  Checking balance...")
    try:
        balance = wallet.get_balance()
        balance_eth = balance / 10**18
        
        print(f"✅ Balance retrieved!")
        print(f"   {balance_eth:.6f} ETH")
        print(f"   ({balance:,} Wei)")
        
        # Balance status
        if balance_eth == 0:
            print("\n⚠️  NO BALANCE!")
            print("   You need testnet ETH to send transactions.")
            print("\n💡 Get free testnet ETH from:")
            print("   https://www.alchemy.com/faucets/base-sepolia")
            return
        elif balance_eth < 0.01:
            print("\n⚠️  LOW BALANCE!")
            print("   You may want to get more testnet ETH.")
            print("   Recommended: At least 0.05 ETH for testing")
        else:
            print("\n✅ BALANCE IS GOOD!")
            print("   You're ready to send transactions!")
        
    except Exception as e:
        print(f"❌ Failed to check balance: {e}")
        return
    
    # Check nonce
    print("\n6️⃣  Checking transaction count...")
    try:
        nonce = wallet.get_nonce()
        print(f"✅ Transaction count (nonce): {nonce}")
        
        if nonce == 0:
            print("   This wallet hasn't sent any transactions yet")
        else:
            print(f"   This wallet has sent {nonce} transaction(s)")
    except Exception as e:
        print(f"⚠️  Could not get nonce: {e}")
    
    # Block explorer link
    print("\n7️⃣  Block Explorer:")
    explorer_url = f"https://sepolia.basescan.org/address/{wallet.address}"
    print(f"   {explorer_url}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"   Address:  {wallet.address}")
    print(f"   Balance:  {balance_eth:.6f} ETH")
    print(f"   Nonce:    {nonce}")
    print(f"   Network:  Base Sepolia (Chain ID: {chain_id})")
    
    # Status
    if balance_eth > 0.01:
        print("\n✅ ALL CHECKS PASSED!")
        print("   You're ready to run demos!")
        print("\n🚀 Next step:")
        print("   python examples/send_demo.py")
    elif balance_eth > 0:
        print("\n⚠️  Low balance but can test small transactions")
        print("   Consider getting more testnet ETH")
    else:
        print("\n❌ Need testnet ETH to continue")
        print("   Visit: https://www.alchemy.com/faucets/base-sepolia")
    
    print("="*70)


if __name__ == "__main__":
    check_wallet()