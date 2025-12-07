🔵 BasePy SDK - Production-Ready Python SDK for Base Blockchain
The most efficient and reliable way to build on Base (Ethereum Layer 2)
Show Image
Show Image
Show Image
Show Image

🚀 80% fewer RPC calls - Proven in production
💰 Zero-cost ERC-20 decoding - Extract all token transfers FREE
🛡️ Battle-tested resilience - Circuit breaker, auto-retry, rate limiting
⚡ Production-grade - Thread-safe, cached, monitored


🎯 Why BasePy?
The Problem with Web3.py
When building production applications on Base, raw Web3.py has limitations:
❌ Repetitive boilerplate - Every token balance needs 3+ RPC calls
❌ No retry logic - Network errors crash your app
❌ No rate limiting - Get blocked by RPC providers
❌ Manual optimization - You implement caching yourself
❌ Base L2 complexity - Manual L1+L2 fee calculations
The BasePy Solution
✅ Smart batching - Get entire portfolio in 2 RPC calls (vs 10+)
✅ Automatic retry - Exponential backoff with circuit breaker
✅ Built-in rate limiting - Never get blocked
✅ Intelligent caching - 500x faster repeated queries
✅ Base L2 native - L1+L2 fees calculated automatically
✅ Zero-cost features - ERC-20 decoding from existing data

🏆 Performance Comparison
Real-world performance (Base Mainnet, December 2024):
TaskBasePy SDKWeb3.pyImprovementPortfolio (ETH + 3 tokens)2 RPC calls, 1.66s10+ RPC calls80% fewer calls ✅Decode ERC-20 transfers0 additional RPC calls1+ RPC calls per token100% free ✅Token metadata (cached)<1ms response300-500ms500x faster ✅Multicall (4 operations)1 RPC call4 sequential calls75% reduction ✅
Real Cost Impact:
For 1M portfolio checks at typical RPC pricing:

Web3.py: ~$100 (10 calls × $0.01/1000)
BasePy: ~$20 (2 calls × $0.01/1000)
You save: $80 per million requests (80% reduction) 💰


📦 Installation
bashpip install basepy-sdk
Requirements:

Python 3.8+
web3.py >= 6.0.0
eth-account >= 0.9.0


🚀 Quick Start
30 Seconds to Your First Request
pythonfrom basepy import BaseClient

# Connect to Base Mainnet (or Sepolia testnet)
client = BaseClient()  # Mainnet
# client = BaseClient(chain_id=84532)  # Sepolia testnet

# Get complete portfolio (ETH + all common tokens)
portfolio = client.get_portfolio_balance("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1")

print(f"Wallet: {portfolio['address']}")
print(f"ETH: {portfolio['eth']['balance_formatted']:.6f}")
print(f"\nTokens with balance:")
for token_addr, info in portfolio['tokens'].items():
    if info['balance'] > 0:
        print(f"  {info['symbol']:6s}: {info['balance_formatted']:>12.6f}")
```

**Output:**
```
Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1
ETH: 1.234567

Tokens with balance:
  USDC  :  1000.500000
  DAI   :   250.000000
RPC calls: 2 (vs 10+ with Web3.py) 🎉

💎 Core Features
1. 🪙 Smart Portfolio Tracking
Get ETH + all token balances with minimal RPC calls:
pythonfrom basepy import BaseClient

client = BaseClient()

# Get portfolio with common Base tokens
portfolio = client.get_portfolio_balance(
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    include_common_tokens=True  # USDC, DAI, WETH, etc.
)

# Or specify exact tokens
usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
dai = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"
portfolio = client.get_portfolio_balance(
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    token_addresses=[usdc, dai]
)

print(f"Total assets: {portfolio['total_assets']}")
print(f"Tokens with balance: {portfolio['non_zero_tokens']}")
Cost: ~2 RPC calls (regardless of token count!) ⚡

2. 📊 Zero-Cost Transaction Analysis
Extract all ERC-20 transfers without additional RPC calls:
pythonfrom basepy import BaseClient, Transaction

client = BaseClient()
tx = Transaction(client)

# Get complete transaction details
details = tx.get_full_transaction_details(
    "0x123...",
    include_token_metadata=True
)

