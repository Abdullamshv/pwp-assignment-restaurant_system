# This file is mainly designed for managing restaurant orders, including creating new orders,
# adding items, applying and removing discounts or promo codes, processing checkouts, and
# handling active orders. It provides functions for order item management, discount logic,
# order status updates, and transaction processing in a point-of-sale system.

from utils.helpers import calculate_order_total, calculate_custom_price, generate_receipt, load_file, save_to_file
from utils.display import view_order_details, show_promo_codes
from datetime import datetime

def apply_discount_to_entire_order(order_id, current_orders, menu_items, discount_type):
    """Apply discount to the entire order with proper sequential calculation"""
    # Calculate order total using comprehensive logic
    subtotal = 0
    for item in current_orders[order_id].get("items", []):
        item_code = item[0]
        qty = item[1]
        
        if "item_details" in current_orders[order_id] and item_code in current_orders[order_id]["item_details"]:
            price = calculate_custom_price(
                item_code, 
                current_orders[order_id]["item_details"][item_code], 
                menu_items,
                current_orders[order_id]
            )
        elif "cart_contents" in current_orders[order_id] and any(
            c['id'] == item_code for c in current_orders[order_id]["cart_contents"]
        ):
            customized_desc = next(
                (c['custom_description'] for c in current_orders[order_id]["cart_contents"] 
                if c['id'] == item_code and 'custom_description' in c),
                None
            )
            if customized_desc:
                price = calculate_custom_price(item_code, customized_desc, menu_items, current_orders[order_id])
            else:
                price = menu_items.get(item_code, {}).get('price', 0)
        else:
            price = menu_items.get(item_code, {}).get('price', 0)
        
        subtotal += price * qty
    
    # Calculate remaining value after existing discounts
    existing_discounts = [d for d in current_orders[order_id].get("discounts", []) 
                        if d.get('apply_to') == 'total']
    item_discounts = [d for d in current_orders[order_id].get("discounts", [])
                     if d.get('apply_to') == 'specific_item']
    
    # Calculate total discounts already applied to items
    total_item_discounts = sum(d.get('amount', 0) for d in item_discounts)
    
    # Calculate remaining value that can be discounted
    remaining_value = max(0, subtotal - total_item_discounts - sum(d.get('amount', 0) for d in existing_discounts))
    
    if discount_type == '1':  # Percentage discount
        try:
            percentage = float(input("Enter discount percentage for entire order (0-100): ").strip())
            if percentage <= 0 or percentage > 100:
                print("Percentage must be between 0-100.")
                return
    
            discount_amount = round(remaining_value * percentage / 100, 2)
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
            save_to_file(current_orders, "current_active_orders.txt")
            print(f"Applied {percentage}% discount to entire order (-RM{discount_amount:.2f})")

        except ValueError:
            print("Please enter a valid number.")

    else:  # Fixed amount discount
        try:
            amount = float(input(f"Enter fixed discount amount for entire order (max RM{remaining_value:.2f}): ").strip())
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
            save_to_file(current_orders, "current_active_orders.txt")
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
    
    items_with_prices = []
    for idx, item in enumerate(current_orders[order_id]["items"], 1):
        item_code = item[0]
        qty = item[1]
        
        # Get display name
        item_name = menu_items[item_code]['name']
        if "item_details" in current_orders[order_id] and item_code in current_orders[order_id]["item_details"]:
            item_name = current_orders[order_id]["item_details"][item_code]
        
        # Calculate price using same logic as view_order_details
        if "item_details" in current_orders[order_id] and item_code in current_orders[order_id]["item_details"]:
            price = calculate_custom_price(
                item_code, 
                current_orders[order_id]["item_details"][item_code], 
                menu_items,
                current_orders[order_id]
            )
        elif "cart_contents" in current_orders[order_id] and any(
            c['id'] == item_code for c in current_orders[order_id]["cart_contents"]
        ):
            customized_desc = next(
                (c['custom_description'] for c in current_orders[order_id]["cart_contents"] 
                if c['id'] == item_code and 'custom_description' in c),
                None
            )
            if customized_desc:
                price = calculate_custom_price(item_code, customized_desc, menu_items, current_orders[order_id])
            else:
                price = menu_items[item_code]['price']
        else:
            price = menu_items[item_code]['price']
        
        total = price * qty
        items_with_prices.append((idx, item_code, item_name, qty, price, total))
        
        print(f"[{idx}] {item_name:<60} {f'x{qty}':>5} RM{total:>7.2f}")
    
    print("-" * 80)
    print("=" * 80)

    try:
        user_input = input("Enter item number to discount: ").strip()
        
        if not user_input:
            print("No input provided.")
            return
            
        item_idx = int(user_input) - 1
        
        if 0 <= item_idx < len(items_with_prices):
            _, item_code, item_name, item_qty, item_price, item_total = items_with_prices[item_idx]
            
            # Calculate existing discounts for this specific item
            existing_discounts = [
                d for d in current_orders[order_id].get("discounts", [])
                if d.get('item_code') == item_code
            ]
            total_discount_applied = sum(d.get('amount', 0) for d in existing_discounts)
            remaining_value = max(0, item_total - total_discount_applied)

            if discount_type == '1':  # Percentage
                try:
                    percentage_input = input(f"Enter discount percentage for {item_name} (0-100): ").strip()
                    if not percentage_input:
                        print("No percentage entered.")
                        return
                        
                    percentage = float(percentage_input)
                    if percentage <= 0 or percentage > 100:
                        print("Percentage must be between 0-100.")
                        return

                    discount_amount = round(remaining_value * percentage / 100, 2)
                    if discount_amount <= 0:
                        print(f"Cannot apply discount - item already fully discounted (remaining value: RM{remaining_value:.2f})")
                        return

                    current_orders[order_id].setdefault("discounts", []).append({
                        "type": "percentage",
                        "value": percentage,
                        "description": f"{percentage}% off on {item_name}",
                        "apply_to": "specific_item",
                        "item_code": item_code,
                        "amount": discount_amount
                    })
                    save_to_file(current_orders, "current_active_orders.txt")
                    print(f"Applied {percentage}% discount to {item_name} (-RM{discount_amount:.2f})")
                    
                except ValueError:
                    print("Please enter a valid percentage number.")
                    return

            else:  # Fixed amount
                try:
                    amount_input = input(f"Enter fixed discount amount for {item_name} (max RM{remaining_value:.2f}): ").strip()
                    if not amount_input:
                        print("No amount entered.")
                        return
                        
                    amount = float(amount_input)
                    if amount <= 0:
                        print("Amount must be positive.")
                        return

                    if amount > remaining_value:
                        print(f"Discount cannot exceed remaining item value (RM{remaining_value:.2f})")
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
                    
                except ValueError:
                    print("Please enter a valid amount number.")
                    return

            calculate_order_total(order_id, current_orders, menu_items)
            view_order_details("Order Details", order_id, current_orders[order_id], menu_items)
        else:
            print("Invalid item number!")
            
    except ValueError:
        print(f"Please enter a valid item number (1-{len(current_orders[order_id]['items'])}).")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please try again.")

