from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template, request, Blueprint, session, url_for
import psycopg2
lab5 =Blueprint("lab5", __name__)

# Подключение библиотеки psycopg2 для взаимодействия с PostgreSQL
def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="knowledge_base",
        user="egor_knowledge_base",
        password="admin")
    return conn;

# Закрытие соединения с БД
def dbClose(cursor, connection):
    cursor.close()
    connection.close()

# Обработчик маршрута "/lab5"
@lab5.route("/lab5")
def main():
    visibleUser = "Аноним"
    # Проверка наличия имени пользователя в сессии
    if 'username' in session:
        visibleUser = session['username']
    return render_template('lab5.html', username=visibleUser)

# Обработчик маршрута "/lab5/users"
@lab5.route("/lab5/users")
def users():
    # Подключение к БД
    conn = dbConnect()
    cur = conn.cursor()
    # Выполнение SQL-запроса для получения имен пользователей
    cur.execute("SELECT username FROM users;")
    result = cur.fetchall()
    # Закрытие соединения с БД
    dbClose(cur, conn)

    # Создание списка имен пользователей из результата запроса
    user_names = [user[0] for user in result]

    # Возвращение HTML-страницы, передавая список имен пользователей в шаблон
    return render_template('users.html', users=user_names)

# Обработчик маршрута "/lab5/register"
@lab5.route('/lab5/register', methods=["GET", "POST"])
def registerPage():
    errors = ""
    visibleUser = session.get("username", "Аноним")

    # Обработка GET-запроса
    if request.method == "GET":
        return render_template("register.html", errors=errors, username=visibleUser)

    username = request.form.get("username")
    password = request.form.get("password")

    # Проверка наличия значений username и password
    if not (username or password):
        errors = "Пожалуйста, заполните все поля"
        print(errors)
        return render_template("register.html", errors=errors)

    # Хеширование пароля и подключение к БД
    hashPassword = generate_password_hash(password)
    conn = dbConnect()
    cur = conn.cursor()

    # Проверка наличия пользователя с указанным именем
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    if cur.fetchone() is not None:
        errors = "Пользователь с данным именем уже существует"
        dbClose(cur, conn)
        return render_template("register.html", errors=errors)

    # Вставка нового пользователя в БД
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashPassword))
    conn.commit()
    dbClose(cur, conn)
    return redirect("/lab5/login")

# Обработчик маршрута "/lab5/login"
@lab5.route('/lab5/login', methods=["GET", "POST"])
def loginPage():
    errors = ""
    visibleUser = "Аноним"
    visibleUser = session.get('username', '')

    # Обработка GET-запроса
    if request.method == "GET":
        return render_template("login2.html", errors=errors, username=visibleUser)

    username = request.form.get("username")
    password = request.form.get("password")

    # Проверка наличия значений username и password
    if not (username or password):
        errors = "Пожалуйста, заполните все поля"
        return render_template("login2.html", errors=errors, username=visibleUser)

    conn = dbConnect()
    cur = conn.cursor()

    # Выполнение SQL-запроса для проверки логина и пароля
    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()

    # Проверка результата запроса
    if result is None:
        errors = "Неправильный логин или пароль"
        dbClose(cur, conn)
        return render_template("login.html", errors=errors)

    userID, hashPassword = result
    # Проверка совпадения хешированного пароля
    if check_password_hash(hashPassword, password):
        session['id'] = userID
        session['username'] = username
        dbClose(cur, conn)
        return redirect("/lab5")
    else:
        errors = "Неправильный логин или пароль"
        return render_template("login2.html", errors=errors)

# Обработчик маршрута "/lab5/new_article"
@lab5.route("/lab5/new_article", methods=["GET", "POST"])
def createArticle():
    errors = ""
    visibleUser = session.get("username", "Аноним")
    userID = session.get("id")

    # Проверка авторизации пользователя
    if userID is not None:
        # Обработка GET-запроса
        if request.method == "GET":
            return render_template("new_article.html", username=visibleUser, errors="")

        # Обработка POST-запроса
        if request.method == "POST":
            text_article = request.form.get("text_article")
            title = request.form.get("title_article")

            # Проверка наличия текста и заголовка
            if not text_article or not title:
                errors = "Заполните все поля"
                return render_template("new_article.html", errors=errors, username=visibleUser)

            # Подключение к БД
            conn = dbConnect()
            cur = conn.cursor()

            # Выполнение SQL-запроса для вставки новой статьи
            cur.execute("INSERT INTO articles (user_id, title, article_text) VALUES (%s, %s, %s) RETURNING id",
                        (userID, title, text_article))
            
            # Получение ID вновь созданной статьи
            new_article_id = cur.fetchone()[0]
            
            # Фиксация изменений в БД и закрытие соединения
            conn.commit()
            dbClose(cur, conn)

            # Редирект на страницу новой статьи
            return redirect(url_for('lab5.getArticle', article_id=new_article_id))

    # Редирект на страницу входа, если пользователь не авторизован
    return redirect("/lab5/login")