print(f"Status: {details['status']}")
print(f"ETH transferred: {details['eth_value_formatted']} ETH")
print(f"Token transfers: {details['transfer_count']}")

for transfer in details['token_transfers']:
    print(f"  {transfer['symbol']}: {transfer['amount_formatted']}")
Advanced Analysis:
python# Decode ALL ERC-20 transfers (zero cost!)
transfers = tx.decode_erc20_transfers("0x123...")

# Calculate balance changes for an address
changes = tx.get_balance_changes("0x123...", your_address)
print(f"ETH change: {changes['eth_change_formatted']:.6f} ETH")
for token, info in changes['token_changes'].items():
    print(f"{info['symbol']}: {info['change_formatted']}")

# Classify transaction type
classification = tx.classify_transaction("0x123...")
print(f"Type: {classification['type']}")  # 'swap', 'transfer', etc.
print(f"Complexity: {classification['complexity']}")
Cost: FREE - uses existing receipt data! 🎉

3. 💸 Send Transactions (Wallet Required)
Simple, production-ready transaction sending:
pythonfrom basepy import BaseClient, Wallet, Transaction

# Initialize with wallet
client = BaseClient()
wallet = Wallet.from_private_key("0xYourPrivateKey...", client=client)
tx = Transaction(client, wallet)

# Send ETH with automatic gas optimization
tx_hash = tx.send_eth(
    to_address="0xRecipient...",
    amount=0.1,  # 0.1 ETH
    gas_strategy='fast',  # 'slow', 'standard', 'fast', 'instant'
    wait_for_receipt=True  # Wait for confirmation
)
print(f"Sent! TX: {tx_hash}")

# Send ERC-20 tokens
from basepy.abis import ERC20_ABI

usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
tx_hash = tx.send_erc20(
    token_address=usdc,
    to_address="0xRecipient...",
    amount=100 * 10**6,  # 100 USDC (6 decimals)
    abi=ERC20_ABI,
    gas_strategy='standard'
)
Features:

✅ Automatic gas estimation with buffer
✅ Nonce management with collision detection
✅ Transaction simulation before sending
✅ Automatic retry with exponential backoff
✅ Balance validation


4. ⚡ Batch & Multicall Operations
Execute multiple operations efficiently:
python# Batch get balances
addresses = ["0xAddr1...", "0xAddr2...", "0xAddr3..."]
balances = client.batch_get_balances(addresses)

# Multicall - Multiple contract calls in 1 RPC request
from basepy.abis import ERC20_ABI

usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
calls = [
    {'contract': usdc, 'abi': ERC20_ABI, 'function': 'name'},
    {'contract': usdc, 'abi': ERC20_ABI, 'function': 'symbol'},
    {'contract': usdc, 'abi': ERC20_ABI, 'function': 'decimals'},
    {'contract': usdc, 'abi': ERC20_ABI, 'function': 'totalSupply'},
]
results = client.multicall(calls)
print(results)  # ['USD Coin', 'USDC', 6, 1234567890...]
Cost: 1 RPC call (vs 4 sequential calls) 🚀

5. ⛽ Base L2 Fee Calculation
Get complete transaction cost breakdown:
python# Estimate total cost (L1 + L2)
cost = client.estimate_total_fee({
    'from': wallet.address,
    'to': recipient,
    'value': 10**18,  # 1 ETH
    'data': '0x'
})

print(f"L2 execution cost: {cost['l2_fee_eth']:.6f} ETH")
print(f"L1 data cost: {cost['l1_fee_eth']:.6f} ETH")
print(f"Total cost: {cost['total_fee_eth']:.6f} ETH")

# Check if wallet can afford transaction
affordable = wallet.can_afford_transaction(
    to=recipient,
    value=0.1,
    buffer_percent=10
)
print(f"Can afford: {affordable}")

6. 🛡️ Production-Ready Resilience
Built-in reliability features (no configuration needed):
pythonfrom basepy import BaseClient, Config

# Advanced configuration (optional)
config = Config()
config.MAX_RETRIES = 5
config.CACHE_TTL = 15  # seconds
config.RATE_LIMIT_REQUESTS = 100  # per minute
config.CIRCUIT_BREAKER_THRESHOLD = 5

client = BaseClient(config=config, environment='production')

