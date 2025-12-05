# Base Python SDK - Quick Reference Guide

**One-page cheat sheet for common operations**

---

## 🚀 Setup

```python
from basepy import BaseClient, Transaction, ERC20Contract

# Connect
client = BaseClient()  # Auto-connects to Base Mainnet
```

---

## 💰 Balances

```python
# ETH balance
eth = client.get_balance("0x...")
print(f"{client.format_units(eth, 18)} ETH")

# Complete portfolio (ETH + all tokens) - ONLY 2 RPC CALLS!
portfolio = client.get_portfolio_balance("0x...")
print(f"ETH: {portfolio['eth']['balance_formatted']}")
for token, info in portfolio['tokens'].items():
    print(f"{info['symbol']}: {info['balance_formatted']}")
```

---

## 🪙 Tokens (Easy Mode)

```python
# Use ERC20Contract helper
usdc = ERC20Contract(client, "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Metadata (cached after first call)
print(f"{usdc.name()} ({usdc.symbol()})")  # USD Coin (USDC)
print(f"Decimals: {usdc.decimals()}")  # 6

# Balance
balance = usdc.balance_of("0x...")
print(f"{usdc.format_amount(balance)} USDC")

# Check sufficient balance
has_enough = usdc.has_sufficient_balance("0x...", usdc.parse_amount(100))
```

---

## 📊 Transaction Analysis (ZERO RPC COST!)

```python
tx = Transaction(client)

# Decode ALL token transfers - FREE!
transfers = tx.decode_erc20_transfers(tx_hash)
for t in transfers:
    print(f"{t['token']}: {t['amount']}")

# Complete transaction details
details = tx.get_full_transaction_details(tx_hash, include_token_metadata=True)
print(f"Status: {details['status']}")
for t in details['token_transfers']:
    print(f"{t['symbol']}: {t['amount_formatted']}")

# Balance changes
changes = tx.get_balance_changes(tx_hash, "0x...")
print(f"ETH: {changes['eth_change_formatted']}")
for token, info in changes['token_changes'].items():
    print(f"{info['symbol']}: {info['change_formatted']}")
```

---

## ⛽ Gas & Fees (Base L2)

```python
# Current gas price
gas = client.get_gas_price()
print(f"{gas / 10**9:.2f} Gwei")

# Total cost (L1 + L2)
cost = client.estimate_total_fee({
    'from': '0x...',
    'to': '0x...',
    'value': 10**18,
    'data': '0x'
})
print(f"L2: {cost['l2_fee']}")
print(f"L1: {cost['l1_fee']}")
print(f"Total: {cost['total_fee']}")
```

---

## 🔄 Batch Operations

```python
# Multiple balances in 1 call
balances = client.batch_get_balances([addr1, addr2, addr3])

# Multicall (single RPC for multiple contract calls)
calls = [
    {'contract': token, 'abi': ERC20_ABI, 'function': 'name'},
    {'contract': token, 'abi': ERC20_ABI, 'function': 'symbol'},
]
results = client.multicall(calls)  # ['USD Coin', 'USDC']
```

---

## 🧱 Blocks

```python
# Current block
block_num = client.get_block_number()

# Block details
block = client.get_block('latest')
print(f"Transactions: {len(block['transactions'])}")
```

---

## 🛠️ Utilities

```python
# Convert amounts
wei = client.parse_units(1.5, 18)  # 1.5 ETH → Wei
eth = client.format_units(wei, 18)  # Wei → 1.5 ETH

# Simulate transaction (free test!)
result = client.simulate_transaction(tx_dict)
```

---

## ❌ Error Handling

```python
from basepy.exceptions import ValidationError, RPCError

try:
    balance = client.get_balance("0x...")
except ValidationError:
    print("Invalid address")
except RPCError:
    print("Network error")
```

---

## 📈 Monitoring

```python
# Health check
health = client.health_check()
print(f"Status: {health['status']}")

# Performance metrics
metrics = client.get_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
```

---

## 💡 Pro Tips

### 1. Use Portfolio for Multiple Tokens
```python
# ❌ BAD: 31 RPC calls
for token in tokens:
    balance = get_token_balance(token)

# ✅ GOOD: 2 RPC calls (93% faster!)
portfolio = client.get_portfolio_balance(address, tokens)
```

### 2. Cache Token Metadata
```python
# ❌ BAD: RPC every time
name = contract.functions.name().call()

# ✅ GOOD: Cached after first call
token = ERC20Contract(client, address)
name = token.name()  # Instant!
```

### 3. Zero-Cost Transaction Decoding
```python
# ❌ BAD: Manual parsing
receipt = get_receipt(tx_hash)
# ... parse logs manually ...

# ✅ GOOD: Built-in decoder (FREE!)
transfers = tx.decode_erc20_transfers(tx_hash)
```

---

## 🎯 Common Patterns

### DeFi Portfolio Tracker
```python
portfolio = client.get_portfolio_balance(wallet, include_common_tokens=True)
print(f"ETH: {portfolio['eth']['balance_formatted']}")
for token, info in portfolio['tokens'].items():
    if info['balance'] > 0:
        print(f"{info['symbol']}: {info['balance_formatted']}")
```

### Transaction Monitor
```python
tx = Transaction(client)
details = tx.get_full_transaction_details(tx_hash, include_token_metadata=True)
print(f"Status: {details['status']}")
print(f"Transfers: {details['transfer_count']}")
```

### Token Balance Check
```python
usdc = ERC20Contract(client, usdc_address)
balance = usdc.balance_of(wallet)
print(f"Balance: {usdc.format_amount(balance)} USDC")
```

---

## 🆚 Base SDK vs Web3.py

| Feature | Base SDK | Web3.py |
|---------|----------|---------|
| Portfolio (10 tokens) | 2 calls | 31 calls |
| Token decode | 0 calls | 1+ calls |
| Multicall | Built-in | External lib |
| Auto-retry | ✅ | ❌ |
| Caching | ✅ | ❌ |
| Rate limiting | ✅ | ❌ |
| Thread-safe | ✅ | Partial |

**Result: 60-95% fewer RPC calls = Faster & Cheaper!**

---

## 📚 Full Documentation

See DOCUMENTATION.md for complete API reference and advanced features.

---

**Built for the Base ecosystem 🔵**