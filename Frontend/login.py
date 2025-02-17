import streamlit as st
import forgot_password

# User credentials (static because deciding where to store cred for better secure system)
USER_CREDENTIALS = {
    "user1@example.com": "password123",
    "admin@example.com": "adminpass"
}

# CSS Styling (Inline)
st.markdown("""
    <style>
    /* Center the login form */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        border-radius: 10px;
        background: #ffffff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        font-family: 'Arial', sans-serif;
    }

    .login-container h1 {
        color: #2b3a42;
        font-size: 24px;
        margin-bottom: 20px;
    }

    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 12px;
        width: 100%;
        margin-bottom: 20px;
    }

    /* Login Button */
    .stButton>button {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 5px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        transition: 0.3s;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #0056b3 !important;
    }

    /* Forgot Password Link */
    .forgot-password {
        color: #007bff;
        font-size: 14px;
        text-decoration: none;
        display: block;
        margin-top: 10px;
    }

    .forgot-password:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# Login Form
st.markdown("<div class='login-container'>", unsafe_allow_html=True)
st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if email in USER_CREDENTIALS and USER_CREDENTIALS[email] == password:
        st.success("Login successful!")
    else:
        st.error("Invalid email or password")

# Forgot Password Redirect Button (Simulate page navigation)
if st.button("Forgot Password?"):
    forgot_password.forgot_password()  # Call the function from forgot_password.py

st.markdown("</div>", unsafe_allow_html=True)
