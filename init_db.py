### init_db.py
from app import app, db
from models import User 
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin_user = User(username="admin", password=generate_password_hash("secret123"))
        db.session.add(admin_user)
        db.session.commit()
        print("Админ создан")
    else:
        print("Админ уже существует")