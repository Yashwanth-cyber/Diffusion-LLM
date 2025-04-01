import streamlit as st
import random
import string
import time
import re
import google.generativeai as genai
import numpy as np
from PIL import Image
from io import BytesIO
import base64

# Set your Gemini API key here (hardcoded)
GEMINI_API_KEY = "AIzaSyBCwZfe7lZYeeraL2lLuzfNzi2qaE_7BHE"

# Page configuration
st.set_page_config(
    page_title="Supernatural Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for a professional, aesthetic UI
# - The header still uses a red, blue, and green gradient.
# - Assistant messages remain styled as before.
# - User messages now use a grayscale scheme.
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 6rem;  /* Extra bottom padding for chat input */
        max-width: 1200px;
        background-color: #111;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        margin-bottom: 120px;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    body {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #E5E5E5;
    }
    
    /* Header styling with red, blue, and green gradient */
    .logo-text {
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(135deg, #ff0000, #0000ff, #00ff00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .subheader {
        text-align: center;
        font-size: 1.2rem;
        color: #9ca3af;
        margin-bottom: 40px;
    }
    
    /* Chat container */
    .chat-container {
        padding: 0 20px;
        margin-bottom: 60px;
    }
    
    .message {
        display: flex;
        margin-bottom: 20px;
        align-items: flex-start;
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .assistant-message {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 75%;
        padding: 15px 20px;
        border-radius: 16px;
        font-size: 1rem;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* User message bubble: Grayscale styling */
    .user-bubble {
        background: linear-gradient(135deg, #444, #666);
        color: #fff;
        border-top-right-radius: 4px;
        margin-left: 60px;
    }
    
    /* Assistant message bubble remains unchanged */
    .assistant-bubble {
        background-color: #1e2028;
        border: 1px solid #30333d;
        color: #f1f3f4;
        border-top-left-radius: 4px;
        margin-right: 60px;
    }
    
    /* Avatar styling */
    .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #fff;
        margin: 0 15px;
    }
    
    /* User avatar: Grayscale */
    .user-avatar {
        background-color: #888888;
    }
    
    /* Assistant avatar remains unchanged (blue tone) */
    .assistant-avatar {
        background-color: #0000ff;
    }
    
    /* Bright and noticeable chat input styling */
    .stChatInput textarea {
        background-color: #1a1c23 !important;
        color: #ffffff !important;
        border: 2px solid #32CD32 !important;  /* Bright green border */
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 15px !important;
    }
    
    /* Code block styling */
    .code-block {
        background-color: #161b22;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Roboto Mono', monospace;
        overflow-x: auto;
        border: 1px solid #30333d;
        margin: 10px 0;
    }
    
    code {
        background-color: #1e2028;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.95em;
    }
    
    /* Typing indicator styling */
    .typing-indicator {
        display: flex;
        align-items: center;
    }
    
    .typing-indicator span {
        height: 12px;
        width: 12px;
        margin: 0 2px;
        background-color: #0000ff;
        display: block;
        border-radius: 50%;
        opacity: 0.5;
        animation: blink 1s infinite alternate;
    }
    
    @keyframes blink {
        0% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Diffusing text styling */
    .diffusing-char {
        display: inline-block;
        transition: color 0.2s ease, text-shadow 0.2s ease;
    }
    
    .diffusing-char.stable {
        color: #ffffff;
    }
    
    /* Dim color for processing text */
    .diffusing-char.changing {
        color: #888888;
    }
    
    /* Hide default Streamlit menu and footer */
    #MainMenu, footer, header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Create app header
def create_header():
    st.markdown("<h1 class='logo-text'>Supernatural Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Beyond Intelligence - Where AI Transcends</p>", unsafe_allow_html=True)

# Initialize Gemini API with the hardcoded API key
def initialize_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

# Character pool for diffusion effect
CHAR_POOL = string.ascii_letters + string.digits + string.punctuation + " \n\t"

# Enhanced diffusion text generator with improved transitions
def generate_diffusing_html(target_text, steps=30):
    current_chars = [random.choice(CHAR_POOL) for _ in range(len(target_text))]
    target_chars = list(target_text)
    all_positions = list(range(len(target_chars)))
    random.shuffle(all_positions)
    chars_per_step = max(1, len(target_chars) // steps)
    stable_positions = set()
    
    for step in range(steps + 1):
        new_stable_count = min(step * chars_per_step, len(all_positions))
        stable_positions = set(all_positions[:new_stable_count])
        
        for i in range(len(current_chars)):
            if i in stable_positions:
                current_chars[i] = target_chars[i]
            elif random.random() < 0.7:
                current_chars[i] = random.choice(CHAR_POOL)
                
        progress = min(1.0, step / steps)
        html_parts = []
        for i, char in enumerate(current_chars):
            if i in stable_positions:
                stability = progress
                css_class = "diffusing-char stable"
                color = f"rgb({77 + int(178 * stability)}, {79 + int(176 * stability)}, {85 + int(170 * stability)})"
                style = f"color: {color};"
            else:
                css_class = "diffusing-char changing"
                style = ""
            if char == '<':
                display_char = '&lt;'
            elif char == '>':
                display_char = '&gt;'
            elif char == '&':
                display_char = '&amp;'
            elif char == '\n':
                display_char = '<br>'
            elif char == ' ':
                display_char = '&nbsp;'
            else:
                display_char = char
            html_parts.append(f'<span class="{css_class}" style="{style}">{display_char}</span>')
            
        html = ''.join(html_parts)
        yield html
        
        if step < steps * 0.2 or step > steps * 0.8:
            time.sleep(0.06)
        else:
            time.sleep(0.04)
    
    final_html_parts = []
    for char in target_chars:
        if char == '<':
            display_char = '&lt;'
        elif char == '>':
            display_char = '&gt;'
        elif char == '&':
            display_char = '&amp;'
        elif char == '\n':
            display_char = '<br>'
        elif char == ' ':
            display_char = '&nbsp;'
        else:
            display_char = char
        final_html_parts.append(f'<span class="diffusing-char stable" style="color: #ffffff;">{display_char}</span>')
    
    final_html = ''.join(final_html_parts)
    yield final_html

# Process markdown and code blocks after diffusion
def process_markdown(text):
    if "```" in text:
        pattern = r"```(?:\w+)?\n([\s\S]*?)```"
        def replace_code_block(match):
            code = match.group(1)
            return f'<div class="code-block">{code}</div>'
        text = re.sub(pattern, replace_code_block, text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text

# Display a chat message
def display_message(role, content, is_diffusing=False):
    if role == "user":
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-bubble user-bubble">{content}</div>
            <div class="avatar user-avatar">You</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if is_diffusing:
            message_container = st.empty()
            return message_container
        else:
            st.markdown(f"""
            <div class="message assistant-message">
                <div class="avatar assistant-avatar">SI</div>
                <div class="message-bubble assistant-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)

# Display typing indicator with refined animation
def display_typing_indicator():
    indicator = st.empty()
    indicator.markdown(f"""
    <div class="message assistant-message">
        <div class="avatar assistant-avatar">SI</div>
        <div class="message-bubble assistant-bubble">
            <div class="typing-indicator">
                <span style="animation-delay: 0s;"></span>
                <span style="animation-delay: 0.2s;"></span>
                <span style="animation-delay: 0.4s;"></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return indicator

# Update diffusion text in UI
def update_diffusion_text(container, diffused_text):
    container.markdown(f"""
    <div class="message assistant-message">
        <div class="avatar assistant-avatar">SI</div>
        <div class="message-bubble assistant-bubble">
            {diffused_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main app function
def main():
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = initialize_gemini(GEMINI_API_KEY)
    
    create_header()
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                display_message("user", message["content"])
            else:
                display_message("assistant", message["content"], is_diffusing=False)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Use Streamlit's built-in chat input widget (Enter to submit, Shift+Enter for newline)
    user_input = st.chat_input("Enter your prompt...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.experimental_rerun()
    
    # Process the last user message if it exists
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        typing_indicator = display_typing_indicator()
        try:
            last_user_message = st.session_state.messages[-1]["content"]
            response = st.session_state.gemini_model.generate_content(last_user_message)
            target_text = response.text
            typing_indicator.empty()
            
            diffusion_container = display_message("assistant", "", is_diffusing=True)
            diffusion_steps = 50
            for diffused_html in generate_diffusing_html(target_text, steps=diffusion_steps):
                update_diffusion_text(diffusion_container, diffused_html)
            
            final_processed_text = process_markdown(target_text)
            final_html = final_processed_text.replace('<span class="diffusing-char stable"', 
                                                       '<span class="diffusing-char stable" style="color: #ffffff;"')
            update_diffusion_text(diffusion_container, final_html)
            st.session_state.messages.append({"role": "assistant", "content": final_processed_text})
        except Exception as e:
            typing_indicator.empty()
            error_msg = f"Error: {str(e)}"
            display_message("assistant", error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
