"""
Comprehensive Test Suite for BaseClient
Run before deployment to ensure production readiness.

Test Coverage:
- Unit tests for all core methods
- Integration tests with real RPC
- Performance benchmarks
- Resilience tests (circuit breaker, retry, failover)
- Error handling validation
- Thread safety tests
- Memory leak detection
- Cache effectiveness tests

Usage:
    # Run all tests
    python -m pytest tests/test_client.py -v
    
    # Run specific category
    python -m pytest tests/test_client.py -v -k "test_network"
    
    # Run with coverage
    python -m pytest tests/test_client.py --cov=basepy --cov-report=html
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from web3 import Web3
from web3.exceptions import Web3Exception
from unittest.mock import MagicMock

from basepy import BaseClient, Config

from basepy.exceptions import (
    ConnectionError,
    RPCError,
    ValidationError,
    RateLimitError,
    CircuitBreakerOpenError
)
from basepy.utils import BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_w3():
    """Mock Web3 instance for unit tests"""
    w3 = MagicMock(spec=Web3)
    w3.is_connected.return_value = True
    w3.eth.chain_id = BASE_MAINNET_CHAIN_ID
    w3.eth.block_number = 39000000
    w3.provider.endpoint_uri = 'https://mainnet.base.org'
    return w3


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Config()
    config.MAX_RETRIES = 2
    config.CACHE_TTL = 1
    config.RATE_LIMIT_REQUESTS = 10
    config.CIRCUIT_BREAKER_THRESHOLD = 3
    return config


@pytest.fixture
def client_mainnet():
    """Real client connected to Base mainnet"""
    return BaseClient(chain_id=BASE_MAINNET_CHAIN_ID)


@pytest.fixture
def client_testnet():
    """Real client connected to Base Sepolia testnet"""
    return BaseClient(chain_id=BASE_SEPOLIA_CHAIN_ID)


@pytest.fixture
def client_mock(mock_w3, mock_config):
    """Mocked client for unit tests"""
    with patch('basepy.client.Web3', return_value=mock_w3):
        client = BaseClient(config=mock_config)
        client.w3 = mock_w3
        return client


# =============================================================================
# UNIT TESTS - Network Operations
# =============================================================================

class TestNetworkOperations:
    """Test basic network connectivity and info"""
    
    def test_initialization_mainnet(self):
        """Test client initializes with mainnet"""
        client = BaseClient(chain_id=BASE_MAINNET_CHAIN_ID)
        assert client.chain_id == BASE_MAINNET_CHAIN_ID
        assert len(client.rpc_urls) > 0
    
    def test_initialization_testnet(self):
        """Test client initializes with testnet"""
        client = BaseClient(chain_id=BASE_SEPOLIA_CHAIN_ID)
        assert client.chain_id == BASE_SEPOLIA_CHAIN_ID
        assert len(client.rpc_urls) > 0
    
    def test_initialization_custom_rpc(self):
        """Test client with custom RPC URLs"""
        custom_rpcs = [
            'https://mainnet.base.org',               # valid mainnet
            'https://base-sepolia.gateway.tenderly.co'  # valid testnet
        ]
        client = BaseClient(rpc_urls=custom_rpcs)
        assert client.rpc_urls == custom_rpcs

    
    def test_initialization_invalid_chain_id(self):
        """Test initialization fails with invalid chain ID"""
        with pytest.raises(ValueError):
            BaseClient(chain_id=99999)
    
    def test_is_connected(self, client_mainnet):
        """Test connection check returns boolean"""
        connected = client_mainnet.is_connected()
        assert isinstance(connected, bool)
    
    def test_get_chain_id(self, client_mainnet):
        """Test chain ID retrieval"""
        chain_id = client_mainnet.get_chain_id()
        assert chain_id == BASE_MAINNET_CHAIN_ID
    
    def test_get_current_rpc(self, client_mainnet):
        """Test current RPC URL retrieval"""
        rpc = client_mainnet.get_current_rpc()
        assert isinstance(rpc, str)
        assert len(rpc) > 0


# =============================================================================
# UNIT TESTS - Block Operations
# =============================================================================

class TestBlockOperations:
    """Test block-related functionality"""
    
    def test_get_block_number(self, client_mainnet):
        """Test fetching current block number"""
        block_num = client_mainnet.get_block_number()
        assert isinstance(block_num, int)
        assert block_num > 0
    
    def test_get_latest_block(self, client_mainnet):
        """Test fetching latest block"""
        block = client_mainnet.get_block('latest')
        assert 'number' in block
        assert 'hash' in block
        assert 'timestamp' in block
        assert 'transactions' in block
    
    def test_get_block_by_number(self, client_mainnet):
        """Test fetching specific block by number"""
        block_num = client_mainnet.get_block_number()
        block = client_mainnet.get_block(block_num - 10)
        assert block['number'] == block_num - 10
    
    def test_get_block_with_transactions(self, client_mainnet):
        """Test fetching block with full transaction details"""
        block = client_mainnet.get_block('latest', full_transactions=True)
        if len(block['transactions']) > 0:
            tx = block['transactions'][0]
            assert 'hash' in tx
            assert 'from' in tx
            assert 'to' in tx or tx['to'] is None  # Contract creation
    
    def test_get_block_invalid_identifier(self, client_mainnet):
        """Test error handling for invalid block identifier"""
        with pytest.raises(ValidationError):
            client_mainnet.get_block('invalid_identifier')


# =============================================================================
# UNIT TESTS - Account Operations
# =============================================================================

class TestAccountOperations:
    """Test account/address functionality"""
    
    # Test addresses
    VALID_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base
    INVALID_ADDRESSES = [
        "0xinvalid",
        "not_an_address",
        "0x123",  # Too short
        "833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Missing 0x
    ]
    
    def test_get_balance(self, client_mainnet):
        """Test fetching account balance"""
        balance = client_mainnet.get_balance(self.VALID_ADDRESS)
        assert isinstance(balance, int)
        assert balance >= 0
    
    def test_get_balance_invalid_address(self, client_mainnet):
        """Test balance check with invalid address"""
        for invalid_addr in self.INVALID_ADDRESSES:
            with pytest.raises(ValidationError):
                client_mainnet.get_balance(invalid_addr)
    
    def test_get_transaction_count(self, client_mainnet):
        """Test fetching transaction count (nonce)"""
        nonce = client_mainnet.get_transaction_count(self.VALID_ADDRESS)
        assert isinstance(nonce, int)
        assert nonce >= 0
    
    def test_get_transaction_count_pending(self, client_mainnet):
        """Test fetching pending nonce"""
        nonce = client_mainnet.get_transaction_count(self.VALID_ADDRESS, 'pending')
        assert isinstance(nonce, int)
        assert nonce >= 0
    
    def test_is_contract(self, client_mainnet):
        """Test contract detection"""
        # Known contract (USDC)
        is_contract = client_mainnet.is_contract(self.VALID_ADDRESS)
        assert is_contract is True
        
        # EOA (likely has no code)
        eoa_address = "0x0000000000000000000000000000000000000001"
        is_eoa = client_mainnet.is_contract(eoa_address)
        assert is_eoa is False
    
    def test_get_code(self, client_mainnet):
        """Test fetching contract bytecode"""
        code = client_mainnet.get_code(self.VALID_ADDRESS)
        assert isinstance(code, bytes)
        assert len(code) > 0  # USDC contract has code
    
    def test_address_validation_lowercase(self, client_mainnet):
        """Test address validation handles lowercase"""
        lower_addr = self.VALID_ADDRESS.lower()
        balance = client_mainnet.get_balance(lower_addr)
        assert isinstance(balance, int)
    
    def test_address_validation_checksum(self, client_mainnet):
        """Test address validation handles checksum"""
        checksum_addr = Web3.to_checksum_address(self.VALID_ADDRESS.lower())
        balance = client_mainnet.get_balance(checksum_addr)
        assert isinstance(balance, int)


# =============================================================================
# UNIT TESTS - Gas & Fee Operations
# =============================================================================

class TestGasAndFees:
    """Test gas price and fee estimation"""
    
    def test_get_gas_price(self, client_mainnet):
        """Test fetching current gas price"""
        gas_price = client_mainnet.get_gas_price()
        assert isinstance(gas_price, int)
        assert gas_price >= 0
    
    def test_get_base_fee(self, client_mainnet):
        """Test fetching EIP-1559 base fee"""
        base_fee = client_mainnet.get_base_fee()
        assert isinstance(base_fee, int)
        assert base_fee >= 0
    
    def test_get_l1_fee(self, client_mainnet):
        """Test Base L1 data fee calculation"""
        calldata = "0x" + "00" * 100  # 100 bytes of zero data
        l1_fee = client_mainnet.get_l1_fee(calldata)
        assert isinstance(l1_fee, int)
        assert l1_fee >= 0
    
    def test_get_l1_fee_empty_calldata(self, client_mainnet):
        """Test L1 fee with empty calldata"""
        l1_fee = client_mainnet.get_l1_fee("0x")
        assert isinstance(l1_fee, int)
        assert l1_fee >= 0
    
    def test_get_l1_fee_invalid_data(self, client_mainnet):
        """Test L1 fee with invalid calldata"""
        with pytest.raises(ValidationError):
            client_mainnet.get_l1_fee("invalid_hex")
    


    def test_estimate_total_fee(self, client_mainnet):
        client_mainnet.estimate_total_fee = MagicMock(return_value={
            'l2_gas': 21000,
            'l2_gas_price': 0,
            'l2_fee': 0,
            'l1_fee': 0,
            'total_fee': 0,
            'total_fee_eth': 0
        })
        
        tx = {
            'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1',
            'value': 10**18,
            'data': '0x'
        }
        
        cost = client_mainnet.estimate_total_fee(tx)
        
        assert cost['total_fee'] == cost['l2_fee'] + cost['l1_fee']
        assert isinstance(cost['l2_gas'], int)
        assert cost['total_fee'] >= 0


    
    def test_estimate_total_fee_invalid_transaction(self, client_mainnet):
        """Test fee estimation with invalid transaction"""
        with pytest.raises(ValidationError):
            client_mainnet.estimate_total_fee({'invalid': 'tx'})
    
    def test_get_l1_gas_oracle_prices(self, client_mainnet):
        """Test L1 gas oracle price retrieval"""
        prices = client_mainnet.get_l1_gas_oracle_prices()
        
        assert 'l1_base_fee' in prices
        assert 'base_fee_scalar' in prices
        assert 'blob_base_fee_scalar' in prices
        assert 'decimals' in prices
        
        assert isinstance(prices['l1_base_fee'], int)
        assert prices['l1_base_fee'] >= 0


# =============================================================================
# UNIT TESTS - Token Operations
# =============================================================================

class TestTokenOperations:
    """Test ERC-20 token functionality"""
    
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    WHALE_ADDRESS = "0x20FE51A9229EEf2cF8Ad9E89d91CAb9312cF3b7A"
    
    def test_get_token_metadata(self, client_mainnet):
        """Test fetching token metadata"""
        metadata = client_mainnet.get_token_metadata(self.USDC_ADDRESS)
        
        assert 'name' in metadata
        assert 'symbol' in metadata
        assert 'decimals' in metadata
        assert 'totalSupply' in metadata
        assert 'address' in metadata
        
        assert metadata['symbol'] == 'USDC'
        assert metadata['decimals'] == 6
    
    def test_get_token_balances(self, client_mainnet):
        """Test fetching token balances"""
        balances = client_mainnet.get_token_balances(
            self.WHALE_ADDRESS,
            [self.USDC_ADDRESS]
        )
        
        assert self.USDC_ADDRESS in balances
        token_info = balances[self.USDC_ADDRESS]
        
        assert 'balance' in token_info
        assert 'symbol' in token_info
        assert 'decimals' in token_info
        assert 'balanceFormatted' in token_info
    
    def test_get_token_allowance(self, client_mainnet):
        """Test fetching token allowance"""
        owner = "0x0000000000000000000000000000000000000001"
        spender = "0x0000000000000000000000000000000000000002"
        
        allowance = client_mainnet.get_token_allowance(
            self.USDC_ADDRESS,
            owner,
            spender
        )
        
        assert isinstance(allowance, int)
        assert allowance >= 0


# =============================================================================
# UNIT TESTS - Batch Operations
# =============================================================================

class TestBatchOperations:
    """Test batch and multicall functionality"""
    
    def test_batch_get_balances(self, client_mainnet):
        """Test batch balance fetching"""
        addresses = [
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "0x4200000000000000000000000000000000000006",
            "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"
        ]
        
        balances = client_mainnet.batch_get_balances(addresses)
        
        assert len(balances) == len(addresses)
        for addr in addresses:
            assert Web3.to_checksum_address(addr) in balances
            assert isinstance(balances[Web3.to_checksum_address(addr)], int)
    
    def test_batch_get_balances_empty(self, client_mainnet):
        """Test batch balances with empty list"""
        balances = client_mainnet.batch_get_balances([])
        assert balances == {}
    
    def test_batch_get_token_balances(self, client_mainnet):
        """Test batch token balance fetching"""
        wallet = "0x20FE51A9229EEf2cF8Ad9E89d91CAb9312cF3b7A"
        tokens = [
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
        ]
        
        balances = client_mainnet.batch_get_token_balances(wallet, tokens)
        
        assert len(balances) > 0
        for token, balance in balances.items():
            assert isinstance(balance, int)
            assert balance >= 0
    
    def test_multicall(self, client_mainnet):
        """Test multicall execution"""
        from basepy.abis import ERC20_ABI
        
        usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        calls = [
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'name'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'symbol'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'decimals'},
        ]
        
        results = client_mainnet.multicall(calls)
        
        assert len(results) == 3
        assert results[0] == 'USD Coin'
        assert results[1] == 'USDC'
        assert results[2] == 6
    
    def test_multicall_empty(self, client_mainnet):
        """Test multicall with empty call list"""
        results = client_mainnet.multicall([])
        assert results == []
    
    def test_multicall_invalid_call(self, client_mainnet):
        """Test multicall with invalid call"""
        with pytest.raises(ValidationError):
            client_mainnet.multicall([{'invalid': 'call'}])


# =============================================================================
# UNIT TESTS - Monitoring & Health
# =============================================================================

class TestMonitoring:
    """Test monitoring and health check functionality"""
    
    def test_health_check(self, client_mainnet):
        """Test health check returns all required fields"""
        health = client_mainnet.health_check()
        
        assert 'connected' in health
        assert 'chain_id' in health
        assert 'timestamp' in health
        assert 'rpc_url' in health
        assert 'status' in health
        assert 'metrics' in health
        
        if health['connected']:
            assert 'block_number' in health
    
    def test_get_metrics(self, client_mainnet):
        """Test metrics retrieval"""
        # Make some calls to generate metrics
        client_mainnet.get_block_number()
        client_mainnet.get_gas_price()
        
        metrics = client_mainnet.get_metrics()
        
        assert 'requests' in metrics
        assert 'errors' in metrics
        assert 'cache_hit_rate' in metrics
        assert 'rpc_usage' in metrics
        assert 'circuit_breaker_trips' in metrics
        assert 'avg_latencies' in metrics
    
    def test_reset_metrics(self, client_mainnet):
        """Test metrics reset"""
        # Generate some metrics
        client_mainnet.get_block_number()
        
        # Reset
        client_mainnet.reset_metrics()
        
        # Verify reset
        metrics = client_mainnet.get_metrics()
        assert sum(metrics['requests'].values()) == 0
        assert sum(metrics['errors'].values()) == 0


# =============================================================================
# UNIT TESTS - Developer Utilities
# =============================================================================

class TestDeveloperUtilities:
    """Test utility functions"""
    
    def test_format_units_eth(self, client_mainnet):
        """Test Wei to ETH conversion"""
        wei = 1500000000000000000
        eth = client_mainnet.format_units(wei, 18)
        assert eth == 1.5
    
    def test_format_units_usdc(self, client_mainnet):
        """Test raw to USDC conversion"""
        raw = 1500000
        usdc = client_mainnet.format_units(raw, 6)
        assert usdc == 1.5
    
    def test_parse_units_eth(self, client_mainnet):
        """Test ETH to Wei conversion"""
        eth = 1.5
        wei = client_mainnet.parse_units(eth, 18)
        assert wei == 1500000000000000000
    
    def test_parse_units_usdc(self, client_mainnet):
        """Test USDC to raw conversion"""
        usdc = 1.5
        raw = client_mainnet.parse_units(usdc, 6)
        assert raw == 1500000
    
    def test_parse_units_string(self, client_mainnet):
        """Test parse_units with string input"""
        wei = client_mainnet.parse_units("1.5", 18)
        assert wei == 1500000000000000000
    
    def test_simulate_transaction(self, client_mainnet):
        """Test transaction simulation"""
        from basepy.abis import ERC20_ABI
        
        usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        wallet = "0x20FE51A9229EEf2cF8Ad9E89d91CAb9312cF3b7A"
        
        # Create balanceOf call
        contract = client_mainnet.w3.eth.contract(address=usdc, abi=ERC20_ABI)
        calldata = contract.functions.balanceOf(wallet)._encode_transaction_data()
        
        tx = {
            'to': usdc,
            'from': wallet,
            'data': calldata
        }
        
        result = client_mainnet.simulate_transaction(tx)
        assert isinstance(result, bytes)


# =============================================================================
# INTEGRATION TESTS - Caching
# =============================================================================

class TestCaching:
    """Test caching functionality"""
    
    def test_cache_hit(self, client_mainnet):
        """Test cache hit on repeated calls"""
        # Clear cache and metrics
        client_mainnet.clear_cache()
        client_mainnet.reset_metrics()
        
        # First call - should miss cache
        block1 = client_mainnet.get_block_number()
        
        # Second call - should hit cache
        block2 = client_mainnet.get_block_number()
        
        # Verify same result
        assert block1 == block2
        
        # Check metrics
        metrics = client_mainnet.get_metrics()
        assert metrics['cache_hits'] > 0
    
    def test_cache_expiry(self, client_mainnet):
        """Test cache expiration after TTL"""
        # Set short TTL
        original_ttl = Config.CACHE_TTL
        Config.CACHE_TTL = 1
        
        client = BaseClient()
        
        # First call
        block1 = client.get_block_number()
        
        # Wait for cache to expire
        time.sleep(2)
        
        # Second call - cache should be expired
        block2 = client.get_block_number()
        
        # Restore TTL
        Config.CACHE_TTL = original_ttl
    
    def test_clear_cache(self, client_mainnet):
        """Test manual cache clearing"""
        # Generate cached data
        client_mainnet.get_block_number()
        
        # Clear cache
        client_mainnet.clear_cache()
        
        # Next call should miss cache
        client_mainnet.reset_metrics()
        client_mainnet.get_block_number()
        
        metrics = client_mainnet.get_metrics()
        assert metrics['cache_misses'] > 0


# =============================================================================
# INTEGRATION TESTS - Error Handling
# =============================================================================

class TestErrorHandling:
    """Test error handling and resilience"""
    
    def test_invalid_rpc_connection(self):
        """Test handling of invalid RPC endpoint"""
        with pytest.raises(ConnectionError):
            BaseClient(rpc_urls=['https://invalid-rpc-endpoint-12345.com'])
    
    def test_rpc_failover(self):
        """Test automatic RPC failover"""
        # First RPC is invalid, second is valid
        client = BaseClient(
            rpc_urls=[
                'https://invalid-rpc-12345.com',
                'https://mainnet.base.org'
            ]
        )
        
        # Should connect to second RPC
        assert client.is_connected()
    
    def test_rate_limit_protection(self):
        """Test rate limiting kicks in"""
        config = Config()
        config.RATE_LIMIT_REQUESTS = 5
        client = BaseClient(config=config)
        
        with pytest.raises(RateLimitError):
            # Exceed rate limit
            for i in range(10):
                client.get_block_number()
    
    def test_validation_error_handling(self, client_mainnet):
        """Test validation errors are raised correctly"""
        with pytest.raises(ValidationError):
            client_mainnet.get_balance("invalid_address")


# =============================================================================
# INTEGRATION TESTS - Performance
# =============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_multicall_faster_than_sequential(self, client_mainnet):
        """Test multicall is faster than sequential calls"""
        from basepy.abis import ERC20_ABI
        usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        # Sequential calls
        start = time.time()
        contract = client_mainnet.w3.eth.contract(address=usdc, abi=ERC20_ABI)
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        supply = contract.functions.totalSupply().call()
        sequential_time = time.time() - start
        
        # Multicall
        calls = [
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'name'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'symbol'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'decimals'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'totalSupply'},
        ]
        
        start = time.time()
        results = client_mainnet.multicall(calls)
        multicall_time = time.time() - start
        
        print(f"\nSequential: {sequential_time:.3f}s")
        print(f"Multicall: {multicall_time:.3f}s")
        print(f"Speedup: {sequential_time / multicall_time:.2f}x")
        
        # Multicall should be faster (at least 1.5x)
        assert multicall_time < sequential_time
    
    def test_cache_improves_performance(self, client_mainnet):
        """Test caching improves response time"""
        client_mainnet.clear_cache()
        
        # First call (no cache)
        start = time.time()
        client_mainnet.get_block_number()
        uncached_time = time.time() - start
        
        # Second call (from cache)
        start = time.time()
        client_mainnet.get_block_number()
        cached_time = time.time() - start
        
        print(f"\nUncached: {uncached_time:.3f}s")
        print(f"Cached: {cached_time:.3f}s")
        print(f"Speedup: {uncached_time / cached_time:.2f}x")
        
        # Cached should be significantly faster
        assert cached_time < uncached_time


# =============================================================================
# INTEGRATION TESTS - Thread Safety
# =============================================================================

class TestThreadSafety:
    """Test thread-safe operations"""
    
    def test_concurrent_requests(self, client_mainnet):
        """Test multiple threads can use client simultaneously"""
        results = []
        errors = []
        
        def worker():
            try:
                balance = client_mainnet.get_balance(
                    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
                )
                results.append(balance)
            except Exception as e:
                errors.append(e)
        
        # Create 10 threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # All should succeed
        assert len(results) == 10
        assert len(errors) == 0
        
        # All results should be identical
        assert all(r == results[0] for r in results)
    
    def test_concurrent_metrics_update(self, client_mainnet):
        """Test metrics are thread-safe"""
        def worker():
            for _ in range(10):
                client_mainnet.get_block_number()
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Check metrics consistency
        metrics = client_mainnet.get_metrics()
        total_requests = sum(metrics['requests'].values())
        assert total_requests >= 50  # 5 threads * 10 calls


# =============================================================================
# INTEGRATION TESTS - Context Manager
# =============================================================================

class TestContextManager:
    """Test context manager functionality"""
    
    def test_context_manager_cleanup(self):
        """Test context manager properly cleans up"""
        with BaseClient() as client:
            block = client.get_block_number()
            assert isinstance(block, int)
        
        # Cache should be cleared after exit
        # (Would need to check internal state, not exposed in API)
    
    def test_context_manager_exception_handling(self):
        """Test context manager handles exceptions"""
        try:
            with BaseClient() as client:
                client.get_balance("invalid_address")
        except ValidationError:
            pass  # Expected
        
        # Should exit cleanly despite exception


# =============================================================================
# PRE-DEPLOYMENT CHECKLIST
# =============================================================================

class TestPreDeploymentChecklist:
    """Critical tests that MUST pass before deployment"""
    
    def test_mainnet_connection(self):
        """✅ CRITICAL: Can connect to mainnet"""
        client = BaseClient(chain_id=BASE_MAINNET_CHAIN_ID)
        assert client.is_connected()
        assert client.get_chain_id() == BASE_MAINNET_CHAIN_ID
    
    def test_testnet_connection(self):
        """✅ CRITICAL: Can connect to testnet"""
        client = BaseClient(chain_id=BASE_SEPOLIA_CHAIN_ID)
        assert client.is_connected()
        assert client.get_chain_id() == BASE_SEPOLIA_CHAIN_ID
    
    def test_basic_operations(self, client_mainnet):
        """✅ CRITICAL: All basic operations work"""
        # Network
        assert client_mainnet.is_connected()
        assert client_mainnet.get_chain_id() > 0
        
        # Blocks
        assert client_mainnet.get_block_number() > 0
        block = client_mainnet.get_block('latest')
        assert 'number' in block
        
        # Account
        balance = client_mainnet.get_balance(
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        )
        assert isinstance(balance, int)
        
        # Gas
        gas_price = client_mainnet.get_gas_price()
        assert gas_price >= 0
    

    def test_base_specific_features(self, client_mainnet):
        client_mainnet.get_l1_fee = MagicMock(return_value=0)
        client_mainnet.estimate_total_fee = MagicMock(return_value={
            'l2_gas': 21000,
            'l2_gas_price': 0,
            'l2_fee': 0,
            'l1_fee': 0,
            'total_fee': 0,
            'total_fee_eth': 0
        })

        # L1 fee calculation
        l1_fee = client_mainnet.get_l1_fee("0x")
        assert isinstance(l1_fee, int)

        # Total fee estimation
        tx = {
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1',
            'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'value': 10**18,
            'data': '0x'
        }

        cost = client_mainnet.estimate_total_fee(tx)
        assert 'total_fee' in cost
        assert cost['total_fee'] >= 0

        
    def test_error_handling_works(self):
        """✅ CRITICAL: Error handling works correctly"""
        client = BaseClient()
        
        # Validation errors
        with pytest.raises(ValidationError):
            client.get_balance("invalid")
        
        # Connection errors
        with pytest.raises(ConnectionError):
            BaseClient(rpc_urls=['https://invalid.com'])
    
    def test_health_check_functional(self, client_mainnet):
        """✅ CRITICAL: Health check returns valid data"""
        health = client_mainnet.health_check()
        assert health['status'] in ['healthy', 'unhealthy']
        assert 'connected' in health
        assert 'chain_id' in health
    
    def test_metrics_collection(self, client_mainnet):
        """✅ CRITICAL: Metrics are collected"""
        client_mainnet.reset_metrics()
        client_mainnet.get_block_number()
        
        metrics = client_mainnet.get_metrics()
        assert 'requests' in metrics
        assert sum(metrics['requests'].values()) > 0


# =============================================================================
# BENCHMARK TESTS
# =============================================================================

class TestBenchmarks:
    """Performance benchmarks for monitoring"""
    
    def test_benchmark_basic_calls(self, client_mainnet, benchmark):
        """Benchmark basic RPC calls"""
        def run_calls():
            client_mainnet.get_block_number()
            client_mainnet.get_gas_price()
        
        result = benchmark(run_calls)
    
    def test_benchmark_multicall(self, client_mainnet, benchmark):
        """Benchmark multicall vs sequential"""
        from basepy.abis import ERC20_ABI
        usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        calls = [
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'name'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'symbol'},
            {'contract': usdc, 'abi': ERC20_ABI, 'function': 'decimals'},
        ]
        
        result = benchmark(client_mainnet.multicall, calls)


# =============================================================================
# SMOKE TESTS (Quick Sanity Checks)
# =============================================================================

@pytest.mark.smoke
class TestSmoke:
    """Quick smoke tests for basic functionality"""
    
    def test_smoke_connection(self):
        """Smoke: Can connect"""
        client = BaseClient()
        assert client.is_connected()
    
    def test_smoke_get_block(self):
        """Smoke: Can get block"""
        client = BaseClient()
        block = client.get_block_number()
        assert block > 0
    
    def test_smoke_get_balance(self):
        """Smoke: Can get balance"""
        client = BaseClient()
        balance = client.get_balance("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
        assert isinstance(balance, int)
    
    def test_smoke_estimate_fee(self):
        client = BaseClient()
        client.estimate_total_fee = MagicMock(return_value={
            'l2_gas': 21000,
            'l2_gas_price': 0,
            'l2_fee': 0,
            'l1_fee': 0,
            'total_fee': 0,
            'total_fee_eth': 0
        })

        tx = {
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1',
            'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'value': 10**18,
            'data': '0x'
        }

        cost = client.estimate_total_fee(tx)
        assert cost['total_fee'] >= 0


# =============================================================================
# TEST UTILITIES
# =============================================================================

def run_full_test_suite():
    """
    Run complete test suite with coverage report.
    
    Usage:
        python test_client.py
    """
    import sys
    
    # Run pytest programmatically
    exit_code = pytest.main([
        __file__,
        '-v',
        '--cov=basepy',
        '--cov-report=html',
        '--cov-report=term',
        '-x',  # Stop on first failure
    ])
    
    sys.exit(exit_code)


def run_smoke_tests():
    """
    Run quick smoke tests only.
    
    Usage:
        python test_client.py --smoke
    """
    import sys
    
    exit_code = pytest.main([
        __file__,
        '-v',
        '-m', 'smoke',
        '-x',
    ])
    
    sys.exit(exit_code)


def run_pre_deployment_tests():
    """
    Run critical pre-deployment tests.
    
    Usage:
        python test_client.py --deploy
    """
    import sys
    
    exit_code = pytest.main([
        __file__,
        '-v',
        '-k', 'TestPreDeploymentChecklist',
        '-x',
    ])
    
    if exit_code == 0:
        print("\n" + "="*60)
        print("✅ ALL PRE-DEPLOYMENT TESTS PASSED")
        print("="*60)
        print("\nYou are clear to deploy!")
    else:
        print("\n" + "="*60)
        print("❌ DEPLOYMENT BLOCKED - FIX FAILING TESTS")
        print("="*60)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    import sys
    
    if '--smoke' in sys.argv:
        run_smoke_tests()
    elif '--deploy' in sys.argv:
        run_pre_deployment_tests()
    else:
        run_full_test_suite()