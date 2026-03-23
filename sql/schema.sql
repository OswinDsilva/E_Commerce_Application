-- This file contains the SQL statements to create the database schema for the application.

-- USERS
CREATE TABLE Users (
u_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
username VARCHAR(255) NOT NULL UNIQUE,
password_hash VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL UNIQUE,
phone VARCHAR(20) NOT NULL,
created_at TIMESTAMPTZ NOT NULL
);

-- BANK ACCOUNT
CREATE TABLE Bank_acc (
acc_no INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
bank_name VARCHAR(255) NOT NULL,
expiry_date DATE NOT NULL,
u_id INTEGER NOT NULL,
CONSTRAINT bank_acc_user_fk
FOREIGN KEY (u_id) REFERENCES Users(u_id)
ON DELETE CASCADE
);

-- PRODUCTS
CREATE TABLE Products (
p_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
product_name VARCHAR(255) NOT NULL,
brand VARCHAR(255) NOT NULL,
price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
category VARCHAR(255) NOT NULL,
description TEXT NOT NULL
);

-- INVENTORY (Weak Entity)
CREATE TABLE Inventory (
p_id INTEGER PRIMARY KEY,
quantity INTEGER NOT NULL CHECK (quantity >= 0),
last_updated TIMESTAMPTZ NOT NULL,
CONSTRAINT inventory_product_fk
FOREIGN KEY (p_id) REFERENCES Products(p_id)
ON DELETE CASCADE
);

-- ORDERS
CREATE TABLE Orders (
o_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
order_date DATE NOT NULL,
status VARCHAR(50) NOT NULL CHECK (
status IN ('CREATED','PAID','SHIPPED','DELIVERED','CANCELLED')
),
total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
u_id INTEGER NOT NULL,
acc_no INTEGER,
CONSTRAINT orders_user_fk
FOREIGN KEY (u_id) REFERENCES Users(u_id)
ON DELETE CASCADE,
CONSTRAINT orders_bank_fk
FOREIGN KEY (acc_no) REFERENCES Bank_acc(acc_no)
ON DELETE SET NULL
);

-- INVOICE (1:1 with Orders)
CREATE TABLE Invoice (
i_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
invoice_date DATE NOT NULL,
total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
shipping_address TEXT NOT NULL,
billing_address TEXT NOT NULL,
o_id INTEGER NOT NULL UNIQUE,
CONSTRAINT invoice_order_fk
FOREIGN KEY (o_id) REFERENCES Orders(o_id)
ON DELETE CASCADE
);

-- ORDERED ITEMS (Junction Table)
CREATE TABLE ordered_items (
o_id INTEGER NOT NULL,
p_id INTEGER NOT NULL,
quantity INTEGER NOT NULL CHECK (quantity > 0),
price_at_purchase DECIMAL(10,2) NOT NULL CHECK (price_at_purchase >= 0),
PRIMARY KEY (o_id, p_id),
CONSTRAINT ordered_items_order_fk
FOREIGN KEY (o_id) REFERENCES Orders(o_id)
ON DELETE CASCADE,
CONSTRAINT ordered_items_product_fk
FOREIGN KEY (p_id) REFERENCES Products(p_id)
ON DELETE CASCADE
);
