import os
import json

PROMO_FILE = os.path.join("data", "promo_codes.txt")

def load_lines_from_file(filename, default=[]):
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        return default
    with open(filepath, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def manage_user_accounts():
    while True:
        users = load_lines_from_file("users.txt", default=[])
        print("\n--- User Accounts ---")
        if users:
            for i, user in enumerate(users, 1):
                print(f"{i}. {user}")
        else:
            print("No users found.")

        print("\nOptions:")
        print("1. Add User")
        print("2. Delete User")
        print("3. Back")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            new_user = input("Enter new user info (e.g. username,password,role): ").strip()
            if new_user:
                users.append(new_user)
                save_lines_to_file("users.txt", users)
                print("User added successfully.")
            else:
                print("User info cannot be empty.")

        elif choice == "2":
            try:
                index = int(input("Enter the number of the user to delete: "))
                if 1 <= index <= len(users):
                    removed = users.pop(index - 1)
                    save_lines_to_file("users.txt", users)
                    print(f"User '{removed}' deleted.")
                else:
                    print("Invalid user number.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "3":
            break

        else:
            print("Invalid choice. Try again.")

def save_lines_to_file(filename, lines):
    filepath = os.path.join("data", filename)
    with open(filepath, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line.strip() + "\n")
            
def view_all_orders():
    orders_file = os.path.join("data", "current_active_orders.txt")
    if not os.path.exists(orders_file):
        print("No orders found.")
        return

    try:
        with open(orders_file, "r") as f:
            all_orders = json.load(f)
    except json.JSONDecodeError:
        print("Error reading orders.")
        return

    if not all_orders:
        print("No orders found.")
        return

    print("\n=== All Orders ===")
    for order_id, order in all_orders.items():
        print(f"\nOrder ID: {order_id}")
        print(f"Customer: {order.get('display_name')}")
        print(f"Order Type: {order.get('type')}")
        print(f"Table Number: {order.get('table_number', 'N/A')}")
        print("Items:")
        for item in order.get("cart_contents", []):
            print(f"  - {item['name']} x{item['quantity']} (RM{item['price']:.2f})")

        promo_code = order.get("promo_code")
        if promo_code:
            print(f"Promo Code Applied: {promo_code}")
        else:
            print("Promo Code Applied: None")

        print(f"Total: RM{order.get('total', 0):.2f}")
        print(f"Timestamp: {order.get('timestamp')}")
        print(f"Status: {order.get('status')}")
        
def track_finances():
    orders_file = os.path.join("data", "current_active_orders.txt")
    if not os.path.exists(orders_file):
        print("No orders found.")
        return

    try:
        with open(orders_file, "r") as f:
            all_orders = json.load(f)
    except json.JSONDecodeError:
        print("Error reading orders.")
        return

    total_revenue = 0
    dine_in_count = 0
    takeaway_count = 0
    total_discounts = 0
    promo_codes_used = []

    for order_id, order in all_orders.items():
        total_revenue += order.get("total", 0)

        if order.get("type") == "Dine-In":
            dine_in_count += 1
        elif order.get("type") == "Takeaway":
            takeaway_count += 1

        # Суммируем скидки из discounts
        for discount in order.get("discounts", []):
            total_discounts += discount.get("amount", 0)
            if discount.get("promo_code"):
                promo_codes_used.append(discount["promo_code"])

    print("\n=== Financial Summary ===")
    print(f"Total revenue: RM{total_revenue:.2f}")
    print(f"Total dine-in orders: {dine_in_count}")
    print(f"Total takeaway orders: {takeaway_count}")
    print(f"Total discounts given: RM{total_discounts:.2f}")

    if promo_codes_used:
        print("\nPromo codes used:")
        for code in promo_codes_used:
            print(f"- {code}")

def manage_inventory():
    inventory = load_lines_from_file("menu_data.py", default=[])
    print("\n--- Inventory (Menu Items) ---")
    for item in inventory:
        print(item)
        
def view_customer_feedback():
    feedback = load_lines_from_file("review.txt", default=[])
    print("\n--- Customer Feedback ---")
    for review in feedback:
        print(review)


def load_promos():
    try:
        with open(PROMO_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_promos(promos):
    with open(PROMO_FILE, "w") as f:
        json.dump(promos, f, indent=4)

def view_all_promo_codes():
    promos = load_promos()
    if not promos:
        print("\nNo promo codes available.")
        return

    print("\n=== All Promo Codes ===")
    for code, details in promos.items():
        print(f"\nCode: {code}")
        print(f"  Description: {details.get('description', '-')}")
        print(f"  Type: {details.get('type')} ({details.get('value')})")
        print(f"  Apply to: {details.get('apply_to')}")
        if details.get('apply_to') == "specific_item":
            print(f"  Item Code: {details.get('item_code')}")
    print()

def add_promo_code():
    promos = load_promos()

    code = input("Enter promo code name (e.g., BIGSALE): ").strip().upper()
    if not code or code in promos:
        print("Invalid or duplicate promo code.")
        return

    type_ = input("Type (fixed/percentage): ").strip().lower()
    if type_ not in ("fixed", "percentage"):
        print("Invalid type.")
        return

    try:
        value = float(input("Enter discount value: ").strip())
    except ValueError:
        print("Invalid value.")
        return

    description = input("Enter description: ").strip()

    apply_to = input("Apply to ('total' or 'specific_item'): ").strip().lower()
    item_code = ""
    if apply_to == "specific_item":
        item_code = input("Enter item code (e.g., B1): ").strip().upper()

    promos[code] = {
        "type": type_,
        "value": value,
        "description": description,
        "apply_to": apply_to
    }
    if item_code:
        promos[code]["item_code"] = item_code

    save_promos(promos)
    print(f"Promo code '{code}' added successfully.")

def delete_promo_code():
    promos = load_promos()
    if not promos:
        print("No promo codes to delete.")
        return

    code = input("Enter the promo code to delete: ").strip().upper()
    if code not in promos:
        print("Promo code not found.")
        return

    del promos[code]
    save_promos(promos)
    print(f"Promo code '{code}' deleted.")
    
def manage_promo_codes():
    while True:
        print("\n=== Promo Code Management ===")
        print("1. View All Promo Codes")
        print("2. Add New Promo Code")
        print("3. Delete Promo Code")
        print("4. Back")

        choice = input("Choose option (1-4): ").strip()

        if choice == "1":
            view_all_promo_codes()
        elif choice == "2":
            add_promo_code()
        elif choice == "3":
            delete_promo_code()
        elif choice == "4":
            break
        else:
            print("Invalid option.")