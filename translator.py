import streamlit as st
from googletrans import Translator, LANGUAGES as GOOGLE_LANGUAGES
import functools
from config import LANGUAGES

# Initialize the translator with retries
def get_translator():
    try:
        return Translator(service_urls=['translate.google.com'])
    except:
        return None

translator = get_translator()

def translate_text(text, target_language='en', source_language=None):
    """
    Translate text to target language with better error handling
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (default: 'en')
        source_language (str, optional): Source language code. If None, it's auto-detected.
        
    Returns:
        str: Translated text
    """
    # Return early if text is None or empty
    if not text or not isinstance(text, str) or text.strip() == "":
        return text
        
    # Return original text if translator isn't available
    if not translator:
        return text
        
    # Return original text if it's already in English and contains only ASCII
    if target_language == 'en' and all(c.isascii() for c in text):
        return text
    
    try:
        # Ensure target_language is valid
        target_language = str(target_language).lower() if target_language else 'en'
        if target_language not in GOOGLE_LANGUAGES:
            return text
            
        # Attempt translation
        translation = translator.translate(text, dest=target_language, src=source_language or 'auto')
        return translation.text if translation and hasattr(translation, 'text') else text
    except Exception as e:
        print(f"Translation error: {str(e)}")  # Log error but don't show to user
        return text  # Return original text if translation fails

def get_translator_for_user(user_language='en'):
    """
    Returns a partial function that translates to the user's preferred language
    
    Args:
        user_language (str): User's preferred language code
        
    Returns:
        function: Translator function preset with the user's language
    """
    # Validate language code
    user_language = user_language if user_language in GOOGLE_LANGUAGES else 'en'
    return functools.partial(translate_text, target_language=user_language)

def translate_messages(messages, target_language):
    """
    Translate a list of messages to the target language
    
    Args:
        messages (list): List of message dictionaries
        target_language (str): Target language code
        
    Returns:
        list: Translated messages
    """
    if not translator:  # If translator isn't available, return original messages
        return messages
        
    for message in messages:
        if not isinstance(message, dict):
            continue
            
        original_lang = message.get('original_language', 'en')
        content = message.get('content', '')
        
        # Only translate if content exists and languages differ
        if content and original_lang != target_language:
            message['translated_content'] = translate_text(
                content, 
                target_language=target_language,
                source_language=original_lang
            )
        else:
            message['translated_content'] = content
    
    return messages

def detect_language(text):
    """
    Detect the language of a text
    
    Args:
        text (str): Text to detect language for
        
    Returns:
        str: Language code
    """
    if not text or not isinstance(text, str) or not translator:
        return 'en'
        
    try:
        detection = translator.detect(text)
        return detection.lang if detection and hasattr(detection, 'lang') else 'en'
    except:
        return 'en'  # Default to English if detection fails