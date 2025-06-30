from utils.helpers import load_file
from utils.order_management import view_active_orders
from utils.display import show_menu, show_promo_codes, daily_sales_report

def cashier_menu():
    while True:
        current_orders = load_file("current_active_orders.txt")
        transactions = load_file("transactions.txt")
        menu_items = load_file("menu_items.txt")
        promo_codes = load_file("promo_codes.txt")

        print("\n=== Cashier Menu ===")
        print("1. Current Active Orders")
        print("2. Daily Sales Report")
        print("3. View Menu")
        print("4. View Promo Codes")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == '1':
            view_active_orders(current_orders, menu_items, transactions)

        elif choice == '2':
            daily_sales_report(transactions, menu_items)

        elif choice == '3':
            show_menu(menu_items)
            input("\nPress Enter to return to main menu...")

        elif choice == '4':
            show_promo_codes(promo_codes)
            input("\nPress Enter to return to main menu...")
            
        elif choice == '5':
            print("Exiting the cashier system. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cashier_menu()