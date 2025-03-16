import streamlit as st
import razorpay
import json
import hashlib
from database import *
from config import *

# Initialize Razorpay client with your keys
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def generate_order_id(transaction_id, amount):
    """Generate a Razorpay order ID"""
    try:
        data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'txn_{transaction_id}',
            'payment_capture': 1
        }
        order = client.order.create(data=data)
        return order['id']
    except Exception as e:
        print(f"Error creating Razorpay order: {e}")  # Log error
        return None

def verify_payment_signature(payment_id, order_id, signature):
    """Verify Razorpay payment signature"""
    try:
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        client.utility.verify_payment_signature(params_dict)
        return True
    except Exception as e:
        print(f"Payment verification failed: {e}")  # Log error
        return False

def display_payment_page(translator_func, transaction_id, amount, user_details):
    """Display payment page with Razorpay integration"""
    st.header(translator_func("Complete Payment"))
    
    # Create Razorpay order
    order_id = generate_order_id(transaction_id, amount)
    
    if not order_id:
        st.error(translator_func("Failed to create payment order. Please try again."))
        if st.button(translator_func("Back to Dashboard")):
            st.session_state.page = "dashboard"
        return False
    
    # Store order ID in session
    st.session_state.order_id = order_id
    
    # Display payment details
    st.subheader(translator_func("Payment Details"))
    st.write(f"**{translator_func('Transaction ID')}:** {transaction_id}")
    st.write(f"**{translator_func('Amount')}:** ₹{amount:.2f}")
    
    # Razorpay payment form
    payment_options = {
        'key': RAZORPAY_KEY_ID,
        'amount': int(amount * 100),
        'currency': 'INR',
        'name': 'AgroConnect',
        'description': f'Payment for Transaction #{transaction_id}',
        'order_id': order_id,
        'prefill': {
            'name': user_details['name'],
            'email': user_details['email'],
            'contact': user_details['phone']
        },
        'theme': {
            'color': '#4CAF50'
        }
    }
    
    # Create payment button with proper styling
    st.markdown("""
        <style>
        .razorpay-payment-button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            margin: 10px 0;
            width: 100%;
        }
        .razorpay-payment-button:hover {
            background-color: #45a049;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Razorpay payment script
    payment_script = f"""
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <script>
        var options = {json.dumps(payment_options)};
        var rzp = new Razorpay(options);
        
        document.getElementById('pay-button').onclick = function(e) {{
            rzp.open();
            e.preventDefault();
        }}
        
        rzp.on('payment.success', function(response) {{
            window.location.href = "/?razorpay_payment_id=" + response.razorpay_payment_id + 
                                 "&razorpay_order_id=" + response.razorpay_order_id +
                                 "&razorpay_signature=" + response.razorpay_signature;
        }});
        </script>
        <button id="pay-button" class="razorpay-payment-button">{translator_func('Pay Now')}</button>
    """
    
    st.markdown(payment_script, unsafe_allow_html=True)
    
    # Back button
    if st.button(translator_func("Cancel Payment")):
        st.session_state.page = "dashboard"
        return False
    
    # Handle payment callback
    if 'razorpay_payment_id' in st.session_state:
        payment_id = st.session_state.razorpay_payment_id
        order_id = st.session_state.razorpay_order_id
        signature = st.session_state.razorpay_signature
        
        if verify_payment_signature(payment_id, order_id, signature):
            if update_payment_status(transaction_id, payment_id, 'completed'):
                st.success(translator_func("Payment successful!"))
                st.session_state.page = "dashboard"
                return True
            else:
                st.error(translator_func("Payment verification failed. Please contact support."))
                return False
    
    return True

def handle_payment_callback():
    """Handle Razorpay payment callback"""
    try:
        params = st.query_params()
        payment_id = params.get('razorpay_payment_id', [None])[0]
        order_id = params.get('razorpay_order_id', [None])[0]
        signature = params.get('razorpay_signature', [None])[0]
        
        if payment_id and order_id and signature:
            st.session_state.razorpay_payment_id = payment_id
            st.session_state.razorpay_order_id = order_id
            st.session_state.razorpay_signature = signature
            return True
        
        return False
    except Exception as e:
        print(f"Error processing payment callback: {e}")  # Log error
        return False