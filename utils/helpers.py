# helpers.py provides utility functions 
# Helper functions for loading data, processing orders, calculating totals, and generating receipts

import json
import os
from datetime import datetime


def load_file(file):
    try:
        with open(os.path.join("data", file), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file} not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error in {file}: {e}.")
        return {}

def save_to_file (data, file):
    """Save current orders to current_active_orders.txt"""
    try:
        with open(os.path.join("data", file), "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving current orders: {e}")

def get_total_ordered_quantity(item_code, current_orders):
    total = 0
    for order in current_orders.values():
        for code, qty in order["items"]:
            if code == item_code:
                total += qty
    return total

def calculate_order_total(order_id, current_orders, menu_items):
    order = current_orders[order_id]
    subtotal = 0
    item_totals = {}

    for item_code, qty in order["items"]:
        price = menu_items[item_code]['price']
        item_total = price * qty
        item_totals[item_code] = item_total
        subtotal += item_total

    total = subtotal
    discount_details = []

    for discount in order.get("discounts", []):
        if discount["apply_to"] == "specific_item":
            item_code = discount["item_code"]
            if item_code in item_totals:
                item_total = item_totals[item_code]
                remaining_value = item_total - sum(
                    d['amount'] for d in discount_details
                    if d.get('item_code') == item_code
                )

                if discount["type"] == "percentage":
                    discount_amount = min(item_total * discount["value"] / 100, remaining_value)
                else:
                    discount_amount = min(discount["value"], remaining_value)

                if discount_amount > 0:
                    total -= discount_amount
                    discount_details.append({
                        'description': discount['description'],
                        'amount': discount_amount,
                        'item_code': item_code
                    })

        elif discount["apply_to"] in ["food", "beverage"]:
            applicable_total = sum(
                item_totals[code] for code in item_totals
                if menu_items[code]['category'] == discount["apply_to"]
            )

            if discount["type"] == "percentage":
                discount_amount = applicable_total * discount["value"] / 100
            else:
                discount_amount = discount["value"]

            discount_amount = min(discount_amount, total)
            if discount_amount > 0:
                total -= discount_amount
                discount_details.append({
                    'description': discount['description'],
                    'amount': discount_amount
                })

        else:
            if discount["type"] == "percentage":
                discount_amount = subtotal * discount["value"] / 100
            else:
                discount_amount = discount["value"]

            discount_amount = min(discount_amount, total)
            if discount_amount > 0:
                total -= discount_amount
                discount_details.append({
                    'description': discount['description'],
                    'amount': discount_amount
                })

    return {
        'subtotal': subtotal,
        'total': total,
        'discount_details': discount_details,
        'item_totals': item_totals
    }

def generate_receipt_lines(order_id, order, payment_method, menu_items):
    lines = []
    
    # Constants for receipt formatting
    TOTAL_WIDTH = 80
    ITEM_NAME_WIDTH = 45
    QTY_WIDTH = 10
    PRICE_WIDTH = 10
    TOTAL_COL_WIDTH = 10
    
    # Header
    lines.append("=" * TOTAL_WIDTH)
    lines.append(f"{'RECEIPT':^{TOTAL_WIDTH}}")
    lines.append("=" * TOTAL_WIDTH)
    lines.append(f"Order ID: {order_id}")
    lines.append(f"Type: {order.get('type', 'N/A')}")
    if order.get('display_name'):
        lines.append(f"Customer: {order['display_name']}")
        
    if order['type'] == 'Dine-In':
        lines.append(f"Table Number: {order.get('table_number', 'N/A')}")
    
    # Timestamp handling
    order_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Date: {order_timestamp}")
    
    # Payment Method
    if payment_method:
        lines.append(f"Payment Method: {payment_method.title()}")
    
    lines.append("-" * TOTAL_WIDTH)
    
    # Items header
    lines.append(f"{'Item':<{ITEM_NAME_WIDTH}} {'Qty':^{QTY_WIDTH}} {'Price':>{PRICE_WIDTH}} {'Total':>{TOTAL_COL_WIDTH}}")
    lines.append("-" * TOTAL_WIDTH)
    
    subtotal = 0
    for item_code, qty in order.get("items", []):
        item = menu_items.get(item_code)
        if not item:
            lines.append(f"ERROR: Item '{item_code}' not found in menu. Skipping.")
            continue

        line_total = qty * item['price']
        subtotal += line_total
        lines.append(
            f"{item['name']:<{ITEM_NAME_WIDTH}} "
            f"{f'x{qty}':^{QTY_WIDTH}} "
            f"RM{item['price']:>{PRICE_WIDTH-1}.2f} "
            f"RM{line_total:>{TOTAL_COL_WIDTH-1}.2f}"
        )
    
    total_discount = 0
    if order.get('discounts'):
        lines.append("-" * TOTAL_WIDTH)
        lines.append(f"{'Discount Apply:'}")
        for discount in order['discounts']:
            amount = discount.get('amount', 0)
            total_discount += amount
            lines.append(
                f"- {discount.get('description', 'Discount'):<{TOTAL_WIDTH-14}}"
                f"-RM{amount:>9.2f}"
            )
    if order.get("remarks"):
        lines.append(f"\nRemarks: {order['remarks']}")
    # Totals section
    lines.append("=" * TOTAL_WIDTH)
    lines.append(f"{'Subtotal:':<{TOTAL_WIDTH-12}} RM{subtotal:>{TOTAL_COL_WIDTH-1}.2f}")
    
    if total_discount > 0:
        lines.append(f"{'Discounts:':<{TOTAL_WIDTH-13}} -RM{total_discount:>{TOTAL_COL_WIDTH-1}.2f}")
        lines.append("-" * TOTAL_WIDTH)
    
    # Tax calculation
    taxable_amount = subtotal - total_discount
    if taxable_amount < 0:
       taxable_amount = 0.00
    tax = taxable_amount * 0.06  # 6% tax
    lines.append(f"{'Tax (6%):':<{TOTAL_WIDTH-12}} RM{tax:>{TOTAL_COL_WIDTH-1}.2f}")

    final_total = taxable_amount + tax

    lines.append(f"{'TOTAL:':<{TOTAL_WIDTH-12}} RM{final_total:>{TOTAL_COL_WIDTH-1}.2f}")
    lines.append("=" * TOTAL_WIDTH)
    
    return lines

def generate_receipt(order_id, order, payment_method, menu_items):
    """Generate and save a formatted receipt"""
    try:
        # Ensure receipts directory exists
        os.makedirs("receipts", exist_ok=True)
        
        # Generate receipt content
        receipt_lines = generate_receipt_lines(order_id, order, payment_method, menu_items)
        receipt_text = "\n".join(receipt_lines)
        
        # Print to console
        print(f"\n{receipt_text}")
        
        # Save to file
        filename = f"receipt_{order_id}.txt"
        filepath = os.path.join("receipts", filename)
        
        with open(filepath, "w") as f:
            f.write(receipt_text)
            
        print(f"Receipt saved to {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error generating receipt: {e}")
        return None