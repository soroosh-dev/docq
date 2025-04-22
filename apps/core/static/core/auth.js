// API configuration
const LOGIN_URL = SERVER_URL + 'user/token/';
const LOGOUT_URL = SERVER_URL + 'user/logout/';

// Handle login form submission
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');

    try {
        const response = await fetch(LOGIN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access);
        window.location.href = '/dashboard/';
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Invalid username or password';
        errorDiv.classList.remove('d-none');
    }
});

// Handle logout
function logout() {
    fetchWithAuth(LOGOUT_URL, {
        method: 'POST'
    }).then(() => {
        localStorage.removeItem('token');
        window.location.href = '/login/';
    }).catch(error => {
        console.error('Logout error:', error);
        localStorage.removeItem('token');
        window.location.href = '/login/';
    });
} 