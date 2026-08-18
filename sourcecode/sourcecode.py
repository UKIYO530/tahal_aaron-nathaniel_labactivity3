import sqlite3

class Product:
    """Represents a single product in memory (Data Transfer Object)."""
    
    def __init__(self, product_id: str, name: str, price: float, stock_quantity: int = 0):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity

    def get_total_value(self) -> float:
        """Calculates the total financial value of this specific stock."""
        return self.stock_quantity * self.price

    def __str__(self):
        return f"[{self.product_id}] {self.name} | Stock: {self.stock_quantity} | Price: ${self.price:.2f}"


class InventoryDatabaseManager:
    """Manages the SQL Database connection and operations for Products."""
    
    def __init__(self, db_name="inventory.db"):
        # Uses a file-based database so data is saved permanently.
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._initialize_schema()

    def _initialize_schema(self):
        """Creates the SQL table if it doesn't already exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def register_product(self, product: Product):
        """Translates a Product object into an SQL INSERT statement."""
        try:
            self.cursor.execute('''
                INSERT INTO products (product_id, name, price, stock_quantity)
                VALUES (?, ?, ?, ?)
            ''', (product.product_id, product.name, product.price, product.stock_quantity))
            self.conn.commit()
            print(f"✅ SUCCESS: '{product.name}' added to the database.")
        except sqlite3.IntegrityError:
            print(f"❌ Error: Product ID '{product.product_id}' already exists.")

    def update_stock(self, product_id: str, new_quantity: int):
        """Updates the stock quantity of an existing product."""
        self.cursor.execute('''
            UPDATE products 
            SET stock_quantity = ? 
            WHERE product_id = ?
        ''', (new_quantity, product_id))
        self.conn.commit()
        
        if self.cursor.rowcount > 0:
            print(f"✅ SUCCESS: Product '{product_id}' stock updated to {new_quantity}.")
        else:
            print(f"❌ Error: Product '{product_id}' not found.")

    def delete_product(self, product_id: str):
        """Removes a product from the database."""
        self.cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
        self.conn.commit()
        
        if self.cursor.rowcount > 0:
            print(f"✅ SUCCESS: Product '{product_id}' has been deleted.")
        else:
            print(f"❌ Error: Product '{product_id}' not found.")

    def print_inventory_report(self):
        """Fetches all rows, converts to objects, and prints a report."""
        print("\n=== SQL DATABASE INVENTORY REPORT ===")
        self.cursor.execute('SELECT * FROM products')
        rows = self.cursor.fetchall()
        
        if not rows:
            print("The inventory is currently empty.")
            print("-" * 36)
            return

        total_system_value = 0.0
        for row in rows:
            product = Product(*row)
            print(product)
            total_system_value += product.get_total_value()
            
        print("-" * 36)
        print(f"Total Database Value: ${total_system_value:.2f}")

    def __del__(self):
        """Ensures the database connection is closed when the object is destroyed."""
        self.conn.close()


# ==========================================
# INTERACTIVE EXECUTION SCRIPT
# ==========================================
def main():
    # Instantiate the DB Manager
    db_system = InventoryDatabaseManager()
    
    print("Welcome to the Interactive SQL Inventory Manager!")

    while True:
        print("\n" + "="*30)
        print("1. Add a New Product")
        print("2. View Full Inventory Report")
        print("3. Update Product Stock")
        print("4. Delete a Product")
        print("5. Exit System")
        print("="*30)
        
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            print("\n--- Add New Product ---")
            p_id = input("Enter Product ID (e.g., T-001): ").strip()
            
            if not p_id:
                print("❌ Error: Product ID cannot be empty.")
                continue
                
            p_name = input("Enter Product Name: ").strip()
            
            try:
                p_price = float(input("Enter Price (e.g., 19.99): "))
                p_stock = int(input("Enter Initial Stock Quantity: "))
                
                if p_price < 0 or p_stock < 0:
                    print("❌ Error: Price and stock cannot be negative.")
                    continue
                    
            except ValueError:
                print("❌ Error: Invalid input. Please enter numbers for price and stock.")
                continue
            
            new_product = Product(product_id=p_id, name=p_name, price=p_price, stock_quantity=p_stock)
            db_system.register_product(new_product)

        elif choice == '2':
            db_system.print_inventory_report()

        elif choice == '3':
            print("\n--- Update Product Stock ---")
            p_id = input("Enter Product ID to update: ").strip()
            try:
                new_stock = int(input("Enter new stock quantity: "))
                if new_stock < 0:
                    print("❌ Error: Stock cannot be negative.")
                    continue
                db_system.update_stock(p_id, new_stock)
            except ValueError:
                print("❌ Error: Please enter a valid number for stock.")

        elif choice == '4':
            print("\n--- Delete Product ---")
            p_id = input("Enter Product ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete '{p_id}'? (y/n): ").strip().lower()
            if confirm == 'y':
                db_system.delete_product(p_id)
            else:
                print("Deletion cancelled.")

        elif choice == '5':
            print("Exiting the Inventory Manager. Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()