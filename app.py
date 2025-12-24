import os
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
import stripe
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)
app.secret_key='your_secret_key_here'

stripe.api_key=os.getenv('STRIPE_SECRET_KEY')
YOUR_DOMAIN='http://127.0.0.1:5000'

products = [
    {
        'id': 1,
        'name': 'T-Shirt',
        'price': 20.00,
        'description': 'Comfortable cotton t-shirt',
        'image': 'https://media.istockphoto.com/id/515750480/photo/mans-white-t-shirt.jpg?s=612x612&w=0&k=20&c=qKNa13XtQkx0ZPt7HcEGNan6ey_A1yWmZc5bKAJuWFE='
    },
    {
        'id': 2,
        'name': 'Mug',
        'price': 10.00,
        'description': 'Ceramic coffee mug',
        'image': 'https://static.vecteezy.com/system/resources/previews/054/698/157/large_2x/minimalist-white-ceramic-coffee-mug-isolated-on-white-background-for-product-display-and-design-mockups-photo.jpg'
    },
    {
        'id': 3,
        'name': 'Hat',
        'price': 15.00,
        'description': 'Stylish baseball hat',
        'image': 'https://www.shutterstock.com/image-photo/stylish-black-baseball-cap-on-600nw-2585100255.jpg'
    },
]
@app.route('/')
def product_list():
    return render_template('products.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        # Check if already in cart
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += 1
                break
        else:
            session['cart'].append({'id': product_id, 'name': product['name'], 'price': product['price'], 'quantity': 1})
        session.modified = True
    return redirect(url_for('product_list'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    # Always calculate total, even if cart is empty (will be 0.0)
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def create_checkout_session():
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('cart'))

    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item['name']},
                'unit_amount': int(item['price'] * 100),  
            },
            'quantity': item['quantity'],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

@app.route('/success')
def success():
    session.pop('cart', None)  # Clear cart after successful payment
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run()