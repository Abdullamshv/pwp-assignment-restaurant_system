from utils.order_management import view_active_orders
from utils.display import show_menu, show_promo_codes, daily_sales_report

def cashier_menu():
    while True:

        print("\n=== Cashier Menu ===")
        print("1. Current Active Orders")
        print("2. Daily Sales Report")
        print("3. View Menu")
        print("4. View Promo Codes")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == '1':
            view_active_orders()

        elif choice == '2':
            daily_sales_report()

        elif choice == '3':
            show_menu()
            input("\nPress Enter to return to main menu...")

        elif choice == '4':
            show_promo_codes()
            input("\nPress Enter to return to main menu...")
            
        elif choice == '5':
            print("Exiting the cashier system. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cashier_menu()