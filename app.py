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
        app.logger.debug(f"Request JSON: {request.get_json()}")

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Инициализация клиента Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL", "https://sergei.openai.azure.com/"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE"),
    api_version="2024-05-01-preview"  # Убедись, что версия API актуальна
)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message') if data else None

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Формирование чатов в новом формате
        messages = [
            {"role": "system", "content": "Ты помощник ИИ, помогай пользователям с вопросами по резюме, навыкам и опыту работы."},
            {"role": "user", "content": user_message}
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