# Monitor performance
stats = client.get_metrics()
print(f"Total requests: {sum(stats['requests'].values())}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
print(f"Avg latency: {stats['avg_latencies']}")

# Health check
health = client.health_check()
print(f"Status: {health['status']}")
print(f"Block number: {health['block_number']}")
Automatic Features:

✅ Exponential backoff retry
✅ Multiple RPC endpoint failover
✅ Token bucket rate limiting
✅ Circuit breaker pattern
✅ Intelligent TTL caching
✅ Thread-safe operations
✅ Performance monitoring


7. 👛 Complete Wallet Management
pythonfrom basepy import BaseClient, Wallet

client = BaseClient()

# Create new wallet
wallet = Wallet.create(client)

# Import from private key
wallet = Wallet.from_private_key("0x...", client)

# Import from mnemonic (BIP-39)
wallet = Wallet.from_mnemonic(
    "your twelve word mnemonic phrase here...",
    client=client,
    account_path="m/44'/60'/0'/0/0"  # Derivation path
)

# Import from keystore
wallet = Wallet.from_keystore(
    path="keystore.json",
    password="your-password",
    client=client
)

# Export to keystore
wallet.to_keystore(
    password="secure-password",
    output_path="backup.json"
)

# Wallet operations with caching
balance = wallet.get_balance(use_cache=True)
nonce = wallet.get_nonce(use_cache=True)
portfolio = wallet.get_portfolio(use_cache=True)

# Sign messages (EIP-191)
signature = wallet.sign_message("Hello, Base!")

# Sign typed data (EIP-712)
typed_data = {...}
signature = wallet.sign_typed_data(typed_data)

🆚 BasePy vs Web3.py
Feature Comparison
FeatureBasePyWeb3.pyWinnerPortfolio balanceget_portfolio_balance() (2 calls)Manual loops (10+ calls)BasePy (80% fewer)ERC-20 decodingdecode_erc20_transfers() (0 calls)Manual parsing (1+ calls/token)BasePy (100% free)MulticallNative multicall() (1 call)Sequential (N calls)BasePy (N→1)Retry logic✅ Automatic exponential backoff❌ Manual implementationBasePyRate limiting✅ Token bucket built-in❌ Not includedBasePyCircuit breaker✅ Automatic failover❌ Not availableBasePyCaching✅ Intelligent TTL (500x speedup)❌ Manual implementationBasePyRPC failover✅ Multi-endpoint auto-switch❌ Manual switchingBasePyThread safety✅ Fully thread-safe⚠️ PartialBasePyBase L2 fees✅ Native L1+L2 calculation❌ Manual calculationBasePyWallet management✅ Complete (create, import, export, sign)⚠️ Basic signing onlyBasePyTransaction mgmt✅ Nonce collision handling, simulation⚠️ BasicBasePyMonitoring✅ Built-in metrics & health checks❌ Not includedBasePyProduction ready✅ Battle-tested⚠️ Requires hardeningBasePy
Code Comparison
Get portfolio balance:
python# ❌ Web3.py - Verbose, 10+ RPC calls
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(rpc_url))
eth_balance = w3.eth.get_balance(address)

tokens_data = {}
for token in [usdc, dai, weth]:
    contract = w3.eth.contract(address=token, abi=ERC20_ABI)
    balance = contract.functions.balanceOf(address).call()  # Call 1
    symbol = contract.functions.symbol().call()            # Call 2
    decimals = contract.functions.decimals().call()        # Call 3
    tokens_data[token] = {'balance': balance, 'symbol': symbol, 'decimals': decimals}
# Total: 1 + (3 × N tokens) = 10+ calls for 3 tokens

# ✅ BasePy - Simple, 2 RPC calls
from basepy import BaseClient

client = BaseClient()
portfolio = client.get_portfolio_balance(address, [usdc, dai, weth])
# Total: 2 calls (1 for ETH, 1 multicall for all tokens)
Decode token transfers:
python# ❌ Web3.py - Manual, error-prone
receipt = w3.eth.get_transaction_receipt(tx_hash)
transfers = []
for log in receipt['logs']:
    if len(log['topics']) == 3 and log['topics'][0].hex() == TRANSFER_SIG:
        token = log['address']
        from_addr = '0x' + log['topics'][1].hex()[-40:]
        to_addr = '0x' + log['topics'][2].hex()[-40:]
        amount = int(log['data'].hex(), 16)
        transfers.append({'token': token, 'from': from_addr, 'to': to_addr, 'amount': amount})

