from utils.customer_functions.customer_acc import customer_account_management
from utils.customer_functions.product_browsing import product_browsing
from utils.customer_functions.cart_management import cart_management
from utils.customer_functions.order_tracking import order_tracking
from utils.customer_functions.dishes_review import dishes_review
from utils.helpers import load_file
from utils.display import show_menu
import os


def load_initial_data():
    os.makedirs("data", exist_ok=True)
    for file in ["carts.txt", "current_active_orders.txt","customers.txt" "review.txt"]:
        if not os.path.exists(f"data/{file}"):
            open(f"data/{file}", "w").close()

    return {
        'current_user': None,
        'menu': load_file("menu_items.txt"),
        'promo_codes': load_file("promo_codes.txt")
    }


def customer_main():
    state = load_initial_data()
    current_orders = {} 
    transactions = []
    menu_items = load_file('menu_items.txt')
    promo_codes = load_file('promo_codes.txt')

    while True:
        print("\n" + "=" * 40)
        print("=" * 40)
        print("1. Account Management")
        print("2. Browse Menu")
        print("3. My Cart")
        print("4. Order Tracking")
        print("5. Dish Reviews")
        print("6. Exit")

        choice = input("\nChoose (1-6): ").strip()

        if choice == "1":
            state['current_user'] = customer_account_management(
                state['current_user'])
        elif choice == "2":
            product_browsing(state['menu'])
        elif choice == "3":
            state['current_user'] = cart_management(
                state['current_user'], state['menu'])
        elif choice == "4":
            state['current_user'] = order_tracking(state['current_user'])
        elif choice == "5":
            state['current_user'] = dishes_review(state['current_user'])
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    customer_main()
