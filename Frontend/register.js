document.getElementById('registrationForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get form values
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const documentId = document.getElementById('documentid').value.trim();
    const dob = document.getElementById('dob').value;

    // Clear previous errors
    clearErrors();

    // Validate form
    let isValid = true;

    if (!fullName) {
        showError('fullName', 'Full name is required');
        isValid = false;
    }

    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError('email', 'Please enter a valid email');
        isValid = false;
    }

    if (!password) {
        showError('password', 'Password is required');
        isValid = false;
    } else if (password.length < 8) {
        showError('password', 'Password must be at least 8 characters');
        isValid = false;
    }

    if (!confirmPassword) {
        showError('confirmPassword', 'Please confirm your password');
        isValid = false;
    } else if (password !== confirmPassword) {
        showError('confirmPassword', 'Passwords do not match');
        isValid = false;
    }

    if (!documentId) {
        showError('documentid', 'Document ID is required');
        isValid = false;
    }

    if (!dob) {
        showError('dob', 'Date of birth is required');
        isValid = false;
    }

    if (isValid) {
        const userData = {
            fullName,
            email,
            documentId,
            dob,
            registeredAt: new Date().toISOString()
        };

        // Save user data (you may change to localStorage or real API)
        sessionStorage.setItem('currentUser', JSON.stringify(userData));

        // Redirect
        window.location.href = 'verifyid.html';
    }
});

// Show error below the field
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.createElement('div');
    error.className = 'error';
    error.textContent = message;
    field.insertAdjacentElement('afterend', error);
    field.style.borderColor = '#e74c3c';
}

// Clear all previous errors
function clearErrors() {
    document.querySelectorAll('.error').forEach(el => el.remove());
    document.querySelectorAll('input').forEach(input => input.style.borderColor = '#ccc');
}

// Email validation pattern
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// // Dark mode toggle
document.getElementById('themeToggle').addEventListener('click', function () {
    const isDarkMode = document.documentElement.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
});

// // File preview
// document.getElementById('docUpload').addEventListener('change', function (event) {
//     const file = event.target.files[0];
//     const preview = document.getElementById('preview');
//     preview.innerHTML = '';

//     if (file && file.type.startsWith('image/')) {
//         const reader = new FileReader();
//         reader.onload = function (e) {
//             const img = document.createElement('img');
//             img.src = e.target.result;
//             preview.appendChild(img);
//         };
//         reader.readAsDataURL(file);
//     }
// });