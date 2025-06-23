"""
display.py
Functions for displaying menus, promo codes, and order details in a restaurant system.
"""

from datetime import datetime


# ==============================================
# CORE DISPLAY FUNCTIONS
# ==============================================

def show_menu(menu_items):
    """Display the menu with consistent formatting and availability."""
    # Header section
    print(f"\n{'=' * 80}")
    print(f"{f'{"MENU"}':^{80}}")
    print(f"{'=' * 80}")
    
    # Column headers
    print(f"{'Code':<6} | "
          f"{'Name':<30} | "
          f"{'Price':<9} | "
          f"{'Category':<11} | "
          f"{'Availability':>9}")
    print("-" * 80)

    # Menu items
    for code, item in menu_items.items():
        print(f"{code:<6} | "
              f"{item['name']:<30} | "
              f"RM{item['price']:>7.2f} | "
              f"{item['category']:<11} | "
              f"{item['availability']:>9}")
    
    print("=" * 80)

def show_promo_codes(promo_codes):
    """Display promo codes with consistent formatting."""
    print(f"\n{'=' * 80}")
    print(f"{f'{"PROMO CODES"}':^{80}}")
    print(f"{'=' * 80}")
    
    # Column headers
    print(f"{'Code':<17} | {'Type':<12} | {'Value':<8} | {'Description':<30}")
    print("-" * 80)

    # Promo items
    for code, promo in promo_codes.items():
        value_str = f"{promo['value']}%" if promo['type'] == 'percentage' else f"${promo['value']:.2f}"
        print(f"{code:<17} | {promo['type']:<12} | {value_str:<8} | {promo.get('description', ''):<30}")
    
    print("=" * 80)

# ==============================================
# ORDER DISPLAY FUNCTIONS
# ==============================================

def view_order_details(header, order_id, order, menu_items):
    """Display detailed breakdown of a single order in receipt-style format."""
    # Constants for formatting (matching receipt style)

    # Header
    print(f"\n{'=' * 80}")
    print(f"{f'{header}':^{80}}")
    print(f"{'=' * 80}")
    print(f"Order ID: {order_id}")
    print(f"Type: {order.get('type', 'N/A')}")
    if order.get('display_name'):
        print(f"Customer: {order['display_name']}")
        
    if order['type'] == 'Dine-In':
        print(f"Table Number: {order.get('table_number', 'N/A')}")
    
    # Timestamp handling
    order_timestamp = order.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Date: {order_timestamp}")

    print("-" * 80)
    
    # Items header
    print(f"{'Item':<{45}} {'Qty':^{10}} {'Price':>{10}} {'Total':>{10}}")
    print("-" * 80)
    
    subtotal = 0
    for item_code, qty in order.get("items", []):
        item = menu_items.get(item_code)
        if not item:
            print(f"ERROR: Item '{item_code}' not found in menu. Skipping.")
            continue

        line_total = qty * item['price']
        subtotal += line_total
        print(
            f"{item['name']:<{45}} "
            f"{f'x{qty}':^{10}} "
            f"RM{item['price']:>{9}.2f} "
            f"RM{line_total:>{9}.2f}"
        )
    
    total_discount = 0
    if order.get('discounts'):
        print("-" * 80)
        print(f"{'Discount Apply:'}")
        for discount in order['discounts']:
            amount = discount.get('amount', 0)
            total_discount += amount
            print(
                f"- {discount.get('description', 'Discount'):<{66}}"
                f"-RM{amount:>9.2f}"
            )

    if order.get("remarks"):
        print(f"\nRemarks: {order['remarks']}")

    # Totals section
    print("=" * 80)
    print(f"{'Subtotal:':<{68}} RM{subtotal:>{9}.2f}")
    
    if total_discount > 0:
        print(f"{'Discounts:':<{67}} -RM{total_discount:>{9}.2f}")
        print("-" * 80)
    
    taxable_amount = subtotal - total_discount
    if taxable_amount < 0:
        taxable_amount = 0.00

    tax = taxable_amount * 0.06
    print(f"{'Tax (6%):':<68} RM{tax:>{9}.2f}")

    final_total = taxable_amount + tax
    print(f"{'TOTAL:':<68} RM{final_total:>{9}.2f}")
    print("=" * 80)

# ==============================================
# REPORT FUNCTIONS
# ==============================================

