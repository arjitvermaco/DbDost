import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta
import json

fake = Faker()

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=input("Enter MySQL root password: "),
        database="ecommerce"
    )

def generate_categories(cursor):
    try:
        # First, insert main categories
        main_categories = [
            ("Electronics", "Electronic devices and accessories"),
            ("Clothing", "Fashion and apparel"),
            ("Books", "Books and publications"),
            ("Home & Garden", "Home improvement and garden supplies"),
            ("Sports", "Sports equipment and accessories")
        ]
        
        # Insert main categories and get their IDs
        for name, description in main_categories:
            cursor.execute(
                "INSERT INTO categories (name, description, parent_category_id) VALUES (%s, %s, NULL)",
                (name, description)
            )
            parent_id = cursor.lastrowid
            
            # Generate and insert sub-categories for this parent
            sub_categories = [
                (f"Sub-category {j} of {name}", 
                 f"Description for sub-category {j}",
                 parent_id)
                for j in range(1, 11)
            ]
            
            cursor.executemany(
                "INSERT INTO categories (name, description, parent_category_id) VALUES (%s, %s, %s)",
                sub_categories
            )
            
    except Exception as e:
        print(f"Error in generate_categories: {e}")
        raise e

def generate_product_name():
    """Generate a realistic product name"""
    adjectives = ['Premium', 'Deluxe', 'Professional', 'Classic', 'Modern', 'Ultra', 'Smart', 'Essential']
    products = [
        # Electronics
        'Laptop', 'Smartphone', 'Headphones', 'Tablet', 'Smartwatch', 'Camera', 'Speaker', 'Monitor',
        # Clothing
        'T-Shirt', 'Jeans', 'Jacket', 'Sweater', 'Dress', 'Shoes', 'Hat', 'Socks',
        # Books
        'Novel', 'Cookbook', 'Textbook', 'Magazine', 'Journal', 'Guide', 'Manual', 'Biography',
        # Home & Garden
        'Chair', 'Lamp', 'Table', 'Pillow', 'Plant', 'Tool Set', 'Blanket', 'Vase',
        # Sports
        'Ball', 'Racket', 'Gloves', 'Shoes', 'Bag', 'Mat', 'Weights', 'Helmet'
    ]
    brands = ['TechPro', 'StyleCo', 'HomeLife', 'SportMax', 'EcoBasics', 'LuxuryPlus', 'ValuePro', 'PrimeBrand']
    
    return f"{random.choice(adjectives)} {random.choice(brands)} {random.choice(products)}"

def get_category_ids(cursor) -> list:
    """Get all valid category IDs from the database"""
    cursor.execute("SELECT category_id FROM categories")
    return [row[0] for row in cursor.fetchall()]

def generate_products(cursor):
    # Get valid category IDs first
    category_ids = get_category_ids(cursor)
    if not category_ids:
        raise Exception("No categories found in database")
    
    products = []
    for _ in range(50):
        # Select a random valid category ID
        category_id = random.choice(category_ids)
        product = (
            generate_product_name(),
            fake.text(max_nb_chars=200),
            category_id,
            round(random.uniform(10, 1000), 2),
            random.randint(0, 100),
            fake.ean13()
        )
        products.append(product)
    
    cursor.executemany(
        """INSERT INTO products 
           (name, description, category_id, price, stock_quantity, sku)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        products
    )

def format_phone_number(phone: str) -> str:
    """Format phone number to fit in VARCHAR(20)"""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    # Format as XXX-XXX-XXXX
    if len(digits) >= 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"
    return digits[:20]  # Fallback: just return truncated digits

def generate_customers(cursor):
    customers = []
    for _ in range(50):
        customer = (
            fake.first_name()[:50],  # Limit to 50 chars
            fake.last_name()[:50],   # Limit to 50 chars
            fake.email()[:100],      # Limit to 100 chars
            format_phone_number(fake.phone_number())  # Format phone number
        )
        customers.append(customer)
    
    cursor.executemany(
        """INSERT INTO customers 
           (first_name, last_name, email, phone)
           VALUES (%s, %s, %s, %s)""",
        customers
    )

def generate_addresses(cursor):
    addresses = []
    for customer_id in range(1, 51):
        for _ in range(random.randint(1, 3)):
            address = (
                customer_id,
                random.choice(['home', 'work', 'other']),
                fake.street_address(),
                fake.city(),
                fake.state(),
                fake.postcode(),
                fake.country(),
                random.choice([True, False])
            )
            addresses.append(address)
    
    cursor.executemany(
        """INSERT INTO addresses 
           (customer_id, address_type, street_address, city, state, postal_code, country, is_default)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        addresses
    )

def generate_orders(cursor):
    orders = []
    order_items = []
    
    for _ in range(100):
        customer_id = random.randint(1, 50)
        # Get customer's addresses
        cursor.execute(
            "SELECT address_id FROM addresses WHERE customer_id = %s",
            (customer_id,)
        )
        customer_addresses = cursor.fetchall()
        if not customer_addresses:
            continue
            
        shipping_address = random.choice(customer_addresses)[0]
        billing_address = random.choice(customer_addresses)[0]
        
        # Create order
        order = (
            customer_id,
            random.choice(['pending', 'processing', 'shipped', 'delivered']),
            shipping_address,
            billing_address,
            0  # Total amount will be updated later
        )
        cursor.execute(
            """INSERT INTO orders 
               (customer_id, status, shipping_address_id, billing_address_id, total_amount)
               VALUES (%s, %s, %s, %s, %s)""",
            order
        )
        order_id = cursor.lastrowid
        
        # Generate order items
        total_amount = 0
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, 50)
            quantity = random.randint(1, 5)
            
            # Get product price
            cursor.execute(
                "SELECT price FROM products WHERE product_id = %s",
                (product_id,)
            )
            unit_price = cursor.fetchone()[0]
            subtotal = unit_price * quantity
            total_amount += subtotal
            
            order_item = (
                order_id,
                product_id,
                quantity,
                unit_price,
                subtotal
            )
            cursor.execute(
                """INSERT INTO order_items 
                   (order_id, product_id, quantity, unit_price, subtotal)
                   VALUES (%s, %s, %s, %s, %s)""",
                order_item
            )
        
        # Update order total
        cursor.execute(
            "UPDATE orders SET total_amount = %s WHERE order_id = %s",
            (total_amount, order_id)
        )

def generate_reviews(cursor):
    reviews = []
    for _ in range(200):
        review = (
            random.randint(1, 50),  # product_id
            random.randint(1, 50),  # customer_id
            random.randint(1, 5),   # rating
            fake.text(max_nb_chars=200)  # comment
        )
        reviews.append(review)
    
    cursor.executemany(
        """INSERT INTO reviews 
           (product_id, customer_id, rating, comment)
           VALUES (%s, %s, %s, %s)""",
        reviews
    )

def main():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        print("Generating categories...")
        generate_categories(cursor)
        
        print("Generating products...")
        generate_products(cursor)
        
        print("Generating customers...")
        generate_customers(cursor)
        
        print("Generating addresses...")
        generate_addresses(cursor)
        
        print("Generating orders and order items...")
        generate_orders(cursor)
        
        print("Generating reviews...")
        generate_reviews(cursor)
        
        conn.commit()
        print("Sample data generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main() 