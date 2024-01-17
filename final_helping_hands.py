import sqlite3
import re
# Create SQLite database and establish connection
conn = sqlite3.connect('hh.db')
cursor = conn.cursor()

# Create Employee table with auto-incrementing ID
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Employee (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        preferred_role TEXT,
        gender INTEGER
    )
''')

# Create AssistanceRequest table with auto-incrementing ID and foreign key reference
cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssistanceRequest (
        req_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER,
        gender INTEGER,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (emp_id) REFERENCES Employee(employee_id)
        FOREIGN KEY (gender) REFERENCES Employee(gender)
    )
''')

# Create Shop table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Shop (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        available_positions INTEGER,
        gender INTEGER,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT 
    )
''')

# Class definition for Employee
class Employee:
    def __init__(self, name, contact, preferred_role=None, gender=None):
        self.name = name
        self.contact = contact
        self.preferred_role = preferred_role
        self.gender = gender

    def save_to_db(self):
        cursor.execute('''
            INSERT INTO Employee (name, contact, preferred_role, gender)
            VALUES (?, ?, ?, ?)
        ''', (self.name, self.contact, self.preferred_role, self.gender))
        conn.commit()
        return cursor.lastrowid  # Return the last inserted row ID (employee_id)

# Function to offer assistance
def offer_assistance(emp_id, gender, date, time, status='Pending'):
    cursor.execute('''
        INSERT INTO AssistanceRequest (emp_id, gender, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (emp_id, gender, date, time, status))
    conn.commit()
    return cursor.lastrowid  # Return the last inserted row ID (req_id)

# Function to view assistance requests for a user
def view_assistance(emp_id):
    cursor.execute('SELECT * FROM AssistanceRequest WHERE emp_id=?', (emp_id,))
    return cursor.fetchall()

# Function to modify details of an assistance request
def modify_assistance(req_id, date, time):
    cursor.execute('''
        UPDATE AssistanceRequest
        SET date=?, time=?
        WHERE req_id=?
    ''', (date, time, req_id))
    conn.commit()

# Function to cancel an assistance request
def cancel_assistance(req_id):
    cursor.execute('DELETE FROM AssistanceRequest WHERE req_id=?', (req_id,))
    conn.commit()

# Function to view all assistance requests for an admin
def view_all_assistance():
    cursor.execute('SELECT * FROM AssistanceRequest')
    return cursor.fetchall()

# Function to create a shop entry
def create_shop(name, available_positions, gender, date, time):
    cursor.execute('''
        INSERT INTO Shop (name, available_positions, gender, date, time)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, available_positions, gender, date, time))
    conn.commit()

def validate_contact(contact):
    # Validate contact using a simple regex
    contact_pattern = re.compile(r'^\d{10}$')
    return bool(contact_pattern.match(contact))

def grant_assistance():
    try:
        cursor.execute('''
            UPDATE AssistanceRequest
            SET status="Granted"
            WHERE status="Pending" AND EXISTS (
                SELECT *
                FROM Shop
                WHERE
                    Shop.gender = AssistanceRequest.gender
                    AND Shop.date = AssistanceRequest.date
                    AND Shop.time >= AssistanceRequest.time
            )
        ''')
        conn.commit()

        cursor.execute('''
            UPDATE Shop
            SET available_positions = available_positions - 1
            WHERE name IN (
                SELECT Shop.name
                FROM Shop
                JOIN AssistanceRequest ON Shop.gender = AssistanceRequest.gender
                    AND Shop.date = AssistanceRequest.date
                    AND Shop.time >= AssistanceRequest.time
                WHERE AssistanceRequest.status = "Granted"
            )
        ''')
        conn.commit()

        print("Assistance requests granted successfully! Available positions updated.")

    except sqlite3.Error as e:
        print(f"Error granting assistance: {e}") 
# Interactive front-end functions
def view_all_shop():
    cursor.execute('SELECT * FROM shop')
    return cursor.fetchall()
def print_user_menu():
    print("\n===== User Menu =====")
    print("1. Offer Assistance")
    print("2. View My Assistance Requests")
    print("3. Modify Assistance Request")
    print("4. Cancel Assistance Request")
    print("5. Exit")

def print_admin_menu():
    print("\n===== Admin Menu =====")
    print("1. View All Assistance Requests")
    print("2. Grant Assistance")
    print("3. Create Shop Entry")
    print("4.view shop")
    print("5. Exit")

def main():
    while True:
        role = input("Choose your role (user/admin): ").lower()

        if role == 'user':
            print_user_menu()
            choice = input("Enter your choice (1-5): ")

            if choice == '1':
                name = input("Enter your name: ")
                contact = input("Enter your contact information: ")
                preferred_role = input("Enter your preferred role: ")
                gender = input("Enter your gender: ")
                date = input("Enter date: ")
                time = input("Enter time: ")

                new_employee = Employee(name, contact, preferred_role, gender)
                emp_id = new_employee.save_to_db()

                req_id = offer_assistance(emp_id, gender, date, time)
                print(f"Assistance offered successfully! Your Employee ID: {emp_id}, Request ID: {req_id}")

            elif choice == '2':
                emp_id = int(input("Enter your Employee ID: "))
                requests = view_assistance(emp_id)
                print("Your Assistance Requests:")
                for request in requests:
                    print(request)

            elif choice == '3':
                req_id = int(input("Enter the ID of the request to modify: "))
                date = input("Enter new date: ")
                time = input("Enter new time: ")
                modify_assistance(req_id, date, time)
                print("Assistance request modified successfully!")

            elif choice == '4':
                req_id = int(input("Enter the ID of the request to cancel: "))
                cancel_assistance(req_id)
                print("Assistance request canceled successfully!")

            elif choice == '5':
                print("Exiting User Menu. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

        elif role == 'admin':
            print_admin_menu()
            admin_choice = input("Enter your choice (1-5): ")

            if admin_choice == '1':
                all_requests = view_all_assistance()
                print("All Assistance Requests:")
                for request in all_requests:
                    print(request)

            elif admin_choice == '2':
                grant_assistance()
                
            elif admin_choice == '3':
                name = input("Enter shop name: ")
                available_positions = int(input("Enter available positions: "))
                gender = input("Enter gender: ")
                date = input("Enter date: ")
                time = input("Enter time: ")
                create_shop(name, available_positions, gender, date, time)
                print("Shop entry created successfully!")

            elif admin_choice=='4':
                requests = view_all_shop()
                print("Your Shop Requests:")
                for request in requests:
                    print(request)
                break
            elif admin_choice == '5':
                print("Exiting Admin Menu. Goodbye!")
                break


            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

        else:
            print("Invalid role. Please enter 'user' or 'admin.")

if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
