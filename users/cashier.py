from utils.order_management import order_management
from utils.display import show_menu, show_promo_codes, daily_sales_report
from utils.helpers import load_menu_items, load_promo_codes

def cashier_menu():
    current_orders = {} 
    transactions = []
    dine_in_counter = 1
    take_away_counter = 1
    menu_items = load_menu_items()
    promo_codes = load_promo_codes()

    while True:
        print("\n=== Cashier Menu ===")
        print("1. Order Management")
        print("2. Daily Sales Report")
        print("3. View Menu")
        print("4. View Promo Codes")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == '1':
            dine_in_counter, take_away_counter = order_management(
                current_orders, transactions, menu_items, promo_codes, dine_in_counter, take_away_counter
                )

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

    ####