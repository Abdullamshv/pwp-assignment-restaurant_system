def display_menu_by_category(menu, category):
    print(f"\n=== {category.upper()} ===")
    for item_id, item in menu.items():
        if item.get('category') == category:
            price = item.get('base_price', item.get('price', 0))
            print(f"\n{item_id}. {item['name']} - RM{price:.2f}")

            if 'contents' in item and item['contents']:
                print("   Includes:")
                for content_id, qty in item['contents'].items():
                    content_name = menu.get(content_id, {}).get('name', 'Unknown')
                    print(f"   - {qty}x {content_name}")

            if 'ingredients' in item and item['ingredients']:
                customizable = [ing for ing, det in item['ingredients'].items() if not det.get('default', True)]
                if customizable:
                    print("   Customizable: Yes")

def product_browsing(menu):
    while True:
        print("\n===========================================")
        print("=============== BROWSE MENU ===============")
        print("===========================================")
        print("1. Burgers")
        print("2. Sides")
        print("3. Drinks")
        print("4. Set Meals")
        print("5. Back")

        choice = input("Choose category (1-5): ").strip()

        categories = {
            "1": "Burgers",
            "2": "Sides",
            "3": "Drinks",
            "4": "Meals"
        }

        if choice in categories:
            display_menu_by_category(menu, categories[choice])
        elif choice == "5":
            break
        else:
            print("Invalid choice")

        input("\nPress Enter to continue...")
