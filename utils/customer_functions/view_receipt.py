def view_receipt(current_user):
    import json, os

    path = os.path.join("data", "current_active_orders.txt")
    if not os.path.exists(path):
        print("No orders found.")
        return

    with open(path, "r") as f:
        orders = json.load(f)

    found = False
    for order_id, order in orders.items():
        if order.get('system_user') == current_user:
            found = True
            print(f"\n=== RECEIPT for {current_user} ===")
            print(f"Order ID: {order_id}")
            print(f"Date: {order['timestamp']}")
            print(f"Type: {order['type']}")
            if order['type'] == "Dine-In":
                print(f"Table: {order['table_number']}")
            print("Items:")
            total = 0
            for item in order['cart_contents']:
                subtotal = item['price'] * item['quantity']
                total += subtotal
                remarks = f" (Remarks: {item['remarks']})" if item['remarks'] else ""
                print(f" - {item['name']} x{item['quantity']} RM{subtotal:.2f}{remarks}")
            print(f"Total: RM{total:.2f}")
            print(f"Status: {order['status']}")
            print(f"Order Remarks: {order.get('remarks', 'None')}")
    if not found:
        print("No orders found for you.")
