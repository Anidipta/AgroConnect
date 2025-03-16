import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DB_PATH = os.path.join(BASE_DIR, "data", "agroconnect.db")

# Razorpay configuration
RAZORPAY_KEY_ID = "rzp_test_QBRE6pSY6tyRB8"
RAZORPAY_KEY_SECRET = "fpQBZoXg8YiJnuROYwQKSW0R"

# Languages
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'ur': 'Urdu',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'or': 'Odia'
}

# App settings
APP_NAME = "AgroConnect"
APP_TAGLINE = "Connecting Farmers to Global Markets"
APP_DESCRIPTION = "A platform for farmers to sell their crops directly to buyers"

# Theme colors
THEME_COLORS = {
    "primary": "#4CAF50",    # Green
    "secondary": "#8BC34A",  # Light Green
    "accent": "#FF9800",     # Orange
    "background": "#F5F5F5", # Light Gray
    "text": "#333333"        # Dark Gray
}