def daily_sales_report(transactions, menu_items):
    """Generate a professional daily sales report with perfect alignment."""
    print(f"\n{'=' * 80}")
    print(f"{f'{"DAILY SALES REPORT"}':^{80}}")
    print(f"{'=' * 80}")
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\nDate: {today}")
    
    # Filter transactions for today only
    today_transactions = {
        order_id: trans for order_id, trans in transactions.items() 
        if trans.get('timestamp', '').startswith(today)
    }
    
    if not today_transactions:
        print("\nNo transactions found for today!")
        return
    # Calculate report data
    report_data = _calculate_report_data(today_transactions, menu_items)
    
    # Financial summary
    
    print(f"\n{'-' * 80}")
    print(f"{f' {"Financial Summary"} ':^{80}}")
    print(f"\n{'-' * 80}")

    print(f"{'Total Discounts Given:':<64}RM{report_data['total_discounts']:>14.2f}")
    print(f"{'Total Sales Amount:':<64}RM{report_data['total_sales']:>14.2f}")
    print(f"{'Total Orders:':<64}{report_data['order_count']:>15}")
    
    # Payment and order type breakdown
    
    # Standard count format function
    def format_count(count):
        return f"({count:>8} order{'s' if count != 1 else ' '})"
    
    # Payment breakdown (now matching order type style)
    print("\nBreakdown by Payment Method:")
    for method, data in report_data['payment_types'].items():
        count_text = format_count(data['count'])
        print(f"{f'    - {method.title()}:':<47}{count_text:>15}RM{data['total']:>14.2f}")
    
    # Order type breakdown (original format maintained)
    print("\nBreakdown by Order Type:")
    dine_in_text = format_count(report_data['dine_in']['count'])
    take_away_text = format_count(report_data['take_away']['count'])
    
    print(f"{'    - Dine-In:':<47}{dine_in_text:>15}RM{report_data['dine_in']['total']:>14.2f}")
    print(f"{'    - Take Away:':<47}{take_away_text:>15}RM{report_data['take_away']['total']:>14.2f}")

    
    # Top selling items
    if not report_data["top_items"]:
        return
    
    

    print(f"\n{'-' * 80}")
    print(f"{f' {"Top Selling Items"} ':^{80}}")
    print(f"{'-' * 80}")

    for i, (item_code, qty) in enumerate(report_data['top_items'], 1):
        item_name = menu_items.get(item_code, {}).get('name', f'Unknown Item ({item_code})')
        print(f"{f'{i}. {item_name}':<65}{f'{qty} units':>15}")

    # Transaction details
    print(f"\n{'=' * 80}")
    print(f"{f'{"Transaction Details"}':^{80}}")
    print(f"{'=' * 80}")
    
    # Get column configs['transaction']
    
    # Header (using fixed widths from config)
    header = (
        f"{'#':<8} "
        f"{'Order ID':<16} "
        f"{'Payment':<20} "
        f"{'Type':<17} "
        f"{'Amount':>15}"
    )
    print(header)
    print("-" * 80)
    
    transactions_list = list(today_transactions.items())  # Convert to list for indexing
    # Data rows (using same fixed widths)
    for i, (order_id, trans) in enumerate(transactions_list, 1):
        row = (
            f"[{i}]:".ljust(8) + " " +
            order_id.ljust(16) + " " +  # Use the dictionary key as order_id
            trans['payment_method'].title().ljust(20) + " " +
            trans['type'].replace('-', ' ').title().ljust(17) + " " +
            f"${trans['total']:>14.2f}"
        )
        print(row)
    
    # Interactive section
    print("-" * 80)
    while True:
        choice = input("\nEnter Order Number to view details or 'done' to exit: ")
        if choice.lower() == 'done':
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(transactions_list):
                order_id = transactions_list[idx][0]
                receipt_file = f"receipts/receipt_{order_id}.txt"
                try:
                    with open(receipt_file, "r") as f:
                        print(f.read())
                        
                except FileNotFoundError:
                    print(f"\nReceipt for order {order_id} not found!")
            else:
                print("Invalid order number!")
        except ValueError:
            print("Please enter a valid number or 'done'")

    

# ==============================================
# HELPER FUNCTIONS
# =============================================
 
def _calculate_report_data(transactions, d):
    """Calculate all data needed for the sales report."""
    # Payment breakdown
    payment_types = {
        'cash': {'total': 0, 'count': 0},
        'card': {'total': 0, 'count': 0},
        'touch n go': {'total': 0, 'count': 0}
    }
    
    # Initialize other metrics
    total_sales = 0
    total_discounts = 0
    item_sales = {}
    dine_in_count = 0
    dine_in_total = 0
    take_away_count = 0
    take_away_total = 0

    for order_id, transaction in transactions.items():
        # Update totals
        total_sales += transaction['total']
        total_discounts += (transaction.get('subtotal', transaction['total']) - transaction['total'])
        
        # Update payment types
        payment_method = transaction.get('payment_method')
        if payment_method in payment_types:
            payment_types[payment_method]['total'] += transaction['total']
            payment_types[payment_method]['count'] += 1
        
        # Update item sales
        for item in transaction.get('items', []):
            item_code = item[0]
            qty = item[1]
            item_sales[item_code] = item_sales.get(item_code, 0) + qty
        
        # Update order type counts
        if transaction.get('type') == 'Dine-In':
            dine_in_count += 1
            dine_in_total += transaction['total']
        elif transaction.get('type') == 'Take Away':
            take_away_count += 1
            take_away_total += transaction['total']
    
    return {
        'total_sales': total_sales,
        'total_discounts': total_discounts,
        'order_count': len(transactions),
        'payment_types': payment_types,
        'dine_in': {
            'count': dine_in_count,
            'total': dine_in_total
        },
        'take_away': {
            'count': take_away_count,
            'total': take_away_total
        },
        'top_items': sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    }
 