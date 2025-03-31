// Reference to the authentication service
const auth = firebase.auth();

// DOM elements
const errorMessage = document.getElementById('error-message');

// Handle signup form submission
if (document.getElementById('signupForm')) {
    const signupForm = document.getElementById('signupForm');
    
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get user info
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Clear previous error messages
        errorMessage.textContent = '';
        
        // Validate password length
        if (password.length < 6) {
            errorMessage.textContent = 'Password must be at least 6 characters';
            return;
        }
        
        // Create user with email and password
        auth.createUserWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Update the user's profile with their name
                return userCredential.user.updateProfile({
                    displayName: name
                });
            })
            .then(() => {
                // Redirect to homepage after successful signup
                window.location.href = 'index.html';
            })
            .catch((error) => {
                // Handle errors
                errorMessage.textContent = error.message;
            });
    });
}

// Handle login form submission
if (document.getElementById('loginForm')) {
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get user info
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Clear previous error messages
        errorMessage.textContent = '';
        
        // Sign in with email and password
        auth.signInWithEmailAndPassword(email, password)
            .then(() => {
                // Redirect to homepage after successful login
                window.location.href = 'index.html';
            })
            .catch((error) => {
                // Handle errors
                errorMessage.textContent = error.message;
            });
    });
    
    // Handle password reset
    const resetPassword = document.getElementById('reset-password');
    
    resetPassword.addEventListener('click', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        if (!email) {
            errorMessage.textContent = 'Please enter your email address';
            return;
        }
        
        // Send password reset email
        auth.sendPasswordResetEmail(email)
            .then(() => {
                errorMessage.textContent = 'Password reset email sent. Please check your inbox.';
                errorMessage.style.color = '#10B981'; // Green color for success message
            })
            .catch((error) => {
                errorMessage.textContent = error.message;
            });
    });
}

// Check authentication state
auth.onAuthStateChanged((user) => {
    // You can use this to update the UI based on authentication state
    const currentPage = window.location.pathname.split('/').pop();
    
    if (user) {
        // User is signed in
        // Add user profile link to navbar if signed in
        const navbarItems = document.querySelectorAll('.hidden.md\\:flex.items-center.space-x-8');
        if (navbarItems.length > 0) {
            // Check if user menu already exists
            if (!document.getElementById('userProfileLink')) {
                const userProfileElement = document.createElement('a');
                userProfileElement.id = 'userProfileLink';
                userProfileElement.href = '#';
                userProfileElement.className = 'flex items-center text-gray-700 hover:text-primary';
                
                // Add user icon and name
                userProfileElement.innerHTML = `
                    <i class="ri-user-line mr-1"></i>
                    <span>${user.displayName || 'Profile'}</span>
                `;
                
                // Add logout button
                const logoutBtn = document.createElement('a');
                logoutBtn.href = '#';
                logoutBtn.className = 'ml-8 text-gray-700 hover:text-primary';
                logoutBtn.innerHTML = '<i class="ri-logout-box-line mr-1"></i> Logout';
                logoutBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    auth.signOut().then(() => {
                        window.location.href = 'index.html';
                    });
                });
                
                navbarItems[0].appendChild(userProfileElement);
                navbarItems[0].appendChild(logoutBtn);
            }
        }
        
        // If on login or signup page, redirect to home
        if (currentPage === 'login.html' || currentPage === 'signup.html') {
            window.location.href = 'index.html';
        }
    } else {
        // No user is signed in
        // Remove user profile link from navbar if signed out
        const userProfileLink = document.getElementById('userProfileLink');
        if (userProfileLink) {
            userProfileLink.parentNode.removeChild(userProfileLink);
        }
        
        // Add protected pages here
        const protectedPages = ['dashboard.html', 'profile.html', 'settings.html'];
        
        if (protectedPages.includes(currentPage)) {
            window.location.href = 'login.html';
        }
    }
});