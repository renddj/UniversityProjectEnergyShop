# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import Optional, List
# import bcrypt
# import jwt
# import os
# from datetime import datetime, timedelta

# from database import get_db, engine
# import models

# # Создаём все таблицы в БД при запуске (если их нет)
# models.Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Energy Shop API", description="API интернет-магазина энергетиков")

# # CORS — разрешаем фронтенду обращаться к бэкенду
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # В продакшне укажи конкретный домен
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
# security = HTTPBearer(auto_error=False)


# # ──────────────────────────────────────────
# # Pydantic-схемы (структуры данных для API)
# # ──────────────────────────────────────────

# class UserRegister(BaseModel):
#     username: str
#     email: str
#     password: str

# class UserLogin(BaseModel):
#     email: str
#     password: str

# class ProductCreate(BaseModel):
#     name: str
#     brand: str
#     price: float
#     volume: str
#     short_description: str
#     full_description: str
#     image_url: str
#     in_stock: int = 1

# class ProductUpdate(BaseModel):
#     name: Optional[str] = None
#     brand: Optional[str] = None
#     price: Optional[float] = None
#     volume: Optional[str] = None
#     short_description: Optional[str] = None
#     full_description: Optional[str] = None
#     image_url: Optional[str] = None
#     in_stock: Optional[int] = None

# class CartItemAdd(BaseModel):
#     product_id: int
#     quantity: int = 1


# # ──────────────────────────────────────────
# # Вспомогательные функции
# # ──────────────────────────────────────────

# def hash_password(password: str) -> str:
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# def verify_password(password: str, hashed: str) -> bool:
#     return bcrypt.checkpw(password.encode(), hashed.encode())

# def create_token(user_id: int, role: str) -> str:
#     payload = {
#         "user_id": user_id,
#         "role": role,
#         "exp": datetime.utcnow() + timedelta(days=7)
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):
#     """Декодирует токен и возвращает текущего пользователя. Возвращает None если не авторизован."""
#     if not credentials:
#         return None
#     try:
#         payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
#         user = db.query(models.User).filter(models.User.id == payload["user_id"]).first()
#         return user
#     except Exception:
#         return None

# def require_auth(current_user = Depends(get_current_user)):
#     """Требует авторизации, иначе 401"""
#     if not current_user:
#         raise HTTPException(status_code=401, detail="Необходима авторизация")
#     return current_user

# def require_admin(current_user = Depends(get_current_user)):
#     """Требует роли администратора, иначе 403"""
#     if not current_user:
#         raise HTTPException(status_code=401, detail="Необходима авторизация")
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Недостаточно прав")
#     return current_user


# # ──────────────────────────────────────────
# # Эндпоинты: Авторизация
# # ──────────────────────────────────────────

# @app.post("/api/register", summary="Регистрация нового пользователя")
# def register(data: UserRegister, db: Session = Depends(get_db)):
#     # Проверяем, не занят ли email
#     if db.query(models.User).filter(models.User.email == data.email).first():
#         raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
#     if db.query(models.User).filter(models.User.username == data.username).first():
#         raise HTTPException(status_code=400, detail="Имя пользователя занято")

#     user = models.User(
#         username=data.username,
#         email=data.email,
#         password_hash=hash_password(data.password),
#         role="user"
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     token = create_token(user.id, user.role)
#     return {"token": token, "username": user.username, "role": user.role}


# @app.post("/api/login", summary="Вход в аккаунт")
# def login(data: UserLogin, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == data.email).first()
#     if not user or not verify_password(data.password, user.password_hash):
#         raise HTTPException(status_code=400, detail="Неверный email или пароль")

#     token = create_token(user.id, user.role)
#     return {"token": token, "username": user.username, "role": user.role}


# @app.get("/api/me", summary="Информация о текущем пользователе")
# def get_me(current_user = Depends(require_auth)):
#     return {"id": current_user.id, "username": current_user.username, "role": current_user.role}


# # ──────────────────────────────────────────
# # Эндпоинты: Товары
# # ──────────────────────────────────────────

# @app.get("/api/products", summary="Список всех товаров")
# def get_products(db: Session = Depends(get_db)):
#     products = db.query(models.Product).all()
#     return [
#         {
#             "id": p.id,
#             "name": p.name,
#             "brand": p.brand,
#             "price": p.price,
#             "volume": p.volume,
#             "short_description": p.short_description,
#             "image_url": p.image_url,
#             "in_stock": p.in_stock,
#         }
#         for p in products
#     ]


