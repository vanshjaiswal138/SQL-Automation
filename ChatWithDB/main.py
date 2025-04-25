import os
import mysql.connector
from dotenv import load_dotenv
from sql_translator import SQLTranslator

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "1231")
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database connection successful!")
            
            # Connect to default database if specified
            default_db = os.getenv("DB_NAME")
            if default_db:
                self.switch_database(default_db)
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def list_databases(self):
        """List all available databases"""
        try:
            self.cursor.execute("SHOW DATABASES")
            databases = [db['Database'] for db in self.cursor.fetchall()]
            return [db for db in databases if db not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
        except mysql.connector.Error as err:
            print(f"Error listing databases: {err}")
            return []

    def switch_database(self, database_name):
        """Switch to a different database"""
        try:
            # First check if the database exists
            self.cursor.execute("SHOW DATABASES")
            databases = [db['Database'] for db in self.cursor.fetchall()]
            
            if database_name not in databases:
                print(f"Database {database_name} does not exist")
                return False
                
            # Close existing connection
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
                
            # Create new connection with the selected database
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "1231"),
                database=database_name
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Verify the connection
            if not self.connection.is_connected():
                print("Failed to establish connection to the database")
                return False
                
            print(f"Switched to database: {database_name}")
            return True
        except mysql.connector.Error as err:
            print(f"Error switching to database {database_name}: {err}")
            return False

    def get_current_database(self):
        """Get the name of the current database"""
        try:
            self.cursor.execute("SELECT DATABASE()")
            return self.cursor.fetchone()['DATABASE()']
        except mysql.connector.Error as err:
            print(f"Error getting current database: {err}")
            return None

    def _create_database(self):
        """Create the database if it doesn't exist"""
        try:
            temp_conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "1234")
            )
            temp_cursor = temp_conn.cursor()
            db_name = os.getenv("DB_NAME", "project")
            temp_cursor.execute(f"CREATE DATABASE {db_name}")
            temp_cursor.close()
            temp_conn.close()
            
            # Reconnect with the new database
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "1234"),
                database=db_name
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Create initial tables
            self._create_initial_tables()
            print(f"Database '{db_name}' created successfully!")
        except mysql.connector.Error as err:
            print(f"Failed to create database: {err}")
            raise
    
    def _create_initial_tables(self):
        """Create initial tables in the database"""
        try:
            # Create USERS table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS USERS (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    NAME VARCHAR(100) NOT NULL
                )
            """)
            self.connection.commit()
            print("Initial tables created successfully!")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
            
    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                affected_rows = self.cursor.rowcount
                return f"{affected_rows} row(s) affected"
            else:
                result = self.cursor.fetchall()
                if not result:
                    return "No results found"
                return result
        except Exception as e:
            return f"Error executing query: {e}"
    
    def get_schema(self):
        """Get the database schema information"""
        schema = {}
        
        try:
            # Check if we have a valid connection
            if not self.connection or not self.connection.is_connected():
                print("Database connection is not active")
                return {}
                
            # Get current database
            current_db = self.get_current_database()
            if not current_db:
                print("No database selected")
                return {}
                
            # Get all tables
            self.cursor.execute("SHOW TABLES")
            tables = [table[f'Tables_in_{current_db}'] for table in self.cursor.fetchall()]
            
            if not tables:
                print(f"No tables found in database {current_db}")
                return {}
            
            # Get columns for each table
            for table in tables:
                try:
                    self.cursor.execute(f"DESCRIBE {table}")
                    columns = [row['Field'] for row in self.cursor.fetchall()]
                    schema[table.lower()] = columns
                except mysql.connector.Error as err:
                    print(f"Error getting columns for table {table}: {err}")
                    continue
                
            return schema
        except Exception as e:
            print(f"Error fetching schema: {str(e)}")
            return {}
            
    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
        print("Database connection closed")

def display_results(results):
    """Format and display query results"""
    if isinstance(results, str):
        print(results)
        return
        
    if not results:
        print("No results found")
        return
        
    # Print table headers
    headers = results[0].keys()
    header_row = " | ".join(str(h).upper() for h in headers)
    separator = "-" * len(header_row)
    
    print(separator)
    print(header_row)
    print(separator)
    
    # Print rows
    for row in results:
        print(" | ".join(str(row[h]) for h in headers))
    
    print(separator)
    print(f"Total rows: {len(results)}")

def main():
    db = Database()
    translator = SQLTranslator()
    
    while True:
        print("\n=== MySQL Automation Tool ===")
        print("1. Execute SQL query")
        print("2. Convert natural language to SQL")
        print("3. Add test data")
        print("4. Update schema information")
        print("5. Switch database")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            query = input("Enter SQL query: ")
            result = db.execute_query(query)
            display_results(result)
            
        elif choice == "2":
            nl_query = input("Enter your request in natural language: ")
            sql_query = translator.translate(nl_query)
            print("\nGenerated SQL Query:")
            print(sql_query)
            
            if sql_query.startswith("Error:"):
                print(sql_query)
                continue
                
            execute = input("\nDo you want to execute this query? (y/n): ")
            if execute.lower() == 'y':
                result = db.execute_query(sql_query)
                display_results(result)
                
                # Update schema after potential structure changes
                if sql_query.strip().upper().startswith("CREATE TABLE"):
                    schema = db.get_schema()
                    for table, columns in schema.items():
                        translator.update_schema(table, columns)
                    print("Schema updated after table creation.")
        
        elif choice == "3":
            print("Adding test data to USERS table...")
            db.execute_query("INSERT INTO USERS (name) VALUES ('Vansh')")
            db.execute_query("INSERT INTO USERS (name) VALUES ('Anuj')")
            db.execute_query("INSERT INTO USERS (name) VALUES ('Arihant')")
            print("Test data added successfully!")
            
        elif choice == "4":
            print("Updating schema information...")
            schema = db.get_schema()
            for table, columns in schema.items():
                translator.update_schema(table, columns)
            print("Current database schema:")
            for table, columns in translator.get_table_schema().items():
                print(f"Table: {table}")
                for column in columns:
                    print(f"  - {column}")
        
        elif choice == "5":
            print("\nAvailable databases:")
            databases = db.list_databases()
            for i, db_name in enumerate(databases, 1):
                print(f"{i}. {db_name}")
            
            try:
                db_choice = int(input("\nSelect database number: "))
                if 1 <= db_choice <= len(databases):
                    selected_db = databases[db_choice - 1]
                    if db.switch_database(selected_db):
                        # Update schema for the new database
                        schema = db.get_schema()
                        translator = SQLTranslator()  # Reset translator
                        for table, columns in schema.items():
                            translator.update_schema(table, columns)
                        print(f"Switched to database: {selected_db}")
                        print("Schema updated for the new database.")
                else:
                    print("Invalid database selection.")
            except ValueError:
                print("Please enter a valid number.")
            
        elif choice == "6":
            db.close()
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


# database.execute("show databases")

# for i in database:
#     print(i)


# database.execute("create database if not exists project")

# mysql.database = "project"


# Creating Tables


# database.execute("CREATE TABLE IF NOT EXISTS USERS (ID INT AUTO_INCREMENT PRIMARY KEY, NAME VARCHAR(100)) ")

# Checking for table if created or not

# database.execute("show tables")

# for i in database:
#     print(i)


# def insert_(name):
#     query = "INSERT INTO USERS (name) VALUES (%s)"
#     database.execute(query , (name,))
#     mysql.commit()
    
# insert_("Vansh")
# insert_("Anuj")
# insert_("Arihant")

    