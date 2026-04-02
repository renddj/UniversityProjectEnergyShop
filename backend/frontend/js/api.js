// // api.js — общие функции для работы с бэкендом
// // Этот файл подключается на каждой странице

// // Адрес бэкенда — при деплое замени на реальный URL Railway
// const API_URL = "";

// // ──────────────────────────────────────────
// // Работа с токеном (авторизация)
// // ──────────────────────────────────────────

// function getToken() {
//     return localStorage.getItem("token");
// }

// function getUser() {
//     const user = localStorage.getItem("user");
//     return user ? JSON.parse(user) : null;
// }

// function saveAuth(token, username, role) {
//     localStorage.setItem("token", token);
//     localStorage.setItem("user", JSON.stringify({ username, role }));
// }

// function logout() {
//     localStorage.removeItem("token");
//     localStorage.removeItem("user");
//     window.location.href = "index.html";
// }

// function isLoggedIn() {
//     return !!getToken();
// }

// function isAdmin() {
//     const user = getUser();
//     return user && user.role === "admin";
// }

// // ──────────────────────────────────────────
// // Базовая функция запроса к API
// // ──────────────────────────────────────────

// async function apiRequest(method, endpoint, body = null) {
//     const headers = { "Content-Type": "application/json" };
//     const token = getToken();
//     if (token) {
//         headers["Authorization"] = `Bearer ${token}`;
//     }

//     const config = { method, headers };
//     if (body) config.body = JSON.stringify(body);

//     const response = await fetch(`${API_URL}${endpoint}`, config);
//     const data = await response.json();

//     if (!response.ok) {
//         throw new Error(data.detail || "Ошибка запроса");
//     }
//     return data;
// }

// // ──────────────────────────────────────────
// // Обновление шапки сайта в зависимости от авторизации
// // ──────────────────────────────────────────

// function updateNavbar() {
//     const user = getUser();
//     const navAuth = document.getElementById("nav-auth");
//     const navCart = document.getElementById("nav-cart");
//     const navAdmin = document.getElementById("nav-admin");

//     if (!navAuth) return; // На этой странице нет навбара

//     if (user) {
//         navAuth.innerHTML = `
//             <span class="nav-username">👤 ${user.username}</span>
//             <a href="#" onclick="logout()">Выйти</a>
//         `;
//         if (navCart) navCart.style.display = "inline";
//         if (navAdmin && user.role === "admin") navAdmin.style.display = "inline";
//     } else {
//         navAuth.innerHTML = `<a href="login.html">Войти</a>`;
//         if (navCart) navCart.style.display = "none";
//         if (navAdmin) navAdmin.style.display = "none";
//     }
// }

// // Вызываем при загрузке каждой страницы
// document.addEventListener("DOMContentLoaded", updateNavbar);

// api.js — общие функции для работы с бэкендом

const API_URL = "";  // При деплое замени на реальный URL Railway

// ──────────────────────────────────────────
// Авторизация
// ──────────────────────────────────────────

function getToken()   { return localStorage.getItem("token"); }
function getUser()    { const u = localStorage.getItem("user"); return u ? JSON.parse(u) : null; }
function isLoggedIn() { return !!getToken(); }
function isAdmin()    { const u = getUser(); return u && u.role === "admin"; }

function saveAuth(token, username, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify({ username, role }));
    mergeGuestCartOnLogin();   // сливаем гостевую корзину после входа
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "index.html";
}

// ──────────────────────────────────────────
// Базовый запрос к API
// ──────────────────────────────────────────

async function apiRequest(method, endpoint, body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const response = await fetch(`${API_URL}${endpoint}`, config);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Ошибка запроса");
    return data;
}

// ──────────────────────────────────────────
// Гостевая корзина (localStorage)
// Используется когда пользователь НЕ авторизован
// ──────────────────────────────────────────

function getGuestCart() {
    try { return JSON.parse(localStorage.getItem("guest_cart") || "[]"); }
    catch { return []; }
}

function saveGuestCart(cart) {
    localStorage.setItem("guest_cart", JSON.stringify(cart));
    updateCartBadge();
}

function addToGuestCart(product) {
    const cart = getGuestCart();
    const existing = cart.find(item => item.product.id === product.id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ cart_item_id: `guest_${product.id}`, quantity: 1, product });
    }
    saveGuestCart(cart);
}

function removeFromGuestCart(productId) {
    saveGuestCart(getGuestCart().filter(item => item.product.id !== productId));
}

function clearGuestCart() {
    localStorage.removeItem("guest_cart");
    updateCartBadge();
}

// После входа — перекладываем гостевую корзину на сервер
async function mergeGuestCartOnLogin() {
    const guestCart = getGuestCart();
    if (guestCart.length === 0) return;
    for (const item of guestCart) {
        try {
            await apiRequest("POST", "/api/cart", { product_id: item.product.id, quantity: item.quantity });
        } catch (_) {}
    }
    clearGuestCart();
}

// Единый метод добавления в корзину (гость или авторизованный)
async function addToCartUnified(product, onSuccess) {
    if (isLoggedIn()) {
        try {
            await apiRequest("POST", "/api/cart", { product_id: product.id, quantity: 1 });
            updateCartBadge();
            if (onSuccess) onSuccess();
        } catch (e) { alert("Ошибка: " + e.message); }
    } else {
        addToGuestCart(product);
        if (onSuccess) onSuccess();
    }
}

// ──────────────────────────────────────────
// Счётчик товаров на иконке корзины
// ──────────────────────────────────────────

async function updateCartBadge() {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    let count = 0;
    if (isLoggedIn()) {
        try {
            const items = await apiRequest("GET", "/api/cart");
            count = items.reduce((sum, i) => sum + i.quantity, 0);
        } catch (_) {}
    } else {
        count = getGuestCart().reduce((sum, i) => sum + i.quantity, 0);
    }
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-flex" : "none";
}

// ──────────────────────────────────────────
// Обновление шапки сайта
// ──────────────────────────────────────────

function updateNavbar() {
    const user    = getUser();
    const navAuth = document.getElementById("nav-auth");
    const navAdmin = document.getElementById("nav-admin");

    if (!navAuth) return;

    if (user) {
        navAuth.innerHTML = `
            <span class="nav-username">👤 ${user.username}</span>
            <a href="#" onclick="logout()">Выйти</a>
        `;
        if (navAdmin && user.role === "admin") navAdmin.style.display = "inline";
    } else {
        navAuth.innerHTML = `<a href="login.html">Войти</a>`;
        if (navAdmin) navAdmin.style.display = "none";
    }

    // Корзина всегда видна (и гостям тоже)
    updateCartBadge();
}

document.addEventListener("DOMContentLoaded", updateNavbar);