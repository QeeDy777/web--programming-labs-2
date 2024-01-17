# Импорт необходимых модулей Flask
from flask import Blueprint, render_template, request, abort, jsonify
from datetime import datetime

# Создание Blueprint с именем "lab8"
lab8 = Blueprint('lab8', __name__)

# Маршрут для отображения главной страницы
@lab8.route('/lab8/')
def main():
    return render_template('lab8/index.html')

# Список курсов с начальными данными
courses = [
    {"name": "c++", "videos": 3, "price": 3000},
    {"name": "basic", "videos": 30, "price": 0},
    {"name": "c#", "videos": 8}
]

# Маршрут для получения списка курсов
@lab8.route('/lab8/api/courses/', methods=['GET'])
def get_courses():
    return jsonify(courses)

# Маршрут для получения информации о конкретном курсе по индексу
@lab8.route('/lab8/api/courses/<int:course_num>', methods=['GET'])
def get_course(course_num):
    if 0 <= course_num < len(courses):
        return jsonify(courses[course_num])
    else:
        abort(404)

# Маршрут для удаления курса по индексу
@lab8.route('/lab8/api/courses/<int:course_num>', methods=['DELETE'])
def del_course(course_num):
    if 0 <= course_num < len(courses):
        del courses[course_num]
        return '', 204  # Возвращаем успешный HTTP-статус без содержимого
    else:
        abort(404)

# Маршрут для обновления информации о курсе по индексу
@lab8.route('/lab8/api/courses/<int:course_num>', methods=['PUT'])
def put_course(course_num):
    if 0 <= course_num < len(courses):
        # Получаем данные о курсе из JSON-запроса
        course = request.get_json()
        # Обновляем информацию о курсе, используя переданные данные
        courses[course_num]['name'] = course.get('name', courses[course_num]['name'])
        courses[course_num]['videos'] = course.get('videos', courses[course_num]['videos'])
        courses[course_num]['price'] = course.get('price', None)  
        return jsonify(courses[course_num])
    else:
        abort(404)

# Маршрут для добавления нового курса
@lab8.route('/lab8/api/courses/', methods=['POST'])
def add_course():
    # Получаем данные о новом курсе из JSON-запроса
    course = request.get_json()
    # Добавляем дополнительные данные, такие как дата создания
    course['createdAt'] = datetime.now()
    course['price'] = course.get('price', None)  
    # Добавляем новый курс в список
    courses.append(course)
    return {"num": len(courses)-1}  # Возвращаем номер нового курса в списке