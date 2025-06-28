from datetime import datetime
from utils.helpers import calculate_custom_price

def show_menu(menu_items):
    print(f"\n{'=' * 80}")
    print(f"{'MENU':^{80}}")
    print(f"{'=' * 80}")
    print(f"{'Code':<6} | {'Name':<30} | {'Price':<9} | {'Category':<11} | {'Availability':>9}")
    print("-" * 80)
    for code, item in menu_items.items():
        print(f"{code:<6} | {item['name']:<30} | RM{item['price']:>7.2f} | {item['category']:<11} | {item['availability']:>9}")
    print("=" * 80)

def show_promo_codes(promo_codes):
    print(f"\n{'=' * 80}")
    print(f"{'PROMO CODES':^{80}}")
    print(f"{'=' * 80}")
    print(f"{'Code':<17} | {'Type':<12} | {'Value':<8} | {'Description':<30}")
    print("-" * 80)
    for code, promo in promo_codes.items():
        value_str = f"{promo['value']}%" if promo['type'] == 'percentage' else f"RM{promo['value']:.2f}"
        print(f"{code:<17} | {promo['type']:<12} | {value_str:<8} | {promo.get('description', ''):<30}")
    print("=" * 80)

def view_order_details(header, order_id, order, menu_items):
    print(f"\n{'=' * 80}")
    print(f"{header:^{80}}")
    print(f"{'=' * 80}")
    print(f"Order ID: {order_id}")
    print(f"Type: {order.get('type', 'N/A')}")
    if order.get('display_name'):
        print(f"Customer: {order['display_name']}")
    if order['type'] == 'Dine-In':
        print(f"Table Number: {order.get('table_number', 'N/A')}")
    print(f"Date: {order.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    print(f"Status: {order.get('status', 'Preparing')}")
    print("-" * 80)
    
    # Items header
    print(f"{'Item':<45} {'Qty':^10} {'Price':>10} {'Total':>10}")
    print("-" * 80)
    
    subtotal = 0
    for item in order.get("items", []):
        item_code = item[0]
        qty = item[1]
        remark = item[2] if len(item) > 2 else ""
        
        item_data = menu_items.get(item_code, {})
        item_name = item_data.get('name', f'Unknown Item ({item_code})')
        
        # Handle customized items
        if "item_details" in order and item_code in order["item_details"]:
            item_name = order["item_details"][item_code]
            price = calculate_custom_price(item_code, order["item_details"][item_code], menu_items, order)
        elif "cart_contents" in order and any(c['id'] == item_code for c in order["cart_contents"]):
            # For combo items, use the price from item_details if available
            customized_desc = next(
                (c['custom_description'] for c in order["cart_contents"] 
                if c['id'] == item_code and 'custom_description' in c),
                None
            )
            if customized_desc:
                price = calculate_custom_price(item_code, customized_desc, menu_items)
            else:
                price = item_data.get('price', 0)
        else:
            price = item_data.get('price', 0)
        
        line_total = qty * price
        subtotal += line_total
        
        print(f"{item_name:<45} {f'x{qty}':^10} RM{price:>9.2f} RM{line_total:>9.2f}")
        if remark:
            print(f"  Remark: {remark}")
        
        if (item_code in menu_items and 'contents' in menu_items[item_code] and "cart_contents" in order and any(c['id'] == item_code for c in order["cart_contents"])):
            print(f"  {'Combo Contents:':<43}")
            for content in order["cart_contents"]:
                if content['id'] == item_code and 'contents' in content:
                    for content_code, content_data in content['contents'].items():
                        if isinstance(content_data, list):
                            for custom_item in content_data:
                                if custom_item.get('customizations'):
                                    custom_name = custom_item['customizations'].get('name', 
                                        menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})'))
                                    print(f"    - {custom_name} x{custom_item.get('quantity', 1)}")
                                else:
                                    content_name = menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})')
                                    print(f"    - {content_name} x{content_data[0].get('quantity', 1)}")
                        elif content_data.get('customizations'):
                            custom_name = content_data['customizations'].get('name', 
                                menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})'))
                            print(f"    - {custom_name} x{content_data.get('quantity', 1)}")
                        else:
                            content_name = menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})')
                            print(f"    - {content_name} x{content_data.get('quantity', 1)}")
    # Discounts
    total_discount = 0
    if order.get('discounts'):
        print("-" * 80)
        print(f"{'Discounts Applied:':<80}")
        for discount in order['discounts']:
            amount = discount.get('amount', 0)
            total_discount += amount
            print(f"- {discount.get('description', 'Discount'):<66}-RM{amount:>9.2f}")
    
    # Order remarks
    if order.get("remarks"):
        print(f"\nOrder Remarks: {order['remarks']}")
    
    # Totals
    print("=" * 80)
    print(f"{'Subtotal:':<68} RM{subtotal:>9.2f}")
    if total_discount > 0:
        print(f"{'Discounts:':<67} -RM{total_discount:>9.2f}")
        print("-" * 80)
    
    taxable_amount = max(0, subtotal - total_discount)
    tax = taxable_amount * 0.06
    print(f"{'Tax (6%):':<68} RM{tax:>9.2f}")
    print(f"{'TOTAL:':<68} RM{(taxable_amount + tax):>9.2f}")
    print("=" * 80)


