import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Job Application Analytics - Simple",
    page_icon="📧",
    layout="wide"
)

def main():
    """Simple test version of the main application."""
    
    # Header
    st.title("📧 Job Application Analytics Dashboard")
    st.markdown("Simple test version - Connect to your email and analyze job application responses.")
    
    # Test basic functionality
    st.subheader("🔧 System Status")
    
    # Check imports
    try:
        from imap_tools import MailBox, AND
        st.success("✅ IMAP tools available")
    except ImportError:
        st.error("❌ IMAP tools not available")
    
    try:
        from bs4 import BeautifulSoup
        st.success("✅ BeautifulSoup available")
    except ImportError:
        st.warning("⚠️ BeautifulSoup not available")
    
    try:
        import openai
        st.success("✅ OpenAI available")
    except ImportError:
        st.warning("⚠️ OpenAI not available")
    
    try:
        from transformers import pipeline
        import torch
        st.success("✅ Transformers/Torch available")
    except ImportError:
        st.warning("⚠️ Transformers/Torch not available")
    
    # Test basic UI
    st.subheader("📊 Test Dashboard")
    
    # Create sample data
    sample_data = {
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'sender': ['company1@example.com', 'company2@example.com', 'company3@example.com'],
        'subject': ['Application Received', 'Interview Invitation', 'Thank you for your interest'],
        'status': ['Other', 'Interview', 'Rejected']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", len(df))
    
    with col2:
        st.metric("Rejected", len(df[df['status'] == 'Rejected']))
    
    with col3:
        st.metric("Interviews", len(df[df['status'] == 'Interview']))
    
    with col4:
        st.metric("Offers", len(df[df['status'] == 'Offer']))
    
    # Display table
    st.subheader("📧 Sample Email Data")
    st.dataframe(df, use_container_width=True)
    
    # Test sidebar
    st.sidebar.header("⚙️ Configuration")
    
    email_provider = st.sidebar.selectbox(
        "Email Provider:",
        ["Gmail"]
    )
    
    ai_mode = st.sidebar.selectbox(
        "AI Classification Mode:",
        ["Keywords"]
    )
    
    if st.sidebar.button("Test Connection"):
        st.success("✅ Connection test successful!")
    
    st.sidebar.info("This is a simplified test version of the app.")

if __name__ == "__main__":
    main()

