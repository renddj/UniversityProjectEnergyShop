# ⚡ ЭнергоМаркет

Учебный проект — интернет-магазин энергетических напитков.

**Стек:** FastAPI (Python) + HTML/CSS/JS + PostgreSQL  
**Хостинг:** Railway.app

---

## Структура проекта

```
energy-shop/
├── backend/
│   ├── main.py          # FastAPI — все маршруты API
│   ├── models.py        # Модели базы данных (таблицы)
│   ├── database.py      # Подключение к PostgreSQL
│   ├── requirements.txt # Зависимости Python
│   └── Procfile         # Команда запуска для Railway
└── frontend/
    ├── index.html       # Главная страница (список товаров)
    ├── product.html     # Страница конкретного товара
    ├── cart.html        # Корзина
    ├── login.html       # Вход и регистрация
    ├── about.html       # О компании
    ├── admin.html       # Панель администратора
    ├── css/style.css    # Стили
    └── js/api.js        # Общие функции для запросов к API
```

---

## Запуск локально (на своём компьютере)

### 1. Установи Python и PostgreSQL

- Python: https://python.org (версия 3.10+)
- PostgreSQL: https://postgresql.org

### 2. Создай базу данных

Открой pgAdmin или psql и выполни:
```sql
CREATE DATABASE energyshop;
CREATE USER energyuser WITH PASSWORD 'energypass';
GRANT ALL PRIVILEGES ON DATABASE energyshop TO energyuser;
```

### 3. Настрой бэкенд

```bash
cd backend

# Создай виртуальное окружение (изолированная среда для Python)
python -m venv venv

# Активируй его (Windows):
venv\Scripts\activate

# Активируй его (Mac/Linux):
source venv/bin/activate

# Установи зависимости
pip install -r requirements.txt
```

### 4. Задай переменную окружения с адресом БД

Windows (PowerShell):
```powershell
$env:DATABASE_URL="postgresql://energyuser:energypass@localhost/energyshop"
```

Mac/Linux:
```bash
export DATABASE_URL="postgresql://energyuser:energypass@localhost/energyshop"
```

### 5. Запусти бэкенд

```bash
uvicorn main:app --reload
```

Бэкенд запустится на http://localhost:8000  
Документация API: http://localhost:8000/docs  ← очень удобно для проверки!

### 6. Заполни базу тестовыми данными

Открой в браузере:
```
http://localhost:8000/api/seed
```

Это создаст:
- 8 товаров
- Аккаунт администратора: `admin@energyshop.ru` / `admin123`

### 7. Открой фронтенд

Просто открой файл `frontend/index.html` в браузере.  
Или используй расширение **Live Server** в VS Code.

---

## Деплой на Railway

### Шаг 1 — GitHub

```bash
# В корне проекта (папка energy-shop)
git init
git add .
git commit -m "первый коммит"

# Создай репозиторий на github.com, затем:
git remote add origin https://github.com/ТВО_ИМЯ/energy-shop.git
git push -u origin main
```

### Шаг 2 — Railway

1. Зайди на https://railway.app и войди через GitHub
2. Нажми **"New Project"** → **"Deploy from GitHub repo"**
3. Выбери свой репозиторий `energy-shop`
4. Railway спросит какую папку деплоить — укажи `backend`
5. Нажми **"Add Service"** → **"Database"** → **"PostgreSQL"**
6. Railway автоматически добавит переменную `DATABASE_URL` — ничего не нужно делать вручную!
7. В настройках сервиса (Variables) добавь переменную:
   - `SECRET_KEY` = любая длинная случайная строка, например `mySuperSecretKey2024`

### Шаг 3 — Обнови адрес API во фронтенде

В файле `frontend/js/api.js` замени строку:
```javascript
const API_URL = "http://localhost:8000";
```
на URL твоего Railway-сервиса, например:
```javascript
const API_URL = "https://energy-shop-production.up.railway.app";
```

### Шаг 4 — Фронтенд

Фронтенд — это просто HTML-файлы. Их можно:
- Хостить на **GitHub Pages** (бесплатно): Settings → Pages → Deploy from branch → /frontend
- Или положить в папку `backend/static/` и раздавать через FastAPI

### Шаг 5 — Заполни тестовыми данными

После деплоя открой в браузере:
```
https://ТВО_URL.railway.app/api/seed
```

---

## Роли пользователей

| Роль | Что может |
|------|-----------|
| Гость | Смотреть товары |
| Пользователь | Смотреть товары + корзина |
| Администратор | Всё выше + добавлять/редактировать/удалять товары |

Сменить роль пользователя на admin можно через psql:
```sql
UPDATE users SET role = 'admin' WHERE email = 'почта@пример.ru';
```

---

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
