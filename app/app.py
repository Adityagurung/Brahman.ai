# app.py - Enhanced UI with Fixed Submit Button and Toast Notifications
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
    """Inject custom CSS for enhanced UI design"""
    st.markdown("""
    <style>
    /* Hide the default submit button */
    .stFormSubmitButton > button {
        display: none;
    }
    
    /* Container for text area with integrated button */
    .textarea-container {
        position: relative;
        width: 100%;
    }
    
    /* Enhanced text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e0e6ed !important;
        font-size: 16px !important;
        padding-right: 60px !important;
        transition: all 0.3s ease !important;
        resize: vertical !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #20B2AA !important;
        box-shadow: 0 0 0 3px rgba(32, 178, 170, 0.1) !important;
        outline: none !important;
    }
    
    /* Fix for textarea container positioning */
    .stTextArea > div {
        position: relative !important;
    }
    
    /* Custom submit button positioned inside textarea */
    .custom-submit-button {
        position: absolute !important;
        right: 10px !important;
        top: 15px !important;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #20B2AA 0%, #008B8B 100%);
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(32, 178, 170, 0.4);
        transition: all 0.3s ease;
        z-index: 1000;
        pointer-events: all;
    }
    
    .custom-submit-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(32, 178, 170, 0.6);
        background: linear-gradient(135deg, #008B8B 0%, #20B2AA 100%);
    }
    
    .custom-submit-button:active {
        transform: scale(0.95);
    }
    
    /* Enhanced arrow with longer tail like ChatGPT */
    .submit-arrow {
        width: 0;
        height: 0;
        border-left: 12px solid white;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
        margin-left: 3px;
    }
    
    /* Form styling */
    .stForm {
        border: none !important;
        padding: 0 !important;
    }
    
    /* Fixed height feedback container to prevent layout shifts */
    .feedback-container {
        min-height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .feedback-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
    }
    
    .feedback-message {
        min-height: 30px;
        display: flex;
        align-items: center;
    }
    
    /* Toast notification styles */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 9999;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    }
    
    .toast.show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .toast.success {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    }
    
    .toast.error {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    }
    
    .toast.info {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        border-radius: 8px !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    /* Thumbs up button */
    .feedback-buttons .stButton:first-child > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    .feedback-buttons .stButton:first-child > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Thumbs down button */
    .feedback-buttons .stButton:nth-child(2) > button {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        color: white !important;
    }
    
    .feedback-buttons .stButton:nth-child(2) > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
    }
    
    /* Reset button styling */
    .reset-button > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        width: 100% !important;
    }
    
    .reset-button > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    </style>
    
    <script>
    // Toast notification function
    function showToast(message, type = 'success') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        // Add to document
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Hide and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
    
    // Enhanced submit button click handler
    function submitForm() {
        const form = document.querySelector('[data-testid="stForm"]');
        const submitButton = form.querySelector('[data-testid="stFormSubmitButton"] button');
        if (submitButton) {
            submitButton.click();
            return true;
        }
        return false;
    }
    
    // Keyboard shortcut handler
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            submitForm();
        }
    });
    </script>
    """, unsafe_allow_html=True)

