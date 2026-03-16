# ЭнергоМаркет

Учебный проект по дисциплине "Веб-разработка". Интернет-магазин энергетических напитков.

## Стек

- **Бэкенд:** Python, FastAPI, SQLAlchemy
- **Фронтенд:** HTML, CSS, JavaScript
- **БД:** PostgreSQL
- **Хостинг:** Railway

## Структура проекта

```
energy-shop/
├── backend/
│   ├── main.py          # маршруты API
│   ├── models.py        # модели БД
│   ├── database.py      # подключение к БД
│   ├── requirements.txt
│   └── Procfile
└── frontend/
    ├── index.html       # список товаров
    ├── product.html     # страница товара
    ├── cart.html        # корзина
    ├── login.html       # вход / регистрация
    ├── about.html       # о компании
    ├── admin.html       # панель администратора
    ├── css/style.css
    └── js/api.js
```

## Запуск

### Требования
- Python 3.10+
- PostgreSQL

### Установка

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

Создать БД в PostgreSQL:
```sql
CREATE DATABASE energyshop;
```

Задать переменную окружения:
```bash
DATABASE_URL=postgresql://user:password@localhost/energyshop
```

Запустить сервер:
```bash
uvicorn main:app --reload
```

Документация API доступна по адресу `http://localhost:8000/docs`

Заполнить БД тестовыми данными: `GET /api/seed`  
Тестовый аккаунт администратора: `admin@energyshop.ru` / `admin123`

### Фронтенд

Открыть `frontend/index.html` в браузере или использовать Live Server в VS Code.

## Функционал

- Просмотр каталога товаров с фильтрацией по бренду
- Страница отдельного товара с подробным описанием
- Регистрация и авторизация (JWT)
- Корзина для авторизованных пользователей
- Админ-панель для управления товарами (CRUD)

## Роли

| Роль | Права |
|------|-------|
| Гость | Просмотр товаров |
| Пользователь | Просмотр + корзина |
| Администратор | Полное управление товарами |

## API эндпоинты

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | /api/register | Регистрация | Все |
| POST | /api/login | Вход | Все |
| GET | /api/me | Мои данные | Авторизованные |
| GET | /api/products | Список товаров | Все |
| GET | /api/products/{id} | Один товар | Все |
| POST | /api/products | Добавить товар | Только админ |
| PUT | /api/products/{id} | Обновить товар | Только админ |
| DELETE | /api/products/{id} | Удалить товар | Только админ |
| GET | /api/cart | Моя корзина | Авторизованные |
| POST | /api/cart | Добавить в корзину | Авторизованные |
| DELETE | /api/cart/{id} | Удалить из корзины | Авторизованные |
| POST | /api/seed | Заполнить БД | Все (только для теста!) |