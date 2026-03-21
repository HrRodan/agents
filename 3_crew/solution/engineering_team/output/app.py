import gradio as gr
from accounts import Account, InsufficientFundsError, InsufficientSharesError, get_share_price

# Global account instance (single user demo)
account = None

def create_account(account_id, owner_name):
    global account
    account = Account(account_id, owner_name)
    return f"Account created: {account_id} for {owner_name}", ""

def deposit(amount):
    global account
    if account is None:
        return "Error: Please create an account first", ""
    try:
        account.deposit(float(amount))
        return f"Deposited ${float(amount):.2f}. Cash balance: ${account.get_cash_balance():.2f}", ""
    except ValueError as e:
        return "", str(e)

def withdraw(amount):
    global account
    if account is None:
        return "Error: Please create an account first", ""
    try:
        account.withdraw(float(amount))
        return f"Withdrew ${float(amount):.2f}. Cash balance: ${account.get_cash_balance():.2f}", ""
    except (ValueError, InsufficientFundsError) as e:
        return "", str(e)

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Error: Please create an account first", ""
    try:
        account.buy_shares(symbol.upper(), float(quantity))
        return f"Bought {quantity} shares of {symbol.upper()}. Cash balance: ${account.get_cash_balance():.2f}", ""
    except (ValueError, InsufficientFundsError) as e:
        return "", str(e)

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Error: Please create an account first", ""
    try:
        account.sell_shares(symbol.upper(), float(quantity))
        return f"Sold {quantity} shares of {symbol.upper()}. Cash balance: ${account.get_cash_balance():.2f}", ""
    except (ValueError, InsufficientSharesError) as e:
        return "", str(e)

def get_status():
    global account
    if account is None:
        return "Please create an account first"
    holdings = account.get_holdings()
    holdings_str = ", ".join([f"{sym}: {qty}" for sym, qty in holdings.items()]) if holdings else "None"
    status = f"""Account: {account.account_id} ({account.owner_name})
Cash Balance: ${account.get_cash_balance():.2f}
Portfolio Value: ${account.get_portfolio_value():.2f}
Total Value: ${account.get_total_value():.2f}
Profit/Loss: ${account.get_profit_loss():.2f}
Holdings: {holdings_str}"""
    return status

def get_transactions():
    global account
    if account is None:
        return "Please create an account first"
    transactions = account.get_transaction_history()
    if not transactions:
        return "No transactions yet"
    lines = []
    for tx in transactions:
        symbol = tx.symbol or "N/A"
        lines.append(f"{tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {tx.type.value.upper():10} | {symbol:5} | Qty: {tx.quantity:6.2f} | ${tx.total_amount:9.2f}")
    return "\n".join(lines)

def get_available_prices():
    prices = {"AAPL": get_share_price("AAPL"), "TSLA": get_share_price("TSLA"), "GOOGL": get_share_price("GOOGL")}
    return "\n".join([f"{sym}: ${price:.2f}" for sym, price in prices.items()])

with gr.Blocks(title="Trading Simulation") as app:
    gr.Markdown("# Trading Simulation Platform")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Create Account")
            acc_id = gr.Textbox(label="Account ID", value="ACC001")
            owner = gr.Textbox(label="Owner Name", value="Demo Trader")
            create_btn = gr.Button("Create Account")
            create_msg = gr.Textbox(label="Result")
            create_err = gr.Textbox(label="Error", visible=False)
        
        with gr.Column():
            gr.Markdown("### Available Share Prices")
            prices_btn = gr.Button("Show Prices")
            prices_text = gr.Textbox(label="Prices", lines=3)
            prices_btn.click(get_available_prices, outputs=prices_text)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Deposit Funds")
            dep_amt = gr.Number(label="Amount", value=10000)
            dep_btn = gr.Button("Deposit")
            dep_msg = gr.Textbox(label="Result")
        
        with gr.Column():
            gr.Markdown("### Withdraw Funds")
            with_amt = gr.Number(label="Amount", value=1000)
            with_btn = gr.Button("Withdraw")
            with_msg = gr.Textbox(label="Result")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Buy Shares")
            buy_sym = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
            buy_qty = gr.Number(label="Quantity", value=1)
            buy_btn = gr.Button("Buy")
            buy_msg = gr.Textbox(label="Result")
        
        with gr.Column():
            gr.Markdown("### Sell Shares")
            sell_sym = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
            sell_qty = gr.Number(label="Quantity", value=1)
            sell_btn = gr.Button("Sell")
            sell_msg = gr.Textbox(label="Result")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Account Status")
            status_btn = gr.Button("Refresh Status")
            status_text = gr.Textbox(label="Status", lines=6)
            status_btn.click(get_status, outputs=status_text)
        
        with gr.Column():
            gr.Markdown("### Transaction History")
            tx_btn = gr.Button("Show Transactions")
            tx_text = gr.Textbox(label="Transactions", lines=6)
            tx_btn.click(get_transactions, outputs=tx_text)
    
    # Wire up buttons
    create_btn.click(create_account, inputs=[acc_id, owner], outputs=[create_msg, create_err])
    dep_btn.click(deposit, inputs=[dep_amt], outputs=[dep_msg, dep_msg])
    with_btn.click(withdraw, inputs=[with_amt], outputs=[with_msg, with_msg])
    buy_btn.click(buy_shares, inputs=[buy_sym, buy_qty], outputs=[buy_msg, buy_msg])
    sell_btn.click(sell_shares, inputs=[sell_sym, sell_qty], outputs=[sell_msg, sell_msg])

if __name__ == "__main__":
    app.launch()