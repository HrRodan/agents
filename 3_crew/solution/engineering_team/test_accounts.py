
import unittest
from datetime import datetime
from accounts import (
    Account,
    TransactionType,
    Transaction,
    get_share_price,
    InsufficientFundsError,
    InsufficientSharesError
)


class TestGetSharePrice(unittest.TestCase):
    """Tests for the get_share_price function."""
    
    def test_known_symbols_return_expected_prices(self):
        """Test that known symbols return correct prices."""
        self.assertEqual(get_share_price("AAPL"), 175.50)
        self.assertEqual(get_share_price("TSLA"), 240.00)
        self.assertEqual(get_share_price("GOOGL"), 140.25)
    
    def test_unknown_symbol_raises_value_error(self):
        """Test that unknown symbols raise ValueError."""
        with self.assertRaises(ValueError) as context:
            get_share_price("INVALID")
        self.assertIn("Unknown symbol", str(context.exception))


class TestTransactionType(unittest.TestCase):
    """Tests for the TransactionType enum."""
    
    def test_transaction_types_exist(self):
        """Test that all expected transaction types exist."""
        self.assertEqual(TransactionType.DEPOSIT.value, "deposit")
        self.assertEqual(TransactionType.WITHDRAWAL.value, "withdrawal")
        self.assertEqual(TransactionType.BUY.value, "buy")
        self.assertEqual(TransactionType.SELL.value, "sell")
    
    def test_transaction_types_count(self):
        """Test that we have exactly 4 transaction types."""
        self.assertEqual(len(TransactionType), 4)


class TestTransaction(unittest.TestCase):
    """Tests for the Transaction NamedTuple."""
    
    def test_transaction_creation(self):
        """Test that a transaction can be created with all fields."""
        tx = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.DEPOSIT,
            symbol=None,
            quantity=0,
            price=0.0,
            total_amount=1000.0
        )
        self.assertEqual(tx.type, TransactionType.DEPOSIT)
        self.assertIsNone(tx.symbol)
        self.assertEqual(tx.quantity, 0)
        self.assertEqual(tx.total_amount, 1000.0)
    
    def test_transaction_immutable(self):
        """Test that transaction fields cannot be modified after creation."""
        tx = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.DEPOSIT,
            symbol=None,
            quantity=0,
            price=0.0,
            total_amount=1000.0
        )
        with self.assertRaises(AttributeError):
            tx.total_amount = 500.0


class TestAccountCreation(unittest.TestCase):
    """Tests for Account initialization."""
    
    def test_account_initial_state(self):
        """Test that a new account has zero balance and no holdings."""
        acc = Account("ACC001", "John Doe")
        self.assertEqual(acc.account_id, "ACC001")
        self.assertEqual(acc.owner_name, "John Doe")
        self.assertEqual(acc.get_cash_balance(), 0.0)
        self.assertEqual(acc.get_holdings(), {})
    
    def test_account_attributes_set(self):
        """Test that account_id and owner_name are properly set."""
        acc = Account("TEST123", "Jane Smith")
        self.assertEqual(acc.account_id, "TEST123")
        self.assertEqual(acc.owner_name, "Jane Smith")


