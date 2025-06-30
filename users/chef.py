import json
import os
import sys
import textwrap

# import active orders function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.order_management import chef_view_active_orders

# Ensure the parent directory is in the path for module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Constant file names

DATA_DIR = os.path.join(project_root, "data")
RECIPE_FILE = os.path.join(DATA_DIR, "recipe.txt")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.txt")
EQUIPMENT_FILE = os.path.join(DATA_DIR, "equipment.txt")

# Utility Functions    

def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_data(file_path, data_dict):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data_dict, file, indent=4)

def input_non_empty(prompt):
    value = ""
    while not value:
        value = input(prompt).strip()
        if not value:
            print("Input cannot be empty!")
    return value

def input_positive_int(prompt):
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Input cannot be empty!")
            continue
        try:
            value = int(user_input)
            if value > 0:
                return value
            else:
                print("Please enter a positive number!")
        except ValueError:
            print("Please enter a valid number!")

def load_all_data():
    recipe_data = load_data(RECIPE_FILE)
    inventory_data = load_data(INVENTORY_FILE)
    equipment_data = load_data(EQUIPMENT_FILE)
    inventory_data = {k.lower(): v for k, v in inventory_data.items()}
    return recipe_data, inventory_data, equipment_data

def save_all_data(recipe_data, inventory_data, equipment_data):
    save_data(RECIPE_FILE, recipe_data)
    save_data(INVENTORY_FILE, inventory_data)
    save_data(EQUIPMENT_FILE, equipment_data)

# Recipe Functions 

def view_recipe(recipe_data):
    print("\n" + "-" * 80)
    print(f"{'AVAILABLE RECIPES':^80}")
    print("-" * 80)

    if recipe_data:
        header = f"{'No.':<4} {'Recipe Name':<20} {'Ingredients'}"
        print(header)
        print("-" * 80)

        for i, (name, ingredients) in enumerate(recipe_data.items(), 1):
            ing_text = ", ".join(ingredients)
            wrapped_lines = textwrap.wrap(ing_text, width=52) or [""]

            print(f"{i:<4} {name:<20} {wrapped_lines[0]}")
            for extra_line in wrapped_lines[1:]:
                print(f"{'':<4} {'':<20} {extra_line}")
    else:
        print("No recipe found.".center(80))

    print("-" * 80)
    input("\nPress Enter to return to menu...")
    return recipe_data

def add_recipe(recipe_data):
    recipe_name = input_non_empty("Enter recipe name: ")
    ingredients = input_non_empty("Enter ingredients (comma separated): ").split(",")
    recipe_data[recipe_name] = [i.strip().lower() for i in ingredients]
    print(f"Recipe '{recipe_name}' added!")
    input("\nPress Enter to return to menu...")
    return recipe_data

def update_recipe(recipe_data):
    if not recipe_data:
        print("No recipes available to update.")
        input("\nPress Enter to return to menu...")
        return recipe_data

    print("\nSelect a recipe to update:")
    for i, name in enumerate(recipe_data.keys(), 1):
        print(f"{i}. {name}")

    while True:
        choice = input_positive_int("\nEnter recipe number to update: ")
        if 1 <= choice <= len(recipe_data):
            break
        print("Invalid choice. Please try again.")

    recipe_name = list(recipe_data.keys())[choice-1]
    new_ingredients = input_non_empty(f"Enter new ingredients for '{recipe_name}': ").split(",")
    recipe_data[recipe_name] = [i.strip().lower() for i in new_ingredients] # Remove empty strings and convert ingredients to lowercase
    print(f"Updated recipe '{recipe_name}'.")
    input("\nPress Enter to return to menu...")
    return recipe_data

def delete_recipe(recipe_data):
    if not recipe_data:
        print("No recipes available to delete.")
        input("\nPress Enter to return to menu...")
        return recipe_data

    print("\nSelect a recipe to delete:")
    for i, name in enumerate(recipe_data.keys(), 1):
        print(f"{i}. {name}")

    while True:
        choice = input_positive_int("\nEnter recipe number to delete: ")
        if 1 <= choice <= len(recipe_data):
            break
        print("Invalid choice. Please try again.")

    recipe_name = list(recipe_data.keys())[choice-1]
    del recipe_data[recipe_name]
    print(f"Deleted recipe '{recipe_name}'.")
    input("\nPress Enter to return to menu...")
    return recipe_data

