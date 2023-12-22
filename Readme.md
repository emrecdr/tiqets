# Project Name

This project reads orders and ticket barcodes data from CSV files, validates the data, and generates an output containing the customer ID, order ID, and a list of ticket barcodes for each order. It also calculates the top N customers who bought the most books and the number of unused book barcodes. This project mainly uses the [Polars](https://pola-rs.github.io) library for data processing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation 

### Locally
To install locally, you need to have Python 3 installed on your machine. You will also need to install the dependencies using pip:
```bash
pip install --no-cache-dir -r requirements.txt
```

### Docker
To run this application in a docker container, you need to have `docker` installed on your machine and then execute following command from root directory of the project:
```bash
docker build --tag tiqets-assignment-app .
```

## Usage

You can run the application with the names of the orders and books CSV files as arguments.
The script will then read these files, match each order to a barcode (or multiple if they are present) and to a customer, and output this information to a csv file under "out" folder. 
It will also print out a list of top N  customers that bought the most amount of tickets (default is 5) along with their count and amount of unused barcodes.
The script checks for duplicate barcodes and orders without barcodes. Any invalid data is logged and ignored for the output.

### Locally
Python script can be executed locally by providing only required parameters:

```bash
python ./src/app.py orders.csv barcodes.csv 
```

OR by also including optional parameters:

```bash
python ./src/app.py orders.csv barcodes.csv --file_path data --top_n 3 --debug
```

### Docker
The outputs will be saved in `out` directory, which is mounted to your local filesystem at `./out`.
To execute from a Docker container use:

```bash
docker run -v ./out:/home/appuser/app/out py-solution-app orders.csv barcodes.csv
```
OR   
```bash
docker run -v ./out:/home/appuser/app/out py-solution-app orders.csv barcodes.csv --file_path data --top_n 3 --debug
```

## Moving forward
Inorder to store this data set in a SQL database, we can design a simple relational db schema with three tables: Customers, Orders, and Barcodes like below:

```text
+------------------------+        +----------------------+        +-------------------+
|      Customers         |        |       Orders         |        |     Barcodes      |
+------------------------+        +----------------------+        +-------------------+
| PK: customer_id        |        | PK: order_id         |        | PK: barcode       |
|     customer_name      |        |     customer_id (FK) |        |     order_id (FK) |
+------------------------+        +----------------------+        +-------------------+

```

Simplified SQL representation of the schema:

```sql
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(255)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Barcodes (
    barcode INT PRIMARY KEY,
    order_id INT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
```

Here's a breakdown of the tables:
 * Customers: This table contains information about the customers. The customer_id column is the primary key for this table.
 * Orders: This table contains information about the orders. The order_id column is the primary key for this table. The customer_id column is a foreign key that references the customer_id column in the Customers table.
 * Barcodes: This table contains information about the barcodes. The barcode column is the primary key for this table. The order_id column is a foreign key that references the order_id column in the Orders table.

With this data model, we can represent the given dataset in a structured way.

For better performance, we can add indexes on foreign key columns:
```sql
CREATE INDEX idx_orders_customer_id ON Orders (customer_id);
CREATE INDEX idx_barcodes_order_id ON Barcodes (order_id);
```