# Обработчик маршрута "/lab5/articles/<string:article_id>"
@lab5.route('/lab5/articles/<string:article_id>')
def getArticle(article_id):
    userID = session.get("id")
    # Проверка авторизации пользователя
    if userID is not None:
        # Подключение к БД
        conn = dbConnect()
        cur = conn.cursor()

        # Выполнение SQL-запроса для получения статьи
        cur.execute("SELECT title, article_text FROM articles WHERE id = %s AND user_id = %s", (article_id, userID))

        # Получение одной строки результата запроса
        articleBody = cur.fetchone()

        # Закрытие соединения с БД
        dbClose(cur, conn)

        # Проверка наличия статьи и отображение шаблона
        if articleBody is not None:
            text = articleBody[1].splitlines()
            return render_template("articleN.html", article_text=text, article_title=articleBody[0], username=session.get("username"))

    # Возвращение сообщения "Not found!", если статья не найдена
    return "Not found!"

# Add this route to your existing Flask application
@lab5.route('/lab5/user_articles')
def userArticles():
    # Check if the user is authenticated
    userID = session.get("id")
    if userID is not None:
        # Connect to the database
        conn = dbConnect()
        cur = conn.cursor()

        # Execute SQL query to retrieve user's articles
        cur.execute("SELECT id, title, article_text FROM articles WHERE user_id = %s", (userID,))
        articles = [{'id': article[0], 'title': article[1], 'text': article[2]} for article in cur.fetchall()]

        # Close the database connection
        dbClose(cur, conn)

        # Render the user_articles.html template with the retrieved articles
        return render_template('user_articles.html', articles=articles, username=session.get("username"))

    # Redirect to the login page if the user is not authenticated
    return redirect("/lab5/login")

# Добавьте этот роут в ваше существующее приложение Flask
@lab5.route('/lab5/logout')
def logout():
    # Очистите сессию или убедитесь, что у вас есть механизм удаления JWT-токена
    # Ниже приведен пример для Flask-Login, который использует сессии
    session.clear()

    # После очистки сессии, выполните перенаправление на страницу входа
    return redirect("/lab5/login")


# Обработчик маршрута "/lab5/add_to_favorites/<int:article_id>"
@lab5.route("/lab5/add_to_favorites/<int:article_id>")
def addToFavorites(article_id):
    userID = session.get("id")

    # Проверка авторизации пользователя
    if userID is not None:
        # Подключение к БД
        conn = dbConnect()
        cur = conn.cursor()

        # Выполнение SQL-запроса для добавления статьи в избранное
        cur.execute("UPDATE articles SET is_favorite = true WHERE id = %s AND user_id = %s", (article_id, userID))

        # Фиксация изменений в БД и закрытие соединения
        conn.commit()
        dbClose(cur, conn)

        # Редирект на страницу, откуда пришел запрос (или на другую страницу)
        return redirect(request.referrer)

    # Редирект на страницу входа, если пользователь не авторизован
    return redirect("/lab5/login")


# Обработчик маршрута "/lab5/publish_article/<int:article_id>"
@lab5.route("/lab5/publish_article/<int:article_id>")
def publishArticle(article_id):
    userID = session.get("id")

    # Проверка авторизации пользователя
    if userID is not None:
        # Подключение к БД
        conn = dbConnect()
        cur = conn.cursor()

        # Выполнение SQL-запроса для опубликования статьи
        cur.execute("UPDATE articles SET is_public = true WHERE id = %s AND user_id = %s", (article_id, userID))

        # Фиксация изменений в БД и закрытие соединения
        conn.commit()
        dbClose(cur, conn)

        # Редирект на страницу, откуда пришел запрос (или на другую страницу)
        return redirect(request.referrer)

    # Редирект на страницу входа, если пользователь не авторизован
    return redirect("/lab5/login")


# Обработчик маршрута "/lab5/like_article/<int:article_id>"
@lab5.route("/lab5/like_article/<int:article_id>")
def likeArticle(article_id):
    userID = session.get("id")

    # Проверка авторизации пользователя
    if userID is not None:
        # Подключение к БД
        conn = dbConnect()
        cur = conn.cursor()

        # Выполнение SQL-запроса для увеличения счетчика лайков
        cur.execute("UPDATE articles SET likes = likes + 1 WHERE id = %s", (article_id,))

        # Фиксация изменений в БД и закрытие соединения
        conn.commit()
        dbClose(cur, conn)

        # Редирект на страницу, откуда пришел запрос (или на другую страницу)
        return redirect(request.referrer)

    # Редирект на страницу входа, если пользователь не авторизован
    return redirect("/lab5/login")
