from flask import Flask
from flask_mail import Mail
from .config import Config

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aba_said_01'

    # تحميل إعدادات التطبيق من ملف config.py
    app.config.from_object(Config)

    # تهيئة البريد
    mail.init_app(app)

    # 🧠 تسجيل الـ Blueprints الخاصة بكل جزء من الموقع
    from .routes.main_routes import main_bp
    from .routes.merchant_routes import merchant_bp
    from .routes.admin_routes import admin_bp
    from .routes.delivery_routes import delivery_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(merchant_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(delivery_bp)

    return app
