import json
import os
from datetime import datetime

def load_file(file):
    try:
        with open(os.path.join("data", file), "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Error: {file} not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error in {file}: {e}.")
        return {}

def save_to_file(data, file):
    try:
        with open(os.path.join("data", file), "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving file: {e}")

def load_order_counters():
    try:
        with open("data/order_counters.txt", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"dine_in": 1, "take_away": 1}

def save_order_counters(counters):
    os.makedirs("data", exist_ok=True)
    with open("data/order_counters.txt", "w") as f:
        json.dump(counters, f, indent=4)
        
def calculate_custom_price(item_code, item_description, menu_items, order=None):
    if item_code not in menu_items:
        return 0
    
    # For combo items
    if 'contents' in menu_items[item_code]:  
        if order and 'cart_contents' in order:
            for item in order['cart_contents']:
                if isinstance(item, dict) and item.get('id') == item_code:
                    addons_total = 0
                    for content_code, content_data in item.get('contents', {}).items():
                        if isinstance(content_data, list):
                            for custom_item in content_data:
                                if custom_item and isinstance(custom_item, dict) and custom_item.get('customizations'):
                                    base_price = menu_items.get(content_code, {}).get('price', 0)
                                    custom_price = custom_item['customizations'].get('price', base_price)
                                    quantity = custom_item.get('quantity', 1)
                                    addons_total += (custom_price - base_price) * quantity
                    return menu_items[item_code]['price'] + addons_total
        return menu_items[item_code]['price']
    
    # For regular items with add-ons
    if "+" in item_description:
        total_price = menu_items[item_code]['price']
        customizations = [c.strip() for c in item_description.split("+")[1:]]
        
        if 'ingredients' in menu_items[item_code]:
            for ingredient in customizations:
                if ingredient in menu_items[item_code]['ingredients']:
                    total_price += menu_items[item_code]['ingredients'][ingredient]['price']
        return total_price
    
    return menu_items[item_code]['price']
    

def calculate_order_total(order_id, current_orders, menu_items):
    order = current_orders[order_id]
    subtotal = 0
    item_totals = {}

    for item in order["items"]:
        item_code = item[0]
        qty = item[1]
        
        # Get base price or customized price
        if "item_details" in order and item_code in order["item_details"]:
            price = calculate_custom_price(item_code, order["item_details"][item_code], menu_items)
        else:
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
                discount_amount = calculate_discount_amount(
                    discount, 
                    item_totals[item_code],
                    [d for d in discount_details if d.get('item_code') == item_code]
                )
                if discount_amount > 0:
                    total -= discount_amount
                    discount_details.append({
                        **discount,
                        'amount': discount_amount
                    })
        else:
            discount_amount = calculate_discount_amount(
                discount,
                subtotal - sum(d['amount'] for d in discount_details)
            )
            if discount_amount > 0:
                total -= discount_amount
                discount_details.append({
                    **discount,
                    'amount': discount_amount
                })

    return {
        'subtotal': subtotal,
        'total': total,
        'discount_details': discount_details,
        'item_totals': item_totals
    }

def calculate_discount_amount(discount, applicable_amount, existing_discounts=[]):
    remaining_value = applicable_amount - sum(d.get('amount', 0) for d in existing_discounts)
    
    if discount["type"] == "percentage":
        return min(applicable_amount * discount["value"] / 100, remaining_value)
    else:
        return min(discount["value"], remaining_value)

