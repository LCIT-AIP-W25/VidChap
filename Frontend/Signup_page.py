import streamlit as st
#from user_data_handler import save_user_data, load_user_data

# CSS Styling (Inline)
st.markdown("""
    <style>
    .signup-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        border-radius: 10px;
        background: #ffffff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        font-family: 'Arial', sans-serif;
    }

    .signup-container h1 {
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
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 5px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        transition: 0.3s;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #218838 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Signup Form
st.markdown("<div class='signup-container'>", unsafe_allow_html=True)
st.title("Sign Up")

first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
email = st.text_input("Email")
phone_number = st.text_input("Phone Number")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
security_answer = st.text_input("What is your favorite color?", type="password")

if st.button("Sign Up"):
    users = load_user_data() #to be done after connecting database
    if email in users:
        st.error("Email is already registered. Please log in.")
    else:
        users[email] = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "username": username,
            "password": password,   
            "security_answer": security_answer
        }
        save_user_data(users) 
        st.success("Sign up successful! You can now log in.")

st.markdown("</div>", unsafe_allow_html=True)

# Back to Login page link
st.markdown("<a href='login.py'>Back to Login</a>", unsafe_allow_html=True)
