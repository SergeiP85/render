import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv

import openai  # Импортируем openai
# from openai.error import OpenAIError

# Ваши локальные импорты
from models import db
from routes import app_routes
from admin import init_admin

load_dotenv()  # Загружаем переменные окружения из .env файла

# Устанавливаем переменную окружения FLASK_APP для миграций (если нужно)
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

# Указываем URL базы данных напрямую, например, SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Используем переменную окружения для секретного ключа
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Настройка клиента OpenAI с использованием Azure
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Получаем ключ из переменной окружения
openai.api_type = "azure"  # Указываем, что используем Azure

# Маршрут для обработки сообщений чат-бота
@app.route("/chat", methods=["POST"])
def chat():
    # Получаем JSON данные из запроса
    data = request.get_json()
    
    # Извлекаем сообщение пользователя
    user_message = data.get('message') if data else None

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Отправка сообщения в Azure OpenAI с новым API
        response = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": user_message}],
            model="gpt-35-turbo",  # Укажите модель (например, gpt-4o)
        )

        bot_reply = response['choices'][0]['message']['content'].strip()  # Получаем текст ответа
        return jsonify({"reply": bot_reply})

    except openai.error.OpenAIError as e:
        app.logger.error(f"Ошибка при обращении к OpenAI API: {e}")
        return jsonify({"error": "Ошибка при обращении к OpenAI API"}), 500
    
    except Exception as e:
        print("Отправляем запрос в OpenAI API...")
        app.logger.error(f"Неизвестная ошибка: {e}")
        return jsonify({"error": "Неизвестная ошибка"}), 500
        

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
