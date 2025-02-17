import streamlit as st
import random
import string

# User credentials (static because deciding where to store cred for better secure system)
USER_DATA = {
    "user1@example.com": {"username": "user1", "security_answer": "blue"},
    "admin@example.com": {"username": "admin", "security_answer": "apple"}
}

# Function to generate a temporary password
def generate_temp_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Forgot Password Page Layout
def forgot_password():
    st.markdown("""
        <style>
        .forgot-container {
            max-width: 400px;
            margin: auto;
            padding: 40px;
            border-radius: 10px;
            background: #ffffff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-family: 'Arial', sans-serif;
        }

        .forgot-container h1 {
            color: #2b3a42;
            font-size: 24px;
            margin-bottom: 20px;
        }

        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 12px;
            width: 100%;
            margin-bottom: 20px;
        }

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

        .back-to-login {
            color: #007bff;
            font-size: 14px;
            text-decoration: none;
            display: block;
            margin-top: 10px;
        }

        .back-to-login:hover {
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='forgot-container'>", unsafe_allow_html=True)
    st.title("🔑 Forgot Password")
    
    # Input email for password reset
    email = st.text_input("Enter your registered email")

    if email in USER_DATA:
        st.success("Email found. Answer the security question below.")
        security_question = "What is your favorite color?"
        answer = st.text_input(security_question)

        if st.button("Submit"):
            if answer.lower() == USER_DATA[email]["security_answer"].lower():
                temp_password = generate_temp_password()
                st.session_state["temp_password"] = temp_password  # Store temporary password
                st.success(f"Your temporary password is: **{temp_password}**")
                st.warning("Use this password to log in, then change it immediately.")
            else:
                st.error("Incorrect answer. Try again.")
    elif email:
        st.error("Email not found. Please try again.")

    # Back to login page link
    st.markdown("<a class='back-to-login' href='login.py'>Back to Login</a>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
