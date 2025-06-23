# This file is mainly designed for managing restaurant orders, including creating new orders,
# adding items, applying and removing discounts or promo codes, processing checkouts, and
# handling active orders. It provides functions for order item management, discount logic,
# order status updates, and transaction processing in a point-of-sale system.

from utils.helpers import calculate_order_total, generate_receipt, load_file, save_to_file
from utils.display import view_order_details, show_promo_codes
from datetime import datetime


def apply_discount_to_entire_order(order_id, current_orders, menu_items, discount_type):
    # Calculate order total and existing discounts
    calc = calculate_order_total(order_id, current_orders, menu_items)
    order_total = calc['total']
    existing_discounts = current_orders[order_id].get("discounts", [])
    remaining_value = order_total - sum(d.get('amount', 0) for d in existing_discounts)
    if discount_type == '1':  # Percentage discount
        try:
            percentage = float(input("Enter discount percentage for entire order (0-100): "))
            if percentage <= 0 or percentage > 100:
                print("Percentage must be between 0-100.")
                return
    
            discount_amount = round(min(order_total * percentage / 100, remaining_value), 2)
            if discount_amount <= 0:
                print(f"Cannot apply discount - order already fully discounted (remaining value: RM{remaining_value:.2f})")
                return

            current_orders[order_id].setdefault("discounts", []).append({
                "type": "percentage",
                "value": percentage,
                "description": f"{percentage}% off entire order",
                "apply_to": "total",
                "amount": discount_amount
            })
            save_to_file(current_orders, "current_active_orders.txt")  # Save after applying discount
            print(f"Applied {percentage}% discount to entire order (-RM{discount_amount:.2f})")

        except ValueError:
            print("Please enter a valid number.")

    else:  # Fixed amount discount
        try:
            amount = float(input(f"Enter fixed discount amount for entire order (max RM{remaining_value:.2f}): "))
            if amount <= 0:
                print("Amount must be positive.")
                return
            if amount > remaining_value:
                print(f"Discount cannot exceed remaining order value (RM{remaining_value:.2f})")
                return

            current_orders[order_id].setdefault("discounts", []).append({
                "type": "fixed",
                "value": amount,
                "description": f"RM{amount:.2f} off entire order",
                "apply_to": "total",
                "amount": amount
            })
            save_to_file(current_orders, "current_active_orders.txt")  # Save after applying discount
            print(f"Applied RM{amount:.2f} discount to entire order")

        except ValueError:
            print("Please enter a valid number.")

    calculate_order_total(order_id, current_orders, menu_items)
    view_order_details("Order Details", order_id, current_orders[order_id], menu_items)

def apply_discount_to_specific_item(order_id, current_orders, menu_items, discount_type):
    """Apply discount to a specific menu item"""
    print("=" * 80)
    print(f"{'Current Order Items':^{80}}")
    print("=" * 80)
    for idx, (item_code, qty) in enumerate(current_orders[order_id]["items"], 1):
        item = menu_items[item_code]
        print(f"[{idx}]. {item['name']:<65} Qty: {qty:>3}")
    print("-" * 80)
    print("=" * 80)

    try:
        item_idx = int(input("Enter item number to discount: ")) - 1
        if 0 <= item_idx < len(current_orders[order_id]["items"]):
            item_code = current_orders[order_id]["items"][item_idx][0]
            item_name = menu_items[item_code]['name']
            item_price = menu_items[item_code]['price']
            item_qty = current_orders[order_id]["items"][item_idx][1]
            item_total = item_price * item_qty

            existing_discounts = [
                d for d in current_orders[order_id].get("discounts", [])
                if d.get('item_code') == item_code
            ]
            remaining_value = max(0, item_total - sum(d.get('amount', 0) for d in existing_discounts))

            if discount_type == '1':  # Percentage
                percentage = float(input(f"Enter discount percentage for {item_name} (0-100): "))
                if percentage <= 0 or percentage > 100:
                    print("Percentage must be between 0-100.")
                    return

                discount_amount = round(min(item_total * percentage / 100, remaining_value), 2)
                if discount_amount <= 0:
                    print(
                        f"Cannot apply discount - item already fully discounted (remaining value: RM{remaining_value:.2f})")
                    return

                current_orders[order_id].setdefault("discounts", []).append({
                    "type": "percentage",
                    "value": percentage,
                    "description": f"{percentage}% off on {item_name}",
                    "apply_to": "specific_item",
                    "item_code": item_code,
                    "amount": discount_amount
                })
                save_to_file(current_orders, "current_active_orders.txt")  # Save after applying discount
                print(f"Applied {percentage}% discount to {item_name} (-RM{discount_amount:.2f})")

            else:  # Fixed amount
                amount = float(input(
                    f"Enter fixed discount amount for {item_name} (max RM{remaining_value:.2f}): "))
                if amount <= 0:
                    print("Amount must be positive.")
                    return

                if amount > remaining_value:
                    print(
                        f"Discount cannot exceed remaining item value (RM{remaining_value:.2f})")
                    return

                current_orders[order_id].setdefault("discounts", []).append({
                    "type": "fixed",
                    "value": amount,
                    "description": f"RM{amount:.2f} off on {item_name}",
                    "apply_to": "specific_item",
                    "item_code": item_code,
                    "amount": amount
                })
                save_to_file(current_orders, "current_active_orders.txt")  
                print(f"Applied RM{amount:.2f} discount to {item_name}")

            calculate_order_total(order_id, current_orders, menu_items)
            view_order_details("Order Details", order_id, current_orders[order_id], menu_items)
        else:
            print("Invalid item number!")
    except ValueError:
        print("Please enter valid numbers.")

