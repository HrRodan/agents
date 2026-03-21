# Design Document: Trading Simulation Account Management System

## Module Specification: `accounts.py`

### Overview
This module provides a complete, self-contained account management system for a trading simulation platform. It implements the `Account` class which manages cash balances, share holdings, transaction history, and profit/loss calculations. The module includes a test implementation of the `get_share_price()` function with fixed prices for AAPL, TSLA, and GOOGL.

### Architecture

#### Exceptions
The module defines two custom exceptions for business rule violations:
- `InsufficientFundsError`: Raised when withdrawing beyond cash balance or buying shares without adequate funds
- `InsufficientSharesError`: Raised when attempting to sell more shares than currently held

#### Data Structures
- `TransactionType` (Enum): Enumeration of transaction types (DEPOSIT, WITHDRAWAL, BUY, SELL)
- `Transaction` (NamedTuple): Immutable record of each transaction containing timestamp, type, symbol, quantity, price per share, and total amount

#### External Price Feed
- `get_share_price(symbol: str) -> float`: Returns current market price for supported symbols (AAPL: $175.50, TSLA: $240.00, GOOGL: $140.25). Raises `ValueError` for unknown symbols.

#### Core Class: `Account`

**Constructor**
```python
def __init__(self, account_id: str, owner_name: str)
```
Initializes a new account with zero balance, empty holdings, and empty transaction history. Tracks cumulative deposits and withdrawals separately for P&L calculation.

**Cash Management Methods**
```python
def deposit(self, amount: float) -> None
```
Adds cash to the account. Validates positive amount. Creates a DEPOSIT transaction record. Updates total deposits tracker.

```python
def withdraw(self, amount: float) -> None
```
Removes cash from the account. Validates that `amount <= cash_balance` to prevent negative balance. Creates a WITHDRAWAL transaction record. Updates total withdrawals tracker. Raises `InsufficientFundsError` if overdraft attempted.

**Trading Methods**
```python
def buy_shares(self, symbol: str, quantity: float) -> None
```
Purchases shares by symbol. Validates positive quantity and sufficient cash (`quantity * price <= cash_balance`). Updates cash balance (reduction) and holdings dictionary (accumulation). Creates BUY transaction with negative total_amount (cash outflow). Raises `InsufficientFundsError` or `ValueError`.

```python
def sell_shares(self, symbol: str, quantity: float) -> None
```
Sells shares by symbol. Validates positive quantity and sufficient holdings (`quantity <= current_holdings`). Updates cash balance (increase) and holdings dictionary (reduction, removes entry if quantity reaches zero). Creates SELL transaction with positive total_amount (cash inflow). Raises `InsufficientSharesError` or `ValueError`.

**Reporting Methods**
```python
def get_cash_balance(self) -> float
```
Returns current available cash.

```python
def get_holdings(self) -> Dict[str, float]
```
Returns shallow copy of holdings dictionary mapping symbol to quantity owned.

```python
def get_portfolio_value(self) -> float
```
Calculates current market value of all holdings by summing `quantity * get_share_price(symbol)` for each position. Handles missing prices gracefully (skips unknown symbols).

```python
def get_total_value(self) -> float
```
Returns `cash_balance + portfolio_value`.

```python
def get_profit_loss(self) -> float
```
Calculates trading P&L as: `Total Value - (Total Deposits - Total Withdrawals)`. Positive value indicates profit, negative indicates loss.

```python
def get_transaction_history(self) -> List[Transaction]
```
Returns chronological list of all transactions (deposits, withdrawals, buys, sells) as `Transaction` namedtuples.

### Complete Implementation