# @app.get("/api/products/{product_id}", summary="Подробная информация о товаре")
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Товар не найден")
#     return {
#         "id": product.id,
#         "name": product.name,
#         "brand": product.brand,
#         "price": product.price,
#         "volume": product.volume,
#         "short_description": product.short_description,
#         "full_description": product.full_description,
#         "image_url": product.image_url,
#         "in_stock": product.in_stock,
#     }


# @app.post("/api/products", summary="Добавить товар (только админ)")
# def create_product(data: ProductCreate, db: Session = Depends(get_db), admin = Depends(require_admin)):
#     product = models.Product(**data.dict())
#     db.add(product)
#     db.commit()
#     db.refresh(product)
#     return {"message": "Товар добавлен", "id": product.id}


# @app.put("/api/products/{product_id}", summary="Обновить товар (только админ)")
# def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), admin = Depends(require_admin)):
#     product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Товар не найден")

#     # Обновляем только те поля, которые переданы
#     for field, value in data.dict(exclude_none=True).items():
#         setattr(product, field, value)

#     db.commit()
#     return {"message": "Товар обновлён"}


# @app.delete("/api/products/{product_id}", summary="Удалить товар (только админ)")
# def delete_product(product_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
#     product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Товар не найден")
#     db.delete(product)
#     db.commit()
#     return {"message": "Товар удалён"}


# # ──────────────────────────────────────────
# # Эндпоинты: Корзина
# # ──────────────────────────────────────────

# @app.get("/api/cart", summary="Получить корзину текущего пользователя")
# def get_cart(db: Session = Depends(get_db), current_user = Depends(require_auth)):
#     items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
#     result = []
#     for item in items:
#         product = item.product
#         result.append({
#             "cart_item_id": item.id,
#             "quantity": item.quantity,
#             "product": {
#                 "id": product.id,
#                 "name": product.name,
#                 "brand": product.brand,
#                 "price": product.price,
#                 "volume": product.volume,
#                 "image_url": product.image_url,
#             }
#         })
#     return result


# @app.post("/api/cart", summary="Добавить товар в корзину")
# def add_to_cart(data: CartItemAdd, db: Session = Depends(get_db), current_user = Depends(require_auth)):
#     # Проверяем, существует ли товар
#     product = db.query(models.Product).filter(models.Product.id == data.product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Товар не найден")

#     # Если товар уже в корзине — увеличиваем количество
#     existing = db.query(models.CartItem).filter(
#         models.CartItem.user_id == current_user.id,
#         models.CartItem.product_id == data.product_id
#     ).first()

#     if existing:
#         existing.quantity += data.quantity
#     else:
#         item = models.CartItem(user_id=current_user.id, product_id=data.product_id, quantity=data.quantity)
#         db.add(item)

#     db.commit()
#     return {"message": "Товар добавлен в корзину"}


# @app.delete("/api/cart/{item_id}", summary="Удалить товар из корзины")
# def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user = Depends(require_auth)):
#     item = db.query(models.CartItem).filter(
#         models.CartItem.id == item_id,
#         models.CartItem.user_id == current_user.id
#     ).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Элемент корзины не найден")
#     db.delete(item)
#     db.commit()
#     return {"message": "Товар удалён из корзины"}


# # ──────────────────────────────────────────
# # Заполнение тестовыми данными
# # ──────────────────────────────────────────

# @app.post("/api/seed", summary="Заполнить БД тестовыми товарами и админом")
# def seed_db(db: Session = Depends(get_db)):
#     # Создаём администратора если нет
#     if not db.query(models.User).filter(models.User.email == "admin@energyshop.ru").first():
#         admin = models.User(
#             username="admin",
#             email="admin@energyshop.ru",
#             password_hash=hash_password("admin123"),
#             role="admin"
#         )
#         db.add(admin)