class TestAccountDeposit(unittest.TestCase):
    """Tests for Account.deposit method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_deposit_positive_amount(self):
        """Test that depositing a positive amount increases balance."""
        self.acc.deposit(1000.0)
        self.assertEqual(self.acc.get_cash_balance(), 1000.0)
    
    def test_deposit_adds_to_transaction_history(self):
        """Test that deposit creates a transaction record."""
        self.acc.deposit(500.0)
        history = self.acc.get_transaction_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].type, TransactionType.DEPOSIT)
        self.assertEqual(history[0].total_amount, 500.0)
    
    def test_deposit_zero_raises_error(self):
        """Test that depositing zero raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.acc.deposit(0)
        self.assertIn("positive", str(context.exception).lower())
    
    def test_deposit_negative_raises_error(self):
        """Test that depositing negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.acc.deposit(-100.0)
    
    def test_multiple_deposits(self):
        """Test that multiple deposits accumulate correctly."""
        self.acc.deposit(1000.0)
        self.acc.deposit(500.0)
        self.acc.deposit(250.0)
        self.assertEqual(self.acc.get_cash_balance(), 1750.0)


class TestAccountWithdraw(unittest.TestCase):
    """Tests for Account.withdraw method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_withdraw_positive_amount(self):
        """Test that withdrawing a positive amount decreases balance."""
        self.acc.deposit(1000.0)
        self.acc.withdraw(300.0)
        self.assertEqual(self.acc.get_cash_balance(), 700.0)
    
    def test_withdraw_adds_to_transaction_history(self):
        """Test that withdraw creates a transaction record."""
        self.acc.deposit(1000.0)
        self.acc.withdraw(200.0)
        history = self.acc.get_transaction_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1].type, TransactionType.WITHDRAWAL)
        self.assertEqual(history[1].total_amount, -200.0)
    
    def test_withdraw_exact_balance(self):
        """Test that withdrawing the exact balance works."""
        self.acc.deposit(1000.0)
        self.acc.withdraw(1000.0)
        self.assertEqual(self.acc.get_cash_balance(), 0.0)
    
    def test_withdraw_insufficient_funds(self):
        """Test that withdrawing more than balance raises InsufficientFundsError."""
        self.acc.deposit(100.0)
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(200.0)
    
    def test_withdraw_zero_raises_error(self):
        """Test that withdrawing zero raises ValueError."""
        self.acc.deposit(1000.0)
        with self.assertRaises(ValueError):
            self.acc.withdraw(0)
    
    def test_withdraw_negative_raises_error(self):
        """Test that withdrawing negative amount raises ValueError."""
        self.acc.deposit(1000.0)
        with self.assertRaises(ValueError):
            self.acc.withdraw(-50.0)
    
    def test_withdraw_preserves_remaining_balance(self):
        """Test that failed withdrawal does not change balance."""
        self.acc.deposit(100.0)
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(200.0)
        self.assertEqual(self.acc.get_cash_balance(), 100.0)


class TestAccountBuyShares(unittest.TestCase):
    """Tests for Account.buy_shares method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_buy_shares_success(self):
        """Test successful share purchase."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        # 10 * 175.50 = 1755.00
        self.assertAlmostEqual(self.acc.get_cash_balance(), 245.0, places=2)
        self.assertEqual(self.acc.get_holdings()["AAPL"], 10)
    
    def test_buy_shares_adds_to_transaction_history(self):
        """Test that buy creates a transaction record."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 5)
        history = self.acc.get_transaction_history()
        self.assertEqual(history[1].type, TransactionType.BUY)
        self.assertEqual(history[1].symbol, "AAPL")
        self.assertEqual(history[1].quantity, 5)
    
    def test_buy_shares_insufficient_funds(self):
        """Test that buying without enough funds raises error."""
        self.acc.deposit(100.0)
        with self.assertRaises(InsufficientFundsError):
            self.acc.buy_shares("AAPL", 10)
    
    def test_buy_shares_zero_quantity(self):
        """Test that buying zero shares raises ValueError."""
        self.acc.deposit(2000.0)
        with self.assertRaises(ValueError):
            self.acc.buy_shares("AAPL", 0)
    
    def test_buy_shares_negative_quantity(self):
        """Test that buying negative shares raises ValueError."""
        self.acc.deposit(2000.0)
        with self.assertRaises(ValueError):
            self.acc.buy_shares("AAPL", -5)
    
    def test_buy_shares_invalid_symbol(self):
        """Test that buying invalid symbol raises ValueError."""
        self.acc.deposit(2000.0)
        with self.assertRaises(ValueError):
            self.acc.buy_shares("INVALID", 5)
    
    def test_buy_multiple_purchases_same_symbol(self):
        """Test that buying same symbol accumulates quantity."""
        self.acc.deposit(5000.0)
        self.acc.buy_shares("AAPL", 5)
        self.acc.buy_shares("AAPL", 3)
        self.assertEqual(self.acc.get_holdings()["AAPL"], 8)
    
    def test_buy_multiple_purchases_different_symbols(self):
        """Test that buying different symbols works correctly."""
        self.acc.deposit(10000.0)
        self.acc.buy_shares("AAPL", 10)
        self.acc.buy_shares("TSLA", 5)
        holdings = self.acc.get_holdings()
        self.assertEqual(holdings["AAPL"], 10)
        self.assertEqual(holdings["TSLA"], 5)


class TestAccountSellShares(unittest.TestCase):
    """Tests for Account.sell_shares method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_sell_shares_success(self):
        """Test successful share sale."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        self.acc.sell_shares("AAPL", 5)
        self.assertEqual(self.acc.get_holdings()["AAPL"], 5)
        # Cash should be 245 + (5 * 175.50) = 1122.50
        self.assertAlmostEqual(self.acc.get_cash_balance(), 1122.50, places=2)
    
    def test_sell_shares_adds_to_transaction_history(self):
        """Test that sell creates a transaction record."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 5)
        self.acc.sell_shares("AAPL", 2)
        history = self.acc.get_transaction_history()
        self.assertEqual(history[2].type, TransactionType.SELL)
        self.assertEqual(history[2].symbol, "AAPL")
        self.assertEqual(history[2].quantity, 2)
    
    def test_sell_all_shares_removes_from_holdings(self):
        """Test that selling all shares removes symbol from holdings."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        self.acc.sell_shares("AAPL", 10)
        self.assertNotIn("AAPL", self.acc.get_holdings())
    
    def test_sell_shares_insufficient_shares(self):
        """Test that selling more than owned raises InsufficientSharesError."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 5)
        with self.assertRaises(InsufficientSharesError):
            self.acc.sell_shares("AAPL", 10)
    
    def test_sell_shares_zero_quantity(self):
        """Test that selling zero shares raises ValueError."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 5)
        with self.assertRaises(ValueError):
            self.acc.sell_shares("AAPL", 0)
    
    def test_sell_shares_negative_quantity(self):
        """Test that selling negative shares raises ValueError."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 5)
        with self.assertRaises(ValueError):
            self.acc.sell_shares("AAPL", -3)
    
    def test_sell_shares_not_owned(self):
        """Test that selling shares not owned raises error."""
        self.acc.deposit(2000.0)
        with self.assertRaises(InsufficientSharesError):
            self.acc.sell_shares("AAPL", 5)
    
    def test_sell_preserves_other_holdings(self):
        """Test that selling from one symbol preserves others."""
        self.acc.deposit(10000.0)
        self.acc.buy_shares("AAPL", 10)
        self.acc.buy_shares("TSLA", 5)
        self.acc.sell_shares("AAPL", 5)
        holdings = self.acc.get_holdings()
        self.assertEqual(holdings["AAPL"], 5)
        self.assertEqual(holdings["TSLA"], 5)