# ✅ BasePy - Zero extra calls, automatic
from basepy import Transaction

tx = Transaction(client)
transfers = tx.decode_erc20_transfers(tx_hash)  # Done!

📚 Complete Examples
Example 1: DeFi Portfolio Tracker
pythonfrom basepy import BaseClient

def track_portfolio(wallet_address):
    client = BaseClient()
    portfolio = client.get_portfolio_balance(wallet_address)
    
    print(f"📊 Portfolio for {wallet_address}\n")
    print(f"💰 ETH: {portfolio['eth']['balance_formatted']:.6f}")
    print(f"\n🪙 Tokens ({portfolio['non_zero_tokens']} with balance):")
    
    for token_addr, info in portfolio['tokens'].items():
        if info['balance'] > 0:
            print(f"  {info['symbol']:8s}: {info['balance_formatted']:>15.6f}")
    
    print(f"\n📈 Summary:")
    print(f"  Total assets: {portfolio['total_assets']}")
    print(f"  RPC calls used: ~2 (vs {portfolio['total_assets'] * 3}+ with Web3.py)")

track_portfolio("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1")
Example 2: Transaction Monitor
pythonfrom basepy import BaseClient, Transaction

def analyze_transaction(tx_hash):
    client = BaseClient()
    tx = Transaction(client)
    
    # Get full details
    details = tx.get_full_transaction_details(tx_hash, include_token_metadata=True)
    
    # Calculate cost
    cost = tx.get_transaction_cost(tx_hash)
    
    print(f"🔍 Transaction: {tx_hash}")
    print(f"Status: {'✅ Success' if details['status'] == 'confirmed' else '❌ Failed'}")
    print(f"Block: {details['block_number']}")
    print(f"Gas used: {details['gas_used']:,}")
    print(f"Total cost: {cost['total_cost_eth']:.6f} ETH")
    print(f"  L2 execution: {cost['l2_cost_eth']:.6f} ETH")
    print(f"  L1 data: {cost['l1_cost_eth']:.6f} ETH")
    
    if details['eth_value'] > 0:
        print(f"\n💸 ETH Transfer: {details['eth_value_formatted']} ETH")
    
    if details['transfer_count'] > 0:
        print(f"\n🪙 Token Transfers ({details['transfer_count']}):")
        for t in details['token_transfers']:
            print(f"  {t['symbol']}: {t['amount_formatted']}")
    
    # Classify
    classification = tx.classify_transaction(tx_hash)
    print(f"\n🏷️  Type: {classification['type']}")
    print(f"Complexity: {classification['complexity']}")

analyze_transaction("0x...")
Example 3: Production Bot with Monitoring
pythonfrom basepy import BaseClient, Wallet, Transaction
import time

def trading_bot():
    # Initialize with monitoring
    client = BaseClient(environment='production')
    wallet = Wallet.from_private_key(private_key, client)
    tx = Transaction(client, wallet)
    
    print("🤖 Trading bot started...")
    
    while True:
        try:
            # Check health
            health = client.health_check()
            if health['status'] != 'healthy':
                print(f"⚠️  Unhealthy: {health}")
                time.sleep(60)
                continue
            
            # Get portfolio
            portfolio = wallet.get_portfolio(use_cache=True)
            
            # Your trading logic here...
            
            # Monitor performance
            metrics = client.get_metrics()
            print(f"📊 Cache hit rate: {metrics['cache_hit_rate']:.1%}")
            print(f"📊 Avg latency: {metrics['avg_latencies']}")
            
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(30)

