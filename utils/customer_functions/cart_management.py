import os
import json
from datetime import datetime
from utils.helpers import load_file, load_order_counters, save_order_counters

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
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Menu file not found или содержит ошибку!")
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
        with open("data/current_active_orders.txt", "r") as f:
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

    with open("data/current_active_orders.txt", "w") as f:
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

    for item in cart:
        if item['type'] == 'combo':
            print(f"\n{item['name']} (Customized):")
            for comp_id, components in item['contents'].items():
                # Handle both list and dictionary formats
                if isinstance(components, list):
                    for component in components:
                        if component['customizations']:
                            print(f"  - {component['quantity']}x {component['customizations']['name']}")
                elif isinstance(components, dict) and components['customizations']:
                    print(f"  - {components['quantity']}x {components['customizations']['name']}")

    total = sum(item['price'] * item['quantity'] for item in cart)
    print(f"\nTOTAL: RM{total:.2f}")

def customize_item(menu_item, full_menu=None, is_combo_part=False, component_id=None):
    item_id = component_id if component_id else menu_item.get('id')

    item = {
        'id': item_id,
        'name': menu_item.get('name', 'Unnamed Item'),
        'price': menu_item.get('price', 0),
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

    if item['type'] == 'combo' and full_menu:
        print(f"\n{'=' * 30}\n⚡ Customizing {item['name']} Combo ⚡\n{'=' * 30}")
        item['contents'] = {}

        for comp_id, fixed_qty in menu_item.get('contents', {}).items():
            component = full_menu.get(comp_id, {})
            if not component:
                continue

            if component.get('category') == 'Burgers':
                print(f"\n {component.get('name', 'Burger')} x{fixed_qty}")
                burgers_to_customize = 0

                if fixed_qty > 1:
                    try:
                        burgers_to_customize = int(input(
                            f"How many burgers to customize? (0-{fixed_qty}): "
                        ))
                        burgers_to_customize = max(0, min(fixed_qty, burgers_to_customize))
                    except ValueError:
                        print("Invalid input. Customizing none.")

                for i in range(burgers_to_customize):
                    print(f"\nCustomizing Burger #{i + 1}:")
                    customized = customize_item(component, full_menu, is_combo_part=True, component_id=comp_id)
                    if comp_id not in item['contents']:
                        item['contents'][comp_id] = []
                    item['contents'][comp_id].append({
                        'quantity': 1,
                        'customizations': customized
                    })
                    item['price'] += (customized.get('price', 0) - component.get('price', 0))

                if fixed_qty - burgers_to_customize > 0:
                    if comp_id not in item['contents']:
                        item['contents'][comp_id] = []
                    item['contents'][comp_id].append({
                        'quantity': fixed_qty - burgers_to_customize,
                        'customizations': None
                    })

            elif component.get('category') == 'Drinks':
                remaining_qty = fixed_qty
                drink_changes = []

                print(f"\n Original Drink: {component.get('name', 'Drink')} x{fixed_qty}")

                while remaining_qty > 0:
                    print(f"\nDrinks left to customize: {remaining_qty}")
                    print("Available drinks:")
                    drinks = {k: v for k, v in full_menu.items() if v.get('category') == 'Drinks'}
                    for d_id, drink in drinks.items():
                        print(f"{d_id}. {drink.get('name', 'Drink')} (RM{drink.get('price', 0):.2f})")

                    choice = input("Enter drink ID or 'keep' remaining: ").strip().upper()
                    if choice == 'KEEP':
                        break
                    if choice not in drinks:
                        print("Invalid choice! Try again.")
                        continue

                    while True:
                        try:
                            change_qty = int(input(
                                f"How many {drinks[choice].get('name', 'Drink')}? (1-{remaining_qty}): "
                            ))
                            if 1 <= change_qty <= remaining_qty:
                                drink_changes.append({
                                    'id': choice,
                                    'qty': change_qty,
                                    'price': drinks[choice].get('price', 0)
                                })
                                remaining_qty -= change_qty
                                break
                            print(f"Must be 1-{remaining_qty}")
                        except ValueError:
                            print("Numbers only!")

                if drink_changes:
                    item['contents'][comp_id] = []
                    for change in drink_changes:
                        item['contents'][comp_id].append({
                            'quantity': change['qty'],
                            'customizations': {
                                'substituted_id': change['id'],
                                'name': drinks[change['id']].get('name', 'Drink'),
                                'price_diff': change['price'] - component.get('price', 0)
                            }
                        })
                        item['price'] += (change['price'] - component.get('price', 0)) * change['qty']

                    if remaining_qty > 0:
                        item['contents'][comp_id].append({
                            'quantity': remaining_qty,
                            'customizations': None
                        })
                else:
                    item['contents'][comp_id] = {
                        'quantity': fixed_qty,
                        'customizations': None
                    }

            else:
                print(f"\n {component.get('name', 'Side')} x{fixed_qty} (Standard)")
                item['contents'][comp_id] = {
                    'quantity': fixed_qty,
                    'customizations': None
                }

    elif menu_item.get('category') == 'Burgers' and menu_item.get('ingredients'):
        print("\nCustomizable ingredients:")
        for ing, details in menu_item.get('ingredients', {}).items():
            if not details.get('default', True):
                if input(f"Add {ing} (+RM{details.get('price', 0):.2f})? (y/n): ").lower() == 'y':
                    item['price'] += details.get('price', 0)
                    item['name'] += f" +{ing}"

    if not is_combo_part:
        item['remarks'] = input("\n Special instructions (press Enter to skip): ").strip()

    return item

def checkout(current_user, cart):
    if not cart:
        print("Cannot checkout - cart is empty!")
        return False

    display_cart(cart)

    total = sum(item['price'] * item['quantity'] for item in cart)
    print(f"\nTOTAL: RM{total:.2f}")

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

    counters = load_order_counters()
    if order_type == "1":
        order_id = f"D{counters['dine_in']:02d}"
        counters['dine_in'] += 1
    else:
        order_id = f"T{counters['take_away']:02d}"
        counters['take_away'] += 1
    save_order_counters(counters)

    table_num = ""
    if order_type == "1":
        table_num = input("Enter table number: ").strip()
        while not table_num.isdigit():
            print("Invalid table number!")
            table_num = input("Enter table number: ").strip()

    remarks = input("Enter order remarks (optional): ").strip()

    existing_orders = load_all_orders()
    
    order_data = {
        order_id: {
            "system_user": current_user,
            "display_name": customer_name,
            "type": "Dine-In" if order_type == "1" else "Takeaway",
            "table_number": table_num,
            "items": [[item['id'], item['quantity'], item.get('remarks', '')] for item in cart],
            "item_details": {item['id']: item['name'] for item in cart},
            "cart_contents": [item for item in cart],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "remarks": remarks,
            "status": "Pending"
        }
    }

    save_order(order_data)

    print(f"\n=== ORDER CONFIRMATION ===")
    print(f"Order ID: {order_id}")
    print(f"Customer: {customer_name}")
    print("Items:")
    for item_id, qty, item_remarks in order_data[order_id]['items']:
        print(f"  - {item_id} x{qty}" + (f" (Remarks: {item_remarks})" if item_remarks else ""))
    print(f"Remarks: {remarks if remarks else 'None'}")

    save_cart(current_user, [])
    return True

def cart_management(current_user, menu):
    menu = load_file("menu_items.txt")
    if not current_user:
        print("Please login first")
        return current_user

    for item_id in menu:
        if 'price' in menu[item_id]:
            menu[item_id]['price'] = menu[item_id]['price']

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
                    print(f"{item_id}. {item['name']} - RM{item['price']:.2f}")

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
