import sqlite3

def init_db():
    """Create tables if they don't already exist."""
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()

            # Create newsletter table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS newsletter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL
                )
            ''')

            # Create incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'Pending'
                )
            ''')

            # Create contact table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            ''')

            # Create admin table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            conn.commit()
            print("Tables created successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

def query_table(table_name):
    """Query and print all data from a table."""
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if rows:
                print(f"\nData from {table_name}:")
                for row in rows:
                    print(row)
            else:
                print(f"No data found in {table_name}.")
    except Exception as e:
        print(f"Error querying {table_name}: {e}")

def add_admin(username, password):
    """Add an admin user to the database."""
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            print("Admin user added successfully!")
    except Exception as e:
        print(f"Error adding admin: {e}")

def main():
    """Main menu for database management."""
    while True:
        print("\nDatabase Management Menu:")
        print("1. Initialize Database")
        print("2. View Newsletter Subscriptions")
        print("3. View Reported Incidents")
        print("4. View Contact Messages")
        print("5. Add Admin User")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            init_db()
        elif choice == '2':
            query_table("newsletter")
        elif choice == '3':
            query_table("incidents")
        elif choice == '4':
            query_table("contact")
        elif choice == '5':
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            add_admin(username, password)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