def apply_promo_code(order_id, current_orders, menu_items, promo_codes):
    """Apply promo code with proper sequential discount calculation"""
    show_promo_codes(promo_codes)
    
    promo_code = input("\nEnter promo code (or 'done' to cancel): ").strip().upper()
    if not promo_code:
        print("No promo code entered.")
        return
    if promo_code.lower() == 'done':
        return
    
    if promo_code not in promo_codes:
        print("Invalid promo code. Please check the code and try again.")
        return

    promo = promo_codes[promo_code]

    # Check if promo already applied
    existing_promos = [d for d in current_orders[order_id].get("discounts", []) 
                      if d.get('promo_code') == promo_code]
    if existing_promos:
        print("This promo code has already been applied.")
        return

    if promo['apply_to'] == 'specific_item':
        item_code = promo.get('item_code')
        if not item_code:
            print("Promo code configuration error: missing item code.")
            return
            
        # Check if item exists in order
        item_in_order = False
        item_qty = 0
        for item in current_orders[order_id]["items"]:
            if item[0] == item_code:
                item_in_order = True
                item_qty = item[1]
                break
                
        if not item_in_order:
            print(f"No {menu_items.get(item_code, {}).get('name', 'specified item')} in order for this promo.")
            return
        
        # Calculate price using same logic as view_order_details
        price = 0
        if "item_details" in current_orders[order_id] and item_code in current_orders[order_id]["item_details"]:
            price = calculate_custom_price(
                item_code, 
                current_orders[order_id]["item_details"][item_code], 
                menu_items,
                current_orders[order_id]
            )
        elif "cart_contents" in current_orders[order_id] and any(
            c['id'] == item_code for c in current_orders[order_id]["cart_contents"]
        ):
            customized_desc = next(
                (c['custom_description'] for c in current_orders[order_id]["cart_contents"] 
                if c['id'] == item_code and 'custom_description' in c),
                None
            )
            if customized_desc:
                price = calculate_custom_price(item_code, customized_desc, menu_items, current_orders[order_id])
            else:
                price = menu_items.get(item_code, {}).get('price', 0)
        else:
            price = menu_items.get(item_code, {}).get('price', 0)
        
        applicable_total = price * item_qty

        # Calculate existing discounts for this specific item
        existing_discounts = sum(
            d['amount'] for d in current_orders[order_id].get("discounts", [])
            if d.get('item_code') == item_code
        )
        remaining_value = max(0, applicable_total - existing_discounts)

    elif promo['apply_to'] == 'total':
        # For total order discounts
 # For total order discounts
        subtotal = 0
        for item in current_orders[order_id].get("items", []):
            item_code = item[0]
            qty = item[1]
            
            if "item_details" in current_orders[order_id] and item_code in current_orders[order_id]["item_details"]:
                price = calculate_custom_price(
                    item_code, 
                    current_orders[order_id]["item_details"][item_code], 
                    menu_items,
                    current_orders[order_id]
                )
            elif "cart_contents" in current_orders[order_id] and any(
                c['id'] == item_code for c in current_orders[order_id]["cart_contents"]
            ):
                customized_desc = next(
                    (c['custom_description'] for c in current_orders[order_id]["cart_contents"] 
                    if c['id'] == item_code and 'custom_description' in c),
                    None
                )
                if customized_desc:
                    price = calculate_custom_price(item_code, customized_desc, menu_items, current_orders[order_id])
                else:
                    price = menu_items.get(item_code, {}).get('price', 0)
            else:
                price = menu_items.get(item_code, {}).get('price', 0)
            
            subtotal += price * qty

        # Calculate existing discounts
        existing_discounts = current_orders[order_id].get("discounts", [])
        total_discounts_applied = sum(d.get('amount', 0) for d in existing_discounts)
        remaining_value = max(0, subtotal - total_discounts_applied)
    else:
        print("Invalid promo code application type.")
        return

    if remaining_value <= 0:
        print("Cannot apply discount - no applicable value remains for this promo.")
        return

    # Calculate discount amount based on remaining value
    if promo['type'] == 'percentage':
        discount_amount = round(remaining_value * promo['value'] / 100, 2)
    else:  # fixed amount
        discount_amount = min(promo['value'], remaining_value)

    if discount_amount <= 0:
        print("Cannot apply discount - discount amount would be zero or negative.")
        return

    # Apply promo
    discount_entry = {
        "type": promo['type'],
        "value": promo['value'],
        "amount": discount_amount,
        "description": promo.get('description', f"Promo {promo_code}"),
        "apply_to": promo['apply_to'],
        "promo_code": promo_code
    }
    if promo['apply_to'] == 'specific_item':
        discount_entry['item_code'] = promo['item_code']

    current_orders[order_id].setdefault("discounts", []).append(discount_entry)
    save_to_file(current_orders, "current_active_orders.txt")
    print(f"Successfully applied promo: {promo['description']} (-RM{discount_amount:.2f})")

    # Update and show order
    calculate_order_total(order_id, current_orders, menu_items)
    view_order_details("Order Details", order_id, current_orders[order_id], menu_items)