def daily_sales_report(transactions, menu_items):
    print(f"\n{'=' * 80}")
    print(f"{'DAILY SALES REPORT':^{80}}")
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
    print(f"{'Financial Summary':^{80}}")
    print(f"{'-' * 80}")

    print(f"{'Total Discounts Given:':<64}RM{report_data['total_discounts']:>14.2f}")
    print(f"{'Total Sales Amount:':<64}RM{report_data['total_sales']:>14.2f}")
    print(f"{'Total Orders:':<64}{report_data['order_count']:>15}")
    
    # Payment and order type breakdown
    
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
    print(f"{"Top Selling Items"} :^{80}")
    print(f"{'-' * 80}")

    for i, (item_code, qty) in enumerate(report_data['top_items'], 1):
        item_name = menu_items.get(item_code, {}).get('name', f'Unknown Item ({item_code})')
        print(f"{f'{i}. {item_name}':<65}{f'{qty} units':>15}")

    # Transaction details
    print(f"\n{'=' * 80}")
    print(f"{'Transaction Details':^{80}}")
    print(f"{'=' * 80}")

    header = (
        f"{'#':<8} "
        f"{'Order ID':<16} "
        f"{'Payment':<20} "
        f"{'Type':<17} "
        f"{'Amount':>15}"
    )
    print(header)
    print("-" * 80)
    
    transactions_list = list(today_transactions.items())  
    for i, (order_id, trans) in enumerate(transactions_list, 1):
        row = (
            f"[{i}]:".ljust(8) + " " +
            order_id.ljust(16) + " " +  
            trans['payment_method'].title().ljust(20) + " " +
            trans['type'].replace('-', ' ').title().ljust(16) + " " +
            f"RM{trans['total']:>14.2f}"
        )
        print(row)
    
    # Interactive section
    print("-" * 80)
    while True:
        choice = input("\nEnter Order Number to view details or 'done' to exit: ").strip()
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

def _calculate_report_data(transactions, d):
    # Payment breakdown
    payment_types = {
        'cash': {'total': 0, 'count': 0},
        'card': {'total': 0, 'count': 0},
        "touch 'n go": {'total': 0, 'count': 0}
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
        total_discounts += sum(d['amount'] for d in transaction.get('discounts', []))
        
        # Normalize payment method for comparison
        payment_method = transaction.get('payment_method', '').lower()
        if "card" in payment_method:
            payment_types['card']['total'] += transaction['total']
            payment_types['card']['count'] += 1
        elif "cash" in payment_method:
            payment_types['cash']['total'] += transaction['total']
            payment_types['cash']['count'] += 1
        elif "touch" in payment_method.lower() or "n go" in payment_method.lower():
            payment_types["touch 'n go"]['total'] += transaction['total']
            payment_types["touch 'n go"]['count'] += 1
        
        # Update item sales
        for item in transaction.get('items', []):
            item_code = item[0]
            qty = item[1]
            item_sales[item_code] = item_sales.get(item_code, 0) + qty
        
        # Normalize order type for comparison
        order_type = transaction.get('type', '').lower()
        if "dine" in order_type:  # Matches "Dine-In" or "Dine In"
            dine_in_count += 1
            dine_in_total += transaction['total']
        else:  # Assume anything else is takeaway
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
 