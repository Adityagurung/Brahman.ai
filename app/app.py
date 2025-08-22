# app.py - Enhanced UI with Custom Submit Button
import streamlit as st
import time
import uuid
from rag import get_answer
from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
    get_model_usage_stats
)


def print_log(message):
    """Print log message"""
    print(message, flush=True)


def inject_custom_css():
    """Inject enhanced custom CSS with all fixes"""
    st.markdown("""
    <style>
    /* Hide the default submit button */
    .stFormSubmitButton > button {
        display: none;
    }
    
    /* Enhanced form container */
    .stForm {
        border: none !important;
        padding: 0 !important;
        position: relative;
    }
    
    /* Custom submit button container - positioned relative to form */
    .custom-submit-container {
        position: relative;
        display: block;
        width: 100%;
    }
    
    /* Enhanced custom submit button styles */
    .custom-submit-button {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        width: 40px;
        height: 40px;
        background: #20b2aa; /* TEAL color */
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(32, 178, 170, 0.4);
        transition: all 0.3s ease;
        z-index: 1000;
        pointer-events: auto;
    }
    
    .custom-submit-button:hover {
        transform: translateY(-50%) scale(1.1);
        box-shadow: 0 6px 20px rgba(32, 178, 170, 0.6);
        background: #008b8b; /* Darker teal on hover */
    }
    
    .custom-submit-button:active {
        transform: translateY(-50%) scale(0.95);
        background: #006666;
    }
    
    /* Enhanced arrow - made longer and more prominent */
    .submit-arrow {
        width: 0;
        height: 0;
        border-left: 12px solid white; /* Increased from 8px to 12px */
        border-top: 8px solid transparent; /* Increased from 6px to 8px */
        border-bottom: 8px solid transparent; /* Increased from 6px to 8px */
        margin-left: 3px; /* Increased margin for better centering */
        transform: rotate(-90deg);
    }
    
    /* Enhanced text area styling with proper padding for button */
    .stTextArea > div > div > textarea {
        padding-right: 55px !important;
        border-radius: 15px !important;
        border: 2px solid #e0e6ed !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #20b2aa !important;
        box-shadow: 0 0 0 3px rgba(32, 178, 170, 0.15) !important;
        outline: none !important;
    }
    
    /* Enhanced feedback section styling */
    .feedback-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f8ff 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e8f0fe;
        margin-top: 20px;
    }
    
    /* Fixed feedback buttons container */
    .feedback-buttons-container {
        display: flex;
        gap: 15px;
        align-items: flex-start;
        min-height: 50px; /* Fixed height to prevent layout shifts */
    }
    
    /* Enhanced feedback buttons */
    .stButton > button {
        border-radius: 25px !important;
        border: 2px solid transparent !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        height: 45px !important;
        min-width: 120px !important;
    }
    
    /* Thumbs up button styling */
    .feedback-buttons-container .stButton:nth-child(1) > button {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        color: white !important;
    }
    
    .feedback-buttons-container .stButton:nth-child(1) > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* Thumbs down button styling */
    .feedback-buttons-container .stButton:nth-child(2) > button {
        background: linear-gradient(135deg, #f44336, #da190b) !important;
        color: white !important;
    }
    
    .feedback-buttons-container .stButton:nth-child(2) > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(244, 67, 54, 0.4) !important;
    }
    
    /* Fixed feedback message container */
    .feedback-message {
        min-height: 50px;
        display: flex;
        align-items: center;
        margin-left: 20px;
        flex: 1;
    }
    
    /* Enhanced title styling */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 30px;
    }
    
    /* Enhanced metrics styling */
    .metric-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #20b2aa;
        margin-bottom: 10px;
    }
    
    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9ff !important;
        border-radius: 10px !important;
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Loading spinner enhancement */
    .stSpinner > div {
        border-top-color: #20b2aa !important;
    }
    
    /* Success message enhancement */
    .stSuccess {
        background-color: #e8f5e8 !important;
        border-left: 5px solid #4CAF50 !important;
        border-radius: 10px !important;
    }
    
    /* Warning message enhancement */
    .stWarning {
        background-color: #fff3e0 !important;
        border-left: 5px solid #ff9800 !important;
        border-radius: 10px !important;
    }
    
    /* Error message enhancement */
    .stError {
        background-color: #ffebee !important;
        border-left: 5px solid #f44336 !important;
        border-radius: 10px !important;
    }
    
    /* Info message enhancement */
    .stInfo {
        background-color: #e3f2fd !important;
        border-left: 5px solid #2196f3 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    print_log("Starting the RAG Travel Assistant application")
    
    # Inject custom CSS
    inject_custom_css()
    
    # Set page config
    st.set_page_config(
        page_title="Travel RAG Assistant",
        page_icon="🌍",
        layout="wide"
    )
    
    # Enhanced title
    st.markdown('<h1 class="main-title">🌍 Travel RAG Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #666; margin-bottom: 30px;'>Ask me anything about travel destinations!</p>", unsafe_allow_html=True)

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")

    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False
    
    if "current_answer_data" not in st.session_state:
        st.session_state.current_answer_data = None

    # Enhanced sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Model selection
        model_choice = st.selectbox(
            "Select a model:",
            ["openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini", "ollama/phi3"],
            index=0
        )
        print_log(f"User selected model: {model_choice}")

        # Search type selection
        search_type = st.radio(
            "Select search type:", 
            ["semantic", "hybrid"],
            index=0
        )
        print_log(f"User selected search type: {search_type}")

    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### ❓ Ask Your Question")
        
        # Enhanced form with fixed button functionality
        with st.form(key="question_form", clear_on_submit=False, border=False):
            # Container for custom button positioning
            st.markdown('<div class="custom-submit-container">', unsafe_allow_html=True)
            
            # User input
            user_input = st.text_area(
                "",  # Empty label for cleaner look
                placeholder="e.g., What are the must-see places in Karnataka?\n\n💡 Tip: Press Ctrl+Enter or click the teal arrow to submit",
                height=120,
                key="user_question",
                label_visibility="collapsed"
            )
            
            # Hidden form submit button (we'll use custom styling)
            submitted = st.form_submit_button("Submit", use_container_width=False)
            
            # Fixed custom submit button with proper JavaScript
            button_html = '''
            <div class="custom-submit-button" 
                 onclick="
                    const submitBtn = document.querySelector('button[kind=\\"formSubmit\\"]');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                 "
                 title="Submit your question">
                <div class="submit-arrow"></div>
            </div>
            <script>
                // Enhanced keyboard support
                document.addEventListener('keydown', function(e) {
                    if (e.ctrlKey && e.key === 'Enter') {
                        const submitBtn = document.querySelector('button[kind=\\"formSubmit\\"]');
                        if (submitBtn) {
                            submitBtn.click();
                        }
                    }
                });
            </script>
            '''
            st.markdown(button_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Process form submission
        if submitted and user_input.strip():
            with st.spinner("🔍 Processing your question..."):
                print_log(f"User asked: '{user_input}'")
                
                print_log(f"Getting answer using {model_choice} model and {search_type} search")
                start_time = time.time()
                answer_data = get_answer(user_input, model_choice, search_type)
                end_time = time.time()
                
                print_log(f"Answer received in {end_time - start_time:.2f} seconds")
                
                # Save conversation using the same conversation_id
                print_log(f"Saving conversation with ID: {st.session_state.conversation_id}")
                save_conversation(st.session_state.conversation_id, user_input, answer_data)
                print_log("Conversation saved successfully")
                
                # Store in session state for feedback functionality
                st.session_state.current_answer_data = answer_data

        elif submitted and not user_input.strip():
            st.warning("⚠️ Please enter a question before submitting.")

        # Display answer if available
        if st.session_state.current_answer_data:
            answer_data = st.session_state.current_answer_data
            
            # Display answer
            st.success("✅ Answer Generated Successfully!")
            st.markdown("### 💬 Answer:")
            st.markdown(f"<div style='background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #20b2aa; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 15px 0;'>{answer_data['answer']}</div>", unsafe_allow_html=True)

            # Display metadata
            with st.expander("📊 Response Details"):
                col_meta1, col_meta2 = st.columns(2)
                
                with col_meta1:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("⏱️ Response Time", f"{answer_data['response_time']:.2f}s")
                    st.metric("🎯 Relevance", answer_data['relevance'])
                    st.metric("🤖 Model Used", answer_data['model_used'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_meta2:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("📝 Total Tokens", answer_data['total_tokens'])
                    st.metric("🔍 Search Results", answer_data['search_results_count'])
                    if answer_data["openai_cost"] > 0:
                        st.metric("💰 OpenAI Cost", f"${answer_data['openai_cost']:.4f}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Enhanced feedback section with fixed alignment
            st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
            st.markdown("### 💭 Was this answer helpful?")
            
            # Fixed feedback buttons container
            st.markdown('<div class="feedback-buttons-container">', unsafe_allow_html=True)
            feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 2])
            
            with feedback_col1:
                thumbs_up_clicked = st.button("👍 Helpful", key="thumbs_up")
            
            with feedback_col2:
                thumbs_down_clicked = st.button("👎 Not Helpful", key="thumbs_down")
            
            with feedback_col3:
                # Fixed message container with consistent height
                st.markdown('<div class="feedback-message">', unsafe_allow_html=True)
                if thumbs_up_clicked:
                    if not st.session_state.feedback_given:
                        save_feedback(st.session_state.conversation_id, 1)
                        st.session_state.feedback_given = True
                        st.success("Thank you for your positive feedback! 👍")
                        print_log(f"Positive feedback saved for conversation: {st.session_state.conversation_id}")
                    else:
                        st.info("Feedback already recorded for this conversation.")
                
                elif thumbs_down_clicked:
                    if not st.session_state.feedback_given:
                        save_feedback(st.session_state.conversation_id, -1)
                        st.session_state.feedback_given = True
                        st.error("Thank you for your feedback. We'll try to improve! 👎")
                        print_log(f"Negative feedback saved for conversation: {st.session_state.conversation_id}")
                    else:
                        st.info("Feedback already recorded for this conversation.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Reset for next question
        if st.button("🔄 Ask Another Question", use_container_width=True):
            st.session_state.conversation_id = str(uuid.uuid4())
            st.session_state.feedback_given = False
            st.session_state.current_answer_data = None
            print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
            st.rerun()

    with col2:
        st.markdown("### 📊 Statistics")
        
        # Feedback stats
        try:
            feedback_stats = get_feedback_stats()
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("👍 Positive Feedback", feedback_stats['thumbs_up'])
            st.metric("👎 Negative Feedback", feedback_stats['thumbs_down'])
            
            total_feedback = feedback_stats['thumbs_up'] + feedback_stats['thumbs_down']
            if total_feedback > 0:
                satisfaction_rate = (feedback_stats['thumbs_up'] / total_feedback) * 100
                st.metric("😊 Satisfaction Rate", f"{satisfaction_rate:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error("Could not load feedback statistics")
            print_log(f"Error loading feedback stats: {e}")

        # Recent conversations
        st.markdown("### 🕐 Recent Conversations")
        
        # Relevance filter
        relevance_filter = st.selectbox(
            "Filter by relevance:",
            ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"],
            key="relevance_filter"
        )

        try:
            recent_conversations = get_recent_conversations(
                limit=3, 
                relevance=relevance_filter if relevance_filter != "All" else None
            )

            for i, conv in enumerate(recent_conversations):
                with st.expander(f"Q{i+1}: {conv['question'][:50]}..."):
                    st.write(f"**Q:** {conv['question']}")
                    st.write(f"**A:** {conv['answer'][:200]}...")
                    st.write(f"**Relevance:** {conv['relevance']}")
                    st.write(f"**Model:** {conv['model_used']}")
                    # Display timestamp in local timezone
                    st.write(f"**Time:** {conv['timestamp']}")
                    if conv['feedback']:
                        feedback_text = "👍 Positive" if conv['feedback'] > 0 else "👎 Negative"
                        st.write(f"**Feedback:** {feedback_text}")

        except Exception as e:
            st.error("Could not load recent conversations")
            print_log(f"Error loading conversations: {e}")

    # Enhanced footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 15px; margin-top: 30px;'>
            <p style='font-size: 1.1em; font-weight: 600; color: #333;'><em>🌍 Travel RAG Assistant - Powered by AI</em></p>
            <p style='color: #666;'><small>💡 Tip: Use Ctrl+Enter or click the teal arrow to submit quickly!</small></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("Travel RAG Assistant application started")
    main()