def apply_promo_code(order_id, current_orders, menu_items, promo_codes):
    """Apply a promo code to the order"""
    show_promo_codes(promo_codes)
    promo_code = input("\nEnter promo code: ").strip().upper()
    if promo_code in promo_codes:
        promo = promo_codes[promo_code]

        # Check if promo already applied
        if any(d.get('promo_code') == promo_code for d in
               current_orders[order_id].get("discounts", [])):
            print("This promo code has already been applied.")
            return

        elif promo['apply_to'] == 'specific_item':
            item_code = promo.get('item_code')
            if not item_code or not any(item[0] == item_code for item in current_orders[order_id]["items"]):
                print(f"No valid item in order for this promo.")
                return
            item_total = sum(
                qty * menu_items[item_code]['price']
                for code, qty in current_orders[order_id]["items"]
                if code == item_code
            )
            existing_discounts = sum(
                d['amount'] for d in current_orders[order_id].get("discounts", [])
                if d.get('item_code') == item_code
            )
            remaining_value = item_total - existing_discounts

        elif promo['apply_to'] == 'total':
            calc = calculate_order_total(order_id, current_orders, menu_items)
            applicable_total = calc['total']
            existing_discounts = sum(d['amount'] for d in calc['discount_details'])
            remaining_value = applicable_total - existing_discounts

        else:
            print("Invalid promo code application type.")
            return

        # Calculate the discount amount
        if promo['type'] == 'percentage':
            discount_amount = min(remaining_value * promo['value'] / 100, remaining_value)
        else:
            discount_amount = min(promo['value'], remaining_value)

        if discount_amount <= 0:
            print("No value left to discount for this promo.")
            return

        # Apply promo
        discount_entry = {
            "type": promo['type'],
            "value": promo['value'],
            "amount": discount_amount,
            "description": promo['description'],
            "apply_to": promo['apply_to'],
            "promo_code": promo_code
        }
        if promo['apply_to'] == 'specific_item':
            discount_entry['item_code'] = promo['item_code']

        current_orders[order_id].setdefault("discounts", []).append(discount_entry)
        save_to_file(current_orders, "current_active_orders.txt")
        print(f"Applied promo: {promo['description']} (-RM{discount_amount:.2f})")

        calculate_order_total(order_id, current_orders, menu_items)
        view_order_details("Order Details", order_id, current_orders[order_id], menu_items)
    else:
        print("Invalid promo code.")
        
def apply_new_discount(order_id, current_orders, menu_items, promo_codes):
    """Apply a new discount to the order"""
    print("\nSelect Discount Type:")
    print("1. Percentage Discount")
    print("2. Fixed Amount Discount")
    print("3. Promo Code")
    discount_choice = input("Enter choice (1-3): ").strip()

    if discount_choice in ['1', '2']:
        print("\nApply discount to:")
        print("1. Specific food item")
        print("2. Entire order")
        apply_to = input("Enter choice (1-2): ").strip()

        if apply_to == '1':  # Specific item
            apply_discount_to_specific_item(order_id, current_orders, menu_items, discount_choice)
        elif apply_to == '2':
            apply_discount_to_entire_order(order_id, current_orders, menu_items, discount_choice)
        else:
            print("Invalid choice.")

    elif discount_choice == '3':  # Promo Code
        apply_promo_code(order_id, current_orders, menu_items, promo_codes)
    else:
        print("Invalid choice.")

