from flask import Blueprint, render_template, request, redirect, url_for, flash, session ,  send_from_directory
import mysql.connector
import uuid
import json
from datetime import datetime
from ..config import Config
import os

main_bp = Blueprint('main', __name__)

# دالة الاتصال بقاعدة البيانات
def get_db_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)

# دالة لحساب عدد المنتجات في السلة
def get_cart_count():
    return sum(session.get("cart", {}).values())


@main_bp.route('/uploads/images_product/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# الصفحة الرئيسية
@main_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM products WHERE quantity = 0")
        conn.commit()

        cursor.execute("""
            SELECT p.id, p.name, p.price, p.image, p.category, 
                   m.name AS merchant_name, m.phone AS merchant_phone
            FROM products p
            JOIN merchants m ON p.merchant_id = m.id
        """)
        products = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('main/index.html', products=products, cart_count=get_cart_count())


# تفاصيل منتج
@main_bp.route('/product/<int:product_id>')
def product_details(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT p.*, m.name AS merchant_name, m.phone AS merchant_phone
            FROM products p
            JOIN merchants m ON p.merchant_id = m.id
            WHERE p.id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            flash("المنتج غير موجود!", "warning")
            return redirect(url_for('main.index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('main/product_details.html', product=product, cart_count=get_cart_count())


# إضافة للسلة
@main_bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('main.index'))


# عرض السلة
@main_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    if not cart:
        return render_template('main/cart.html', cart_items=[], cart_count=0, total_price=0)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id, name, price, image FROM products WHERE id IN (%s)" % ','.join(['%s'] * len(cart))
    cursor.execute(query, list(cart.keys()))
    products = cursor.fetchall()

    total_price = 0
    for product in products:
        product_id_str = str(product["id"])
        if product_id_str in cart:
            product["quantity"] = cart[product_id_str]
            total_price += product["price"] * product["quantity"]

    cursor.close()
    conn.close()

    return render_template('main/cart.html', cart_items=products, cart_count=len(cart), total_price=total_price)


# إزالة منتج من السلة
@main_bp.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session.modified = True
    return redirect(url_for('main.view_cart'))


# إفراغ السلة
@main_bp.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('main.view_cart'))


# تنفيذ الطلب
@main_bp.route('/checkout', methods=['POST'])
def checkout():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    cart_data = request.form.get('cart_data')

    if not name or not phone or not address or not cart_data:
        return "جميع الحقول مطلوبة", 400

    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        return "بيانات السلة غير صالحة", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (name, phone, address))
        customer_id = cursor.lastrowid

        code_order = str(uuid.uuid4())[:8]
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in cart:
            product_id = item.get("id")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)

            cursor.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            if not result or result[0] < quantity:
                return f"المنتج {product_id} غير متوفر بالكمية المطلوبة", 400

            total_price = price * quantity
            cursor.execute("""
                INSERT INTO orders (product_id, quantity, total_price, customer_id, code_order, order_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (product_id, quantity, total_price, customer_id, code_order, order_date))

            cursor.execute("UPDATE products SET quantity = quantity - %s WHERE id = %s", (quantity, product_id))

        conn.commit()
        session.pop('cart', None)

        return redirect(url_for('main.order_success', code_order=code_order, order_date=order_date))

    except Exception as e:
        conn.rollback()
        return f"حدث خطأ: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


# نجاح الطلب
@main_bp.route('/order_success')
def order_success():
    code_order = request.args.get('code_order')
    order_date = request.args.get('order_date')
    return render_template('main/order_success.html', code_order=code_order, order_date=order_date)


# صفحة البحث عن الطلب
@main_bp.route('/search_order', methods=['GET', 'POST'])
def search_order():
    order = None
    error = None
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        code_order = request.form.get('code_order')
        if code_order:
            cursor.execute("""
                SELECT orders.id, orders.code_order, orders.order_date, orders.status,
                       customers.name, customers.phone, customers.address 
                FROM orders 
                JOIN customers ON orders.customer_id = customers.id 
                WHERE orders.code_order = %s
            """, (code_order,))
            order = cursor.fetchone()
            if not order:
                error = "لم يتم العثور على طلب بهذا الرقم."

    cursor.close()
    conn.close()

    return render_template('main/search_order.html', order=order, error=error)
@main_bp.route('/about')
def about():
    return render_template('main/about.html')