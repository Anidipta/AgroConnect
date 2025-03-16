import streamlit as st
import os
from datetime import datetime
import base64
from config import *

def setup_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_css():
    """Load custom CSS styles"""
    css = f"""
    <style>
        /* Main theme colors */
        :root {{
            --primary: {THEME_COLORS['primary']};
            --secondary: {THEME_COLORS['secondary']};
            --accent: {THEME_COLORS['accent']};
            --background: {THEME_COLORS['background']};
            --text: {THEME_COLORS['text']};
        }}
        
        /* Header styling */
        .main .block-container {{
            padding-top: 1rem;
        }}
        
        h1, h2, h3 {{
            color: var(--primary);
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: var(--primary);
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary);
            color: var(--text);
        }}
        
        /* Card styling */
        div[data-testid="stVerticalBlock"] > div {{
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        /* Form styling */
        div[data-baseweb="input"] > div {{
            border-radius: 4px;
        }}
        
        div[data-baseweb="select"] > div {{
            border-radius: 4px;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: var(--primary);
        }}
        
        /* Header logo */
        .logo-title {{
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .logo-title img {{
            height: 50px;
            margin-right: 10px;
        }}
        
        /* Footer */
        footer {{
            text-align: center;
            padding: 1rem;
            color: var(--text);
            font-size: 0.8rem;
        }}
        
        /* Razorpay button */
        .razorpay-payment-button {{
            background-color: var(--primary);
            color: white;
            border-radius: 4px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
            display: block;
        }}
        
        .razorpay-payment-button:hover {{
            background-color: var(--secondary);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def display_logo_header(translator_func):
    """Display logo and app name in header"""
    logo_html = f"""
    <div class="logo-title">
        <img src="data:image/png;base64,{get_base64_logo()}" alt="AgroConnect Logo">
        <h1>{APP_NAME}</h1>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown(f"##### *{translator_func('Connecting Farmers to Global Markets')}*")
    st.markdown("---")

def get_base64_logo():
    """Return base64 encoded placeholder logo"""
    # This is a placeholder. In a real app, you'd use a real logo file
    # For now, we'll create a simple SVG as a placeholder
    logo_svg = """
    <svg width="50" height="50" xmlns="http://www.w3.org/2000/svg">
        <rect width="50" height="50" fill="#4CAF50" rx="10" ry="10"/>
        <text x="50%" y="50%" font-family="Arial" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">🌾</text>
    </svg>
    """
    return base64.b64encode(logo_svg.encode()).decode()

def display_footer(translator_func):
    """Display footer with copyright and current year"""
    current_year = datetime.now().year
    footer_html = f"""
    <footer>
        <p>&copy; {current_year} {APP_NAME} - {translator_func('All Rights Reserved')}</p>
    </footer>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize the session state with default values"""
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'selected_crop' not in st.session_state:
        st.session_state.selected_crop = None
    
    if 'transaction_id' not in st.session_state:
        st.session_state.transaction_id = None
    
    if 'order_id' not in st.session_state:
        st.session_state.order_id = None

def format_currency(amount):
    """Format amount as Indian Rupees"""
    return f"₹{amount:,.2f}"

def format_date(date_str):
    """Format date string for display"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%d %b %Y, %H:%M")
    except:
        return date_str