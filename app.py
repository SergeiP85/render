import logging
import os
from urllib import request
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from models import db
from routes import app_routes
from admin import init_admin
from azure.ai.openai import ChatCompletionClient # type: ignore
from azure.core.credentials import AzureKeyCredential # type: ignore

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
def log_form_data():
    if request.method == 'POST':
        # Логируем данные формы в консоль
        print(f"Form data: {request.form}")
        app.logger.debug(f"Form data: {request.form}")

# Указываем URL базы данных напрямую, например, SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Используем переменную окружения для секретного ключа
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Можно задать default, если переменной нет

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Настройки Azure OpenAI
AZURE_API_KEY = os.getenv('AZURE_API_KEY', '123')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT', '123')
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME', '123')

client = ChatCompletionClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_API_KEY))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Формируем запрос к Azure OpenAI
    response = client.get_chat_completions(
        deployment_id="portfoliobot",
        messages=[{"role": "user", "content": user_message}]
    )

    bot_reply = response.result.choices[0].message['content']
    return jsonify({"reply": bot_reply})

# Регистрация маршрутов и админки
app.register_blueprint(app_routes)
init_admin(app)

# Настроим логирование ошибок
logging.basicConfig(filename='error.log', level=logging.ERROR)  # ✅ Теперь это работает правильно

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
    app.config['FLASK_DEBUG'] = True
    app.run(host='0.0.0.0', port=10000)
