import mysql.connector
from werkzeug.security import generate_password_hash

# إعدادات الاتصال بقاعدة البيانات
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",  # عدل حسب إعدادك
    "database": "sooqlink_db"
}

# معلومات المشرف
username = "admin"
email = "admin@example.com"
raw_password = "admin123"  # كلمة مرور بسيطة للتجربة - يفضل تغييرها

# توليد كلمة المرور المشفّرة
hashed_password = generate_password_hash(raw_password)

# الاتصال بقاعدة البيانات
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO admins (username, password, email)
        VALUES (%s, %s, %s)
    """, (username, hashed_password, email))

    conn.commit()
    print(f"✅ تم إنشاء المشرف '{username}' بنجاح!")

except mysql.connector.IntegrityError:
    print(f"⚠️ اسم المستخدم '{username}' موجود مسبقًا.")
except Exception as e:
    print("❌ حدث خطأ أثناء إنشاء المشرف:", e)
finally:
    cursor.close()
    conn.close()
