-- Create the Customer table
CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY,
    age INTEGER
);

-- Create the Sales table
CREATE TABLE Sales (
    sales_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
);

-- Create the Items table
CREATE TABLE Items (
    item_id INTEGER PRIMARY KEY,
    item_name TEXT
);

-- Create the Orders table
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    sales_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (sales_id) REFERENCES Sales (sales_id),
    FOREIGN KEY (item_id) REFERENCES Items (item_id)
);