class TestAccountPortfolio(unittest.TestCase):
    """Tests for Account portfolio valuation methods."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_get_portfolio_value_empty(self):
        """Test that empty portfolio has zero value."""
        self.assertEqual(self.acc.get_portfolio_value(), 0.0)
    
    def test_get_portfolio_value_single_holding(self):
        """Test portfolio value with single holding."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        # 10 * 175.50 = 1755.00
        self.assertAlmostEqual(self.acc.get_portfolio_value(), 1755.0, places=2)
    
    def test_get_portfolio_value_multiple_holdings(self):
        """Test portfolio value with multiple holdings."""
        self.acc.deposit(10000.0)
        self.acc.buy_shares("AAPL", 10)   # 1755.00
        self.acc.buy_shares("TSLA", 5)    # 1200.00
        # Total: 2955.00
        self.assertAlmostEqual(self.acc.get_portfolio_value(), 2955.0, places=2)
    
    def test_get_total_value(self):
        """Test total value combines cash and portfolio."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        # Cash: 245.00, Portfolio: 1755.00, Total: 2000.00
        self.assertAlmostEqual(self.acc.get_total_value(), 2000.0, places=2)
    
    def test_get_total_value_cash_only(self):
        """Test total value with cash only."""
        self.acc.deposit(1000.0)
        self.assertEqual(self.acc.get_total_value(), 1000.0)


class TestAccountProfitLoss(unittest.TestCase):
    """Tests for Account.get_profit_loss method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_profit_loss_no_activity(self):
        """Test profit/loss is zero when no activity."""
        self.assertEqual(self.acc.get_profit_loss(), 0.0)
    
    def test_profit_loss_cash_only_profit(self):
        """Test profit/loss with deposits only."""
        self.acc.deposit(1000.0)
        self.assertEqual(self.acc.get_profit_loss(), 1000.0)
    
    def test_profit_loss_buy_sell_profit(self):
        """Test profit calculation after buying and selling at higher price."""
        # With fixed prices, selling at same price = break even on trade
        # but we have cash remaining
        self.acc.deposit(1000.0)
        self.acc.buy_shares("AAPL", 5)   # Cost: 877.50
        self.acc.sell_shares("AAPL", 5)  # Proceeds: 877.50
        # Cash: 1000.00, Portfolio: 0, Deposits: 1000
        # Profit: 1000 - 1000 = 0
        self.assertAlmostEqual(self.acc.get_profit_loss(), 0.0, places=2)
    
    def test_profit_loss_with_withdrawals(self):
        """Test profit/loss considers withdrawals."""
        self.acc.deposit(1000.0)
        self.acc.withdraw(300.0)
        # Net investment: 1000 - 300 = 700
        self.assertAlmostEqual(self.acc.get_profit_loss(), 700.0, places=2)


