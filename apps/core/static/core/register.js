// API configuration
const REGISTER_URL = SERVER_URL + 'user/';

// Handle registration form submission
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    const errorDiv = document.getElementById('registerError');
    const successDiv = document.getElementById('registerSuccess');

    // Reset messages
    errorDiv.classList.add('d-none');
    successDiv.classList.add('d-none');

    // Validate password
    if (password !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.classList.remove('d-none');
        return;
    }

    if (password.length < 8) {
        errorDiv.textContent = 'Password must be at least 8 characters long';
        errorDiv.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch(REGISTER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        successDiv.textContent = 'Registration successful! Redirecting to login...';
        successDiv.classList.remove('d-none');

        // Redirect to login page after 2 seconds
        setTimeout(() => {
            window.location.href = '/login/';
        }, 2000);

    } catch (error) {
        console.error('Registration error:', error);
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('d-none');
    }
}); 