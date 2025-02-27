import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv

import openai  # Импортируем openai
from openai import AzureOpenAI

# Ваши локальные импорты
from models import db
from routes import app_routes
from admin import init_admin

load_dotenv()  # Загружаем переменные окружения из .env файла

os.environ["FLASK_APP"] = "app.py"

print("✅ Flask загружен и работает!")

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Настройка логирования
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

# Логирование данных формы при POST-запросах
@app.before_request
def log_request_data():
    if request.method == 'POST':
        app.logger.debug(f"Request headers: {request.headers}")
        app.logger.debug(f"Request data: {request.data}")

        if request.content_type == "application/json":
            json_data = request.get_json(silent=True)  # <-- Добавили silent=True
            app.logger.debug(f"Request JSON: {json_data}")


# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Инициализация клиента Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL", "https://sergei.openai.azure.com/"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE"),
    api_version="2024-05-01-preview"  # Убедись, что версия API актуальна
)

# Резюме Сергея Пастушенко
resume_text = """
Ты ИИ помощник, который отвечает на вопросы только касательно профессионального опыта Сергея Пастушенко на основе вот этого резюме:

Sergei Pastushenko
Communications and Intranet Manager
New York City, Authorized to Work, No Sponsorship Required, spastushenko85@gmail.com, 
646-359-7314, LinkedIn

SUMMARY
Communications professional with 15 years of experience. Skilled in implementing strategies at the intersection of HR, PR, Marketing, and IT to boost company business outcomes and employee NPS.

SKILLS
Communications Strategy; Intranet; DEI Initiatives; Media Relations; Employee Engagement; Internal Communications; Cross-functional Collaboration; Administrative Management; Events; Data Analytics; Video&Photo Editing; Digital Content; Copywriting; Document Workflow; Microsoft Office; SharePoint; Adobe Creative Suite; Asana; Slack; Trello; HTML; CSS; Java Script; VS Code; Salesforce; ERP Systems; Japanese language JLPT N4; English(C2); Russian (native)

EXPERIENCE
Intranet Manager, PEC Transportation Holding, pecom.ru, 03.2023 - 09.2023; Moscow, Russia
• Enhanced employee engagement through the implementation of communication strategies for a workforce of 12,000+ across 9 business units via email and intranet
• Revamped intranet UI, prototyped new HR services, ideas, contests and TV sections, improved gamification with 50+ features, and launched merchandise shop for employees
• Spearheaded inclusion program that resulted in a 20% increase in eNPS, encompassing training sessions, events, and Corporate University relaunch

Intranet and Community Manager, X5 Retail Group, 10.2020 - 02.2023; Moscow, Russia
• Managed internal communication, keeping 350,000 employees across 15 business units informed and aligned with corporate objectives
• Utilized data-driven insights to continuously improve employee engagement through targeted communication initiatives and direct marketing
• Supervised the merge of 5 intranet SharePoint platforms into an in-house intranet solution, improving employee resource accessibility and satisfaction

Internal Communications and Event Manager, Novikom Bank, 09.2018 - 03.2020; Moscow, Russia
• Created digital content for internal communications, connecting 1,300 employees via newsletters and the intranet, measuring success through tangible metrics and feedback
• Planned and conducted up to 30 events a year, driving employee involvement in corporate life and promoting corporate values, mission and culture
• Streamlined learning and development systems, maintaining and updating 50+ courses annually

PR, Communications and Marketing Manager, Deutsche Bank, 06.2010 - 01.2017; Moscow, Russia
• Collaborated with senior leadership in order to proactively interact with press requests for interviews, comments, and quotes, managing up to 50 inquiries from journalists monthly
• Composed bi-lingual content for internal channels, Corp TV, social media, press-releases and quarterly Newsletters with up to 20+ articles in each
• Organized business, corporate social responsibility and sustainability events, contributing to increased satisfaction of 1200 employees, shareholders and clients

EDUCATION and CERTIFICATES
Bachelor's Degree in Engineering, State Polytechnic University 09.2004 - 06.2009; Moscow, Russia
Academy of Professional Competencies, pedagogical diploma 06-09.2020; Moscow, Russia

Communications: External Communications Framework, Internal Communications Framework, Corporate Communications (2024)
Data analysis: Data-Driven Decisions, Prepare Data for Exploration, Google Data Analytics, Process Data from Dirty to Clean, Data Through the Art of Visualization (2024)
Web development: Introduction to Front-End Development, HTML and CSS in depth (2024)
"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message') if data else None

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Формирование чатов в новом формате
        messages = [
            {"role": "system", "content": "Ты помощник ИИ, отвечающий только на вопросы касательно профессионального опыта Сергея Пастушенко на основе его резюме. Отвечай очень коротко и по существу. Всегда отвечай от первого лица будто ты и есть Сергей Пастушенкою"},
            {"role": "user", "content": user_message},
            {"role": "user", "content": resume_text},  # Добавляем резюме как контекст
        ]

        # Создание завершения чата
        completion = client.chat.completions.create(
            model="gpt-35-turbo",  # Проверь правильность названия deployment в Azure
            messages=messages,
            max_tokens=100,
            temperature=0.7,
        )

        # Выводим структуру объекта completion
        print(completion)

        # Получение ответа от модели
        bot_reply = completion.choices[0].message.content.strip()
        return jsonify({"reply": bot_reply})

    except Exception as e:
        app.logger.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({"error": str(e)}), 500

# Регистрация маршрутов и админки
app.register_blueprint(app_routes)
init_admin(app)

# Настроим логирование ошибок
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Обработчик ошибки 404 (Страница не найдена)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

# Обработчик ошибки 500 (Внутренняя ошибка сервера)
@app.errorhandler(500)
def internal_server_error(error):
    logging.error(f"Ошибка 500: {error}")
    return render_template('errors/500.html', error=error), 500

# Обработчик всех других ошибок
@app.errorhandler(Exception)
def handle_exception(error):
    logging.error(f"Неизвестная ошибка: {error}")
    return render_template('errors/general.html', error=error), 500

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
