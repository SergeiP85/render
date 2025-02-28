from flask import current_app
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models import Page, db, AboutMeSection, Experience, HeroContent, User, Project, Settings, ChatSettings, Reference
import json
from flask import jsonify
from flask_login import current_user

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/blog')
def blog():
    pages = Page.query.all()  # Получаем все страницы
    return render_template('blog.html', pages=pages)

# Главная страница
@app_routes.route('/')
def index():
    hero = HeroContent.query.first()
    about_me_section = AboutMeSection.query.first()
    experiences = Experience.query.all()
    projects = Project.query.all()
    settings = Settings.query.first()  # Получаем настройки
    references = Reference.query.all()
    chat_settings = ChatSettings.query.first()
    


    return render_template('index.html', hero=hero, about_me_section=about_me_section, experiences=experiences, projects=projects, chat_settings=chat_settings, show_github=settings.show_github if settings else False, references=references)

@app_routes.route('/page/<slug>')
def show_page(slug):
    if not slug:
        current_app.logger.warning("Пустой slug при попытке загрузить страницу.")
        return render_template('errors/404.html'), 404

    try:
        page = Page.query.filter_by(slug=slug).first_or_404()

        # Получаем контент-блоки с проверкой
        content_blocks = page.get_content_blocks()

        # Пытаемся извлечь необходимые данные
        image_url = None
        teaser_text = None
        category = "Uncategorized"

        for block in content_blocks:
            if block['type'] == 'full_image' and not image_url:
                image_url = block['image_url']
            elif block['type'] == 'text_header':
                teaser_text = block['subtitle']
            elif block['type'] == 'category':
                category = block['text']

        return render_template('page_template.html', page=page, content_blocks=content_blocks,
                               image_url=image_url, teaser_text=teaser_text, category=category)

    except Exception as e:
        current_app.logger.error(f"Ошибка при загрузке страницы с slug '{slug}': {str(e)}")
        return render_template('errors/500.html'), 500




@app_routes.route('/admin/page/create', methods=['GET', 'POST'])
@login_required
def create_page():
    pages = Page.query.all()

    if request.method == 'POST':
        slug = request.form['slug']
        title = request.form['title']
        content = request.form['content']
        image_url = request.form.get('image_url')  # Получаем URL картинки
        teaser_text = request.form.get('teaser_text')  # Получаем тизер
        category = request.form.get('category')  # Получаем категорию

        # Проверка на уникальность slug
        if Page.query.filter_by(slug=slug).first():
            return render_template('pages_list.html', pages=pages)

        # Создание нового объекта страницы с автором и новыми полями
        new_page = Page(
            slug=slug, 
            title=title, 
            content=content, 
            user_id=current_user.id,  # Связка с текущим пользователем
            image_url=image_url,  # Устанавливаем URL картинки
            teaser_text=teaser_text,  # Устанавливаем тизер
            category=category  # Устанавливаем категорию
        )
        db.session.add(new_page)
        db.session.commit()

        return redirect(url_for('admin.index'))

    return render_template('create_page.html')


@app_routes.route('/admin/pages', methods=['GET'])
@login_required
def pages_list():
    # Получаем все страницы из базы данных
    pages = Page.query.all()
    return render_template('pages_list.html', pages=pages)

# Редактирование страницы
@app_routes.route('/admin/page/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_page(id):
    page = Page.query.get_or_404(id)

    if request.method == 'POST':
        page.slug = request.form['slug']
        page.title = request.form['title']
        page.content = request.form['content']

        db.session.commit()

        return redirect(url_for('admin.index'))

    return render_template('edit_page.html', page=page)

# Удаление страницы
@app_routes.route('/page/delete/<int:id>', methods=['POST'])
@login_required
def delete_page(id):
    page = Page.query.get_or_404(id)
    pages = Page.query.all()
    db.session.delete(page)
    db.session.commit()


    return render_template('pages_list.html', pages=pages)

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    print("Request content-type:", request.content_type)
    print("Raw request data:", request.get_data())  # Покажет весь POST-запрос
    print("Form data:", request.form)  # Покажет распарсенные данные формы
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.index'))
    return render_template('login.html')

@app_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app_routes.login'))

@app_routes.route('/add_reference', methods=['POST'])
def add_reference():
    quote = request.form.get('quote')
    reviewer = request.form.get('reviewer')
    position = request.form.get('position')
    linkedin_url = request.form.get('linkedin_url')
    image_url = request.form.get('image_url')

    new_reference = Reference(
        quote=quote, reviewer=reviewer, position=position,
        linkedin_url=linkedin_url, image_url=image_url
    )
    db.session.add(new_reference)
    db.session.commit()
    
    return redirect(url_for('app_routes.references'))