def remove_existing_discounts(order_id, current_orders, menu_items):
    """Remove an existing discount from the order"""
    if not current_orders[order_id].get("discounts"):
        print("No discounts applied to this order.")
        return

    print("=" * 80)
    print(f"{'Applied Discounts':^{80}}")
    print("=" * 80)
    for idx, discount in enumerate(current_orders[order_id]["discounts"], 1):
        desc = discount['description']
        if discount.get('apply_to') == 'specific_item':
            item_name = menu_items[discount['item_code']]['name']
            desc = f"{discount['description']} on {item_name}"
        print(f"[{idx}]. {desc}")
    print("-" * 80)
    print("=" * 80)
    try:
        remove_idx = int(input("Enter discount number to remove (or 0 to cancel): ")) - 1
        if remove_idx == -1:
            return
        if 0 <= remove_idx < len(current_orders[order_id]["discounts"]):
            removed = current_orders[order_id]["discounts"].pop(remove_idx)
            save_to_file(current_orders, "current_orders.txt")  # Save after applying discount
            print(f"Removed discount: {removed['description']}")
            
            calculate_order_total(order_id, current_orders, menu_items)
            view_order_details("Order Details", order_id, current_orders[order_id], menu_items)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

def manage_discounts(order_id, current_orders, menu_items, promo_codes):
    """Handle all discount operations for an order"""
    if order_id not in current_orders:
        print("No active order found!")
        return
    
    while True:
        print("\n=== Discount Management ===")
        print("1. Apply Discount")
        print("2. Remove Discount")
        print("3. Back")
        
        disc_choice = input("Select an option: ").strip()

        # Apply Discount
        if disc_choice == '1':
            apply_new_discount(order_id, current_orders, menu_items, promo_codes)
        
        # Remove Discount
        elif disc_choice == '2':
            remove_existing_discounts(order_id, current_orders, menu_items)
            
        # Back to Order Actions
        elif disc_choice == '3':
            break
        
        else:
            print("Invalid choice. Please try again.")


def process_checkout(order_id, order, current_orders, menu_items, transactions):
    calc = calculate_order_total(order_id, current_orders, menu_items)

    view_order_details("Order Details", order_id, order, menu_items)
    while True:
        print("\nEnter Payment Method:")
        print("1. Cash")
        print("2. Card")
        print("3. Touch 'N Go")
        print("4. Cancel")

        payment_method = input("Enter Choice:").strip()

        if payment_method == "1":
           payment_method =  'Cash'
           break
        if payment_method == "2":
           payment_method =  'Card'
           break
        if payment_method == "3":
           payment_method =  "Touch 'N Go"
           break
        if payment_method == "4":
           print("Transaction cancelled.")
           return
        else:
            print("Invalid payment method.")

    transactions[order_id] = {
        "type": order["type"],
        "items": order["items"],
        "discounts": calc['discount_details'],
        "total": calc['total'],
        "payment_method": payment_method,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(f"\nTransaction successful! Order {order_id} processed with {payment_method} payment.")
    save_to_file(transactions, "transactions.txt")

    generate_receipt(order_id, order, payment_method, menu_items)
    del current_orders[order_id]
    save_to_file(current_orders, "current_active_orders.txt")

    print("\nOrder completed successfully! Refreshing active orders...\n")
    return

def handle_order_actions(order_id, order, current_orders, menu_items, transactions):
    while True:
        promo_codes = load_file('promo_codes.txt')

        print("\nSelect An Option:")
        print("1. Manage Discount")
        print("2. Cancel Order")
        print("3. Checkout")
        print("4. Back ")
        
        action = input("\nEnter Choice: ")
    
        if action == "1":
            manage_discounts(order_id, current_orders, menu_items, promo_codes)
            
        elif action == "2":
            confirm = input(f"Confirm cancel order {order_id}? (y/n): ").lower()
            if confirm == 'y':
                del current_orders[order_id]
                save_to_file(current_orders, "current_active_orders.txt")

                print(f"Order {order_id} cancelled.")
                return
        elif action == "3":
            process_checkout(order_id, order, current_orders, menu_items, transactions)
            return
            
        elif action == "4":
            return
        else:
            print("Invalid choice!")

def view_active_orders(current_orders, menu_items, transactions):
    while True:

        if not current_orders:
            print("\nNo active orders.")
            return

        print("\n" + "="*80)
        print("Active Orders".center(80))
        print("="*80)

        orders_list = list(current_orders.items())
        for idx, (oid, order) in enumerate(orders_list, 1):
            status = order.get('status', 'Preparing')
            line = f"[{idx}]: {oid:12}"
            status_str = f"Status: {status}"
            print(f"{line}{status_str:>{80 - len(line)}}")
            print("-" * 80)
        print("="*80)

        choice = input("\nSelect Order Number to View Details or 'done' to Return: ").strip().lower()
        
        if choice == "done":
            break
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(orders_list):
                oid, order = orders_list[idx]

                view_order_details("Order Details", oid, order, menu_items)
                handle_order_actions(oid, order, current_orders, menu_items, transactions)
            else:
                print("Invalid order number!")
        except ValueError:
            print("Please enter a valid number!")



