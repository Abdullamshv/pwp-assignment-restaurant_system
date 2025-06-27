def load_customers():
    customers = {}
    try:
        with open("data/users.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and "|||" in line:
                    username, pwd = line.split("|||", 1)
                    customers[username] = pwd
    except FileNotFoundError:
        import os
        os.makedirs("data", exist_ok=True)
        with open("data/users.txt", "a"):
            pass
    return customers


def save_customers(customers):
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/users.txt", "a") as f:
        for username, pwd in customers.items():
            f.write(f"{username}|||{pwd}\n")


def customer_account_management(current_user):
    customers = load_customers()

    while True:
        print("\n=== ACCOUNT MANAGEMENT ===")
        print(f"Current user: {current_user or 'Not logged in'}")
        print("1. Register")
        print("2. Login")
        print("3. Logout")
        print("4. Continue as Guest")
        print("5. Back")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            username = input("New username: ").strip()
            if not username:
                print("Username cannot be empty!")
                continue
            if " " in username:
                print("Username cannot contain spaces!")
                continue
            if username in customers:
                print("Username already exists!")
                continue

            password = input("New password: ").strip()
            if not password:
                print("Password cannot be empty!")
                continue
            if " " in password:
                print("Password cannot contain spaces!")
                continue

            customers[username] = password
            save_customers(customers)
            print("Registration successful!")
            return username

        elif choice == "2":
            if current_user:
                print("Already logged in!")
                continue

            username = input("Username: ").strip()
            password = input("Password: ").strip()

            if username in customers and customers[username] == password:
                print("Login successful!")
                return username
            else:
                print("Invalid username or password!")

        elif choice == "3":
            if not current_user:
                print("Not logged in!")
            else:
                print(f"Logged out of {current_user}")
                return None

        elif choice == "4":
            if current_user:
                print("Already logged in!")
                continue

            import random
            guest_id = f"Guest_{random.randint(1000, 9999)}"
            print(f"Continuing as {guest_id}")
            return guest_id

        elif choice == "5":
            return current_user