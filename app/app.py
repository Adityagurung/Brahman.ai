# app.py - Streamlit RAG Application with Feedback
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

def main():
    print_log("Starting the RAG Travel Assistant application")
    
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
        
        # User input
        user_input = st.text_area(
            "Enter your travel question:",
            placeholder="e.g., What are the must-see places in Karnataka?",
            height=100
        )

        if st.button("🔍 Get Answer", type="primary"):
            if user_input.strip():
                print_log(f"User asked: '{user_input}'")
                
                with st.spinner("Processing your question..."):
                    print_log(f"Getting answer using {model_choice} model and {search_type} search")
                    
                    start_time = time.time()
                    answer_data = get_answer(user_input, model_choice, search_type)
                    end_time = time.time()
                    
                    print_log(f"Answer received in {end_time - start_time:.2f} seconds")

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

                # Save conversation to database
                print_log("Saving conversation to database")
                save_conversation(str(uuid.uuid4()), user_input, answer_data)
                #save_conversation(st.session_state.conversation_id, user_input, answer_data)
                print_log("Conversation saved successfully")

                # Feedback section
                st.markdown("---")
                st.markdown("### 💭 Was this answer helpful?")
                
                # Feedback buttons with icons
                feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 4])
                
                with feedback_col1:
                    if st.button("👍 Helpful", key="thumbs_up"):
                        if not st.session_state.feedback_given:
                            save_feedback(st.session_state.conversation_id, 1)
                            st.session_state.feedback_given = True
                            st.success("Thank you for your feedback! 👍")
                            print_log("Positive feedback saved to database")
                        else:
                            st.info("Feedback already recorded for this conversation.")
                
                with feedback_col2:
                    if st.button("👎 Not Helpful", key="thumbs_down"):
                        if not st.session_state.feedback_given:
                            save_feedback(st.session_state.conversation_id, -1)
                            st.session_state.feedback_given = True
                            st.error("Thank you for your feedback. We'll try to improve! 👎")
                            print_log("Negative feedback saved to database")
                        else:
                            st.info("Feedback already recorded for this conversation.")

                # Reset for next question
                if st.button("🔄 Ask Another Question"):
                    st.session_state.conversation_id = str(uuid.uuid4())
                    st.session_state.feedback_given = False
                    st.rerun()
                    #st.experimental_rerun()

            else:
                st.warning("Please enter a question before submitting.")

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
                    if conv['feedback']:
                        feedback_text = "👍 Positive" if conv['feedback'] > 0 else "👎 Negative"
                        st.write(f"**Feedback:** {feedback_text}")

        except Exception as e:
            st.error("Could not load recent conversations")
            print_log(f"Error loading conversations: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p><em>Travel RAG Assistant - Powered by AI and Vector Search</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Travel RAG Assistant application started")
    main()