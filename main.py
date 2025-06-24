import os
from users.cashier import cashier_menu
from users.manager import manager_menu
from users.customer import customer_main

ACCOUNTS_FILE = "data/users.txt"

def load_accounts():
    accounts = {}
    if not os.path.exists(ACCOUNTS_FILE):
        os.makedirs("data", exist_ok=True)
        open(ACCOUNTS_FILE, "w").close()

    with open(ACCOUNTS_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 3:
                username, password, role = parts
                accounts[username] = {"password": password, "role": role}
    return accounts


def login(expected_role):
    accounts = load_accounts()

    print(f"\n=== Login as {expected_role.capitalize()} ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    user = accounts.get(username)
    if user and user["password"] == password and user["role"] == expected_role:
        print(f"\n✅ Logged in successfully as {username} ({expected_role})")
        return True
    else:
        print("❌ Invalid credentials or role mismatch.")
        return False


def main_menu():
    while True:
        print("\n=== System Role Panel ===")
        print("1. Cashier")
        print("2. Manager")
        print("3. Customer")
        print("4. Exit")

        choice = input("Choose role (1-4): ").strip()

        if choice == "1":
            if login("cashier"):
                cashier_menu()
        elif choice == "2":
            if login("manager"):
                manager_menu()
        elif choice == "3":
            customer_main()

        elif choice == "4":
            print("👋 Exiting system.")
            break
        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main_menu()