#     # Тестовые товары
#     sample_products = [
#         {
#             "name": "VOLT ZERO Классик", "brand": "VOLT ZERO", "price": 129.0, "volume": "0.5л",
#             "short_description": "Классический энергетик с мягким вкусом цитруса",
#             "full_description": "VOLT ZERO Классик — это идеальный выбор для тех, кто ищет стабильный заряд энергии без лишних эффектов. Содержит таурин, кофеин и витамины группы B. Мягкий цитрусовый вкус не перебивает, а освежает. Подходит для учёбы, работы и активного отдыха.",
#             "image_url": "https://placehold.co/400x400/1a1a2e/ffffff?text=VOLT+ZERO",
#             "in_stock": 1
#         },
#         {
#             "name": "VOLT ZERO Ледяная Буря", "brand": "VOLT ZERO", "price": 139.0, "volume": "0.5л",
#             "short_description": "Охлаждающий вкус мяты и арбуза",
#             "full_description": "VOLT ZERO Ледяная Буря — лимитированная линейка с эффектом охлаждения. Сочетание мяты и арбуза создаёт ощущение свежести даже в жаркий день. Повышенное содержание витамина C дополнительно поддерживает иммунитет.",
#             "image_url": "https://placehold.co/400x400/0f3460/ffffff?text=VOLT+ICE",
#             "in_stock": 1
#         },
#         {
#             "name": "KRASCH Оригинал", "brand": "KRASCH", "price": 119.0, "volume": "0.45л",
#             "short_description": "Жёсткий заряд для тех кто не останавливается",
#             "full_description": "KRASCH Оригинал — энергетик без компромиссов. Максимально допустимое содержание кофеина, таурин и экстракт гуараны. Вкус ягод с кислинкой. Не рекомендуется людям чувствительным к кофеину, беременным и детям до 18 лет.",
#             "image_url": "https://placehold.co/400x400/e94560/ffffff?text=KRASCH",
#             "in_stock": 1
#         },
#         {
#             "name": "KRASCH Манго-Огонь", "brand": "KRASCH", "price": 129.0, "volume": "0.45л",
#             "short_description": "Тропический манго с острым послевкусием",
#             "full_description": "KRASCH Манго-Огонь — для тех, кто любит экзотику. Сочный манго в начале и лёгкая острота в конце. Состав идентичен оригиналу, но вкусовой профиль совершенно другой. Отлично подходит для ночных сессий и интенсивных тренировок.",
#             "image_url": "https://placehold.co/400x400/f5a623/1a1a1a?text=KRASCH+MANGO",
#             "in_stock": 1
#         },
#         {
#             "name": "NEXUS Focus", "brand": "NEXUS", "price": 159.0, "volume": "0.33л",
#             "short_description": "Для концентрации и умственной работы",
#             "full_description": "NEXUS Focus — это не просто энергетик, а ноотропный напиток. Содержит L-теанин, кофеин и экстракт женьшеня. Снижает уровень тревожности, повышает концентрацию и улучшает память. Без сахара, без синтетических красителей. Идеален для студентов и работников умственного труда.",
#             "image_url": "https://placehold.co/400x400/2d6a4f/ffffff?text=NEXUS+FOCUS",
#             "in_stock": 1
#         },
#         {
#             "name": "NEXUS Night Mode", "brand": "NEXUS", "price": 169.0, "volume": "0.33л",
#             "short_description": "Ночная формула — не спать, но без дрожи",
#             "full_description": "NEXUS Night Mode разработан специально для ночной работы. Умеренная доза кофеина в сочетании с магнием и L-глицином не даёт задремать, но и не вызывает нервозности. Вкус черники и лаванды создаёт расслабляющую атмосферу при максимальной продуктивности.",
#             "image_url": "https://placehold.co/400x400/16213e/a8dadc?text=NEXUS+NIGHT",
#             "in_stock": 0
#         },
#         {
#             "name": "ПУЛЬС Арбуз", "brand": "ПУЛЬС", "price": 99.0, "volume": "0.5л",
#             "short_description": "Доступный отечественный энергетик",
#             "full_description": "ПУЛЬС Арбуз — российский энергетик по доступной цене. Без излишеств: таурин, кофеин, витамин B12. Сочный арбузный вкус делает его одним из самых популярных летних энергетиков. Продаётся во всех крупных сетях страны.",
#             "image_url": "https://placehold.co/400x400/c77dff/1a1a1a?text=ПУЛЬС",
#             "in_stock": 1
#         },
#         {
#             "name": "ПУЛЬС Лесные ягоды", "brand": "ПУЛЬС", "price": 99.0, "volume": "0.5л",
#             "short_description": "Вкус черники, малины и смородины",
#             "full_description": "ПУЛЬС Лесные ягоды — один из первых вкусов линейки ПУЛЬС. Классическое сочетание лесных ягод полюбилось миллионам потребителей. Состав стандартный, качество стабильное, цена честная.",
#             "image_url": "https://placehold.co/400x400/6d23b6/ffffff?text=ПУЛЬС+ЯГОДЫ",
#             "in_stock": 1
#         },
#     ]

