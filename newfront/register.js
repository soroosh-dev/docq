// API configuration
const REGISTER_URL = SERVER_URL + 'user/';

// Handle form submission
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    // Reset messages
    errorMessage.classList.add('d-none');
    successMessage.classList.add('d-none');

    // Validate passwords match
    if (password !== confirmPassword) {
        errorMessage.textContent = 'Passwords do not match';
        errorMessage.classList.remove('d-none');
        return;
    }

    // Validate password strength
    if (password.length < 8) {
        errorMessage.textContent = 'Password must be at least 8 characters long';
        errorMessage.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch(REGISTER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Show success message
            successMessage.textContent = 'Registration successful! Redirecting to login...';
            successMessage.classList.remove('d-none');

            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            // Handle specific error messages from the server
            if (data.username) {
                errorMessage.textContent = data.username[0];
            } else if (data.email) {
                errorMessage.textContent = data.email[0];
            } else if (data.password) {
                errorMessage.textContent = data.password[0];
            } else if (data.detail) {
                errorMessage.textContent = data.detail;
            } else {
                errorMessage.textContent = 'Registration failed. Please try again.';
            }
            errorMessage.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error during registration:', error);
        errorMessage.textContent = 'An error occurred. Please try again.';
        errorMessage.classList.remove('d-none');
    }
}); 