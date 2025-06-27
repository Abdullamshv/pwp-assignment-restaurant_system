import os
import json
from datetime import datetime
from utils.helpers import load_file
def load_cart(user):
    cart = []
    try:
        with open("data/carts.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if parts[0] == user:
                    for item_str in parts[1:]:
                        try:
                            item = eval(item_str)
                            if not isinstance(item, dict):
                                continue
                            if 'remarks' not in item:
                                item['remarks'] = ''
                            cart.append(item)
                        except:
                            continue
                    break
    except (FileNotFoundError, SyntaxError):
        pass
    return cart

def load_menu():
    os.makedirs("data", exist_ok=True)
    try:
        with open("data/menu_items.txt", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Menu file not found or invalid!")
        return {}

def save_cart(user, cart):
    os.makedirs("data", exist_ok=True)
    carts = {}
    try:
        with open("data/carts.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if parts:
                    carts[parts[0]] = parts[1:]
    except FileNotFoundError:
        pass

    carts[user] = [str(item) for item in cart]
    with open("data/carts.txt", "w") as f:
        for username, items in carts.items():
            if username:
                f.write(f"{username}|||{'|||'.join(items)}\n")

def load_all_orders():
    try:
        with open("data/orders.txt", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_order(order_data):
    os.makedirs("data", exist_ok=True)
    all_orders = load_all_orders()
    order_id = next(iter(order_data))

    if 'cart_contents' in order_data[order_id]:
        order_data[order_id]['customizations'] = order_data[order_id]['cart_contents']

    all_orders[order_id] = order_data[order_id]

    with open("data/orders.txt", "w") as f:
        json.dump(all_orders, f, indent=4)

def display_cart(cart):
    if not cart:
        print("\nYour cart is empty")
        return

    print("\n=== YOUR CART ===")
    for idx, item in enumerate(cart, 1):
        remarks = item.get('remarks', '')
        remarks_str = f" [Remarks: {remarks}]" if remarks else ""

        if item.get('type') == 'combo':
            print(f"{idx}. COMBO: {item['name']} x{item['quantity']} - RM{item['price']:.2f}{remarks_str}")
        else:
            print(f"{idx}. {item['name']} x{item['quantity']} - RM{item['price']:.2f}{remarks_str}")

    total = sum(item['price'] * item['quantity'] for item in cart)
    print(f"\nTOTAL: RM{total:.2f}")

def customize_item(menu_item, full_menu=None, is_combo_part=False, component_id=None):
    item_id = component_id if component_id else menu_item.get('id')

    item = {
        'id': item_id,
        'name': menu_item.get('name', 'Unnamed Item'),
        'price': menu_item.get('base_price', 0),
        'quantity': 1,
        'remarks': '',
        'type': 'combo' if 'contents' in menu_item else 'single',
        'contents': {}
    }

    if not is_combo_part and item['type'] == 'single':
        while True:
            try:
                qty = int(input(f"\nEnter quantity for {item['name']} (1-10): "))
                if 1 <= qty <= 10:
                    item['quantity'] = qty
                    break
                print("Please enter 1-10")
            except ValueError:
                print("Numbers only!")

    if not is_combo_part:
        item['remarks'] = input("\n Special instructions (press Enter to skip): ").strip()

    return item


def checkout(current_user, cart):
    if not cart:
        print("Cannot checkout - cart is empty!")
        return False

    display_cart(cart)

    # === PROMO CODE INPUT ===
    promo_codes = load_file("promo_codes.txt")
    promo_code = input("\nEnter promo code (press Enter to skip): ").strip().upper()

    discount_type = None
    discount_value = 0
    discount_target = None

    if promo_code:
        if promo_code in promo_codes:
            promo = promo_codes[promo_code]
            discount_type = promo["type"]
            discount_value = promo["value"]
            discount_target = promo["apply_to"]

            if discount_target == "total":
                print(f"Promo applied: {promo['description']}")
            elif discount_target == "specific_item":
                item_code = promo.get("item_code")
                item_found = False
                for item in cart:
                    if item['id'] == item_code:
                        item_found = True
                        if discount_type == "fixed":
                            item['price'] = max(0, item['price'] - discount_value)
                        elif discount_type == "percentage":
                            item['price'] = round(item['price'] * (1 - discount_value / 100), 2)
                if item_found:
                    print(f"Promo applied: {promo['description']}")
                else:
                    print("Promo code is valid but item not in cart.")
        else:
            print("Invalid promo code.")

    # === CALCULATE TOTAL ===
    total = sum(item['price'] * item['quantity'] for item in cart)

    # If promo is for total
    if promo_code and promo_code in promo_codes and discount_target == "total":
        if discount_type == "fixed":
            total = max(0, total - discount_value)
        elif discount_type == "percentage":
            total = round(total * (1 - discount_value / 100), 2)

    print(f"\nTOTAL after promo: RM{total:.2f}")

    customer_name = current_user
    if current_user.startswith("Guest_"):
        customer_name = input("Enter your name for the order: ").strip()
        while not customer_name:
            print("Name cannot be empty!")
            customer_name = input("Enter your name: ").strip()

    order_type = input("Order type (1 for Dine-In, 2 for Takeaway): ").strip()
    while order_type not in ("1", "2"):
        print("Invalid choice. Please enter 1 or 2.")
        order_type = input("Order type (1 for Dine-In, 2 for Takeaway): ").strip()

    table_num = ""
    if order_type == "1":
        table_num = input("Enter table number: ").strip()
        while not table_num.isdigit():
            print("Invalid table number!")
            table_num = input("Enter table number: ").strip()

    existing_orders = load_all_orders()
    order_id = "D" + str(len(existing_orders) + 1).zfill(2)

    order_data = {
        order_id: {
            "system_user": current_user,
            "display_name": customer_name,
            "type": "Dine-In" if order_type == "1" else "Takeaway",
            "table_number": table_num,
            "items": [[item['id'], item['quantity']] for item in cart],
            "item_details": {item['id']: item['name'] for item in cart},
            "cart_contents": [item for item in cart],
            "total": total,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Preparing",
            "promo_code": promo_code if promo_code in promo_codes else None
        }
    }

    save_order(order_data)

    print(f"\n=== ORDER CONFIRMATION ===")
    print(f"Order ID: {order_id}")
    print(f"Customer: {customer_name}")
    print("Items:")
    for item_id, qty in order_data[order_id]['items']:
        print(f"  - {item_id} x{qty}")
    print(f"Total after promo: RM{total:.2f}")

    save_cart(current_user, [])
    return True


def cart_management(current_user, menu):
    menu = load_file("menu_items.txt")
    if not current_user:
        print("Please login first")
        return current_user

    for item_id in menu:
        if 'price' in menu[item_id]:
            menu[item_id]['base_price'] = menu[item_id]['price']

    cart = load_cart(current_user)

    while True:
        display_cart(cart)

        print("\nOPTIONS:")
        print("1. Add Item")
        print("2. Remove Item")
        print("3. Edit Item Remarks")
        print("4. Checkout")
        print("5. Back")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            print("\n=== MENU ITEMS ===")
            categories = {}
            for item_id, item in menu.items():
                categories.setdefault(item['category'], []).append((item_id, item))

            for category, items in categories.items():
                print(f"\n{category.upper()}")
                for item_id, item in items:
                    print(f"{item_id}. {item['name']} - RM{item['base_price']:.2f}")

            item_id = input("\nEnter item ID: ").strip().upper()
            if item_id in menu:
                item_data = {'id': item_id, **menu[item_id]}
                cart.append(customize_item(item_data, menu))
                save_cart(current_user, cart)
                print("Item added to cart!")
            else:
                print("Invalid item ID!")

        elif choice == "2":
            if not cart:
                print("Cart is empty!")
                continue
            try:
                idx = int(input("Enter item number to remove: ")) - 1
                if 0 <= idx < len(cart):
                    removed = cart.pop(idx)
                    save_cart(current_user, cart)
                    print(f"Removed {removed.get('name', 'item')}")
                else:
                    print("Invalid item number!")
            except ValueError:
                print("Please enter a valid number!")

        elif choice == "3":
            if not cart:
                print("Cart is empty!")
                continue
            try:
                idx = int(input("Enter item number to edit remarks: ")) - 1
                if 0 <= idx < len(cart):
                    new_remarks = input("Enter new remarks: ").strip()
                    cart[idx]['remarks'] = new_remarks
                    save_cart(current_user, cart)
                    print("Remarks updated!")
                else:
                    print("Invalid item number!")
            except ValueError:
                print("Please enter a valid number!")

        elif choice == "4":
            if checkout(current_user, cart):
                return current_user

        elif choice == "5":
            return current_user

        else:
            print("Invalid choice")