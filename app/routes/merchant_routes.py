from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os
from ..config import Config

merchant_bp = Blueprint('merchant', __name__, url_prefix='')

def get_db_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)

# التحقق من امتداد الصور
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ✅ تسجيل تاجر جديد
@merchant_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO merchants (name, phone, email, address, password) VALUES (%s, %s, %s, %s, %s)",
                           (name, phone, email, address, password))
            conn.commit()
            flash("تم التسجيل بنجاح! الرجاء تسجيل الدخول.", "success")
            return redirect(url_for('merchant.login'))
        except mysql.connector.IntegrityError:
            flash("البريد الإلكتروني مستخدم بالفعل!", "danger")
        except mysql.connector.Error as e:
            flash(f"خطأ في قاعدة البيانات: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('merchant/register_merchant.html')

# ✅ تسجيل الدخول
@merchant_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM merchants WHERE email = %s", (email,))
        merchant = cursor.fetchone()
        cursor.close()
        conn.close()

        if merchant and check_password_hash(merchant['password'], password):
            session['merchant_id'] = merchant['id']
            flash("تم تسجيل الدخول بنجاح!", "success")
            return redirect(url_for('merchant.dashboard'))
        else:
            flash("البريد أو كلمة المرور غير صحيحة!", "danger")

    return render_template('merchant/login_merchants.html')

# ✅ تسجيل الخروج
@merchant_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('merchant_id', None)
    flash("تم تسجيل الخروج بنجاح", "success")
    return redirect(url_for('main.index'))

# ✅ لوحة التاجر
@merchant_bp.route('/dashboard')
def dashboard():
    if 'merchant_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "danger")
        return redirect(url_for('merchant.login'))

    merchant_id = session['merchant_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # المنتجات الخاصة بالتاجر
    cursor.execute("SELECT * FROM products WHERE merchant_id = %s", (merchant_id,))
    products = cursor.fetchall()

    # الطلبات المرتبطة بمنتجات التاجر
    cursor.execute("""
        SELECT o.*, p.name AS product_name, c.name AS customer_name 
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        JOIN customers c ON o.customer_id = c.id
        WHERE p.merchant_id = %s
    """, (merchant_id,))
    orders = cursor.fetchall()

    # الإحصائيات
    products_count = len(products)
    orders_count = len(orders)
    users_count = len(set(order['customer_id'] for order in orders))
    total_revenue = sum(order['total_price'] for order in orders)

    cursor.close()
    conn.close()

    return render_template('merchant/dashboard.html',
                           products=products,
                           orders=orders,
                           products_count=products_count,
                           orders_count=orders_count,
                           users_count=users_count,
                           total_revenue=total_revenue)

# ✅ إضافة منتج جديد
@merchant_bp.route('/add_product', methods=['POST'])
def add_product():
    if 'merchant_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "danger")
        return redirect(url_for('merchant.login'))

    merchant_id = session['merchant_id']
    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    quantity = request.form['quantity']

    if 'image' not in request.files:
        flash("لم يتم تحميل صورة!", "danger")
        return redirect(url_for('merchant.dashboard'))

    image_file = request.files['image']
    if image_file.filename == '' or not allowed_file(image_file.filename):
        flash("ملف غير صالح! الصيغ المسموحة: png, jpg, jpeg, gif", "danger")
        return redirect(url_for('merchant.dashboard'))

    filename = secure_filename(image_file.filename)
    image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, price, image, merchant_id, category, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, price, filename, merchant_id, category, quantity))
        conn.commit()
        flash("تمت إضافة المنتج بنجاح!", "success")
    except mysql.connector.Error as e:
        flash(f"خطأ في قاعدة البيانات: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('merchant.dashboard'))

# ✅ تعديل منتج
@merchant_bp.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if 'merchant_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "danger")
        return redirect(url_for('merchant.login'))

    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    quantity = request.form['quantity']
    description = request.form.get('description', '')

    image_filename = None
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename != '':
            from werkzeug.utils import secure_filename
            from ..config import Config
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(Config.UPLOAD_FOLDER, image_filename)
            image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if image_filename:
            cursor.execute("""
                UPDATE products
                SET name=%s, price=%s, category=%s, quantity=%s, description=%s, image=%s
                WHERE id=%s
            """, (name, price, category, quantity, description, image_filename, product_id))
        else:
            cursor.execute("""
                UPDATE products
                SET name=%s, price=%s, category=%s, quantity=%s, description=%s
                WHERE id=%s
            """, (name, price, category, quantity, description, product_id))

        conn.commit()
        flash("تم تعديل المنتج بنجاح", "success")
    except Exception as e:
        conn.rollback()
        flash(f"حدث خطأ أثناء تعديل المنتج: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('merchant.dashboard'))


# ✅ حذف منتج
@merchant_bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("تم حذف المنتج بنجاح", "danger")
    return redirect(url_for('merchant.dashboard'))

# ✅ تغيير حالة الطلب
@merchant_bp.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if 'merchant_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "danger")
        return redirect(url_for('merchant.login'))

    new_status = request.form['status']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("تم تحديث حالة الطلب بنجاح", "success")
    return redirect(url_for('merchant.dashboard'))