def generate_receipt_lines(order_id, order, payment_method, menu_items):
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append(f"{'RECEIPT':^{80}}")
    lines.append("=" * 80)
    lines.append(f"Order ID: {order_id}")
    lines.append(f"Type: {order.get('type', 'N/A')}")
    if order.get('display_name'):
        lines.append(f"Customer: {order['display_name']}")
    if order['type'] == 'Dine-In':
        lines.append(f"Table Number: {order.get('table_number', 'N/A')}")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Payment Method: {payment_method}")
    lines.append("-" * 80)
    
    # Items header
    lines.append(f"{'Item':<45} {'Qty':^10} {'Price':>10} {'Total':>10}")
    lines.append("-" * 80)
    
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

            customized_desc = next(
                (c['custom_description'] for c in order["cart_contents"] 
                if c['id'] == item_code and 'custom_description' in c),
                None
            )
            if customized_desc:
                price = calculate_custom_price(item_code, customized_desc, menu_items, order)
            else:
                price = item_data.get('price', 0)
        else:
            price = item_data.get('price', 0)
        
        line_total = qty * price
        subtotal += line_total
        
        lines.append(f"{item_name:<45} {f'x{qty}':^10} RM{price:>9.2f} RM{line_total:>9.2f}")
        if remark:
            lines.append(f"  Remark: {remark}")
        
        if (item_code in menu_items and 'contents' in menu_items[item_code] and 
            "cart_contents" in order and any(c['id'] == item_code for c in order["cart_contents"])):
            lines.append(f"  {'Combo Contents:':<43}")
            for content in order["cart_contents"]:
                if content['id'] == item_code and 'contents' in content:
                    for content_code, content_data in content['contents'].items():
                        if isinstance(content_data, list):
                            for custom_item in content_data:
                                if custom_item and isinstance(custom_item, dict) and custom_item.get('customizations'):
                                    custom_name = custom_item['customizations'].get('name', 
                                        menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})'))
                                    lines.append(f"    - {custom_name} x{custom_item.get('quantity', 1)}")
                                elif custom_item:
                                    content_name = menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})')
                                    lines.append(f"    - {content_name} x{custom_item.get('quantity', 1)}")
                        elif content_data and isinstance(content_data, dict) and content_data.get('customizations'):
                            custom_name = content_data['customizations'].get('name', 
                                menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})'))
                            lines.append(f"    - {custom_name} x{content_data.get('quantity', 1)}")
                        elif content_data:
                            content_name = menu_items.get(content_code, {}).get('name', f'Unknown ({content_code})')
                            lines.append(f"    - {content_name} x{content_data.get('quantity', 1)}")
    
    # Discounts
    total_discount = 0
    if order.get('discounts'):
        lines.append("-" * 80)
        lines.append(f"{'Discounts Applied:':<80}")
        for discount in order['discounts']:
            amount = discount.get('amount', 0)
            total_discount += amount
            lines.append(f"- {discount.get('description', 'Discount'):<66}-RM{amount:>9.2f}")
    
    # Order remarks
    if order.get("remarks"):
        lines.append(f"\nOrder Remarks: {order['remarks']}")
    
    # Totals
    lines.append("=" * 80)
    lines.append(f"{'Subtotal:':<68} RM{subtotal:>9.2f}")
    if total_discount > 0:
        lines.append(f"{'Discounts:':<67} -RM{total_discount:>9.2f}")
        lines.append("-" * 80)
    
    taxable_amount = max(0, subtotal - total_discount)
    tax = taxable_amount * 0.06
    lines.append(f"{'Tax (6%):':<68} RM{tax:>9.2f}")
    lines.append(f"{'TOTAL:':<68} RM{(taxable_amount + tax):>9.2f}")
    lines.append("=" * 80)
    
    return lines

def generate_receipt(order_id, order, payment_method, menu_items):
    try:
        os.makedirs("receipts", exist_ok=True)
        receipt_lines = generate_receipt_lines(order_id, order, payment_method, menu_items)
        receipt_text = "\n".join(receipt_lines)
        
        print(f"\n{receipt_text}")
        
        filename = f"receipt_{order_id}.txt"
        filepath = os.path.join("receipts", filename)
        with open(filepath, "w") as f:
            f.write(receipt_text)
            
        print(f"Receipt saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error generating receipt: {e}")
        return None