class TestAccountTransactionHistory(unittest.TestCase):
    """Tests for Account.get_transaction_history method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_empty_history(self):
        """Test that new account has empty transaction history."""
        self.assertEqual(len(self.acc.get_transaction_history()), 0)
    
    def test_history_returns_copy(self):
        """Test that get_transaction_history returns a copy."""
        self.acc.deposit(100.0)
        history = self.acc.get_transaction_history()
        history.clear()  # Should not affect internal list
        self.assertEqual(len(self.acc.get_transaction_history()), 1)
    
    def test_history_order(self):
        """Test that transactions are recorded in chronological order."""
        self.acc.deposit(1000.0)
        self.acc.withdraw(200.0)
        self.acc.deposit(500.0)
        history = self.acc.get_transaction_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].type, TransactionType.DEPOSIT)
        self.assertEqual(history[1].type, TransactionType.WITHDRAWAL)
        self.assertEqual(history[2].type, TransactionType.DEPOSIT)


class TestAccountGetHoldings(unittest.TestCase):
    """Tests for Account.get_holdings method."""
    
    def setUp(self):
        self.acc = Account("ACC001", "Test User")
    
    def test_empty_holdings(self):
        """Test that new account has empty holdings."""
        self.assertEqual(self.acc.get_holdings(), {})
    
    def test_holdings_returns_copy(self):
        """Test that get_holdings returns a copy."""
        self.acc.deposit(2000.0)
        self.acc.buy_shares("AAPL", 10)
        holdings = self.acc.get_holdings()
        holdings["AAPL"] = 999  # Should not affect internal dict
        self.assertEqual(self.acc.get_holdings()["AAPL"], 10)


class TestAccountIntegration(unittest.TestCase):
    """Integration tests for complete trading scenarios."""
    
    def test_full_trading_cycle(self):
        """Test a complete trading cycle with deposits, trades, and withdrawals."""
        acc = Account("ACC001", "Test Trader")
        
        # Start with initial deposit
        acc.deposit(10000.0)
        self.assertEqual(acc.get_cash_balance(), 10000.0)
        
        # Buy some stocks
        acc.buy_shares("AAPL", 10)  # 1755.00
        acc.buy_shares("TSLA", 5)   # 1200.00
        
        # Check holdings
        holdings = acc.get_holdings()
        self.assertEqual(holdings["AAPL"], 10)
        self.assertEqual(holdings["TSLA"], 5)
        
        # Sell some shares
        acc.sell_shares("AAPL", 5)
        self.assertEqual(acc.get_holdings()["AAPL"], 5)
        
        # Calculate expected values
        # Cash: 10000 - 1755 - 1200 + (5 * 175.50) = 10000 - 2955 + 877.50 = 7922.50
        expected_cash = 10000.0 - 1755.0 - 1200.0 + 877.50
        self.assertAlmostEqual(acc.get_cash_balance(), expected_cash, places=2)
        
        # Portfolio: 5 AAPL + 5 TSLA = 877.50 + 1200.00 = 2077.50
        expected_portfolio = (5 * 175.50) + (5 * 240.00)
        self.assertAlmostEqual(acc.get_portfolio_value(), expected_portfolio, places=2)
        
        # Total value should equal original deposit (break even without profit)
        self.assertAlmostEqual(acc.get_total_value(), 10000.0, places=2)
        self.assertAlmostEqual(acc.get_profit_loss(), 0.0, places=2)
    
    def test_transaction_count(self):
        """Test that all transactions are recorded."""
        acc = Account("ACC001", "Test Trader")
        acc.deposit(1000.0)
        acc.withdraw(100.0)
        acc.buy_shares("AAPL", 5)
        acc.sell_shares("AAPL", 2)
        
        # Should have exactly 4 transactions
        self.assertEqual(len(acc.get_transaction_history()), 4)
        
        # Verify types
        types = [tx.type for tx in acc.get_transaction_history()]
        self.assertEqual(types[0], TransactionType.DEPOSIT)
        self.assertEqual(types[1], TransactionType.WITHDRAWAL)
        self.assertEqual(types[2], TransactionType.BUY)
        self.assertEqual(types[3], TransactionType.SELL)


if __name__ == "__main__":
    unittest.main()
