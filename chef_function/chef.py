# chef_module.py
# Restaurant Ordering and Management System - Chef Module
# Author: [Your Name]
# Date: [Current Date]

import os
import json
from datetime import datetime

# Symbolic Constants
RECIPES_FILE = "recipes.txt"
EQUIPMENT_FILE = "equipment.txt"
INGREDIENTS_FILE = "ingredients.txt"
CHEF_CREDENTIALS_FILE = "chef_credentials.txt"

class ChefModule:
    """
    Chef Module for Restaurant Management System
    Handles recipe management, inventory checking, and equipment management
    """
    
    def __init__(self):
        """Initialize Chef Module and create necessary files if they don't exist"""
        self.initialize_files()
    
    def initialize_files(self):
        """Create initial data files if they don't exist"""
        try:
            # Initialize recipes file
            if not os.path.exists(RECIPES_FILE):
                with open(RECIPES_FILE, 'w') as f:
                    f.write("")
            
            # Initialize equipment file with default equipment
            if not os.path.exists(EQUIPMENT_FILE):
                default_equipment = [
                    {"id": "EQ001", "name": "Oven", "status": "Working", "last_maintenance": "2024-01-15", "notes": ""},
                    {"id": "EQ002", "name": "Refrigerator", "status": "Working", "last_maintenance": "2024-01-10", "notes": ""},
                    {"id": "EQ003", "name": "Stove", "status": "Working", "last_maintenance": "2024-01-20", "notes": ""},
                    {"id": "EQ004", "name": "Mixer", "status": "Working", "last_maintenance": "2024-01-12", "notes": ""}
                ]
                with open(EQUIPMENT_FILE, 'w') as f:
                    for equipment in default_equipment:
                        f.write(f"{equipment['id']}|{equipment['name']}|{equipment['status']}|{equipment['last_maintenance']}|{equipment['notes']}\n")
            
            # Initialize ingredients file with sample ingredients
            if not os.path.exists(INGREDIENTS_FILE):
                default_ingredients = [
                    {"name": "Chicken", "quantity": 50, "unit": "kg", "min_threshold": 10},
                    {"name": "Rice", "quantity": 100, "unit": "kg", "min_threshold": 20},
                    {"name": "Tomatoes", "quantity": 30, "unit": "kg", "min_threshold": 5},
                    {"name": "Onions", "quantity": 25, "unit": "kg", "min_threshold": 5},
                    {"name": "Oil", "quantity": 20, "unit": "liters", "min_threshold": 5}
                ]
                with open(INGREDIENTS_FILE, 'w') as f:
                    for ingredient in default_ingredients:
                        f.write(f"{ingredient['name']}|{ingredient['quantity']}|{ingredient['unit']}|{ingredient['min_threshold']}\n")
            
            # Initialize chef credentials - REMOVED (Manager handles authentication)
            # Authentication will be handled by Manager module
                    
        except Exception as e:
            print(f"Error initializing files: {e}")
    
    def chef_login(self):
        """Chef login functionality"""
        print("\n" + "="*50)
        print("           CHEF LOGIN")
        print("="*50)
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                username = input("Enter Username: ").strip()
                password = input("Enter Password: ").strip()
                
                if not username or not password:
                    print("Username and password cannot be empty!")
                    attempts += 1
                    continue
                
                # Validate credentials
                with open(CHEF_CREDENTIALS_FILE, 'r') as f:
                    for line in f:
                        if line.strip():
                            stored_username, stored_password, chef_name = line.strip().split('|')
                            if username == stored_username and password == stored_password:
                                self.current_chef = {"username": username, "name": chef_name}
                                print(f"\nWelcome, {chef_name}!")
                                return True
                
                print("Invalid credentials!")
                attempts += 1
                
            except FileNotFoundError:
                print("System error: Credentials file not found!")
                return False
            except Exception as e:
                print(f"Login error: {e}")
                attempts += 1
        
        print("Maximum login attempts exceeded!")
        return False
    
    def display_chef_menu(self):
        """Display main chef menu"""
        print("\n" + "="*50)
        print("           CHEF DASHBOARD")
        print("="*50)
        print("1. Recipe Management")
        print("2. Inventory Check")
        print("3. Equipment Management")
        print("4. Return to Main System")
        print("="*50)
    
    def get_valid_choice(self, min_val, max_val, prompt="Enter your choice: "):
        """Get valid menu choice from user"""
        while True:
            try:
                choice = int(input(prompt))
                if min_val <= choice <= max_val:
                    return choice
                else:
                    print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number!")
    
    # RECIPE MANAGEMENT FUNCTIONS
    def recipe_management_menu(self):
        """Recipe management submenu"""
        while True:
            print("\n" + "="*40)
            print("        RECIPE MANAGEMENT")
            print("="*40)
            print("1. View All Recipes")
            print("2. Add New Recipe")
            print("3. Update Recipe")
            print("4. Delete Recipe")
            print("5. Back to Main Menu")
            print("="*40)
            
            choice = self.get_valid_choice(1, 5)
            
            if choice == 1:
                self.view_all_recipes()
            elif choice == 2:
                self.add_recipe()
            elif choice == 3:
                self.update_recipe()
            elif choice == 4:
                self.delete_recipe()
            elif choice == 5:
                break
    
    def view_all_recipes(self):
        """Display all recipes"""
        try:
            print("\n" + "="*60)
            print("                    ALL RECIPES")
            print("="*60)
            
            with open(RECIPES_FILE, 'r') as f:
                recipes = f.readlines()
            
            if not recipes:
                print("No recipes found!")
                return
            
            for i, recipe_line in enumerate(recipes, 1):
                if recipe_line.strip():
                    recipe_data = recipe_line.strip().split('|')
                    recipe_id = recipe_data[0]
                    recipe_name = recipe_data[1]
                    ingredients = recipe_data[2]
                    instructions = recipe_data[3]
                    prep_time = recipe_data[4]
                    
                    print(f"\n{i}. Recipe ID: {recipe_id}")
                    print(f"   Name: {recipe_name}")
                    print(f"   Ingredients: {ingredients}")
                    print(f"   Instructions: {instructions}")
                    print(f"   Prep Time: {prep_time} minutes")
                    print("-" * 60)
                    
        except FileNotFoundError:
            print("No recipes file found!")
        except Exception as e:
            print(f"Error viewing recipes: {e}")
    
    def add_recipe(self):
        """Add new recipe"""
        try:
            print("\n" + "="*40)
            print("         ADD NEW RECIPE")
            print("="*40)
            
            # Generate recipe ID
            recipe_id = self.generate_recipe_id()
            
            # Get recipe details with validation
            recipe_name = self.get_valid_string("Enter recipe name: ")
            ingredients = self.get_valid_string("Enter ingredients (comma separated): ")
            instructions = self.get_valid_string("Enter cooking instructions: ")
            
            while True:
                try:
                    prep_time = int(input("Enter preparation time (minutes): "))
                    if prep_time > 0:
                        break
                    else:
                        print("Preparation time must be positive!")
                except ValueError:
                    print("Please enter a valid number!")
            
            # Save recipe
            with open(RECIPES_FILE, 'a') as f:
                f.write(f"{recipe_id}|{recipe_name}|{ingredients}|{instructions}|{prep_time}\n")
            
            print(f"\nRecipe '{recipe_name}' added successfully with ID: {recipe_id}")
            
        except Exception as e:
            print(f"Error adding recipe: {e}")
    
    def update_recipe(self):
        """Update existing recipe"""
        try:
            self.view_all_recipes()
            
            recipe_id = input("\nEnter Recipe ID to update: ").strip().upper()
            if not recipe_id:
                print("Recipe ID cannot be empty!")
                return
            
            # Read existing recipes
            recipes = []
            recipe_found = False
            
            with open(RECIPES_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        recipe_data = line.strip().split('|')
                        if recipe_data[0] == recipe_id:
                            recipe_found = True
                            print(f"\nCurrent Recipe Details:")
                            print(f"Name: {recipe_data[1]}")
                            print(f"Ingredients: {recipe_data[2]}")
                            print(f"Instructions: {recipe_data[3]}")
                            print(f"Prep Time: {recipe_data[4]} minutes")
                            
                            # Get updated details
                            print("\nEnter new details (press Enter to keep current):")
                            new_name = input(f"Recipe name ({recipe_data[1]}): ").strip()
                            new_ingredients = input(f"Ingredients ({recipe_data[2]}): ").strip()
                            new_instructions = input(f"Instructions ({recipe_data[3]}): ").strip()
                            new_prep_time = input(f"Prep time ({recipe_data[4]}): ").strip()
                            
                            # Use current values if no new input
                            if not new_name:
                                new_name = recipe_data[1]
                            if not new_ingredients:
                                new_ingredients = recipe_data[2]
                            if not new_instructions:
                                new_instructions = recipe_data[3]
                            if not new_prep_time:
                                new_prep_time = recipe_data[4]
                            else:
                                try:
                                    new_prep_time = str(int(new_prep_time))
                                except ValueError:
                                    print("Invalid prep time, keeping current value")
                                    new_prep_time = recipe_data[4]
                            
                            updated_recipe = f"{recipe_id}|{new_name}|{new_ingredients}|{new_instructions}|{new_prep_time}\n"
                            recipes.append(updated_recipe)
                        else:
                            recipes.append(line)
            
            if not recipe_found:
                print("Recipe not found!")
                return
            
            # Write updated recipes back to file
            with open(RECIPES_FILE, 'w') as f:
                f.writelines(recipes)
            
            print("Recipe updated successfully!")
            
        except FileNotFoundError:
            print("Recipes file not found!")
        except Exception as e:
            print(f"Error updating recipe: {e}")
    
    def delete_recipe(self):
        """Delete recipe"""
        try:
            self.view_all_recipes()
            
            recipe_id = input("\nEnter Recipe ID to delete: ").strip().upper()
            if not recipe_id:
                print("Recipe ID cannot be empty!")
                return
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete recipe {recipe_id}? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled!")
                return
            
            recipes = []
            recipe_found = False
            
            with open(RECIPES_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        recipe_data = line.strip().split('|')
                        if recipe_data[0] != recipe_id:
                            recipes.append(line)
                        else:
                            recipe_found = True
                            print(f"Deleted recipe: {recipe_data[1]}")
            
            if not recipe_found:
                print("Recipe not found!")
                return
            
            # Write remaining recipes back to file
            with open(RECIPES_FILE, 'w') as f:
                f.writelines(recipes)
            
            print("Recipe deleted successfully!")
            
        except FileNotFoundError:
            print("Recipes file not found!")
        except Exception as e:
            print(f"Error deleting recipe: {e}")
    
    def generate_recipe_id(self):
        """Generate unique recipe ID"""
        try:
            with open(RECIPES_FILE, 'r') as f:
                recipes = f.readlines()
            
            if not recipes:
                return "R001"
            
            # Find highest ID number
            max_id = 0
            for recipe in recipes:
                if recipe.strip():
                    recipe_id = recipe.split('|')[0]
                    if recipe_id.startswith('R') and len(recipe_id) == 4:
                        try:
                            id_num = int(recipe_id[1:])
                            max_id = max(max_id, id_num)
                        except ValueError:
                            continue
            
            return f"R{max_id + 1:03d}"
            
        except Exception:
            return "R001"
    
    # INVENTORY CHECK FUNCTIONS
    def inventory_check_menu(self):
        """Inventory check submenu"""
        while True:
            print("\n" + "="*40)
            print("         INVENTORY CHECK")
            print("="*40)
            print("1. View All Ingredients")
            print("2. Check Low Stock Items")
            print("3. Check Recipe Availability")
            print("4. Back to Main Menu")
            print("="*40)
            
            choice = self.get_valid_choice(1, 4)
            
            if choice == 1:
                self.view_all_ingredients()
            elif choice == 2:
                self.check_low_stock()
            elif choice == 3:
                self.check_recipe_availability()
            elif choice == 4:
                break
    
    def view_all_ingredients(self):
        """Display all ingredients inventory"""
        try:
            print("\n" + "="*70)
            print("                    INGREDIENTS INVENTORY")
            print("="*70)
            print(f"{'Ingredient':<20} {'Quantity':<10} {'Unit':<10} {'Min Threshold':<15} {'Status':<10}")
            print("-" * 70)
            
            with open(INGREDIENTS_FILE, 'r') as f:
                ingredients = f.readlines()
            
            if not ingredients:
                print("No ingredients found!")
                return
            
            for ingredient_line in ingredients:
                if ingredient_line.strip():
                    data = ingredient_line.strip().split('|')
                    name = data[0]
                    quantity = int(data[1])
                    unit = data[2]
                    min_threshold = int(data[3])
                    
                    status = "LOW STOCK" if quantity <= min_threshold else "OK"
                    print(f"{name:<20} {quantity:<10} {unit:<10} {min_threshold:<15} {status:<10}")
                    
        except FileNotFoundError:
            print("Ingredients file not found!")
        except Exception as e:
            print(f"Error viewing ingredients: {e}")
    
    def check_low_stock(self):
        """Check and display low stock items"""
        try:
            print("\n" + "="*50)
            print("              LOW STOCK ALERT")
            print("="*50)
            
            low_stock_items = []
            
            with open(INGREDIENTS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = line.strip().split('|')
                        name = data[0]
                        quantity = int(data[1])
                        unit = data[2]
                        min_threshold = int(data[3])
                        
                        if quantity <= min_threshold:
                            low_stock_items.append({
                                'name': name,
                                'quantity': quantity,
                                'unit': unit,
                                'threshold': min_threshold
                            })
            
            if not low_stock_items:
                print("✓ All ingredients are well stocked!")
            else:
                print(f"{'Ingredient':<20} {'Current':<10} {'Min Required':<15}")
                print("-" * 45)
                for item in low_stock_items:
                    print(f"{item['name']:<20} {item['quantity']} {item['unit']:<9} {item['threshold']} {item['unit']}")
                
                print(f"\n⚠️  {len(low_stock_items)} item(s) need restocking!")
                
        except FileNotFoundError:
            print("Ingredients file not found!")
        except Exception as e:
            print(f"Error checking low stock: {e}")
    
    def check_recipe_availability(self):
        """Check if recipe can be prepared with current inventory"""
        try:
            self.view_all_recipes()
            
            recipe_id = input("\nEnter Recipe ID to check availability: ").strip().upper()
            if not recipe_id:
                print("Recipe ID cannot be empty!")
                return
            
            # Find recipe
            recipe_found = False
            recipe_ingredients = ""
            recipe_name = ""
            
            with open(RECIPES_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = line.strip().split('|')
                        if data[0] == recipe_id:
                            recipe_found = True
                            recipe_name = data[1]
                            recipe_ingredients = data[2]
                            break
            
            if not recipe_found:
                print("Recipe not found!")
                return
            
            print(f"\nChecking availability for: {recipe_name}")
            print(f"Required ingredients: {recipe_ingredients}")
            print("\nAvailability Status:")
            print("-" * 40)
            
            # Load current inventory
            inventory = {}
            with open(INGREDIENTS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = line.strip().split('|')
                        inventory[data[0].lower()] = int(data[1])
            
            # Check each ingredient (simplified check - assumes ingredient names match)
            ingredients_list = [ing.strip().lower() for ing in recipe_ingredients.split(',')]
            can_prepare = True
            
            for ingredient in ingredients_list:
                if ingredient in inventory:
                    if inventory[ingredient] > 0:
                        print(f"✓ {ingredient.title()}: Available ({inventory[ingredient]} units)")
                    else:
                        print(f"✗ {ingredient.title()}: Out of stock")
                        can_prepare = False
                else:
                    print(f"? {ingredient.title()}: Not in inventory system")
                    can_prepare = False
            
            print("\n" + "="*40)
            if can_prepare:
                print("✅ Recipe can be prepared!")
            else:
                print("❌ Recipe cannot be prepared - missing ingredients!")
            
        except FileNotFoundError:
            print("Required files not found!")
        except Exception as e:
            print(f"Error checking recipe availability: {e}")
    
    # EQUIPMENT MANAGEMENT FUNCTIONS
    def equipment_management_menu(self):
        """Equipment management submenu"""
        while True:
            print("\n" + "="*40)
            print("      EQUIPMENT MANAGEMENT")
            print("="*40)
            print("1. View All Equipment")
            print("2. Report Equipment Issue")
            print("3. Update Equipment Status")
            print("4. Back to Main Menu")
            print("="*40)
            
            choice = self.get_valid_choice(1, 4)
            
            if choice == 1:
                self.view_all_equipment()
            elif choice == 2:
                self.report_equipment_issue()
            elif choice == 3:
                self.update_equipment_status()
            elif choice == 4:
                break
    
    def view_all_equipment(self):
        """Display all equipment status"""
        try:
            print("\n" + "="*80)
            print("                           EQUIPMENT STATUS")
            print("="*80)
            print(f"{'ID':<8} {'Equipment':<15} {'Status':<12} {'Last Maintenance':<17} {'Notes':<20}")
            print("-" * 80)
            
            with open(EQUIPMENT_FILE, 'r') as f:
                equipment_list = f.readlines()
            
            if not equipment_list:
                print("No equipment found!")
                return
            
            for equipment_line in equipment_list:
                if equipment_line.strip():
                    data = equipment_line.strip().split('|')
                    eq_id = data[0]
                    name = data[1]
                    status = data[2]
                    maintenance = data[3]
                    notes = data[4] if len(data) > 4 else ""
                    
                    # Color coding for status
                    if status == "Broken":
                        status_display = f"🔴 {status}"
                    elif status == "Maintenance":
                        status_display = f"🟡 {status}"
                    else:
                        status_display = f"🟢 {status}"
                    
                    print(f"{eq_id:<8} {name:<15} {status_display:<12} {maintenance:<17} {notes:<20}")
                    
        except FileNotFoundError:
            print("Equipment file not found!")
        except Exception as e:
            print(f"Error viewing equipment: {e}")
    
    def report_equipment_issue(self):
        """Report equipment malfunction or maintenance need"""
        try:
            self.view_all_equipment()
            
            eq_id = input("\nEnter Equipment ID to report issue: ").strip().upper()
            if not eq_id:
                print("Equipment ID cannot be empty!")
                return
            
            # Read current equipment data
            equipment_list = []
            equipment_found = False
            
            with open(EQUIPMENT_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = line.strip().split('|')
                        if data[0] == eq_id:
                            equipment_found = True
                            print(f"\nReporting issue for: {data[1]}")
                            
                            # Get issue details
                            print("\nIssue Type:")
                            print("1. Malfunction/Broken")
                            print("2. Maintenance Required")
                            print("3. Other")
                            
                            issue_choice = self.get_valid_choice(1, 3, "Select issue type: ")
                            
                            if issue_choice == 1:
                                new_status = "Broken"
                            elif issue_choice == 2:
                                new_status = "Maintenance"
                            else:
                                new_status = "Issue Reported"
                            
                            issue_notes = input("Enter issue description: ").strip()
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            
                            # Update equipment record
                            updated_line = f"{data[0]}|{data[1]}|{new_status}|{data[3]}|{issue_notes}\n"
                            equipment_list.append(updated_line)
                        else:
                            equipment_list.append(line)
            
            if not equipment_found:
                print("Equipment not found!")
                return
            
            # Write updated equipment data
            with open(EQUIPMENT_FILE, 'w') as f:
                f.writelines(equipment_list)
            
            print(f"Issue reported successfully for Equipment {eq_id}!")
            print("Manager will be notified of this issue.")
            
        except FileNotFoundError:
            print("Equipment file not found!")
        except Exception as e:
            print(f"Error reporting equipment issue: {e}")
    
    def update_equipment_status(self):
        """Update equipment status (for resolved issues)"""
        try:
            self.view_all_equipment()
            
            eq_id = input("\nEnter Equipment ID to update: ").strip().upper()
            if not eq_id:
                print("Equipment ID cannot be empty!")
                return
            
            equipment_list = []
            equipment_found = False
            
            with open(EQUIPMENT_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        data = line.strip().split('|')
                        if data[0] == eq_id:
                            equipment_found = True
                            print(f"\nCurrent status for {data[1]}: {data[2]}")
                            
                            print("\nNew Status:")
                            print("1. Working")
                            print("2. Maintenance")
                            print("3. Broken")
                            
                            status_choice = self.get_valid_choice(1, 3, "Select new status: ")
                            
                            if status_choice == 1:
                                new_status = "Working"
                            elif status_choice == 2:
                                new_status = "Maintenance"
                            else:
                                new_status = "Broken"
                            
                            notes = input("Enter notes (optional): ").strip()
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            
                            # Update maintenance date if status is working
                            maintenance_date = current_date if new_status == "Working" else data[3]
                            
                            updated_line = f"{data[0]}|{data[1]}|{new_status}|{maintenance_date}|{notes}\n"
                            equipment_list.append(updated_line)
                        else:
                            equipment_list.append(line)
            
            if not equipment_found:
                print("Equipment not found!")
                return
            
            # Write updated equipment data
            with open(EQUIPMENT_FILE, 'w') as f:
                f.writelines(equipment_list)
            
            print("Equipment status updated successfully!")
            
        except FileNotFoundError:
            print("Equipment file not found!")
        except Exception as e:
            print(f"Error updating equipment status: {e}")
    
    def get_valid_string(self, prompt):
        """Get valid non-empty string input"""
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Input cannot be empty! Please try again.")
    
    def run_chef_system(self):
        """Main chef system loop"""
        print("\n" + "="*60)
        print("    RESTAURANT MANAGEMENT SYSTEM - CHEF MODULE")
        print("="*60)
        
        # Main menu loop (authentication handled by Manager)
        while True:
            try:
                self.display_chef_menu()
                choice = self.get_valid_choice(1, 4)
                
                if choice == 1:
                    self.recipe_management_menu()
                elif choice == 2:
                    self.inventory_check_menu()
                elif choice == 3:
                    self.equipment_management_menu()
                elif choice == 4:
                    print("\nReturning to main system...")
                    break
                    
            except KeyboardInterrupt:
                print("\n\nSystem interrupted by user.")
                break
            except Exception as e:
                print(f"System error: {e}")
                print("Please try again.")

def main():
    """Main function to run chef module"""
    chef_system = ChefModule()
    chef_system.run_chef_system()

# Integration point for main system
def get_chef_module():
    """Return chef module instance for integration with main system"""
    return ChefModule()

if __name__ == "__main__":
    main()