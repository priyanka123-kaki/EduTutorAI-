from flask import Flask, render_template, request, redirect, url_for, session
from products import product_list
import boto3
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')  # Replace with your region
orders_table = dynamodb.Table('PickleOrders')  # Create this table in AWS

@app.route('/')
def home():
    return render_template('index.html', products=product_list)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = next((item for item in product_list if item["id"] == product_id), None)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = [item for item in product_list if item["id"] in session.get("cart", [])]
    return render_template('cart.html', cart=cart_items)

@app.route('/checkout')
def checkout():
    cart_items = [item for item in product_list if item["id"] in session.get("cart", [])]
    if cart_items:
        order = {
            'order_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'items': [{'name': item['name'], 'price': item['price']} for item in cart_items],
            'total': sum(item['price'] for item in cart_items),
            'user_email': 'testuser@example.com'  # Placeholder for user profile
        }
        # Store in DynamoDB
        orders_table.put_item(Item=order)
    
    session.pop("cart", None)
    return render_template('confirmation.html')
product_list = [
    {"id": 1, "name": "Mango Pickle", "price": 150, "description": "Spicy homemade mango pickle"},
    {"id": 2, "name": "Lemon Pickle", "price": 120, "description": "Tangy lemon pickle with mustard"},
    {"id": 3, "name": "Mixed Veg Pickle", "price": 180, "description": "Crunchy mix of seasonal vegetables"}
]
<!DOCTYPE html>
<html>
<head>
    <title>Pickles Shop</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Welcome to Homemade Pickles</h1>
    <ul>
        {% for product in products %}
            <li>
                <a href="{{ url_for('product', product_id=product.id) }}">{{ product.name }}</a> - ₹{{ product.price }}
            </li>
        {% endfor %}
    </ul>
    <a href="{{ url_for('cart') }}">🛒 View Cart</a>
</body>
</html>
