import sqlite3
import csv
import random
import pandas as pd
import unittest
from test_extracted_data import TestExtractedData

# Database file name
DB_FILE = 'eastvantagedb.db'

# SQL file with CREATE statements
SQL_FILE = 'CREATE_DDL_STATEMENTS.sql'

class SalesDataProcessor:
    def __init__(self):
        self.conn = None

    def connect_to_database(self):
        """
        The function connects to a SQLite database and prints a message if the connection is successful.
        """
        try:
            self.conn = sqlite3.connect(DB_FILE)
            print(f"Connected to the '{DB_FILE}' database.")
        except Exception as e:
            err_message = f"Error while connecting to the database: {str(e)}"
            raise err_message

    def close_database_connection(self):
        """
        The function `close_database_connection` closes the database connection and prints a message.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_tables(self):
        """
        The function creates tables in a SQLite database, dropping existing tables if they exist.
        """
        try:
            cursor = self.conn.cursor()

            # Drop the tables if they exist
            cursor.executescript('''
                DROP TABLE IF EXISTS Orders;
                DROP TABLE IF EXISTS Sales;
                DROP TABLE IF EXISTS Items;
                DROP TABLE IF EXISTS Customer;
            ''')

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                cursor.execute('PRAGMA foreign_keys = ON;')  # Enable foreign key support
                with open(SQL_FILE, 'r') as f:
                    sql_statements = f.read()
                cursor.executescript(sql_statements)

            print(f"Tables created in the '{DB_FILE}' database successfully.")
        except Exception as e:
            err_message = f"An error occurred while creating tables: {str(e)}"
            raise err_message

    def insert_mock_data(self):
        """
        The function `insert_mock_data` inserts mock data into the Customer, Items, Sales, and Orders
        tables in a database.
        """
        try:
            cursor = self.conn.cursor()

            # Insert data into the Customer table
            for customer_id in range(1, 21):
                age = random.randint(1, 100)  # Generate ages between 1 and 100
                cursor.execute("INSERT INTO Customer (age) VALUES (?)", (age,))
            
            # Insert data into the Items table
            for item_id, item_name in enumerate(['x', 'y', 'z'], start=1):
                cursor.execute("INSERT INTO Items (item_id, item_name) VALUES (?, ?)", (item_id, item_name))
            
            # Insert data into the Sales and Orders tables with specific constraints
            for customer_id in range(1, 21):
                if 18 <= customer_id <= 35:
                    cursor.execute("INSERT INTO Sales (customer_id) VALUES (?)", (customer_id,))
                    sales_id = cursor.lastrowid  

                    for item_id in range(1, 4):
                        quantity = random.randint(1, 5)  # Random non-zero quantities
                        cursor.execute("INSERT INTO Orders (sales_id, item_id, quantity) VALUES (?, ?, ?)", (sales_id, item_id, quantity))
            
            self.conn.commit()  # Commit the data insertion changes
            print("Mock data inserted successfully.")
        except Exception as e:
            err_message = f"An error occurred while inserting mock data: {str(e)}"
            raise err_message



    def extract_total_quantities(self):
        """
        The function `extract_total_quantities` retrieves the total quantities of items purchased by
        customers between the ages of 18 and 35.
        :return: the results of the SQL query as a list of tuples. Each tuple contains the customer ID,
        age, item name, and total quantity for customers between the ages of 18 and 35.
        """
        try:
            query = '''
                SELECT c.customer_id, c.age, i.item_name, SUM(o.quantity) AS total_quantity
                FROM Customer AS c
                INNER JOIN Sales AS s ON c.customer_id = s.customer_id
                INNER JOIN Orders AS o ON s.sales_id = o.sales_id
                INNER JOIN Items AS i ON o.item_id = i.item_id
                WHERE c.age BETWEEN 18 AND 35
                GROUP BY c.customer_id, i.item_name
                HAVING total_quantity > 0
            '''

            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print("Output from purely SQL", results)
            return results
        except Exception as e:
            err_message = f"An error occurred while executing the query: {str(e)}"
            raise err_message

    def write_to_output_file(self, results):
        """
        The function writes the results to an output file in CSV format.
        
        :param results: The `results` parameter is a list of tuples. Each tuple represents a row of data
        that needs to be written to the output file. The elements of each tuple correspond to the values
        of the fields 'Customer', 'Age', 'Item', and 'Quantity' respectively
        """
        try:
            with open('output.csv', 'w', newline='') as csvfile:
                fieldnames = ['Customer', 'Age', 'Item', 'Quantity']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()

                for row in results:
                    writer.writerow({'Customer': row[0], 'Age': row[1], 'Item': row[2], 'Quantity': row[3]})

            print("Results written to the output file successfully.")
        except Exception as e:
            err_message = f"An error occurred while writing to the output file: {str(e)}"
            raise err_message

    def display_results_using_pandas(self):
        """
        The function `display_results_using_pandas` reads data from multiple tables in a database,
        performs joins, filters the data based on age, groups the data by customer, age, and item name,
        sums the quantity, and displays the results using Pandas.
        """
        try:
            customer_df = pd.read_sql_query('SELECT * FROM Customer', self.conn)
            sales_df = pd.read_sql_query('SELECT * FROM Sales', self.conn)
            orders_df = pd.read_sql_query('SELECT * FROM Orders', self.conn)
            items_df = pd.read_sql_query('SELECT * FROM Items', self.conn)
            
            # Perform the joins to replicate the SQL query
            merged_df = customer_df.merge(sales_df, on='customer_id').merge(orders_df, left_on='sales_id', right_on='sales_id').merge(items_df, left_on='item_id', right_on='item_id')
            
            filtered_df = merged_df[(merged_df['age'] >= 18) & (merged_df['age'] <= 35)]
            
            result_df = filtered_df.groupby(['customer_id', 'age', 'item_name'])['quantity'].sum().reset_index()
            
            print(result_df)
            
            print("Results displayed using Pandas.")
        except Exception as e:
            err_message = f"An error occurred while displaying results using Pandas: {str(e)}"
            raise err_message

if __name__ == '__main__':
    try:
        processor = SalesDataProcessor()
        print("----------------------------------------------------------------------")
        processor.connect_to_database()
        processor.create_tables()
        processor.insert_mock_data()
        results = processor.extract_total_quantities()
        
        processor.write_to_output_file(results)
        processor.display_results_using_pandas()
        processor.close_database_connection()

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestExtractedData)
        runner = unittest.TextTestRunner()
        runner.run(suite)
    except Exception as e:
        err_message = f"Exiting program due to -> {str(e)}"
        print(err_message)
