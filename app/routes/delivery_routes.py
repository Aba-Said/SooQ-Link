from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
from flask_mail import Message
from ..config import Config
from .. import mail

delivery_bp = Blueprint('delivery', __name__, url_prefix='')

def get_db_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)

# ✅ صفحة طلب خدمة النقل
@delivery_bp.route('/request_transport', methods=['GET', 'POST'])
def request_transport():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        item_description = request.form.get('item_description')
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')
        email = request.form.get('email')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO transport_requests (full_name, phone, email, item_description, from_location, to_location)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (full_name, phone, email, item_description, from_location, to_location))
            conn.commit()
            request_id = cursor.lastrowid

            # إرسال البريد الإلكتروني
            msg = Message(
                subject="تأكيد طلب خدمة النقل - SooQlink",
                sender=Config.MAIL_USERNAME,
                recipients=[email],
                body=f"""مرحباً {full_name}،

تم استلام طلبك لخدمة النقل بنجاح.

📦 الحمولة: {item_description}
📍 من: {from_location}
📍 إلى: {to_location}
📞 رقم الهاتف: {phone}
📄 رقم الطلب: {request_id}

سنتواصل معك قريباً. شكراً لاستخدامك SooQlink.
"""
            )
            mail.send(msg)

            return redirect(url_for('delivery.transport_success', request_id=request_id))

        except Exception as e:
            conn.rollback()
            flash(f"حدث خطأ أثناء إرسال الطلب أو البريد: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('delivery/request_transport.html')

# ✅ صفحة "وصل" بعد نجاح الطلب
@delivery_bp.route('/transport_success')
def transport_success():
    request_id = request.args.get('request_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM transport_requests WHERE id = %s", (request_id,))
    transport_request = cursor.fetchone()

    cursor.close()
    conn.close()

    if not transport_request:
        flash("لم يتم العثور على الطلب", "danger")
        return redirect(url_for('main.index'))

    return render_template('delivery/transport_success.html', transport_request=transport_request)
