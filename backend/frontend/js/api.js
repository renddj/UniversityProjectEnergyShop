// api.js — общие функции для работы с бэкендом
// Этот файл подключается на каждой странице

// Адрес бэкенда — при деплое замени на реальный URL Railway
const API_URL = "";

// ──────────────────────────────────────────
// Работа с токеном (авторизация)
// ──────────────────────────────────────────

function getToken() {
    return localStorage.getItem("token");
}

function getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
}

// Запрос полной информации о текущем пользователе
async function fetchCurrentUser() {
    if (!isLoggedIn()) return null;
    try {
        return await apiRequest("GET", "/api/users/me");
    } catch (error) {
        console.error("Ошибка при получении данных пользователя:", error);
        return null;
    }
}

function saveAuth(token, username, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify({ username, role }));
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "index.html";
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUser();
    return user && user.role === "admin";
}

// ──────────────────────────────────────────
// Базовая функция запроса к API
// ──────────────────────────────────────────

async function apiRequest(method, endpoint, body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const response = await fetch(`${API_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Ошибка запроса");
    }
    return data;
}

// ──────────────────────────────────────────
// Обновление шапки сайта в зависимости от авторизации
// ──────────────────────────────────────────

function updateNavbar() {
    const user = getUser();
    const navAuth = document.getElementById("nav-auth");
    const navCart = document.getElementById("nav-cart");
    const navAdmin = document.getElementById("nav-admin");

    if (!navAuth) return; // На этой странице нет навбара

    if (user) {
        navAuth.innerHTML = `
            <span class="nav-username">👤 ${user.username}</span>
            <a href="#" onclick="logout()">Выйти</a>
        `;
        if (navCart) navCart.style.display = "inline";
        if (navAdmin && user.role === "admin") navAdmin.style.display = "inline";
    } else {
        navAuth.innerHTML = `<a href="login.html">Войти</a>`;
        if (navCart) navCart.style.display = "none";
        if (navAdmin) navAdmin.style.display = "none";
    }
}

