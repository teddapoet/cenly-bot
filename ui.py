import streamlit as st
import time
import requests
from datetime import datetime

# Import your Cenly bot
try:
    from cenly import cenly
    CENLY_AVAILABLE = True
except ImportError as e:
    CENLY_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Page configuration
st.set_page_config(
    page_title="Cenly AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    
    .chat-input {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #ddd;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def check_ollama_status():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def initialize_bot():
    """Initialize the Cenly bot"""
    if not CENLY_AVAILABLE:
        return False, f"Cannot import Cenly: {IMPORT_ERROR}"
    
    try:
        if 'cenly_bot' not in st.session_state:
            st.session_state.cenly_bot = cenly()
        return True, "Bot initialized successfully"
    except Exception as e:
        return False, f"Failed to initialize: {str(e)}"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 Cenly AI")
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System Status")
    
    if CENLY_AVAILABLE:
        st.markdown('<div class="status-success">✅ Cenly module loaded</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">❌ Import failed</div>', unsafe_allow_html=True)
        st.error(IMPORT_ERROR)
    
    # Check Ollama
    if check_ollama_status():
        st.markdown('<div class="status-success">✅ Ollama running</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">❌ Ollama offline</div>', unsafe_allow_html=True)
        st.warning("Start Ollama: `ollama serve`")
    
    st.markdown("---")
    
    # Controls
    st.markdown("### 🎛️ Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🆕 New", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.rerun()
    
    # Session info
    st.markdown("---")
    st.markdown("### 📈 Session")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    st.markdown(f"**Session ID:**")
    st.code(st.session_state.session_id, language=None)
    
    # About
    st.markdown("---")
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Cenly AI** helps you:
        - Analyze business data
        - Get financial insights
        - Query documents
        - Make data-driven decisions
        
        **Powered by:**
        - Ollama (Gemma)
        - LangChain
        - Vector Search
        """)

# Main content
st.markdown('<h1 class="main-header">🤖 Cenly AI Assistant</h1>', unsafe_allow_html=True)

# Initialize bot
bot_ready = False
if CENLY_AVAILABLE:
    success, message = initialize_bot()
    if success:
        bot_ready = True
    else:
        st.error(f"**Bot Error:** {message}")

# Chat interface
if not bot_ready:
    st.warning("⚠️ Bot not ready. Check sidebar for status.")
    st.info("Make sure Ollama is running and your Cenly module is working properly.")
else:
    # Display messages
    if not st.session_state.messages:
        # Welcome screen
        st.markdown("""
        ### 👋 Welcome to Cenly AI!
        
        I'm your AI business assistant, ready to help you analyze data and provide insights.
        
        **Try asking me:**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 What's our sales trend?", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What's our sales trend?"})
                st.rerun()
            
            if st.button("💰 Analyze financial performance", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Analyze our financial performance"})
                st.rerun()
        
        with col2:
            if st.button("🎯 Show key metrics", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Show me our key business metrics"})
                st.rerun()
                
            if st.button("💡 Business insights", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What insights can you provide?"})
                st.rerun()
    
    else:
        # Show chat history
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])

# Chat input
if bot_ready:
    if prompt := st.chat_input("Ask me anything about your business...", key="main_chat"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Generate bot response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Call your Cenly bot
                    response = st.session_state.cenly_bot.chat(prompt, st.session_state.session_id)
                    
                    # DEBUG: Check what we got back
                    print(f"DEBUG UI: Bot returned: {response}")
                    print(f"DEBUG UI: Type: {type(response)}")
                    
                    # Safety check
                    if response is None:
                        response = "Sorry, I got an empty response. Please try again."
                    elif not isinstance(response, str):
                        response = str(response)
                    
                    # Show response with typing effect
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Typing animation - now safe
                    words = response.split()
                    for i, word in enumerate(words):
                        full_response += word + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                            
                except Exception as e:
                    error_msg = f"""
                     **Error occurred:**
                    
                    ```
                    {str(e)}
                    ```
                    
                    **Troubleshooting:**
                    - Check if Ollama is running (`ollama serve`)
                    - Verify your vector store is set up
                    - Make sure all dependencies are installed
                    - Try refreshing the page
                    """
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem; padding: 2rem 0;'>"
    "Cenly AI Assistant - Powered by Ollama & LangChain"
    "</div>", 
    unsafe_allow_html=True
)