#     if db.query(models.Product).count() == 0:
#         for p in sample_products:
#             db.add(models.Product(**p))

#     db.commit()
#     return {"message": "База данных заполнена тестовыми данными", "admin_email": "admin@energyshop.ru", "admin_password": "admin123"}


# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse

# app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
# app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

# @app.get("/", response_class=FileResponse)
# def serve_index():
#     return "frontend/index.html"

# @app.get("/{page}.html", response_class=FileResponse)
# def serve_page(page: str):
#     return f"frontend/{page}.html"

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

from database import get_db, engine
import models

# Создаём все таблицы в БД при запуске (если их нет)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Energy Shop API", description="API интернет-магазина энергетиков")

# CORS — разрешаем фронтенду обращаться к бэкенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне укажи конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
security = HTTPBearer(auto_error=False)


# ──────────────────────────────────────────
# Pydantic-схемы (структуры данных для API)
# ──────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProductCreate(BaseModel):
    name: str
    brand: str
    price: float
    volume: str
    short_description: str
    full_description: str
    image_url: str
    in_stock: int = 1

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    volume: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: Optional[int] = None

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


# ──────────────────────────────────────────
# Вспомогательные функции
# ──────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Декодирует токен и возвращает текущего пользователя. Возвращает None если не авторизован."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user = db.query(models.User).filter(models.User.id == payload["user_id"]).first()
        return user
    except Exception:
        return None

def require_auth(current_user = Depends(get_current_user)):
    """Требует авторизации, иначе 401"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    return current_user

def require_admin(current_user = Depends(get_current_user)):
    """Требует роли администратора, иначе 403"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return current_user


# ──────────────────────────────────────────
# Эндпоинты: Авторизация
# ──────────────────────────────────────────

@app.post("/api/register", summary="Регистрация нового пользователя")
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Проверяем, не занят ли email
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Имя пользователя занято")

    user = models.User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.role)
    return {"token": token, "username": user.username, "role": user.role}


@app.post("/api/login", summary="Вход в аккаунт")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    token = create_token(user.id, user.role)
    return {"token": token, "username": user.username, "role": user.role}


@app.get("/api/me", summary="Информация о текущем пользователе")
def get_me(current_user = Depends(require_auth)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}


# ──────────────────────────────────────────
# Эндпоинты: Товары
# ──────────────────────────────────────────

@app.get("/api/products", summary="Список всех товаров")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": p.price,
            "volume": p.volume,
            "short_description": p.short_description,
            "image_url": p.image_url,
            "in_stock": p.in_stock,
        }
        for p in products
    ]


@app.get("/api/products/{product_id}", summary="Подробная информация о товаре")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "volume": product.volume,
        "short_description": product.short_description,
        "full_description": product.full_description,
        "image_url": product.image_url,
        "in_stock": product.in_stock,
    }


@app.post("/api/products", summary="Добавить товар (только админ)")
def create_product(data: ProductCreate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    product = models.Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "Товар добавлен", "id": product.id}


@app.put("/api/products/{product_id}", summary="Обновить товар (только админ)")
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Обновляем только те поля, которые переданы
    for field, value in data.dict(exclude_none=True).items():
        setattr(product, field, value)

    db.commit()
    return {"message": "Товар обновлён"}


