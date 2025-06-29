import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.manager_utils import manage_user_accounts
from utils.manager_utils import view_all_orders
from utils.manager_utils import view_customer_feedback
from utils.manager_utils import track_finances
from utils.manager_utils import manage_promo_codes
from .chef import  check_inventory


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def manager_menu():
    while True:
        print("\n=== Manager Menu ===")
        print("1. Manage User Accounts")
        print("2. View Orders")
        print("3. Track Finances")
        print("4. Manage Inventory")
        print("5. View Customer Feedback")
        print("6. Promo Code Management")
        print("7. Exit")

        choice = input("Choose option (1-7): ").strip()

        if choice == "1":
            manage_user_accounts()
        elif choice == "2":
            view_all_orders()
        elif choice == "3":
            track_finances()
        elif choice == "4":
            check_inventory()
        elif choice == "5":
            view_customer_feedback()
        elif choice == "6":
            manage_promo_codes()
        elif choice == "7":
            print("Exiting manager menu.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    manager_menu()

