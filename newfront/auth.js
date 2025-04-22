// Authentication utilities
const API_URL = SERVER_URL+'user/token/';

// Check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

// Redirect to login if not authenticated
function checkAuth() {
    const currentPath = window.location.pathname;
    if (!isAuthenticated() && !currentPath.endsWith('login.html')) {
        window.location.href = 'login.html';
    } else if (isAuthenticated() && currentPath.endsWith('login.html')) {
        window.location.href = 'dashboard.html';
    }
}

// Handle login form submission
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            window.location.href = 'dashboard.html';
        } else {
            errorMessage.textContent = 'Invalid username or password';
            errorMessage.classList.remove('d-none');
        }
    } catch (error) {
        errorMessage.textContent = 'An error occurred. Please try again.';
        errorMessage.classList.remove('d-none');
    }
});

// Handle logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = 'login.html';
}

// Add auth token to fetch requests
function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return Promise.reject('No auth token');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    return fetch(url, { ...options, headers });
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', checkAuth); 