def show_toast(message, toast_type="success"):
    """Show toast notification using JavaScript"""
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        if (typeof showToast === 'function') {{
            showToast('{message}', '{toast_type}');
        }}
    }}, 100);
    </script>
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
    
    st.title("🌍 Travel RAG Assistant")
    st.markdown("Ask me anything about travel destinations!")

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")

    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False
    
    if "current_answer_data" not in st.session_state:
        st.session_state.current_answer_data = None

    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Model selection
    model_choice = st.sidebar.selectbox(
        "Select a model:",
        ["openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini", "ollama/phi3"],
        index=0
    )
    print_log(f"User selected model: {model_choice}")

    # Search type selection
    search_type = st.sidebar.radio(
        "Select search type:", 
        ["semantic", "hybrid"],
        index=0
    )
    print_log(f"User selected search type: {search_type}")

    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Ask Your Question")
        
        # Enhanced form with integrated submit button
        with st.form(key="question_form", clear_on_submit=False, border=False):
            # User input with container for button integration
            user_input = st.text_area(
                "",
                placeholder="e.g., What are the must-see places in Karnataka?\n\nTip: Press Ctrl+Enter or click the teal arrow to submit",
                height=120,
                key="user_question",
                label_visibility="collapsed"
            )
            
            # Hidden form submit button
            submitted = st.form_submit_button("Submit", use_container_width=False)
            
            # Custom submit button positioned absolutely inside the textarea
            st.markdown('''
            <script>
            // Wait for textarea to be rendered, then add button
            setTimeout(function() {
                const textareas = document.querySelectorAll('.stTextArea textarea');
                if (textareas.length > 0) {
                    const textarea = textareas[textareas.length - 1]; // Get the last textarea (current one)
                    const textareaParent = textarea.parentElement;
                    
                    // Remove any existing custom button
                    const existingButton = textareaParent.querySelector('.custom-submit-button');
                    if (existingButton) {
                        existingButton.remove();
                    }
                    
                    // Create and add the button
                    const button = document.createElement('div');
                    button.className = 'custom-submit-button';
                    button.title = 'Submit Question';
                    button.innerHTML = '<div class="submit-arrow"></div>';
                    button.onclick = function() { submitForm(); };
                    
                    textareaParent.appendChild(button);
                }
            }, 100);
            </script>
            ''', unsafe_allow_html=True)

        # Process form submission
        if submitted and user_input.strip():
            with st.spinner("Processing your question..."):
                print_log(f"User asked: '{user_input}'")
                
                print_log(f"Getting answer using {model_choice} model and {search_type} search")
                start_time = time.time()
                answer_data = get_answer(user_input, model_choice, search_type)
                end_time = time.time()
                
                print_log(f"Answer received in {end_time - start_time:.2f} seconds")
                
                # Save conversation
                print_log(f"Saving conversation with ID: {st.session_state.conversation_id}")
                save_conversation(st.session_state.conversation_id, user_input, answer_data)
                print_log("Conversation saved successfully")
                
                # Store in session state for feedback functionality
                st.session_state.current_answer_data = answer_data
                
                # Show success toast
                show_toast("Answer generated successfully! 🎉", "success")

        elif submitted and not user_input.strip():
            st.warning("Please enter a question before submitting.")
            show_toast("Please enter a question first", "error")

        # Display answer if available
        if st.session_state.current_answer_data:
            answer_data = st.session_state.current_answer_data
            
            # Display answer
            st.success("✅ Answer Generated!")
            st.markdown("### Answer:")
            st.write(answer_data["answer"])

            # Display metadata
            with st.expander("📊 Response Details"):
                col_meta1, col_meta2 = st.columns(2)
                
                with col_meta1:
                    st.metric("Response Time", f"{answer_data['response_time']:.2f}s")
                    st.metric("Relevance", answer_data['relevance'])
                    st.metric("Model Used", answer_data['model_used'])
                
                with col_meta2:
                    st.metric("Total Tokens", answer_data['total_tokens'])
                    st.metric("Search Results", answer_data['search_results_count'])
                    if answer_data["openai_cost"] > 0:
                        st.metric("OpenAI Cost", f"${answer_data['openai_cost']:.4f}")

            # Enhanced feedback section with fixed layout
            st.markdown("---")
            st.markdown("### 💭 Was this answer helpful?")
            
            # Fixed-height feedback container
            st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
            st.markdown('<div class="feedback-buttons">', unsafe_allow_html=True)
            
            # Feedback buttons in columns
            feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 4])
            
            with feedback_col1:
                if st.button("👍 Helpful", key="thumbs_up"):
                    if not st.session_state.feedback_given:
                        save_feedback(st.session_state.conversation_id, 1)
                        st.session_state.feedback_given = True
                        show_toast("Thank you for your positive feedback! 👍", "success")
                        print_log(f"Positive feedback saved for conversation: {st.session_state.conversation_id}")
                    else:
                        show_toast("Feedback already recorded for this conversation", "info")
            
            with feedback_col2:
                if st.button("👎 Not Helpful", key="thumbs_down"):
                    if not st.session_state.feedback_given:
                        save_feedback(st.session_state.conversation_id, -1)
                        st.session_state.feedback_given = True
                        show_toast("Thank you for your feedback. We'll improve! 👎", "error")
                        print_log(f"Negative feedback saved for conversation: {st.session_state.conversation_id}")
                    else:
                        show_toast("Feedback already recorded for this conversation", "info")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Feedback status (without layout shifts)
            st.markdown('<div class="feedback-message">', unsafe_allow_html=True)
            if st.session_state.feedback_given:
                st.markdown("*Feedback recorded for this conversation*")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Reset button with enhanced styling
        st.markdown('<div class="reset-button">', unsafe_allow_html=True)
        if st.button("🔄 Ask Another Question"):
            st.session_state.conversation_id = str(uuid.uuid4())
            st.session_state.feedback_given = False
            st.session_state.current_answer_data = None
            print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
            show_toast("Ready for your next question! 🚀", "info")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("📊 Statistics")
        
        # Feedback stats
        try:
            feedback_stats = get_feedback_stats()
            st.metric("👍 Positive Feedback", feedback_stats['thumbs_up'])
            st.metric("👎 Negative Feedback", feedback_stats['thumbs_down'])
            
            total_feedback = feedback_stats['thumbs_up'] + feedback_stats['thumbs_down']
            if total_feedback > 0:
                satisfaction_rate = (feedback_stats['thumbs_up'] / total_feedback) * 100
                st.metric("😊 Satisfaction Rate", f"{satisfaction_rate:.1f}%")
        except Exception as e:
            st.error("Could not load feedback statistics")
            print_log(f"Error loading feedback stats: {e}")

        # Recent conversations
        st.subheader("🕐 Recent Conversations")
        
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
        <div style='text-align: center'>
            <p><em>Travel RAG Assistant - Powered by AI and Vector Search</em></p>
            <p><small>💡 Tip: Use Ctrl+Enter or click the teal arrow to submit quickly!</small></p>
            <p><small>🎯 Enhanced UI with toast notifications and improved user experience</small></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Travel RAG Assistant application started")
    main()