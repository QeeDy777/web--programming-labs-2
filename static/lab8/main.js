// Функция для заполнения списка курсов
function fillCourseList() {
    // Запрос на сервер для получения списка курсов
    fetch('/lab8/api/courses/')
        .then(function (data) {
            return data.json();
        })
        .then(function (courses) {
            // Получаем элемент tbody, куда будем добавлять строки с курсами
            let tbody = document.getElementById('course-list');
            // Очищаем содержимое tbody
            tbody.innerHTML = '';
            // Проходим по каждому курсу и создаем соответствующую строку в таблице
            for (let i = 0; i < courses.length; i++) {
                let tr = document.createElement('tr');

                // Создаем ячейки с информацией о курсе
                let tdName = document.createElement('td');
                tdName.innerText = courses[i].name;

                let tdVideos = document.createElement('td');
                tdVideos.innerText = courses[i].videos;

                let tdPrice = document.createElement('td');
                tdPrice.innerText = courses[i].price !== undefined ? courses[i].price : 'бесплатно';

                let tdDATA = document.createElement('td');
                // Преобразуем дату создания в локальное время и добавляем в ячейку
                let serverDate = new Date(courses[i].createdAt);
                let localDate = new Date(serverDate.getTime() + serverDate.getTimezoneOffset() * 60000);
                tdDATA.innerText = localDate.toLocaleDateString();

                // Создаем кнопки для редактирования и удаления курса
                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';
                editButton.onclick = function () {
                    editCourse(i, courses[i]);
                };

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                delButton.onclick = function () {
                    deleteCourse(i);
                };

                let tdActions = document.createElement('td');
                // Добавляем кнопки в ячейку
                tdActions.append(editButton);
                tdActions.append(delButton);

                // Добавляем все ячейки в строку
                tr.append(tdName);
                tr.append(tdVideos);
                tr.append(tdPrice);
                tr.append(tdActions);
                tr.append(tdDATA);
                // Добавляем строку в tbody
                tbody.append(tr);
            }
        });
}

// Функция для удаления курса
function deleteCourse(num) {
    // Запрашиваем подтверждение перед удалением
    if (!confirm('Вы точно хотите удалить курс?')) {
        return;
    }

    // Отправляем запрос на сервер для удаления курса
    fetch('/lab8/api/courses/' + num, { method: 'DELETE' })
        .then(function () {
            // После успешного удаления обновляем список курсов
            fillCourseList();
        })
        .catch(function (error) {
            // В случае ошибки выводим сообщение в консоль
            console.error('Ошибка при удалении курса:', error);
        });
}

// Функция для отображения модального окна
function showModal() {
    document.querySelector('div.modal').style.display = 'block';
}

// Функция для скрытия модального окна
function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
}

// Функция для закрытия модального окна
function cancel() {
    hideModal();
}

// Функция для добавления нового курса
function addCourse() {
    // Создаем пустой объект курса и очищаем поля в модальном окне
    const course = {};
    delete course.createdAt;
    document.getElementById('num').value = '';
    document.getElementById('name').value = '';
    document.getElementById('videos').value = '';
    document.getElementById('price').value = '';
    showModal();
}

// Функция для отправки данных курса на сервер
function sendCourse() {
    // Получаем значения полей из модального окна
    const num = document.getElementById('num').value;
    const name = document.getElementById('name').value;
    const videos = document.getElementById('videos').value;
    const price = document.getElementById('price').value;

    // Проверяем, если цена равна 0, устанавливаем ее как 'бесплатно'
    const normalizedPrice = price === '0' ? 'бесплатно' : price;

    // Проверяем заполнены ли обязательные поля
    if (!name || !videos) {
        alert('Заполните все поля!');
        return;
    }

    // Формируем объект с данными курса
    const course = {
        name: name,
        videos: videos,
        price: normalizedPrice,
    };

    // Формируем URL и метод запроса в зависимости от наличия номера курса
    const url = '/lab8/api/courses/' + num;
    const method = num ? 'PUT' : 'POST';

    // Отправляем запрос на сервер
    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(course),
    })
    .then(function () {
        // После успешной отправки обновляем список курсов и скрываем модальное окно
        fillCourseList();
        hideModal();
    });
}

// Функция для редактирования курса
function editCourse(num, course) {
    // Заполняем поля в модальном окне данными выбранного курса
    document.getElementById('num').value = num;
    document.getElementById('name').value = course.name;
    document.getElementById('videos').value = course.videos;
    document.getElementById('price').value = course.price === 'бесплатно' ? '0' : course.price;
    delete course.createdAt;
    showModal();
}