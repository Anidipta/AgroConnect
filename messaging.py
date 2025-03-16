import streamlit as st
import time
from database import *
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from translator import detect_language
import os
from datetime import datetime

def get_user_location():
    """Get user's current location using browser's geolocation"""
    location_script = """
    <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var coords = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                window.parent.postMessage({type: "location", coords: coords}, "*");
            },
            function(error) {
                console.error("Error getting location:", error);
            }
        );
    }
    </script>
    """
    st.components.v1.html(location_script, height=0)
    
    # Initialize location in session state if not present
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None

def update_user_location(lat, lng):
    """Update user's location in database"""
    if st.session_state.user:
        geolocator = Nominatim(user_agent="agroconnect")
        try:
            location = geolocator.reverse((lat, lng))
            address = location.address if location else f"{lat}, {lng}"
            
            conn = get_connection()
            conn.execute("""
                UPDATE users 
                SET location = ?, latitude = ?, longitude = ? 
                WHERE id = ?
            """, (address, lat, lng, st.session_state.user['id']))
            conn.commit()
            
            st.session_state.user['location'] = address
            st.session_state.user['latitude'] = lat
            st.session_state.user['longitude'] = lng
            return True
        except Exception as e:
            print(f"Error updating location: {e}")
            return False

def display_chat_interface(translator_func):
    """Display the chat interface with emoji and media support"""
    st.header(translator_func("Messages"))
    
    # Get current user's contacts
    contacts = get_user_contacts(st.session_state.user['id'], st.session_state.user['user_type'])
    
    # Create two columns: one for contacts, one for messages
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader(translator_func("Contacts"))
        
        # Search contacts
        search_query = st.text_input(translator_func("Search contacts..."), key="contact_search")
        
        # Filter contacts based on search
        filtered_contacts = [
            contact for contact in contacts
            if search_query.lower() in contact['name'].lower() or 
               search_query.lower() in contact.get('email', '').lower()
        ] if search_query else contacts
        
        # Display contacts
        for contact in filtered_contacts:
            if st.button(
                f"{contact['name']}\n{contact.get('email', '')}",
                key=f"contact_{contact['id']}",
                use_container_width=True
            ):
                st.session_state.selected_contact = contact
                st.rerun()
    
    with col2:
        if 'selected_contact' in st.session_state:
            contact = st.session_state.selected_contact
            st.subheader(f"Chat with {contact['name']}")
            
            # Get conversation history
            messages = get_conversation(st.session_state.user['id'], contact['id'])
            
            # Create a container for messages with fixed height and scrolling
            with st.container():
                for message in messages:
                    is_sent = message['sender_id'] == st.session_state.user['id']
                    
                    # Format timestamp
                    timestamp = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Message container
                    with st.container():
                        # Apply different styling for sent vs received messages
                        if is_sent:
                            cols = st.columns([2, 8])
                            with cols[1]:
                                st.markdown(
                                    f"""
                                    <div class="message-container sent-message">
                                        <div class="message-bubble message-sent">
                                            <div class="message-content">{message['content']}</div>
                                            <div class="message-footer">
                                                <span class="message-time">{formatted_time}</span>
                                                <span class="message-status">{'✓✓' if message['read'] else '✓'}</span>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        else:
                            cols = st.columns([8, 2])
                            with cols[0]:
                                st.markdown(
                                    f"""
                                    <div class="message-container received-message">
                                        <div class="message-bubble message-received">
                                            <div class="message-content">{message['content']}</div>
                                            <div class="message-footer">
                                                <span class="message-time">{formatted_time}</span>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
            
            # Message input area with emoji and media options
            with st.container():
                # Message input and tools in a single row
                cols = st.columns([1, 4, 1])
                
                with cols[0]:
                    st.markdown(
                        """
                        <div class="message-tools">
                            <button class="tool-button emoji-button" onclick="toggleEmojiPicker()">😊</button>
                            <button class="tool-button" onclick="document.getElementById('image-upload').click()">📷</button>
                            <button class="tool-button" onclick="document.getElementById('video-upload').click()">🎥</button>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with cols[1]:
                    # Add a key prefix to ensure uniqueness across reruns
                    message = st.text_input(
                        "",
                        key=f"message_input_{contact['id']}",
                        placeholder=translator_func("Type a message...")
                    )
                
                with cols[2]:
                    if st.button(translator_func("Send"), use_container_width=True):
                        if message or st.session_state.get('uploaded_image') or st.session_state.get('uploaded_video'):
                            content = message
                            
                            # Handle image upload
                            if 'uploaded_image' in st.session_state and st.session_state.uploaded_image:
                                image_path = save_uploaded_file(
                                    st.session_state.uploaded_image,
                                    "images",
                                    st.session_state.user['id']
                                )
                                content += f"\n<img src='{image_path}' class='message-image' />"
                            
                            # Handle video upload
                            if 'uploaded_video' in st.session_state and st.session_state.uploaded_video:
                                video_path = save_uploaded_file(
                                    st.session_state.uploaded_video,
                                    "videos",
                                    st.session_state.user['id']
                                )
                                content += f"\n<video controls class='message-video'><source src='{video_path}' type='video/mp4'></video>"
                            
                            # Insert message
                            insert_message(
                                st.session_state.user['id'],
                                contact['id'],
                                content,
                                st.session_state.user.get('language', 'en')
                            )
                            
                            # Clear the session state for the next rerun
                            for key in list(st.session_state.keys()):
                                if key.startswith('message_input_') or key in ['uploaded_image', 'uploaded_video']:
                                    del st.session_state[key]
                            
                            # Trigger rerun to refresh the chat
                            st.rerun()
                
                # Hidden file uploaders with unique keys
                uploaded_image = st.file_uploader(
                    "Upload Image",
                    type=["jpg", "jpeg", "png"],
                    key=f"image_upload_{contact['id']}",
                    label_visibility="collapsed"
                )
                if uploaded_image:
                    st.session_state.uploaded_image = uploaded_image
                
                uploaded_video = st.file_uploader(
                    "Upload Video",
                    type=["mp4", "mov", "avi"],
                    key=f"video_upload_{contact['id']}",
                    label_visibility="collapsed"
                )
                if uploaded_video:
                    st.session_state.uploaded_video = uploaded_video
        else:
            st.info(translator_func("Select a contact to start chatting"))

def save_uploaded_file(uploaded_file, folder_type, user_id):
    """Save uploaded media file and return the file path"""
    if uploaded_file is None:
        return None
    
    # Create directory if it doesn't exist
    folder_path = os.path.join("assets", folder_type, str(user_id))
    os.makedirs(folder_path, exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{folder_type}_{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(folder_path, filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def get_buyer_contacts(farmer_id):
    """Get all buyers who have interacted with the farmer"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT u.*, 
               t.created_at as last_interaction,
               COUNT(t.id) as transaction_count
        FROM users u
        LEFT JOIN transactions t ON u.id = t.buyer_id
        WHERE u.user_type = 'buyer'
        AND (
            t.farmer_id = ?
            OR EXISTS (
                SELECT 1 FROM messages m 
                WHERE (m.sender_id = ? AND m.receiver_id = u.id)
                OR (m.sender_id = u.id AND m.receiver_id = ?)
            )
        )
        GROUP BY u.id
        ORDER BY last_interaction DESC
    """, (farmer_id, farmer_id, farmer_id))
    
    contacts = []
    for row in cursor.fetchall():
        contact = dict(row)
        if contact.get('latitude') and contact.get('longitude'):
            contact['distance'] = calculate_distance(
                st.session_state.user.get('latitude'),
                st.session_state.user.get('longitude'),
                contact['latitude'],
                contact['longitude']
            )
        contacts.append(contact)
    
    return contacts

def get_farmer_contacts(buyer_id):
    """Get all farmers who have interacted with the buyer"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT u.*, 
               t.created_at as last_interaction,
               COUNT(t.id) as transaction_count
        FROM users u
        LEFT JOIN transactions t ON u.id = t.farmer_id
        WHERE u.user_type = 'farmer'
        AND (
            t.buyer_id = ?
            OR EXISTS (
                SELECT 1 FROM messages m 
                WHERE (m.sender_id = ? AND m.receiver_id = u.id)
                OR (m.sender_id = u.id AND m.receiver_id = ?)
            )
        )
        GROUP BY u.id
        ORDER BY last_interaction DESC
    """, (buyer_id, buyer_id, buyer_id))
    
    contacts = []
    for row in cursor.fetchall():
        contact = dict(row)
        if contact.get('latitude') and contact.get('longitude'):
            contact['distance'] = calculate_distance(
                st.session_state.user.get('latitude'),
                st.session_state.user.get('longitude'),
                contact['latitude'],
                contact['longitude']
            )
        contacts.append(contact)
    
    return contacts

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    try:
        return round(geodesic((lat1, lon1), (lat2, lon2)).kilometers, 1)
    except:
        return None 