def apply_new_discount(order_id, current_orders, menu_items, promo_codes):
    """Apply a new discount to the order"""
    while True:
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
                break
            elif apply_to == '2':
                apply_discount_to_entire_order(order_id, current_orders, menu_items, discount_choice)
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
                
        elif discount_choice == '3':  # Promo Code
            apply_promo_code(order_id, current_orders, menu_items, promo_codes)
            break
            
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")

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
        remove_idx = int(input("Enter discount number to remove (or 0 to cancel): ").strip()) - 1
        if remove_idx == -1:
            return
        if 0 <= remove_idx < len(current_orders[order_id]["discounts"]):
            removed = current_orders[order_id]["discounts"].pop(remove_idx)
            save_to_file(current_orders, "current_active_orders.txt")  # Save after applying discount
            print(f"Removed discount: {removed['description']}")
            
            calculate_order_total(order_id, current_orders, menu_items)
            view_order_details("Order Details", order_id, current_orders[order_id], menu_items)
        else:
            print("Invalid selection.")
    except ValueError:
        print("3 Please enter a valid number.")

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

    # Ensure total is not negative
    total = max(0, calc['total'])  # This will set negative totals to 0

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
        "item_details": order.get("item_details", {}),
        "customizations": order.get("customizations", []),
        "cart_contents": order.get("cart_contents", []),
        "discounts": calc['discount_details'],
        "subtotal": calc['subtotal'],  # Added for reporting
        "tax": max(0, calc['total'] - calc['subtotal']),  # Ensure tax isn't negative
        "total": total,  # Using the corrected total here
        "payment_method": payment_method,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_user": order.get("system_user", ""),
        "display_name": order.get("display_name", ""),
        "status": "Completed"
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
        
        action = input("\nEnter Choice: ").strip()
    
        if action == "1":
            manage_discounts(order_id, current_orders, menu_items, promo_codes)
            
        elif action == "2":
            confirm = input(f"Confirm cancel order {order_id}? (y/n): ").strip().lower()
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
            print("4 Please enter a valid number!")

