// This file should be included in all pages that need authentication

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    firebase.auth().onAuthStateChanged((user) => {
        if (!user) {
            // Not logged in, redirect to login page
            window.location.href = 'login.html';
        }
    });
});