```python
"""
Account Management Module for Trading Simulation Platform.

This module provides a complete self-contained system for managing trading accounts,
including cash operations, share trading, portfolio valuation, and transaction history.
"""

from datetime import datetime
from typing import Dict, List, Optional, NamedTuple
from enum import Enum


class TransactionType(Enum):
    """Types of account transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BUY = "buy"
    SELL = "sell"


class InsufficientFundsError(Exception):
    """Raised when an operation would result in negative cash balance."""
    pass


class InsufficientSharesError(Exception):
    """Raised when attempting to sell more shares than owned."""
    pass


class Transaction(NamedTuple):
    """
    Represents a single account transaction.
    
    Attributes:
        timestamp: When the transaction occurred
        type: Category of transaction (deposit, withdrawal, buy, sell)
        symbol: Stock ticker for trades, None for cash operations
        quantity: Number of shares (0 for cash operations)
        price: Price per share (0.0 for cash operations)
        total_amount: Cash impact (positive for inflow, negative for outflow)
    """
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str]
    quantity: float
    price: float
    total_amount: float


def get_share_price(symbol: str) -> float:
    """
    Returns the current price of a share.
    
    Test implementation returns fixed prices for known symbols.
    
    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'TSLA', 'GOOGL')
        
    Returns:
        float: Current price per share
        
    Raises:
        ValueError: If symbol is not recognized
    """
    prices = {
        "AAPL": 175.50,
        "TSLA": 240.00,
        "GOOGL": 140.25
    }
    if symbol not in prices:
        raise ValueError(f"Unknown symbol: {symbol}. Available: {list(prices.keys())}")
    return prices[symbol]


class Account:
    """
    Manages a trading account with cash and share holdings.
    
    Attributes:
        account_id (str): Unique identifier for the account
        owner_name (str): Name of the account owner
    """
    
    def __init__(self, account_id: str, owner_name: str):
        """
        Initialize a new trading account with zero balance and no holdings.
        
        Args:
            account_id: Unique account identifier
            owner_name: Name of the account owner
        """
        self.account_id = account_id
        self.owner_name = owner_name
        self._cash_balance = 0.0
        self._total_deposits = 0.0
        self._total_withdrawals = 0.0
        self._holdings: Dict[str, float] = {}  # symbol -> quantity
        self._transactions: List[Transaction] = []
    
    def deposit(self, amount: float) -> None:
        """
        Deposit cash into the account.
        
        Args:
            amount: Amount to deposit (must be positive)
            
        Raises:
            ValueError: If amount is not positive
            
        Side Effects:
            Increases cash balance, records transaction
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self._cash_balance += amount
        self._total_deposits += amount
        
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.DEPOSIT,
            symbol=None,
            quantity=0,
            price=0.0,
            total_amount=amount
        )
        self._transactions.append(transaction)
    
    def withdraw(self, amount: float) -> None:
        """
        Withdraw cash from the account.
        
        Prevents withdrawal if it would result in negative cash balance.
        
        Args:
            amount: Amount to withdraw (must be positive)
            
        Raises:
            ValueError: If amount is not positive
            InsufficientFundsError: If withdrawal exceeds available cash
            
        Side Effects:
            Decreases cash balance, records transaction
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self._cash_balance:
            raise InsufficientFundsError(
                f"Insufficient funds: balance {self._cash_balance:.2f}, requested {amount:.2f}"
            )
        
        self._cash_balance -= amount
        self._total_withdrawals += amount
        
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.WITHDRAWAL,
            symbol=None,
            quantity=0,
            price=0.0,
            total_amount=-amount
        )
        self._transactions.append(transaction)
    
    def buy_shares(self, symbol: str, quantity: float) -> None:
        """
        Buy shares of a stock.
        
        Prevents purchase if there are insufficient funds to cover the total cost.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares to buy (must be positive)
            
        Raises:
            ValueError: If quantity is not positive or symbol is invalid
            InsufficientFundsError: If insufficient cash for purchase
            
        Side Effects:
            Decreases cash, increases holdings, records transaction
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self._cash_balance:
            raise InsufficientFundsError(
                f"Insufficient funds: need {total_cost:.2f}, have {self._cash_balance:.2f}"
            )
        
        self._cash_balance -= total_cost
        
        # Update holdings
        current_qty = self._holdings.get(symbol, 0)
        self._holdings[symbol] = current_qty + quantity
        
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.BUY,
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=-total_cost
        )
        self._transactions.append(transaction)
    
    def sell_shares(self, symbol: str, quantity: float) -> None:
        """
        Sell shares of a stock.
        
        Prevents selling more shares than currently held.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares to sell (must be positive)
            
        Raises:
            ValueError: If quantity is not positive
            InsufficientSharesError: If attempting to sell more shares than owned
            
        Side Effects:
            Increases cash, decreases holdings, records transaction
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        current_qty = self._holdings.get(symbol, 0)
        if quantity > current_qty:
            raise InsufficientSharesError(
                f"Insufficient shares: own {current_qty}, requested {quantity}"
            )
        
        price = get_share_price(symbol)
        total_proceeds = price * quantity
        
        self._cash_balance += total_proceeds
        
        # Update holdings
        new_qty = current_qty - quantity
        if new_qty == 0:
            del self._holdings[symbol]
        else:
            self._holdings[symbol] = new_qty
        
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=total_proceeds
        )
        self._transactions.append(transaction)
    
    def get_cash_balance(self) -> float:
        """Return current cash balance available for trading."""
        return self._cash_balance
    
    def get_holdings(self) -> Dict[str, float]:
        """
        Return current share holdings.
        
        Returns:
            Dictionary mapping stock symbol to quantity owned
        """
        return self._holdings.copy()
    
    def get_portfolio_value(self) -> float:
        """
        Calculate current market value of all share holdings.
        
        Returns:
            Total value of holdings based on current market prices
        """
        total = 0.0
        for symbol, quantity in self._holdings.items():
            try:
                price = get_share_price(symbol)
                total += price * quantity
            except ValueError:
                # Skip symbols with unavailable prices
                continue
        return total
    
    def get_total_value(self) -> float:
        """
        Calculate total account value.
        
        Returns:
            Sum of cash balance and portfolio market value
        """
        return self._cash_balance + self.get_portfolio_value()
    
    def get_profit_loss(self) -> float:
        """
        Calculate profit or loss from trading activities.
        
        Formula: Current Total Value - Net Investment
        Net Investment = Total Deposits - Total Withdrawals
        
        Returns:
            Profit/loss amount (positive for profit, negative for loss)
        """
        net_investment = self._total_deposits - self._total_withdrawals
        return self.get_total_value() - net_investment
    
    def get_transaction_history(self) -> List[Transaction]:
        """
        Return chronological list of all account transactions.
        
        Returns:
            List of Transaction namedtuples in order of execution
        """
        return self._transactions.copy()


# Example usage and basic testing
if __name__ == "__main__":
    # Demonstration of module functionality
    acc = Account("ACC001", "Demo Trader")
    
    # Initial funding
    acc.deposit(10000.00)
    
    # Trading activity
    acc.buy_shares("AAPL", 10)    # Cost: ~1755.00
    acc.buy_shares("TSLA", 5)     # Cost: ~1200.00
    acc.sell_shares("AAPL", 5)    # Proceeds: ~877.50
    
    # Reporting
    print(f"Cash Balance: ${acc.get_cash_balance():.2f}")
    print(f"Portfolio Value: ${acc.get_portfolio_value():.2f}")
    print(f"Total Value: ${acc.get_total_value():.2f}")
    print(f"Profit/Loss: ${acc.get_profit_loss():.2f}")
    print(f"Current Holdings: {acc.get_holdings()}")
    print("\nTransaction History:")
    for tx in acc.get_transaction_history():
        print(f"{tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {tx.type.value.upper():10} | "
              f"{tx.symbol or 'N/A':5} | Qty: {tx.quantity:6.2f} | "
              f"${tx.total_amount:9.2f}")
```

### Design Notes

1. **Thread Safety**: This implementation is not thread-safe. For multi-threaded environments, methods modifying shared state (`deposit`, `withdraw`, `buy_shares`, `sell_shares`) would require locking mechanisms.

2. **Persistence**: The current design is in-memory only. For production use, transactions should be persisted to a database, and the `Account` class would require loading/saving methods or repository pattern integration.

3. **Fractional Shares**: The implementation supports fractional shares (uses `float` for quantities), which is appropriate for modern trading simulations.

4. **P&L Calculation**: The profit/loss calculation uses the standard formula of Current Value minus Net Investment (deposits minus withdrawals). This represents the total return on invested capital.