import unittest
import sqlite3

class TestExtractedData(unittest.TestCase):

    def setUp(self):
        """
        The setUp function connects to a database, executes a query, and fetches the results.
        """
        # Connect to the database and execute the query
        self.conn = sqlite3.connect('eastvantage_db.db')
        self.cursor = self.conn.cursor()

        self.query = '''
            SELECT c.customer_id, c.age, i.item_name, SUM(o.quantity) AS total_quantity
            FROM Customer AS c
            INNER JOIN Sales AS s ON c.customer_id = s.customer_id
            INNER JOIN Orders AS o ON s.sales_id = o.sales_id
            INNER JOIN Items AS i ON o.item_id = i.item_id
            GROUP BY c.customer_id, i.item_name
            HAVING total_quantity > 0
        '''
        self.cursor.execute(self.query)
        self.actual_output = self.cursor.fetchall()

    def test_customer_1_purchases(self):
        """
        The function tests if customer 1 purchased 10 of item X.
        """
        # Verify if Customer 1 bought 10 of Item X only
        customer_id = 1
        item_name = 'x'
        expected_quantity = 10

        match = False
        for row in self.actual_output:
            if row[0] == customer_id and row[2] == item_name:
                match = True
                self.assertEqual(row[3], expected_quantity, f"Unit test failed for customer {customer_id}, item {item_name}")
                break

        if match:
            print(f"Unit test passed for customer {customer_id}, item {item_name}")

    def test_customer_2_purchases(self):
        """
        The function tests if Customer 2 bought 1 of each item only once.
        """
        # Verify if Customer 2 bought 1 of each item only once
        customer_id = 2
        items = ['x', 'y', 'z']

        for item_name in items:
            expected_quantity = 1

            match = False
            for row in self.actual_output:
                if row[0] == customer_id and row[2] == item_name:
                    match = True
                    self.assertEqual(row[3], expected_quantity, f"Unit test failed for customer {customer_id}, item {item_name}")
                    break

            if match:
                print(f"Unit test passed for customer {customer_id}, item {item_name}")

    def test_customer_3_purchases(self):
        """
        The function tests if customer 3 purchased 2 of item Z.
        """
        # Verify if Customer 3 bought 2 of Item Z only
        customer_id = 3
        item_name = 'z'
        expected_quantity = 2

        match = False
        for row in self.actual_output:
            if row[0] == customer_id and row[2] == item_name:
                match = True
                self.assertEqual(row[3], expected_quantity, f"Unit test failed for customer {customer_id}, item {item_name}")
                break

        if match:
            print(f"Unit test passed for customer {customer_id}, item {item_name}")

    def tearDown(self):
        # Close the database connection
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
