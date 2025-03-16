import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import io
from database import *
from translator import *
import base64

def save_uploaded_image(uploaded_file, farmer_id):
    """Save uploaded image and return the file path"""
    if uploaded_file is None:
        return None
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.join("assets", "images", "crops"), exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"crop_{farmer_id}_{timestamp}.jpg"
    file_path = os.path.join("assets", "images", "crops", filename)
    
    # Open and save the image
    img = Image.open(uploaded_file)
    img.save(file_path)
    
    return file_path

def display_crop_listing_form(translator_func, farmer_id):
    """Display form for farmers to list new crops"""
    st.subheader(translator_func("List Your Crop"))
    
    with st.form("crop_listing_form"):
        title = st.text_input(translator_func("Crop Title"))
        description = st.text_area(translator_func("Description"))
        
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input(translator_func("Quantity"), min_value=0.1, step=0.1)
        with col2:
            unit = st.selectbox(
                translator_func("Unit"), 
                options=["kg", "quintal", "ton", "dozen", "piece"]
            )
        
        price = st.number_input(translator_func("Price per") + f" {unit} (₹)", min_value=0.1, step=0.1)
        location = st.text_input(translator_func("Pickup Location"))
        
        uploaded_file = st.file_uploader(translator_func("Upload Image"), type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button(translator_func("List Crop"))
    
    if submitted:
        if not all([title, description, quantity, price, location]):
            st.error(translator_func("All fields are required"))
            return False
        
        # Save image if uploaded
        image_path = None
        if uploaded_file:
            image_path = save_uploaded_image(uploaded_file, farmer_id)
        
        # Insert crop into database
        crop_id = insert_crop(
            farmer_id=farmer_id,
            title=title,
            description=description,
            quantity=quantity,
            unit=unit,
            price=price,
            location=location,
            image_path=image_path
        )
        
        if crop_id:
            st.success(translator_func("Crop listed successfully!"))
            return True
        else:
            st.error(translator_func("Failed to list crop. Please try again."))
            return False
    
    return False

def display_farmer_dashboard(translator_func, farmer_id):
    """Display dashboard for farmers"""
    st.header(translator_func("Farmer Dashboard"))
    
    # Show tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        translator_func("My Crops"), 
        translator_func("List New Crop"),
        translator_func("Sales History")
    ])
    
    with tab1:
        st.header(translator_func("My Listed Crops"))
        crops = get_farmer_crops(farmer_id)
        
        if not crops:
            st.info(translator_func("You haven't listed any crops yet."))
        else:
            for crop in crops:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        if crop['image_path'] and os.path.exists(crop['image_path']):
                            st.image(crop['image_path'], width=150)
                        else:
                            st.markdown("🌱")  # Plant emoji as placeholder
                    
                    with col2:
                        st.subheader(crop['title'])
                        st.write(f"**{translator_func('Price')}:** ₹{crop['price']} / {crop['unit']}")
                        st.write(f"**{translator_func('Quantity')}:** {crop['quantity']} {crop['unit']}")
                        st.write(f"**{translator_func('Location')}:** {crop['location']}")
                        
                        status = translator_func("Available") if crop['available'] else translator_func("Not Available")
                        st.write(f"**{translator_func('Status')}:** {status}")
                    
                    with col3:
                        # Availability toggle button with color
                        button_color = "#4CAF50" if crop['available'] else "#2196F3"  # Green if available, Blue if not
                        button_text = translator_func("Mark as Unavailable") if crop['available'] else translator_func("Mark as Available")
                        
                        st.markdown(f"""
                            <style>
                            div[data-testid="stButton"] button {{
                                background-color: {button_color};
                                color: white;
                                width: 100%;
                                margin-bottom: 10px;
                            }}
                            .delete-button button {{
                                background-color: #f44336 !important;
                                color: white;
                                width: 100%;
                            }}
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # Toggle availability
                        if st.button(button_text, key=f"toggle_{crop['id']}"):
                            new_status = not crop['available']
                            if update_crop_availability(crop['id'], new_status):
                                st.rerun()
                        
                        # Delete button
                        if st.button(translator_func("Delete Crop"), key=f"delete_{crop['id']}", help=translator_func("This action cannot be undone")):
                            if delete_crop(crop['id']):
                                st.success(translator_func("Crop deleted successfully"))
                                st.rerun()
                            else:
                                st.error(translator_func("Failed to delete crop"))
                    
                    st.markdown("---")
    
    with tab2:
        display_crop_listing_form(translator_func, farmer_id)
    
    with tab3:
        st.header(translator_func("Sales History"))
        transactions = get_user_transactions(farmer_id, as_buyer=False)
        
        if not transactions:
            st.info(translator_func("No sales history yet."))
        else:
            for transaction in transactions:
                with st.container():
                    st.subheader(transaction['crop_title'])
                    st.write(f"**{translator_func('Buyer')}:** {transaction['buyer_name']}")
                    st.write(f"**{translator_func('Quantity')}:** {transaction['quantity']} {transaction['unit']}")
                    st.write(f"**{translator_func('Total Amount')}:** ₹{transaction['total_price']}")
                    st.write(f"**{translator_func('Status')}:** {transaction['status']}")
                    st.write(f"**{translator_func('Date')}:** {transaction['created_at']}")
                    
                    st.markdown("---")

def display_marketplace(translator_func, user_id, user_type):
    """Display the marketplace for buyers"""
    st.header(translator_func("Marketplace"))
    
    # Search and filter options
    with st.expander(translator_func("Search & Filter"), expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input(translator_func("Search"))
        
        with col2:
            min_price = st.number_input(translator_func("Min Price (₹)"), min_value=0, value=0)
            max_price = st.number_input(translator_func("Max Price (₹)"), min_value=0, value=10000)
        
        with col3:
            location_filter = st.text_input(translator_func("Location"))
    
    # Get available crops with filters
    crops = get_available_crops(
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        location=location_filter
    )
    
    if not crops:
        st.info(translator_func("No crops available matching your criteria."))
    else:
        # Display crops in cards
        for crop in crops:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if crop['image_path'] and os.path.exists(crop['image_path']):
                        st.image(crop['image_path'], width=150)
                    else:
                        st.markdown("🌱")  # Plant emoji as placeholder
                
                with col2:
                    st.subheader(crop['title'])
                    st.write(f"**{translator_func('Price')}:** ₹{crop['price']} / {crop['unit']}")
                    st.write(f"**{translator_func('Quantity')}:** {crop['quantity']} {crop['unit']}")
                    st.write(f"**{translator_func('Location')}:** {crop['location']}")
                    st.write(f"**{translator_func('Farmer')}:** {crop['farmer_name']}")
                    
                    # Show buy button only for buyers
                    if user_type == "buyer":
                        buy_col, view_col = st.columns(2)
                        with buy_col:
                            if st.button(translator_func("Buy Now"), key=f"buy_{crop['id']}", use_container_width=True):
                                st.session_state.cart = [{
                                    'product_id': crop['id'],
                                    'name': crop['title'],
                                    'price': crop['price'],
                                    'quantity': 1,
                                    'unit': crop['unit'],
                                    'farmer_id': crop['farmer_id']
                                }]
                                st.session_state.page = "checkout"
                                st.rerun()
                        with view_col:
                            if st.button(translator_func("View Details"), key=f"view_{crop['id']}", use_container_width=True):
                                st.session_state.product_id = crop['id']
                                st.session_state.page = "product_detail"
                                st.rerun()
                
                st.markdown("---")

def display_checkout(translator_func, user_id, cart):
    """Display checkout page for buyers"""
    st.header(translator_func("Checkout"))
    
    if not cart:
        st.warning(translator_func("Your cart is empty"))
        if st.button(translator_func("Go to Marketplace")):
            st.session_state.page = "marketplace"
            st.rerun()
        return False
    
    # Calculate total for all items
    total_amount = 0
    
    # Display items in cart
    st.subheader(translator_func("Cart Items"))
    for item in cart:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
                st.write(f"{translator_func('Quantity')}: {item['quantity']} {item['unit']}")
                st.write(f"{translator_func('Price')}: ₹{item['price']} / {item['unit']}")
                item_total = item['quantity'] * item['price']
                st.write(f"{translator_func('Subtotal')}: ₹{item_total:.2f}")
            
            total_amount += item_total
            
            st.markdown("---")
    
    # Display total
    st.subheader(translator_func("Order Summary"))
    st.write(f"**{translator_func('Total Amount')}:** ₹{total_amount:.2f}")
    
    # Checkout button
    if st.button(translator_func("Proceed to Payment"), use_container_width=True):
        # Create transaction for each item
        for item in cart:
            transaction_id = create_transaction(
                crop_id=item['product_id'],
                buyer_id=user_id,
                farmer_id=item['farmer_id'],
                quantity=item['quantity'],
                total_price=item['quantity'] * item['price']
            )
            
            if transaction_id:
                st.session_state.transaction_id = transaction_id
                st.session_state.order_amount = total_amount
                st.session_state.page = "payment"
                st.rerun()
            else:
                st.error(translator_func("Failed to create transaction. Please try again."))
                return False
    
    # Back button
    if st.button(translator_func("Back to Marketplace")):
        st.session_state.page = "marketplace"
        st.rerun()
    
    return True

def display_buyer_dashboard(translator_func, buyer_id):
    """Display dashboard for buyers"""
    st.header(translator_func("Buyer Dashboard"))
    
    # Show tabs for different sections
    tab1, tab2 = st.tabs([
        translator_func("My Purchases"), 
        translator_func("Browse Marketplace")
    ])
    
    with tab1:
        st.header(translator_func("My Purchase History"))
        transactions = get_user_transactions(buyer_id, as_buyer=True)
        
        if not transactions:
            st.info(translator_func("You haven't made any purchases yet."))
        else:
            for transaction in transactions:
                with st.container():
                    st.subheader(transaction['crop_title'])
                    st.write(f"**{translator_func('Farmer')}:** {transaction['farmer_name']}")
                    st.write(f"**{translator_func('Quantity')}:** {transaction['quantity']} {transaction['unit']}")
                    st.write(f"**{translator_func('Total Amount')}:** ₹{transaction['total_price']}")
                    st.write(f"**{translator_func('Status')}:** {translator_func(transaction['status'].capitalize())}")
                    st.write(f"**{translator_func('Date')}:** {transaction['created_at']}")
                    
                    st.markdown("---")
    
    with tab2:
        # Redirect to marketplace
        if st.button(translator_func("Go to Marketplace")):
            st.session_state.page = "marketplace"