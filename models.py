### models.py
from flask import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()



class HeroContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    hidden_text = db.Column(db.Text, nullable=True)
    resume_link = db.Column(db.String(255), nullable=False)
    email_link = db.Column(db.String(255), nullable=False)
    github_link = db.Column(db.String(255), nullable=False)
    linkedin_link = db.Column(db.String(255), nullable=False)

class AboutMeSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="A bit about me")
    content = db.Column(db.Text, nullable=False)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    years = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)  # Ссылка на картинку
    link_url = db.Column(db.String(255), nullable=False)   # Ссылка для перехода
    description = db.Column(db.Text, nullable=False)       # Описание проекта

    def __repr__(self):
        return f"<Project {self.description[:30]}...>"

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_github = db.Column(db.Boolean, default=True)  # Флаг видимости

    def __repr__(self):
        return f"<Settings show_github={self.show_github}>"

class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.Text, nullable=False)
    reviewer = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255), nullable=False)
    linkedin_url = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(355), nullable=True)

class ChatSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False, default="Default chatbot description")
    is_visible = db.Column(db.Boolean, default=True)

import json
from flask import current_app

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)  # JSON content
    published_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date of publication
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Новые поля
    image_url = db.Column(db.String(255), nullable=True)  # URL картинки
    teaser_text = db.Column(db.String(255), nullable=True)  # Тизер
    category = db.Column(db.String(100), nullable=True)  # Категория

    # Связь с пользователем
    user = db.relationship('User', backref=db.backref('created_pages', lazy=True))

    def get_content_blocks(self):
        try:
            # Декодируем JSON в список
            content_blocks = json.loads(self.content)
            if not isinstance(content_blocks, list):
                current_app.logger.error(f"Ошибка: содержимое для страницы '{self.slug}' не является списком.")
                return []
            return content_blocks
        except json.JSONDecodeError:
            current_app.logger.error(f"Ошибка при декодировании JSON для страницы '{self.slug}'.")
            return []
        except Exception as e:
            current_app.logger.error(f"Неизвестная ошибка при получении контент-блоков для страницы '{self.slug}': {str(e)}")
            return []

    def __repr__(self):
        return f"<Page {self.title}>"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    pages = db.relationship('Page', backref='author', lazy=True)