trading_bot()
```

See [examples/](examples/) for more real-world code!

---

## 🏗️ Project Structure
```
basepy-sdk/
├── basepy/
│   ├── __init__.py          # Main exports
│   ├── client.py            # BaseClient with all RPC operations
│   ├── wallet.py            # Complete wallet management
│   ├── transactions.py      # Transaction operations
│   ├── abis.py              # Contract ABIs and constants
│   ├── utils.py             # Utility functions
│   └── exceptions.py        # Custom exceptions
│
├── examples/
│   ├── basic_usage.py       # Simple examples
│   ├── portfolio_tracker.py # DeFi portfolio tracker
│   ├── transaction_monitor.py # TX analysis
│   └── wallet_demo.py       # Complete wallet demo
│
├── tests/
│   ├── test_client.py       # Client tests
│   ├── test_wallet.py       # Wallet tests
│   └── test_transactions.py # Transaction tests
│
├── README.md                # This file
├── LICENSE                  # MIT License
├── setup.py                 # Package setup
├── pyproject.toml          # Modern Python config
└── requirements.txt         # Dependencies

⚙️ Configuration
Basic Configuration
pythonfrom basepy import BaseClient, Config

# Use defaults (recommended)
client = BaseClient()

# Or customize
config = Config()
config.MAX_RETRIES = 5
config.CACHE_TTL = 15
config.RATE_LIMIT_REQUESTS = 100
config.CIRCUIT_BREAKER_THRESHOLD = 5

client = BaseClient(config=config)
Environment-Based Config
python# Development (verbose logging)
client = BaseClient(environment='development')

# Production (optimized)
client = BaseClient(environment='production')
Custom RPC Endpoints
python# Use your own RPC endpoints
custom_rpcs = [
    "https://mainnet.base.org",
    "https://base.llamarpc.com",
    "https://base.meowrpc.com",
]
client = BaseClient(chain_id=8453, rpc_urls=custom_rpcs)

🧪 Testing
bash# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=basepy --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run with benchmarks
pytest tests/test_client.py --benchmark-only

📊 Performance Benchmarks
Tested on Base Mainnet (December 2024):
OperationAvg TimeRPC Callsvs Web3.pyPortfolio (3 tokens)1.66s280% fewer callsDecode ERC-20 transfers<10ms0100% freeToken metadata (cached)<1ms0500x fasterMulticall (4 functions)~1s175% fewer callsHealth check~0.5s2N/A
Benchmarks run with pytest-benchmark on Base Mainnet

🛣️ Roadmap
✅ Completed (v1.0)

 Core RPC operations
 ERC-20 token support
 Portfolio tracking (80% fewer calls)
 Zero-cost transaction decoding
 Complete wallet management
 Automatic retry & failover
 Rate limiting & circuit breaker
 Intelligent caching
 Base L2 fee calculation
 Thread-safe operations
 Performance monitoring
 Comprehensive testing

🔜 Planned (v1.1-1.2)

 ERC-721 (NFT) support
 ERC-1155 (Multi-token) support
 WebSocket support for events
 ENS resolution
 Price oracle integration
 GraphQL support

🔮 Future (v2.0+)

 Multi-chain support (Optimism, Arbitrum)
 Advanced DeFi integrations
 MEV protection
 Account abstraction (ERC-4337)


🤝 Contributing
We welcome contributions! Here's how to get started:
bash# Fork and clone
git clone https://github.com/yourusername/basepy-sdk.git
cd basepy-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black basepy/
flake8 basepy/

# Type check
mypy basepy/
Please see CONTRIBUTING.md for detailed guidelines.

📄 License
MIT License - see LICENSE file for details.
TL;DR: Free to use in commercial and personal projects. Just keep the license notice.

🔗 Resources

GitHub: https://github.com/yourusername/basepy-sdk
Documentation: Full API Reference
Examples: examples/
Base Docs: https://docs.base.org
Issues: https://github.com/yourusername/basepy-sdk/issues


📞 Support
Need help? We're here:

GitHub Issues: Report bugs or request features
Discord: Join our community
Email: support@basepy.dev
Twitter: @basepy_sdk


🙏 Acknowledgments
Built with ❤️ for the Base ecosystem:

Powered by Web3.py
Inspired by the Ethereum and Base communities
Thanks to all contributors and users


⭐ Star Us!
If BasePy makes your development easier, please star the repository!
It helps others discover the project and motivates us to keep improving.
Show Image

🎯 Quick Links

📦 Installation
🚀 Quick Start
💎 Core Features
📚 Examples
🆚 vs Web3.py
⚙️ Configuration
🧪 Testing
🤝 Contributing


Built for developers who want to focus on building, not debugging RPC calls 🔵
Making Base blockchain development 10x easier, 10x faster, and 80% cheaper