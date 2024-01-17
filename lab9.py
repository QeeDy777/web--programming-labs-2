from flask import Blueprint, render_template, request, abort, jsonify, url_for, redirect
from datetime import datetime

lab9 = Blueprint('lab9', __name__)

@lab9.route('/lab9/')
def main():
    return render_template('lab9/index.html')

@lab9.app_errorhandler(404)
def not_found(e):
    return '❄️❄️❄️Нет такой страницы, вернуться обратно <a href="/menu">Меню</a> ❄️❄️❄️', 404


@lab9.route('/lab9/500')
def main1():
    return render_template('lab9/500.html'), 500

@lab9.route('/lab9/new_year_card', methods=['GET', 'POST'])
def new_year_card():
    if request.method == 'POST':
        recipient_name = request.form.get('recipient_name')
        recipient_gender = request.form.get('recipient_gender')
        sender_name = request.form.get('sender_name')

        # Тут можно обработать данные и создать текст открытки

        # Перенаправление на URL с параметрами
        return redirect(url_for('lab9.show_card', recipient_name=recipient_name,
                                recipient_gender=recipient_gender, sender_name=sender_name))

    return render_template('lab9/new_year_card_form.html')

@lab9.route('/lab9/show_card')
def show_card():
    # Получение параметров из URL
    recipient_name = request.args.get('recipient_name')
    recipient_gender = request.args.get('recipient_gender')
    sender_name = request.args.get('sender_name')

    # Создание текста открытки
    card_text = f"С Новым Годом, {recipient_name}! Желаю быть счастлив{'ой' if recipient_gender == 'female' else 'ым'}! С наилучшими пожеланиями, {sender_name}."

    return render_template('lab9/show_card.html', card_text=card_text)