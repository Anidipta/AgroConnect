import streamlit as st
import hashlib
import secrets
import re
from database import *
from config import LANGUAGES
from translator import *

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (basic validation)"""
    pattern = r'^\d{10}$'  # Simple 10-digit validation, modify as needed
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is strong"

def login_form(translator_func):
    """Display and process login form"""
    st.subheader(translator_func("Login to AgroConnect"))
    
    with st.form("login_form"):
        email = st.text_input(translator_func("Email"))
        password = st.text_input(translator_func("Password"), type="password")
        submitted = st.form_submit_button(translator_func("Login"))
    
    if submitted:
        if not email or not password:
            st.error(translator_func("Email and password are required"))
            return None
        
        user = get_user_by_email(email)
        if not user or user['password'] != hash_password(password):
            st.error(translator_func("Invalid email or password"))
            return None
        
        st.success(translator_func("Login successful!"))
        return user
    
    # Link to registration
    if st.button(translator_func("Don't have an account? Register here")):
        st.session_state.page = "register"
    
    return None

def register_form(translator_func):
    """Display and process registration form"""
    st.subheader(translator_func("Register with AgroConnect"))
    
    with st.form("registration_form"):
        name = st.text_input(translator_func("Full Name"))
        email = st.text_input(translator_func("Email"))
        phone = st.text_input(translator_func("Phone Number"))
        location = st.text_input(translator_func("Location"))
        
        user_type = st.selectbox(
            translator_func("I am a"),
            options=["farmer", "buyer"],
            format_func=lambda x: translator_func(x.capitalize())
        )
        
        language = st.selectbox(
            translator_func("Preferred Language"),
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x]
        )
        
        password = st.text_input(translator_func("Password"), type="password")
        confirm_password = st.text_input(translator_func("Confirm Password"), type="password")
        
        submitted = st.form_submit_button(translator_func("Register"))
    
    if submitted:
        # Validate inputs
        if not all([name, email, phone, location, password, confirm_password]):
            st.error(translator_func("All fields are required"))
            return False
        
        if not validate_email(email):
            st.error(translator_func("Invalid email format"))
            return False
        
        if not validate_phone(phone):
            st.error(translator_func("Invalid phone number format"))
            return False
        
        if password != confirm_password:
            st.error(translator_func("Passwords do not match"))
            return False
        
        valid_password, message = validate_password(password)
        if not valid_password:
            st.error(translator_func(message))
            return False
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            st.error(translator_func("Email already registered"))
            return False
        
        # Insert new user
        user_id = insert_user(email, hash_password(password), name, phone, user_type, language, location)
        if user_id:
            st.success(translator_func("Registration successful! Please login."))
            # Redirect to login page
            st.session_state.page = "login"
            return True
        else:
            st.error(translator_func("Registration failed. Please try again."))
            return False
    
    # Link to login
    if st.button(translator_func("Already have an account? Login here")):
        st.session_state.page = "login"
    
    return False

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in st.session_state and st.session_state.user is not None

def logout():
    """Log out the current user"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.session_state.page = "login"
    return True

def change_language(user_id, language):
    """Change user's preferred language"""
    if update_user_language(user_id, language):
        # Update session state
        st.session_state.user['language'] = language
        return True
    return False

def show_language_selector(translator_func):
    """Display language selector in sidebar"""
    selected_language = st.sidebar.selectbox(
        translator_func("Language"),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.user['language'])
    )
    
    if selected_language != st.session_state.user['language']:
        if change_language(st.session_state.user['id'], selected_language):
            st.rerun()