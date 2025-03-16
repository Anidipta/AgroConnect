import streamlit as st
import os
import pandas as pd
from datetime import datetime
import sqlite3

# Import modules
from database import *
from auth import *
from marketplace import *
from payment import *
from translator import *
from utils import (
    setup_page_config, load_css, display_logo_header, 
    display_footer, initialize_session_state
)
from config import LANGUAGES
from messaging import display_chat_interface, get_user_location, update_user_location

def main():
    # Set up page configuration with improved settings
    st.set_page_config(
        page_title="AgroConnect",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Get user location
    get_user_location()
    
    # Handle location updates from JavaScript
    if st.session_state.user_location:
        update_user_location(
            st.session_state.user_location['lat'],
            st.session_state.user_location['lng']
        )
    
    # Custom CSS with better styling
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary: #4CAF50;
            --secondary: #8BC34A;
            --background: #F9FBE7;
            --text: #333333;
            --message-bg: #ffffff;
            --message-text: #000000;
            --message-border: #e0e0e0;
        }
        
        /* Header styling */
        .main-header {
            background-color: var(--primary);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Logo styling */
        .logo-img {
            max-height: 80px;
            margin-right: 15px;
        }
        
        /* Card styling for products */
        .product-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
        .stButton>button {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--secondary);
            transform: translateY(-2px);
        }
        
        /* Message styling */
        .message-container {
            display: flex;
            margin-bottom: 1rem;
            align-items: flex-start;
            width: 100%;
        }
        
        .sent-message {
            justify-content: flex-end;
        }
        
        .received-message {
            justify-content: flex-start;
        }
        
        .message-bubble {
            padding: 0.8rem 1rem;
            border-radius: 15px;
            max-width: 80%;
            background-color: var(--message-bg);
            color: var(--message-text);
            border: 1px solid var(--message-border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .message-sent {
            margin-left: auto;
            border-bottom-right-radius: 5px;
            background-color: #E8F5E9;
        }
        
        .message-received {
            margin-right: auto;
            border-bottom-left-radius: 5px;
            background-color: #F5F5F5;
        }
        
        .message-content {
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        
        .message-footer {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.25rem;
        }
        
        .message-time {
            font-size: 0.75rem;
            color: #666;
        }
        
        .message-status {
            font-size: 0.7rem;
            color: #666;
        }
        
        /* Media message styling */
        .message-media {
            max-width: 300px;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        
        .message-image {
            width: 100%;
            border-radius: 10px;
            cursor: pointer;
        }
        
        .message-video {
            width: 100%;
            border-radius: 10px;
            cursor: pointer;
        }
        
        /* Message tools styling */
        .message-tools {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem;
            align-items: center;
        }
        
        .tool-button {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: all 0.2s ease;
            font-size: 1.2rem;
            width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .tool-button:hover {
            background-color: #f0f0f0;
            transform: scale(1.1);
        }
        
        .emoji-button {
            position: relative;
        }
        
        /* Message input styling */
        .message-input {
            width: 100%;
            padding: 0.8rem 1rem;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s ease;
        }
        
        .message-input:focus {
            border-color: var(--primary);
        }
        
        /* Hide file upload elements */
        [type="file"] {
            display: none;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
            color: #666;
            border-top: 1px solid #ddd;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .product-card {
                padding: 0.5rem;
            }
            
            .message-bubble {
                max-width: 90%;
            }
            
            .message-media {
                max-width: 250px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    init_db()
    
    # Initialize session state with proper defaults
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "user" not in st.session_state:
        st.session_state.user = None
    if "cart" not in st.session_state:
        st.session_state.cart = []
    
    # Handle Razorpay payment callback
    handle_payment_callback()
    
    # Set translator function
    user_language = 'en'  # Default to English
    if is_authenticated():
        user_language = st.session_state.user.get('language', 'en')
    
    translator_func = get_translator_for_user(user_language)
    
    # Display logo and header with better styling
    st.markdown(f'''
    <div class="main-header">
        <img src="assets/images/logo.png" class="logo-img" onerror="this.src='https://via.placeholder.com/80x80?text=AgroConnect'">
        <h1>AgroConnect</h1>
        <p>{translator_func("Connecting farmers and buyers directly")}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar for authenticated users with improved styling
    if is_authenticated():
        with st.sidebar:
            st.markdown(f"### {translator_func('Welcome')}, {st.session_state.user['name']}!")
            
            # Language selector
            st.markdown("#### " + translator_func("Language"))
            selected_language = st.selectbox(
                "",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=list(LANGUAGES.keys()).index(st.session_state.user.get('language', 'en'))
            )
            
            if selected_language != st.session_state.user.get('language', 'en'):
                st.session_state.user['language'] = selected_language
                conn = get_connection()
                conn.execute("UPDATE users SET language = ? WHERE id = ?", 
                            (selected_language, st.session_state.user['id']))
                conn.commit()
                st.rerun()
            
            # Navigation with clear spacing
            st.markdown("---")
            st.markdown("#### " + translator_func("Navigation"))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(translator_func("Dashboard"), key="nav_dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
            
            with col2:
                if st.button(translator_func("Marketplace"), key="nav_marketplace", use_container_width=True):
                    st.session_state.page = "marketplace"
                    st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(translator_func("Messages"), key="nav_messages", use_container_width=True):
                    st.session_state.page = "messages"
                    st.rerun()
            
            with col2:
                if st.button(translator_func("Settings"), key="nav_settings", use_container_width=True):
                    st.session_state.page = "settings"
                    st.rerun()
            
            st.markdown("---")
            if st.button(translator_func("Logout"), key="nav_logout", use_container_width=True):
                logout()
                st.rerun()
    
    # Main content area with container to improve spacing
    with st.container():
        if not is_authenticated():
            # Authentication pages
            if st.session_state.page == "login":
                st.markdown(f"## {translator_func('Login to AgroConnect')}")
                
                with st.form("login_form"):
                    email = st.text_input(translator_func("Email"))
                    password = st.text_input(translator_func("Password"), type="password")
                    
                    submitted = st.form_submit_button(translator_func("Login"))
                    
                    if submitted:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                                        (email, password))
                        user = cursor.fetchone()
                        
                        if user:
                            # Convert row to dictionary using column names
                            columns = [description[0] for description in cursor.description]
                            user_dict = dict(zip(columns, user))
                            st.session_state.user = user_dict
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error(translator_func("Invalid email or password"))
                
                st.markdown("---")
                st.markdown(translator_func("Don't have an account?"))
                if st.button(translator_func("Register")):
                    st.session_state.page = "register"
                    st.rerun()
                    
            elif st.session_state.page == "register":
                st.markdown(f"## {translator_func('Create an Account')}")
                
                with st.form("register_form"):
                    name = st.text_input(translator_func("Full Name"))
                    email = st.text_input(translator_func("Email"))
                    phone = st.text_input(translator_func("Phone Number"))
                    password = st.text_input(translator_func("Password"), type="password")
                    
                    user_type = st.radio(translator_func("I am a"), 
                                        [translator_func("Farmer"), translator_func("Buyer")],
                                        horizontal=True)
                    
                    submitted = st.form_submit_button(translator_func("Register"))
                    
                    if submitted:
                        if not all([name, email, phone, password]):
                            st.error(translator_func("All fields are required"))
                        else:
                            # Insert user record
                            conn = get_connection()
                            try:
                                user_type_val = 'farmer' if user_type == translator_func("Farmer") else 'buyer'
                                conn.execute("""
                                    INSERT INTO users (name, email, phone, password, user_type, language)
                                    VALUES (?, ?, ?, ?, ?, 'en')
                                """, (name, email, phone, password, user_type_val))
                                conn.commit()
                                st.success(translator_func("Registration successful! Please login."))
                                st.session_state.page = "login"
                                st.rerun()
                            except Exception as e:
                                st.error(f"{translator_func('Registration failed')}: {str(e)}")
                
                st.markdown("---")
                st.markdown(translator_func("Already have an account?"))
                if st.button(translator_func("Login")):
                    st.session_state.page = "login"
                    st.rerun()
        else:
            # Pages for authenticated users
            if st.session_state.page == "dashboard":
                if st.session_state.user['user_type'] == 'farmer':
                    display_farmer_dashboard(translator_func, st.session_state.user['id'])
                else:
                    display_buyer_dashboard(translator_func, st.session_state.user['id'])
            
            elif st.session_state.page == "marketplace":
                display_marketplace(translator_func, st.session_state.user['id'], st.session_state.user['user_type'])
                
            elif st.session_state.page == "product_detail" and "product_id" in st.session_state:
                display_product_detail(st.session_state.product_id, translator_func)
                
            elif st.session_state.page == "checkout" and "cart" in st.session_state:
                display_checkout(translator_func, st.session_state.user['id'], st.session_state.cart)
                
            elif st.session_state.page == "payment" and "order_id" in st.session_state:
                display_payment_page(translator_func, st.session_state.transaction_id, st.session_state.order_amount, st.session_state.user)
                
            elif st.session_state.page == "messages":
                display_messages(translator_func)
                
            elif st.session_state.page == "settings":
                display_settings(translator_func)
            
            else:
                # Default to dashboard if page not found
                st.session_state.page = "dashboard"
                st.rerun()

    # Display footer with improved styling
    st.markdown("""
    <div class="footer">
        <p>© 2025 AgroConnect - {}</p>
    </div>
    """.format(translator_func("Connecting farmers and buyers directly")), unsafe_allow_html=True)

# Improved display_product_detail function with better styling
def display_product_detail(product_id, translator_func):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, u.name as farmer_name, u.location 
        FROM crops c 
        JOIN users u ON c.farmer_id = u.id 
        WHERE c.id = ?
    """, (product_id,))
    product = cursor.fetchone()
    
    if not product:
        st.error(translator_func("Product not found"))
        return
    
    # Convert row to dictionary
    columns = [description[0] for description in cursor.description]
    product = dict(zip(columns, product))
    
    st.markdown(f"# {product['title']}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if product['image_path'] and os.path.exists(product['image_path']):
            st.image(product['image_path'], use_column_width=True)
        else:
            st.image("assets/images/default_product.jpg", use_column_width=True)
    
    with col2:
        st.markdown(f"### {translator_func('Product Details')}")
        
        # Use an expander for detailed information
        with st.expander(translator_func("View Details"), expanded=True):
            st.markdown(f"**{translator_func('Price')}:** ₹{product['price']:.2f} per {product['unit']}")
            st.markdown(f"**{translator_func('Available Quantity')}:** {product['quantity']} {product['unit']}")
            st.markdown(f"**{translator_func('Seller')}:** {product['farmer_name']}")
            st.markdown(f"**{translator_func('Location')}:** {product['location']}")
            st.markdown(f"**{translator_func('Description')}:**")
            st.markdown(product['description'])
        
        # Add to cart section with better layout
        st.markdown("### " + translator_func("Purchase Options"))
        
        quantity = st.number_input(
            translator_func("Quantity"), 
            min_value=0.1,
            max_value=float(product['quantity']),
            value=1.0,
            step=0.1
        )
        
        total_price = quantity * product['price']
        st.markdown(f"**{translator_func('Total Price')}:** ₹{total_price:.2f}")
        
        add_cart_col, buy_now_col = st.columns(2)
        
        with add_cart_col:
            if st.button(translator_func("Add to Cart"), key="add_to_cart", use_container_width=True):
                if "cart" not in st.session_state:
                    st.session_state.cart = []
                
                # Check if product already in cart
                found = False
                for i, item in enumerate(st.session_state.cart):
                    if item['product_id'] == product_id:
                        st.session_state.cart[i]['quantity'] += quantity
                        found = True
                        break
                
                if not found:
                    st.session_state.cart.append({
                        'product_id': product_id,
                        'name': product['title'],
                        'price': product['price'],
                        'quantity': quantity,
                        'unit': product['unit'],
                        'farmer_id': product['farmer_id']
                    })
                
                st.success(translator_func("Added to cart"))
                st.balloons()

        with buy_now_col:
            if st.button(translator_func("Buy Now"), key="buy_now", use_container_width=True):
                # Clear existing cart and add this item
                st.session_state.cart = [{
                    'product_id': product_id,
                    'name': product['title'],
                    'price': product['price'],
                    'quantity': quantity,
                    'unit': product['unit'],
                    'farmer_id': product['farmer_id']
                }]
                st.session_state.page = "checkout"
                st.rerun()
   
    # Show message button to contact farmer
    st.markdown("---")
    if st.button(translator_func("Contact Seller")):
        st.session_state.receiver_id = product['farmer_id']
        st.session_state.page = "messages"
        st.rerun()
    
    conn.close()

# Improved display_messages function with better styling
def display_messages(translator_func):
    """Display messages page"""
    display_chat_interface(translator_func)

# Improved display_settings function with better styling
def display_settings(translator_func):
    st.markdown(f"# {translator_func('Account Settings')}")
    
    # Get user data with proper dictionary conversion
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (st.session_state.user['id'],))
    user = cursor.fetchone()
    if user:
        user = dict(user)
    else:
        st.error(translator_func("User data not found"))
        return
    
    tabs = st.tabs([
        translator_func("Profile Information"), 
        translator_func("Password"), 
        translator_func("Notifications"),
        translator_func("Language")
    ])
    
    with tabs[0]:
        with st.form("profile_form"):
            st.markdown(f"### {translator_func('Personal Details')}")
            
            name = st.text_input(translator_func("Full Name"), value=user.get('name', ''))
            email = st.text_input(translator_func("Email Address"), value=user.get('email', ''))
            phone = st.text_input(translator_func("Phone Number"), value=user.get('phone', ''))
            
            if st.session_state.user['user_type'] == 'farmer':
                st.markdown("### " + translator_func("Farm Details"))
                location = st.text_input(translator_func("Farm Location"), value=user.get('location', ''))
                
                # Use multiselect for products they grow
                all_products = ["Rice", "Wheat", "Corn", "Vegetables", "Fruits", "Spices", "Pulses", "Other"]
                current_products = user.get('products', '').split(',') if user.get('products') else []
                products = st.multiselect(
                    translator_func("Products you grow"),
                    options=all_products,
                    default=[p for p in current_products if p in all_products]
                )
                
                # Additional farm details
                farm_size = st.text_input(
                    translator_func("Farm Size (in acres)"), 
                    value=user.get('farm_size', '')
                )
                farming_type = st.selectbox(
                    translator_func("Farming Type"),
                    options=[translator_func("Organic"), translator_func("Traditional"), translator_func("Mixed")],
                    index=0 if user.get('farming_type') == 'Organic' else 
                          1 if user.get('farming_type') == 'Traditional' else 2
                )
            
            submit_button = st.form_submit_button(translator_func("Save Changes"))
            if submit_button:
                # Update user profile
                updates = {
                    'name': name,
                    'email': email,
                    'phone': phone
                }
                
                if st.session_state.user['user_type'] == 'farmer':
                    updates['location'] = location
                    updates['products'] = ','.join(products)
                    updates['farm_size'] = farm_size
                    updates['farming_type'] = farming_type
                
                # Update database
                update_cols = ", ".join([f"{k} = ?" for k in updates.keys()])
                conn.execute(f"UPDATE users SET {update_cols} WHERE id = ?", 
                             (*updates.values(), st.session_state.user['id']))
                conn.commit()
                
                # Update session state
                st.session_state.user.update(updates)
                st.success(translator_func("Profile updated successfully"))
                st.rerun()
    
    with tabs[1]:
        with st.form("password_form"):
            st.markdown(f"### {translator_func('Change Password')}")
            
            current_password = st.text_input(translator_func("Current Password"), type="password")
            new_password = st.text_input(translator_func("New Password"), type="password")
            confirm_password = st.text_input(translator_func("Confirm New Password"), type="password")
            
            submit_password = st.form_submit_button(translator_func("Update Password"))
            if submit_password:
                if not current_password or not new_password:
                    st.error(translator_func("All fields are required"))
                elif new_password != confirm_password:
                    st.error(translator_func("New passwords do not match"))
                else:
                    # Verify current password
                    user_pass = conn.execute("SELECT password FROM users WHERE id = ?", 
                                           (st.session_state.user['id'],)).fetchone()
                    
                    if user_pass and user_pass[0] == current_password:
                        conn.execute("UPDATE users SET password = ? WHERE id = ?", 
                                     (new_password, st.session_state.user['id']))
                        conn.commit()
                        st.success(translator_func("Password updated successfully"))
                    else:
                        st.error(translator_func("Current password is incorrect"))
    
    with tabs[2]:
        with st.form("notification_form"):
            st.markdown(f"### {translator_func('Notification Preferences')}")
            
            email_notifications = st.checkbox(
                translator_func("Receive email notifications"),
                value=user.get('email_notifications', 1) == 1
            )
            
            sms_notifications = st.checkbox(
                translator_func("Receive SMS notifications"),
                value=user.get('sms_notifications', 1) == 1
            )
            
            st.markdown("#### " + translator_func("Notify me about"))
            
            new_messages = st.checkbox(
                translator_func("New messages"),
                value=user.get('notify_messages', 1) == 1
            )
            
            order_updates = st.checkbox(
                translator_func("Order updates"),
                value=user.get('notify_orders', 1) == 1
            )
            
            submit_notifications = st.form_submit_button(translator_func("Save Notification Settings"))
            if submit_notifications:
                conn.execute("""
                    UPDATE users SET 
                        email_notifications = ?,
                        sms_notifications = ?,
                        notify_messages = ?,
                        notify_orders = ?
                    WHERE id = ?
                """, (
                    1 if email_notifications else 0,
                    1 if sms_notifications else 0,
                    1 if new_messages else 0,
                    1 if order_updates else 0,
                    st.session_state.user['id']
                ))
                conn.commit()
                st.success(translator_func("Notification preferences updated"))
    
    with tabs[3]:
        with st.form("language_form"):
            st.markdown(f"### {translator_func('Language Settings')}")
            
            selected_language = st.selectbox(
                translator_func("Select your preferred language"),
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=list(LANGUAGES.keys()).index(user.get('language', 'en'))
            )
            
            submit_language = st.form_submit_button(translator_func("Save Language Settings"))
            if submit_language:
                st.session_state.user['language'] = selected_language
                conn.execute("UPDATE users SET language = ? WHERE id = ?", 
                            (selected_language, st.session_state.user['id']))
                conn.commit()
                st.success(translator_func("Language updated successfully"))
                st.rerun()
    
    conn.close()

# Run the main function
if __name__ == "__main__":
    main()