import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'images_product')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'aba.houcini@cuniv-tindouf.dz'
    MAIL_PASSWORD = 'coqp pukn xxig jckm'

    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'sooqlink_db'
    }