def process_received_order(order_data, current_orders, menu_items):
    try:
        # Generate order ID if not provided
        order_id = order_data.get("system_user", f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Validate required fields
        if "items" not in order_data or not order_data["items"]:
            print("Error: Order contains no items")
            return None
            
        # Calculate prices for customized items
        if "cart_contents" in order_data:
            for item in order_data["cart_contents"]:
                if isinstance(item, dict) and 'id' in item:
                    item_code = item['id']
                    if item_code in menu_items and 'contents' in menu_items[item_code]:  # It's a combo
                        addons_total = 0
                        for content_code, content_data in item.get('contents', {}).items():
                            if isinstance(content_data, list):
                                for custom_item in content_data:
                                    if custom_item and isinstance(custom_item, dict) and custom_item.get('customizations'):
                                        base_price = menu_items.get(content_code, {}).get('price', 0)
                                        custom_price = custom_item['customizations'].get('price', base_price)
                                        quantity = custom_item.get('quantity', 1)
                                        addons_total += (custom_price - base_price) * quantity
                        
                        if addons_total > 0:
                            if "item_details" not in order_data:
                                order_data["item_details"] = {}
                            order_data["item_details"][item_code] = f"{menu_items[item_code]['name']} +Customizations"
                            
                            # Update price in customizations if exists
                            if "customizations" in order_data:
                                for custom in order_data["customizations"]:
                                    if custom.get("id") == item_code:
                                        custom["price"] = menu_items[item_code]['price'] + addons_total

        # Set default values if missing
        order_data.setdefault("status", "Pending")
        order_data.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Save the order
        current_orders[order_id] = order_data
        save_to_file(current_orders, "current_active_orders.txt")
        
        print(f"\nSuccessfully processed order {order_id}")
        view_order_details("New Order Received", order_id, order_data, menu_items)
        return order_id
        
    except Exception as e:
        print(f"Error processing order: {e}")
        return None