# Inventory Check 

def check_inventory(recipe_data, inventory_data):
    if not recipe_data:
        print("No recipes available to check.")
        input("\nPress Enter to return to menu...")
        return recipe_data, inventory_data

    print("\nSelect a recipe to check availability:")
    for i, name in enumerate(recipe_data.keys(), 1):
        print(f"{i}. {name}")

    choice = input_positive_int("\nEnter recipe number to check: ")
    if choice < 1 or choice > len(recipe_data):
        print("Invalid choice!")
        input("\nPress Enter to return to menu...")
        return recipe_data, inventory_data

    recipe_name = list(recipe_data.keys())[choice-1]
    num_servings = input_positive_int(f"How many servings of '{recipe_name}' do you want to check? ")

    required_counts = {}
    for ing in recipe_data[recipe_name]:
        required_counts[ing.lower()] = required_counts.get(ing.lower(), 0) + num_servings

    not_enough = []
    for ing, required_qty in required_counts.items():
        available_qty = inventory_data.get(ing.lower(), 0)
        if available_qty < required_qty:
            missing_qty = required_qty - available_qty
            not_enough.append((ing, required_qty, available_qty, missing_qty))

    if not not_enough:
        print("\n" + "=" * 50)
        print(f"'{recipe_name}' can be prepared! ({num_servings} serving(s))")
        print("=" * 50)
        print("All ingredients are available:")
        for ing, required_qty in required_counts.items():
            available_qty = inventory_data.get(ing.lower(), 0)
            print(f" • {ing}: need {required_qty}, available {available_qty}")
        print("=" * 50)

        for ing, required_qty in required_counts.items():
            inventory_data[ing.lower()] -= required_qty
        print("Inventory updated.")
    else:
        print("\n" + "=" * 50)
        print(f"Sorry! Cannot prepare {num_servings} serving(s) of '{recipe_name}'.")
        print("=" * 50)
        print("Insufficient ingredients:")
        for item, required, available, missing in not_enough:
            print(f" • {item}: need {required}, available {available}, missing {missing}")
        print("=" * 50)

    input("\nPress Enter to return to menu...")
    return recipe_data, inventory_data

# Equipment Issues 

def report_equipment_issue(equipment_data):
    name = input_non_empty("Enter equipment name: ")
    issue = input_non_empty("Describe issue: ")
    equipment_data[name] = issue
    print(f"Issue for '{name}' recorded!")
    input("\nPress Enter to return to menu...")
    return equipment_data

# Manage recipe functions 

def manage_recipes(recipe_data):
    while True:
        print("\nManage Recipes:")
        print("1. View Recipes")
        print("2. Add Recipe")
        print("3. Update Recipe")
        print("4. Delete Recipe")
        print("5. Return to Chef Menu")
        choice = input("Choose (1–5): ").strip()
        if choice == "1":
            recipe_data = view_recipe(recipe_data)
        elif choice == "2":
            recipe_data = add_recipe(recipe_data)
        elif choice == "3":
            recipe_data = update_recipe(recipe_data)
        elif choice == "4":
            recipe_data = delete_recipe(recipe_data)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")
    return recipe_data

# Chef Menu

def chef_menu():
    recipe_data = load_data(RECIPE_FILE)
    inventory_data = load_data(INVENTORY_FILE)
    equipment_data = load_data(EQUIPMENT_FILE)
    while True:
        print("\nChef Menu:")
        print("1. Manage Recipes")
        print("2. Check Inventory")
        print("3. Report Equipment Issue")
        print("4. View Active Orders")
        print("5. Exit")
        choice = input("Choose (1–5): ").strip()
        if choice == "1":
            recipe_data = manage_recipes(recipe_data)
        elif choice == "2":
            recipe_data, inventory_data = check_inventory(recipe_data, inventory_data)
        elif choice == "3":
            equipment_data = report_equipment_issue(equipment_data)
        elif choice == "4":
            chef_view_active_orders()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")
    return recipe_data, inventory_data, equipment_data

# Main

if __name__ == "__main__":
    recipe_data, inventory_data, equipment_data = load_all_data()
    recipe_data, inventory_data, equipment_data = chef_menu(
        recipe_data, inventory_data, equipment_data
    )
    save_all_data(recipe_data, inventory_data, equipment_data)


