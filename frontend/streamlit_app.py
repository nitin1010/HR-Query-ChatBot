import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="HR Resource Query Chatbot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"


def init_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_available' not in st.session_state:
        st.session_state.api_available = False


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except requests.RequestException:
        return False, None


def send_chat_query(query: str, top_k: int = 5):
    """Send chat query to the API."""
    try:
        payload = {"query": query, "top_k": top_k}
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=120  # Increased timeout for GGUF model
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return False, f"Connection Error: {str(e)}"


def search_employees_api(filters: Dict[str, Any]):
    """Search employees using API filters."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/employees/search",
            params=filters,
            timeout=60  # Increased timeout
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code}"
    except requests.RequestException as e:
        return False, f"Connection Error: {str(e)}"


def get_employee_stats():
    """Get employee statistics from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/employees/stats", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code}"
    except requests.RequestException as e:
        return False, f"Connection Error: {str(e)}"


def display_employee_card(employee: Dict[str, Any]):
    """Display employee information in a card format."""
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(f"👤 {employee['name']}")
            st.write(f"**Role:** {employee['role']}")
            st.write(f"**Department:** {employee['department']}")
            st.write(f"**Experience:** {employee['experience_years']} years")

            # Skills as badges
            skills_html = ""
            for skill in employee['skills']:
                skills_html += f'<span style="background-color: #e1f5fe; color: #01579b; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 12px;">{skill}</span> '
            st.markdown(f"**Skills:** {skills_html}", unsafe_allow_html=True)

            # Projects
            if employee['projects']:
                st.write("**Recent Projects:**")
                for project in employee['projects']:
                    st.write(f"• {project}")

        with col2:
            # Availability status
            if employee['availability'] == 'available':
                st.success("✅ Available")
            else:
                st.error("❌ Busy")

            # Similarity score if available
            if 'similarity_score' in employee:
                st.metric("Match Score", f"{employee['similarity_score']:.2f}")


def main():
    """Main Streamlit application."""
    init_session_state()

    # Header
    st.title("🎯 HR Resource Query Chatbot")
    st.markdown("*AI-powered assistant for finding the right employees for your projects*")

    # Check API health
    api_healthy, health_data = check_api_health()
    st.session_state.api_available = api_healthy

    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        if api_healthy:
            st.success("✅ API Connected")
            if health_data:
                st.info(f"RAG System: {'✅' if health_data.get('rag_system_loaded') else '❌'}")
                st.info(f"AI Model: {'✅' if health_data.get('model_loaded') else '❌'}")
        else:
            st.error("❌ API Disconnected")
            st.warning("Please start the FastAPI server first:")
            st.code("uvicorn api.main:app --reload")

        st.divider()

        # Quick search examples
        st.header("💡 Example Queries")
        example_queries = [
            "Find Python developers with 3+ years experience",
            "Who has worked on healthcare projects?",
            "Suggest people for a React Native project",
            "Find developers who know both AWS and Docker",
            "I need someone experienced with machine learning",
            "Show me available frontend developers"
        ]

        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.current_query = query

    # Main content
    if not api_healthy:
        st.error("🔌 Cannot connect to the API server. Please make sure the FastAPI server is running.")
        st.info("Run: `uvicorn api.main:app --reload` in your project directory")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["💬 Chat Query", "📊 Statistics"])

    with tab1:
        st.header("Chat with HR Assistant")

        # Chat input
        query = st.text_input(
            "Ask me anything about finding employees:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., Find Python developers with 3+ years experience",
            key="chat_input"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            top_k = st.slider("Max Results", 1, 10, 5)
        with col2:
            send_button = st.button("🚀 Send Query", type="primary")

        if send_button and query:
            with st.spinner(
                    "🔍 Searching employees and generating AI response... This may take 30-60 seconds for the first query."):
                # Show progress steps
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔍 Step 1/3: Finding relevant employees...")
                progress_bar.progress(33)

                success, result = send_chat_query(query, top_k)

                if success:
                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

                    # Add to chat history
                    st.session_state.chat_history.append({
                        'query': query,
                        'response': result['response'],
                        'employees': result['relevant_employees']
                    })

                    # Display response
                    st.subheader("🤖 AI Response")
                    st.write(result['response'])

                    # Display relevant employees
                    if result['relevant_employees']:
                        st.subheader(f"👥 Found {len(result['relevant_employees'])} Relevant Employees")
                        for emp in result['relevant_employees']:
                            display_employee_card(emp)
                            st.divider()
                    else:
                        st.info("No employees found matching your criteria.")
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Error: {result}")

        # Chat history
        if st.session_state.chat_history:
            st.subheader("📝 Recent Queries")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
                with st.expander(f"Query: {chat['query'][:50]}..."):
                    st.write("**Response:**", chat['response'])
                    if chat['employees']:
                        st.write(f"**Found {len(chat['employees'])} employees**")

    with tab2:
        st.header("Employee Statistics")

        if st.button("📊 Refresh Statistics"):
            with st.spinner("Loading statistics..."):
                success, stats = get_employee_stats()

                if success:
                    # Overview metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Employees", stats['total_employees'])
                    with col2:
                        st.metric("Available", stats['available_employees'])
                    with col3:
                        st.metric("Busy", stats['busy_employees'])
                    with col4:
                        st.metric("Avg Experience", f"{stats['average_experience']} years")

                    # Department distribution
                    st.subheader("👥 Department Distribution")
                    dept_df = pd.DataFrame(list(stats['departments'].items()), columns=['Department', 'Count'])
                    st.bar_chart(dept_df.set_index('Department'))

                    # Top skills
                    st.subheader("🛠️ Top Skills")
                    skills_df = pd.DataFrame(list(stats['top_skills'].items()), columns=['Skill', 'Count'])
                    st.bar_chart(skills_df.set_index('Skill'))

                else:
                    st.error(f"Failed to load statistics: {stats}")


if __name__ == "__main__":
    main()