@app.delete("/api/products/{product_id}", summary="Удалить товар (только админ)")
def delete_product(product_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    db.delete(product)
    db.commit()
    return {"message": "Товар удалён"}


# ──────────────────────────────────────────
# Эндпоинты: Корзина
# ──────────────────────────────────────────

@app.get("/api/cart", summary="Получить корзину текущего пользователя")
def get_cart(db: Session = Depends(get_db), current_user = Depends(require_auth)):
    items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    result = []
    for item in items:
        product = item.product
        result.append({
            "cart_item_id": item.id,
            "quantity": item.quantity,
            "product": {
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "price": product.price,
                "volume": product.volume,
                "image_url": product.image_url,
            }
        })
    return result


@app.post("/api/cart", summary="Добавить товар в корзину")
def add_to_cart(data: CartItemAdd, db: Session = Depends(get_db), current_user = Depends(require_auth)):
    # Проверяем, существует ли товар
    product = db.query(models.Product).filter(models.Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Если товар уже в корзине — увеличиваем количество
    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == data.product_id
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        item = models.CartItem(user_id=current_user.id, product_id=data.product_id, quantity=data.quantity)
        db.add(item)

    db.commit()
    return {"message": "Товар добавлен в корзину"}


@app.delete("/api/cart/{item_id}", summary="Удалить товар из корзины")
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user = Depends(require_auth)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")
    db.delete(item)
    db.commit()
    return {"message": "Товар удалён из корзины"}


# ──────────────────────────────────────────
# Заполнение тестовыми данными
# ──────────────────────────────────────────

@app.post("/api/seed", summary="Заполнить БД тестовыми товарами и админом")
def seed_db(db: Session = Depends(get_db)):
    # Удаляем старые данные в правильном порядке из-за внешних ключей
    db.query(models.OrderItem).delete()
    db.query(models.Order).delete()
    db.query(models.CartItem).delete()
    db.query(models.Product).delete()
    db.query(models.User).delete()
    db.commit()

    # Создаём администратора
    try:
        admin = models.User(
            username="admin",
            email="admin@energyshop.ru",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
    except Exception:
        db.rollback()
        raise

    # Тестовые товары
    sample_products = [
        {
            "name": "VOLT ZERO Классик", "brand": "VOLT ZERO", "price": 129.0, "volume": "0.5л",
            "short_description": "Классический энергетик с мягким вкусом цитруса",
            "full_description": "VOLT ZERO Классик — это идеальный выбор для тех, кто ищет стабильный заряд энергии без лишних эффектов. Содержит таурин, кофеин и витамины группы B. Мягкий цитрусовый вкус не перебивает, а освежает. Подходит для учёбы, работы и активного отдыха.",
            "image_url": "https://placehold.co/400x400/1a1a2e/ffffff?text=VOLT+ZERO",
            "in_stock": 1
        },
        {
            "name": "VOLT ZERO Ледяная Буря", "brand": "VOLT ZERO", "price": 139.0, "volume": "0.5л",
            "short_description": "Охлаждающий вкус мяты и арбуза",
            "full_description": "VOLT ZERO Ледяная Буря — лимитированная линейка с эффектом охлаждения. Сочетание мяты и арбуза создаёт ощущение свежести даже в жаркий день. Повышенное содержание витамина C дополнительно поддерживает иммунитет.",
            "image_url": "https://placehold.co/400x400/0f3460/ffffff?text=VOLT+ICE",
            "in_stock": 1
        },
        {
            "name": "KRASCH Оригинал", "brand": "KRASCH", "price": 119.0, "volume": "0.45л",
            "short_description": "Жёсткий заряд для тех кто не останавливается",
            "full_description": "KRASCH Оригинал — энергетик без компромиссов. Максимально допустимое содержание кофеина, таурин и экстракт гуараны. Вкус ягод с кислинкой. Не рекомендуется людям чувствительным к кофеину, беременным и детям до 18 лет.",
            "image_url": "https://placehold.co/400x400/e94560/ffffff?text=KRASCH",
            "in_stock": 1
        },
        {
            "name": "KRASCH Манго-Огонь", "brand": "KRASCH", "price": 129.0, "volume": "0.45л",
            "short_description": "Тропический манго с острым послевкусием",
            "full_description": "KRASCH Манго-Огонь — для тех, кто любит экзотику. Сочный манго в начале и лёгкая острота в конце. Состав идентичен оригиналу, но вкусовой профиль совершенно другой. Отлично подходит для ночных сессий и интенсивных тренировок.",
            "image_url": "https://placehold.co/400x400/f5a623/1a1a1a?text=KRASCH+MANGO",
            "in_stock": 1
        },
        {
            "name": "NEXUS Focus", "brand": "NEXUS", "price": 159.0, "volume": "0.33л",
            "short_description": "Для концентрации и умственной работы",
            "full_description": "NEXUS Focus — это не просто энергетик, а ноотропный напиток. Содержит L-теанин, кофеин и экстракт женьшеня. Снижает уровень тревожности, повышает концентрацию и улучшает память. Без сахара, без синтетических красителей. Идеален для студентов и работников умственного труда.",
            "image_url": "https://placehold.co/400x400/2d6a4f/ffffff?text=NEXUS+FOCUS",
            "in_stock": 1
        },
        {
            "name": "NEXUS Night Mode", "brand": "NEXUS", "price": 169.0, "volume": "0.33л",
            "short_description": "Ночная формула — не спать, но без дрожи",
            "full_description": "NEXUS Night Mode разработан специально для ночной работы. Умеренная доза кофеина в сочетании с магнием и L-глицином не даёт задремать, но и не вызывает нервозности. Вкус черники и лаванды создаёт расслабляющую атмосферу при максимальной продуктивности.",
            "image_url": "https://placehold.co/400x400/16213e/a8dadc?text=NEXUS+NIGHT",
            "in_stock": 0
        },
        {
            "name": "ПУЛЬС Арбуз", "brand": "ПУЛЬС", "price": 99.0, "volume": "0.5л",
            "short_description": "Доступный отечественный энергетик",
            "full_description": "ПУЛЬС Арбуз — российский энергетик по доступной цене. Без излишеств: таурин, кофеин, витамин B12. Сочный арбузный вкус делает его одним из самых популярных летних энергетиков. Продаётся во всех крупных сетях страны.",
            "image_url": "https://placehold.co/400x400/c77dff/1a1a1a?text=ПУЛЬС",
            "in_stock": 1
        },
        {
            "name": "ПУЛЬС Лесные ягоды", "brand": "ПУЛЬС", "price": 99.0, "volume": "0.5л",
            "short_description": "Вкус черники, малины и смородины",
            "full_description": "ПУЛЬС Лесные ягоды — один из первых вкусов линейки ПУЛЬС. Классическое сочетание лесных ягод полюбилось миллионам потребителей. Состав стандартный, качество стабильное, цена честная.",
            "image_url": "https://placehold.co/400x400/6d23b6/ffffff?text=ПУЛЬС+ЯГОДЫ",
            "in_stock": 1
        },
    ]

    try:
        for p in sample_products:
            db.add(models.Product(**p))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"message": "База данных заполнена тестовыми данными", "admin_email": "admin@energyshop.ru", "admin_password": "admin123"}


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/", response_class=FileResponse)
def serve_index():
    return "frontend/index.html"

@app.get("/{page}.html", response_class=FileResponse)
def serve_page(page: str):
    return f"frontend/{page}.html"

# ──────────────────────────────────────────
# Эндпоинты: Заказы
# ──────────────────────────────────────────

class OrderItemIn(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str
    delivery_method: str
    delivery_address: str
    payment_method: str
    comment: Optional[str] = None
    items: List[OrderItemIn]
    subtotal: float
    delivery_cost: float
    total: float


def _create_order(data: OrderCreate, db: Session, user_id: Optional[int] = None):
    """Общая логика создания заказа (для авторизованных и гостей)."""
    order = models.Order(
        user_id=user_id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_email=data.customer_email,
        delivery_method=data.delivery_method,
        delivery_address=data.delivery_address,
        payment_method=data.payment_method,
        comment=data.comment,
        subtotal=data.subtotal,
        delivery_cost=data.delivery_cost,
        total=data.total,
        status="new",
    )
    db.add(order)
    db.flush()  # чтобы получить order.id до commit

    for item in data.items:
        db.add(models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price,
        ))

    db.commit()
    db.refresh(order)
    return order


@app.post("/api/orders", summary="Создать заказ (авторизованный пользователь)")
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    # Очищаем серверную корзину после оформления
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    order = _create_order(data, db, user_id=current_user.id)
    return {"order_id": order.id, "status": order.status}


@app.post("/api/orders/guest", summary="Создать заказ (гость, без авторизации)")
def create_order_guest(data: OrderCreate, db: Session = Depends(get_db)):
    order = _create_order(data, db, user_id=None)
    return {"order_id": order.id, "status": order.status}


@app.delete("/api/cart/clear", summary="Очистить корзину текущего пользователя")
def clear_cart(db: Session = Depends(get_db), current_user=Depends(require_auth)):
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Корзина очищена"}


@app.get("/api/orders", summary="Мои заказы (авторизованный пользователь)")
def get_my_orders(db: Session = Depends(get_db), current_user=Depends(require_auth)):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "items_count": sum(i.quantity for i in o.items),
        }
        for o in orders
    ]