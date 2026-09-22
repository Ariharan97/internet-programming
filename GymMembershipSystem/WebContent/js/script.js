/* =========================================================
   FITNESS HUB - CLIENT-SIDE INTERACTIVITY & FORM VALIDATION
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Registration Form Validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        initRegisterValidation(registerForm);
    }

    // 2. Initialize Login Form Validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        initLoginValidation(loginForm);
    }

    // 3. Auto-populate selected membership plan from URL query param
    const planSelect = document.getElementById('membership');
    if (planSelect) {
        const urlParams = new URLSearchParams(window.location.search);
        const planParam = urlParams.get('plan');
        if (planParam) {
            const normalizedPlan = planParam.charAt(0).toUpperCase() + planParam.slice(1).toLowerCase();
            for (let option of planSelect.options) {
                if (option.value.toLowerCase() === normalizedPlan.toLowerCase()) {
                    option.selected = true;
                    break;
                }
            }
        }
    }

    // 4. Handle Alert Banner Messages from URL parameters
    handleUrlAlerts();
});

/**
 * Client-Side Registration Form Validation
 */
function initRegisterValidation(form) {
    const fullName = document.getElementById('name');
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');
    const password = document.getElementById('password');
    const membership = document.getElementById('membership');

    form.addEventListener('submit', (event) => {
        let isValid = true;

        // Validate Full Name
        if (!fullName.value.trim()) {
            showError('nameError', 'Full name is required');
            isValid = false;
        } else {
            hideError('nameError');
        }

        // Validate Email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            showError('emailError', 'Email address is required');
            isValid = false;
        } else if (!emailRegex.test(email.value.trim())) {
            showError('emailError', 'Please enter a valid email address');
            isValid = false;
        } else {
            hideError('emailError');
        }

        // Validate Phone Number (Exactly 10 digits)
        const phoneRegex = /^[0-9]{10}$/;
        const cleanPhone = phone.value.trim().replace(/\D/g, '');
        if (!cleanPhone) {
            showError('phoneError', 'Phone number is required');
            isValid = false;
        } else if (!phoneRegex.test(cleanPhone)) {
            showError('phoneError', 'Phone number must be exactly 10 numeric digits');
            isValid = false;
        } else {
            hideError('phoneError');
        }

        // Validate Password (Minimum 6 characters)
        if (!password.value) {
            showError('passwordError', 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            showError('passwordError', 'Password must be at least 6 characters long');
            isValid = false;
        } else {
            hideError('passwordError');
        }

        // Validate Membership Selection
        if (!membership.value || membership.value === '') {
            showError('membershipError', 'Please select a membership plan');
            isValid = false;
        } else {
            hideError('membershipError');
        }

        if (!isValid) {
            event.preventDefault(); // Stop form submission if invalid
        }
    });

    // Real-time phone number constraint (numbers only)
    if (phone) {
        phone.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
        });
    }
}

/**
 * Client-Side Login Form Validation
 */
function initLoginValidation(form) {
    const email = document.getElementById('email');
    const password = document.getElementById('password');

    form.addEventListener('submit', (event) => {
        let isValid = true;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            showError('emailError', 'Email address is required');
            isValid = false;
        } else if (!emailRegex.test(email.value.trim())) {
            showError('emailError', 'Please enter a valid email address');
            isValid = false;
        } else {
            hideError('emailError');
        }

        if (!password.value) {
            showError('passwordError', 'Password is required');
            isValid = false;
        } else {
            hideError('passwordError');
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}

/**
 * Show error message below input field
 */
function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

/**
 * Hide error message below input field
 */
function hideError(elementId) {
    const errorEl = document.getElementById(elementId);
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
}

/**
 * Parses URL search params and displays notification alerts
 */
function handleUrlAlerts() {
    const alertBox = document.getElementById('alertBanner');
    if (!alertBox) return;

    const params = new URLSearchParams(window.location.search);
    
    if (params.has('registered') && params.get('registered') === 'true') {
        alertBox.className = 'alert-banner success';
        alertBox.innerHTML = '<span>✓</span> Registration successful! Please log in below.';
        alertBox.style.display = 'flex';
    } else if (params.has('loggedout') && params.get('loggedout') === 'true') {
        alertBox.className = 'alert-banner success';
        alertBox.innerHTML = '<span>✓</span> You have logged out successfully.';
        alertBox.style.display = 'flex';
    } else if (params.has('error')) {
        alertBox.className = 'alert-banner error';
        alertBox.innerHTML = `<span>⚠️</span> ${decodeURIComponent(params.get('error'))}`;
        alertBox.style.display = 'flex';
    }
}
