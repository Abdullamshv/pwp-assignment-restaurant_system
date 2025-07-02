import json

def load_orders(username):
    try:
        with open("data/current_active_orders.txt", "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            all_orders = json.loads(content)
            return {
                order_id: order
                for order_id, order in all_orders.items()
                if order.get("system_user") == username  
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def order_tracking(current_user):
    if not current_user:
        print("Please login first")
        return current_user

    orders = load_orders(current_user)

    if not orders:
        print("\nNo orders found for your account!")
        return current_user

    print(f"\n=== YOUR ORDER HISTORY ===")
    for order_id, order in sorted(orders.items(), key=lambda x: x[1]['timestamp'], reverse=True):
        print(f"\nOrder ID: {order_id}")
        print(f"Date: {order['timestamp']}")
        print(f"Type: {order['type']}")
        if order['type'] == "Dine-In":
            print(f"Table: {order['table_number']}")

        print("Items:")
        for item_id, qty, item_remarks in order['items']:
            output = f"  - {item_id} x{qty}"

            # Show item name and customizations if available
            if 'item_details' in order and item_id in order['item_details']:
                item_name = order['item_details'][item_id]
                if '+' in item_name:
                    base_name = item_name.split('+')[0]
                    add_ons = item_name.split('+')[1:]
                    output += f" ({base_name} with: {', '.join(add_ons)})"
                else:
                    output += f" ({item_name})"

            if item_remarks:
                output += f" (Remarks: {item_remarks})"

            print(output)

        if 'cart_contents' in order:
            print("\nDetailed Customizations:")
            for item in order['cart_contents']:
                if item.get('type') == 'combo' and 'contents' in item:
                    print(f"\n{item['name']} contains:")
                    for comp_id, components in item['contents'].items():
                        if isinstance(components, list):
                            for component in components:
                                if component.get('customizations'):
                                    custom = component['customizations']
                                    name = custom.get('name', 'Item')
                                    if '+' in name:
                                        base, *addons = name.split('+')
                                        print(f"  - {base.strip()} with: {', '.join(addons)}")
                                    else:
                                        print(f"  - {name}")
                        elif isinstance(components, dict) and components.get('customizations'):
                            custom = components['customizations']
                            name = custom.get('name', 'Item')
                            if '+' in name:
                                base, *addons = name.split('+')
                                print(f"  - {base.strip()} with: {', '.join(addons)}")
                            else:
                                print(f"  - {name}")

        if order.get('remarks'):
            print(f"\nOrder Remarks: {order['remarks']}")
        print("-" * 40)

    input("\nPress Enter to continue...")
    return current_user