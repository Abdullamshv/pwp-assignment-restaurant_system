import json
import os

# ==================== Constant file names ====================

RECIPE_FILE = "recipe.json"
INVENTORY_FILE = "inventory.json"
EQUIPMENT_FILE = "equipment.json"

# ==================== Utility Functions ====================

def load_data(file_path):
    """Load a dictionary from a JSON file, return empty dict if file not found or empty."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_data(file_path, data_dict):
    """Save a dictionary into a file as JSON (pretty-printed)."""
    with open(file_path, "w") as file:
        json.dump(data_dict, file, indent=4)

def input_non_empty(prompt):
    """Prompt until a non-empty string is given."""
    value = ""
    while not value:
        value = input(prompt).strip()
        if not value:
            print("Input cannot be empty!")
    return value

def input_positive_int(prompt):
    """Prompt until a valid positive integer is given."""
    num = None
    while num is None:
        try:
            num = int(input(prompt).strip())
            if num <= 0:
                print("Please enter a number greater than 0!")
                num = None
        except ValueError:
            print("Please enter a valid number!")
    return num

# ==================== Load Data ====================

recipes_data = load_data(RECIPE_FILE)
inventory_data = load_data(INVENTORY_FILE)
equipment_data = load_data(EQUIPMENT_FILE)

# Load inventory and unify to lowercase keys
inventory_data = {k.lower(): v for k, v in inventory_data.items()}

# ==================== Recipe Functions ====================

import textwrap

def view_recipes():
    """Display all available recipes in a clean, aligned format."""
    print("\n" + "-" * 80)
    print(f"{'AVAILABLE RECIPES':^80}")
    print("-" * 80)

    if recipes_data:
        header = f"{'No.':<4} {'Recipe Name':<20} {'Ingredients'}"
        print(header)
        print("-" * 80)

        for i, (name, ingredients) in enumerate(recipes_data.items(), 1):
            ing_text = ", ".join(ingredients)
            wrapped_lines = textwrap.wrap(ing_text, width=52) or [""]

            # First line with index and recipe
            print(f"{i:<4} {name:<20} {wrapped_lines[0]}")

            # Additional lines
            for extra_line in wrapped_lines[1:]:
                print(f"{'':<4} {'':<20} {extra_line}")

    else:
        print("No recipes found.".center(80))

    print("-" * 80)
    input("\nPress Enter to return to menu...")

def add_recipe():
    """Add a new recipe."""
    recipe_name = input_non_empty("Enter recipe name: ")
    ingredients = input_non_empty("Enter ingredients (comma separated): ").split(",")
    recipes_data[recipe_name] = [i.strip() for i in ingredients]
    save_data(RECIPE_FILE, recipes_data)
    print(f"Recipe '{recipe_name}' added!")
    input("\nPress Enter to return to menu...")

def update_recipe():
    """Update an existing recipe."""
    if not recipes_data:
        print("No recipes available to update.")
        input("\nPress Enter to return to menu...")
        return

    print("\nSelect a recipe to update:")
    for i, name in enumerate(recipes_data.keys(), 1):
        print(f"{i}. {name}")

    choice = input_positive_int("\nEnter recipe number to update: ")
    if choice < 1 or choice > len(recipes_data):
        print("Invalid choice!")
    else:
        recipe_name = list(recipes_data.keys())[choice-1]
        new_ingredients = input_non_empty(f"Enter new ingredients for '{recipe_name}': ").split(",")
        recipes_data[recipe_name] = [i.strip() for i in new_ingredients]
        save_data(RECIPE_FILE, recipes_data)
        print(f"Updated recipe '{recipe_name}'.")
    input("\nPress Enter to return to menu...")

def delete_recipe():
    """Delete a selected recipe."""
    if not recipes_data:
        print("No recipes available to delete.")
        input("\nPress Enter to return to menu...")
        return

    print("\nSelect a recipe to delete:")
    for i, name in enumerate(recipes_data.keys(), 1):
        print(f"{i}. {name}")

    choice = input_positive_int("\nEnter recipe number to delete: ")
    if choice < 1 or choice > len(recipes_data):
        print("Invalid choice!")
    else:
        recipe_name = list(recipes_data.keys())[choice-1]
        del recipes_data[recipe_name]
        save_data(RECIPE_FILE, recipes_data)
        print(f"Deleted recipe '{recipe_name}'.")
    input("\nPress Enter to return to menu...")

# ==================== Inventory Check ====================

def check_inventory():
    """Check if a selected recipe can be prepared."""
    if not recipes_data:
        print("No recipes available to check.")
        input("\nPress Enter to return to menu...")
        return

    print("\nSelect a recipe to check availability:")
    for i, name in enumerate(recipes_data.keys(), 1):
        print(f"{i}. {name}")

    choice = input_positive_int("\nEnter recipe number to check: ")
    if choice < 1 or choice > len(recipes_data):
        print("Invalid choice!")
        input("\nPress Enter to return to menu...")
        return

    recipe_name = list(recipes_data.keys())[choice-1]
    num_servings = input_positive_int(f"How many servings of '{recipe_name}' do you want to check? ")

    required_counts = {}
    for ing in recipes_data[recipe_name]:
        required_counts[ing.lower()] = required_counts.get(ing.lower(), 0) + num_servings

    not_enough = []
    for ing, required_qty in required_counts.items():
        available_qty = inventory_data.get(ing.lower(), 0)
        if available_qty < required_qty:
            not_enough.append((ing, required_qty, available_qty))

    if not_enough:
        print("\n" + "=" * 50)
        print(f"Sorry! Cannot prepare {num_servings} serving(s) of '{recipe_name}'.")
        print("=" * 50)
        print("Insufficient ingredients:")
        for item, required, available in not_enough:
            print(f" • {item}: need {required}, available {available}")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print(f"'{recipe_name}' can be prepared! ({num_servings} serving(s))")
        print("=" * 50)

    input("\nPress Enter to return to menu...")

# ==================== Equipment Issues ====================

def report_equipment_issue():
    """Report a new issue for equipment."""
    name = input_non_empty("Enter equipment name: ")
    issue = input_non_empty("Describe issue: ")
    equipment_data[name] = issue
    save_data(EQUIPMENT_FILE, equipment_data)
    print(f"Issue for '{name}' recorded!")
    input("\nPress Enter to return to menu...")

# ==================== Menus ====================

def manage_recipes():
    """Main loop for managing recipes."""
    while True:
        print("\nManage Recipes:")
        print("1. View Recipes")
        print("2. Add Recipe")
        print("3. Update Recipe")
        print("4. Delete Recipe")
        print("5. Return to Chef Menu")
        choice = input("Choose (1–5): ").strip()
        if choice == "1":
            view_recipes()
        elif choice == "2":
            add_recipe()
        elif choice == "3":
            update_recipe()
        elif choice == "4":
            delete_recipe()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

def chef_menu():
    """Main Chef Menu with a loop."""
    while True:
        print("\nChef Menu:")
        print("1. Manage Recipes")
        print("2. Check Inventory")
        print("3. Report Equipment Issue")
        print("4. Exit")
        choice = input("Choose (1–4): ").strip()
        if choice == "1":
            manage_recipes()
        elif choice == "2":
            check_inventory()
        elif choice == "3":
            report_equipment_issue()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

# ==================== Main ====================

if __name__ == "__main__":
    chef_menu()


