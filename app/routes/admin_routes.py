from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash
from ..config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)

# ✅ تسجيل دخول المسؤول
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            flash("تم تسجيل الدخول كمسؤول", "success")
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")

    return render_template('admin/login_admin.html')

# ✅ لوحة تحكم المسؤول
@admin_bp.route('/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("يجب تسجيل الدخول كمسؤول أولاً", "danger")
        return redirect(url_for('admin.admin_login'))

    section = request.args.get('section', 'dashboard')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    merchants = []
    customers = []
    orders = []
    transport_requests = []

    # إحصائيات عامة
    cursor.execute("SELECT COUNT(*) AS total_merchants FROM merchants")
    merchants_count = cursor.fetchone()['total_merchants']

    cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
    customers_count = cursor.fetchone()['total_customers']

    cursor.execute("SELECT COUNT(*) AS total_orders FROM orders")
    orders_count = cursor.fetchone()['total_orders']

    cursor.execute("SELECT SUM(total_price) AS total_revenue FROM orders")
    total_revenue = cursor.fetchone()['total_revenue'] or 0

    # عرض البيانات حسب القسم
    if section == 'merchants':
        cursor.execute("SELECT * FROM merchants")
        merchants = cursor.fetchall()
    elif section == 'customers':
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
    elif section == 'orders':
        cursor.execute("""
            SELECT o.*, p.name AS product_name, c.name AS customer_name, m.name AS merchant_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN customers c ON o.customer_id = c.id
            JOIN merchants m ON p.merchant_id = m.id
            ORDER BY o.order_date DESC
        """)
        orders = cursor.fetchall()
    elif section == 'transport':
        cursor.execute("SELECT * FROM transport_requests ORDER BY request_date DESC")
        transport_requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/admin_dashboard.html',
                           section=section,
                           merchants_count=merchants_count,
                           customers_count=customers_count,
                           orders_count=orders_count,
                           total_revenue=total_revenue,
                           merchants=merchants,
                           customers=customers,
                           orders=orders,
                           transport_requests=transport_requests)

# ✅ تحديث حالة الطلب
@admin_bp.route('/update_order_status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    if 'admin_id' not in session:
        flash("يجب تسجيل الدخول كمسؤول أولاً", "danger")
        return redirect(url_for('admin.admin_login'))

    new_status = request.form.get('status')
    if not new_status:
        flash("يرجى اختيار الحالة", "danger")
        return redirect(url_for('admin.admin_dashboard', section='orders'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        conn.commit()
        flash("تم تحديث حالة الطلب بنجاح", "success")
    except Exception as e:
        conn.rollback()
        flash(f"خطأ أثناء التحديث: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin.admin_dashboard', section='orders'))

# ✅ حذف زبون
@admin_bp.route('/delete_customer/<int:customer_id>', methods=['POST'])
def admin_delete_customer(customer_id):
    if 'admin_id' not in session:
        flash("يجب تسجيل الدخول كمسؤول أولاً", "danger")
        return redirect(url_for('admin.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM orders WHERE customer_id = %s", (customer_id,))
        cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        conn.commit()
        flash("تم حذف العميل بنجاح", "success")
    except Exception as e:
        conn.rollback()
        flash(f"حدث خطأ أثناء الحذف: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin.admin_dashboard', section='customers'))

# ✅ تعديل زبون
@admin_bp.route('/update_customer/<int:customer_id>', methods=['POST'])
def admin_update_customer(customer_id):
    if 'admin_id' not in session:
        flash("يجب تسجيل الدخول كمسؤول أولاً", "danger")
        return redirect(url_for('admin.admin_login'))

    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')

    if not all([name, phone, address]):
        flash("جميع الحقول مطلوبة", "danger")
        return redirect(url_for('admin.admin_dashboard', section='customers'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE customers SET name = %s, phone = %s, address = %s WHERE id = %s
        """, (name, phone, address, customer_id))
        conn.commit()
        flash("تم تحديث بيانات العميل بنجاح", "success")
    except Exception as e:
        conn.rollback()
        flash(f"حدث خطأ أثناء التحديث: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin.admin_dashboard', section='customers'))

@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_id', None)
    flash("تم تسجيل الخروج بنجاح", "success")
    return redirect(url_for('admin.admin_login'))