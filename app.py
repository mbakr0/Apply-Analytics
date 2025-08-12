import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import time
from typing import List, Dict, Optional, Tuple
import re
from pathlib import Path

# Email and AI imports
from imap_tools import MailBox, AND
try:
    from bs4 import BeautifulSoup
    BeautifulSoup_available = True
except ImportError:
    BeautifulSoup = None
    BeautifulSoup_available = False

try:
    import openai
    openai_available = True
except ImportError:
    openai = None
    openai_available = False

# Disable transformers for now to prevent app crashes
pipeline = None
torch = None
transformers_available = False

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Job Application Analytics",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'email_data' not in st.session_state:
    st.session_state.email_data = []
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = None

# Constants
EMAIL_CATEGORIES = ['Rejected', 'Interview', 'Offer', 'Other']
DATA_FILE = 'email_history.csv'
LAST_FETCH_FILE = 'last_fetch.txt'

def check_dependencies():
    """Check and display dependency status."""
    warnings = []
    
    if not BeautifulSoup_available:
        warnings.append("BeautifulSoup4 not found. Some email parsing features may not work properly.")
    
    if not openai_available:
        warnings.append("OpenAI not found. OpenAI classification will not be available.")
    
    if not transformers_available:
        warnings.append("Transformers/Torch not found. Hugging Face classification will not be available.")
    
    if warnings:
        with st.expander("⚠️ Dependency Warnings", expanded=True):
            st.warning("Some optional dependencies are missing:")
            for warning in warnings:
                st.text(f"• {warning}")
            st.info("The app will work with keyword-based classification. Install missing packages for additional features.")
            st.code("pip install beautifulsoup4 openai transformers torch")

def connect_gmail(email: str, password: str) -> Optional[MailBox]:
    """
    Connect to Gmail using IMAP with app password.
    
    Args:
        email: Gmail address
        password: App password (not regular password)
    
    Returns:
        MailBox object if successful, None otherwise
    """
    try:
        mailbox = MailBox('imap.gmail.com')
        mailbox.login(email, password)
        return mailbox
    except Exception as e:
        st.error(f"Gmail connection failed: {str(e)}")
        return None

def fetch_emails_gmail(mailbox: MailBox, limit: int = 200) -> List[Dict]:
    """
    Fetch emails from Gmail using IMAP.
    
    Args:
        mailbox: Connected MailBox object
        limit: Maximum number of emails to fetch
    
    Returns:
        List of email dictionaries
    """
    emails = []
    try:
        for msg in mailbox.fetch(AND(all=True), limit=limit):
            # Extract body text
            body = ""
            if msg.html and BeautifulSoup_available:
                soup = BeautifulSoup(msg.html, 'html.parser')
                body = soup.get_text()
            elif msg.text:
                body = msg.text
            elif msg.html and not BeautifulSoup_available:
                # Fallback: try to extract text from HTML without BeautifulSoup
                import re
                body = re.sub(r'<[^>]+>', '', msg.html)
                body = re.sub(r'\s+', ' ', body).strip()
            
            email_data = {
                'id': msg.uid,
                'date': msg.date,
                'sender': msg.from_,
                'subject': msg.subject,
                'body': body,
                'provider': 'Gmail'
            }
            emails.append(email_data)
        
        return emails
    except Exception as e:
        st.error(f"Error fetching Gmail emails: {str(e)}")
        return []

def classify_email_keywords(text: str) -> str:
    """
    Classify email using keyword matching.
    
    Args:
        text: Email body text
    
    Returns:
        Classification category
    """
    text_lower = text.lower()
    
    # Keywords for each category
    rejected_keywords = [
        'reject', 'rejected', 'unfortunately', 'not selected', 'not chosen',
        'other candidates', 'better qualified', 'position filled', 'no longer',
        'thank you for your interest', 'we regret', 'not moving forward'
    ]
    
    interview_keywords = [
        'interview', 'schedule', 'meeting', 'call', 'discuss', 'next steps',
        'availability', 'calendar', 'zoom', 'teams', 'phone call', 'video call',
        'technical interview', 'behavioral interview', 'onsite', 'remote'
    ]
    
    offer_keywords = [
        'offer', 'congratulations', 'welcome', 'accepted', 'salary', 'compensation',
        'benefits', 'start date', 'employment', 'contract', 'terms', 'package',
        'we are pleased', 'excited to offer', 'joining our team'
    ]
    
    # Check for keywords
    for keyword in rejected_keywords:
        if keyword in text_lower:
            return 'Rejected'
    
    for keyword in interview_keywords:
        if keyword in text_lower:
            return 'Interview'
    
    for keyword in offer_keywords:
        if keyword in text_lower:
            return 'Offer'
    
    return 'Other'

def classify_email_ai(text: str, mode: str = 'openai') -> str:
    """
    Classify email using AI (OpenAI or Hugging Face).
    
    Args:
        text: Email body text
        mode: 'openai' or 'huggingface'
    
    Returns:
        Classification category
    """
    if mode == 'openai':
        return classify_email_openai(text)
    elif mode == 'huggingface':
        return classify_email_huggingface(text)
    else:
        return classify_email_keywords(text)

def classify_email_openai(text: str) -> str:
    """
    Classify email using OpenAI API.
    
    Args:
        text: Email body text
    
    Returns:
        Classification category
    """
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""You are an assistant classifying job application responses. Categories: Rejected, Interview, Offer, Other.
Email text: {text[:1000]}  # Limit text length
Return only the category name."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        
        # Validate result
        if result in EMAIL_CATEGORIES:
            return result
        else:
            return 'Other'
            
    except Exception as e:
        st.warning(f"OpenAI classification failed: {str(e)}. Falling back to keyword classification.")
        return classify_email_keywords(text)

def classify_email_huggingface(text: str) -> str:
    """
    Classify email using Hugging Face transformers.
    
    Args:
        text: Email body text
    
    Returns:
        Classification category
    """
    try:
        # Load model (cached after first load)
        if 'hf_classifier' not in st.session_state:
            model_name = os.getenv('HUGGINGFACE_MODEL', 'facebook/bart-large-mnli')
            st.session_state.hf_classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
        
        classifier = st.session_state.hf_classifier
        
        # Define candidate labels
        candidate_labels = EMAIL_CATEGORIES
        
        # Classify
        result = classifier(text[:512], candidate_labels)  # Limit text length
        
        return result['labels'][0]
        
    except Exception as e:
        st.warning(f"Hugging Face classification failed: {str(e)}. Falling back to keyword classification.")
        return classify_email_keywords(text)

def load_email_history() -> pd.DataFrame:
    """
    Load email history from CSV file.
    
    Returns:
        DataFrame with email history
    """
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Ensure date column is properly formatted
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                # Remove rows with invalid dates
                df = df.dropna(subset=['date'])
            return df
        except Exception as e:
            st.error(f"Error loading email history: {e}")
            return pd.DataFrame(columns=['id', 'date', 'sender', 'subject', 'status', 'provider'])
    else:
        return pd.DataFrame(columns=['id', 'date', 'sender', 'subject', 'status', 'provider'])

def save_email_history(df: pd.DataFrame):
    """
    Save email history to CSV file.
    
    Args:
        df: DataFrame with email history
    """
    df.to_csv(DATA_FILE, index=False)

def update_last_fetch():
    """Update the last fetch timestamp."""
    with open(LAST_FETCH_FILE, 'w') as f:
        f.write(str(datetime.now().timestamp()))

def should_refresh_automatically() -> bool:
    """
    Check if automatic refresh is needed based on last fetch time.
    
    Returns:
        True if refresh is needed, False otherwise
    """
    if not os.path.exists(LAST_FETCH_FILE):
        return True
    
    try:
        with open(LAST_FETCH_FILE, 'r') as f:
            last_fetch = float(f.read().strip())
        
        hours_since_fetch = (datetime.now().timestamp() - last_fetch) / 3600
        refresh_interval = float(os.getenv('REFRESH_INTERVAL_HOURS', 24))
        
        return hours_since_fetch >= refresh_interval
    except:
        return True

def create_dashboard(df: pd.DataFrame):
    """
    Create dashboard visualizations.
    
    Args:
        df: DataFrame with email data
    """
    if df.empty:
        st.info("No email data available. Please fetch emails first.")
        return
    
    # Convert date column to datetime with error handling
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # Remove rows where date conversion failed
        df = df.dropna(subset=['date'])
    except Exception as e:
        st.error(f"Error converting dates: {e}")
        return
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Status Distribution")
        
        # Pie chart
        status_counts = df['status'].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Email Status Distribution"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📈 Status Over Time")
        
        # Bar chart by date
        try:
            df_daily = df.groupby([df['date'].dt.date, 'status']).size().reset_index(name='count')
            df_daily['date'] = pd.to_datetime(df_daily['date'])
        except Exception as e:
            st.error(f"Error creating time series chart: {e}")
            return
        
        fig_bar = px.bar(
            df_daily,
            x='date',
            y='count',
            color='status',
            title="Email Status Over Time"
        )
        fig_bar.update_xaxes(title="Date")
        fig_bar.update_yaxes(title="Count")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Summary statistics
    st.subheader("📋 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", len(df))
    
    with col2:
        st.metric("Rejected", len(df[df['status'] == 'Rejected']))
    
    with col3:
        st.metric("Interviews", len(df[df['status'] == 'Interview']))
    
    with col4:
        st.metric("Offers", len(df[df['status'] == 'Offer']))
    
    # Interactive table
    st.subheader("📧 Email Details")
    
    # Add search and filter options
    search_term = st.text_input("Search emails (sender, subject, or body):")
    
    if search_term:
        mask = (
            df['sender'].str.contains(search_term, case=False, na=False) |
            df['subject'].str.contains(search_term, case=False, na=False) |
            df['body'].str.contains(search_term, case=False, na=False)
        )
        df_filtered = df[mask]
    else:
        df_filtered = df
    
    # Status filter
    status_filter = st.multiselect(
        "Filter by status:",
        options=EMAIL_CATEGORIES,
        default=EMAIL_CATEGORIES
    )
    
    if status_filter:
        df_filtered = df_filtered[df_filtered['status'].isin(status_filter)]
    
    # Display table
    if not df_filtered.empty:
        # Prepare data for display (truncate long text)
        display_df = df_filtered.copy()
        display_df['subject'] = display_df['subject'].str[:50] + '...'
        display_df['sender'] = display_df['sender'].str[:30] + '...'
        try:
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d %H:%M')
        except Exception as e:
            display_df['date'] = display_df['date'].astype(str)
        
        # Reorder columns
        display_df = display_df[['date', 'sender', 'subject', 'status', 'provider']]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No emails match the current filters.")

def main():
    """Main application function."""
    
    # Header
    st.title("📧 Job Application Analytics Dashboard")
    st.markdown("Connect to your email and analyze job application responses with AI-powered classification.")
    
    # Check dependencies
    check_dependencies()
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # AI classification mode - only show available options
    available_modes = ["Keywords"]
    
    if openai_available:
        available_modes.append("OpenAI")
    
    if transformers_available:
        available_modes.append("Hugging Face")
    
    ai_mode = st.sidebar.selectbox(
        "AI Classification Mode:",
        available_modes
    )
    
    # Show info about missing AI modes
    if len(available_modes) == 1:
        st.sidebar.info("💡 Install additional packages for more AI options:")
        if not openai_available:
            st.sidebar.text("• pip install openai (for OpenAI)")
        if not transformers_available:
            st.sidebar.text("• pip install transformers torch (for Hugging Face)")
    
    # Refresh interval
    refresh_interval = st.sidebar.number_input(
        "Auto-refresh interval (hours):",
        min_value=1,
        max_value=168,
        value=int(os.getenv('REFRESH_INTERVAL_HOURS', 24))
    )
    
    # Connection section
    st.sidebar.header("🔗 Email Connection")
    
    gmail_email = st.sidebar.text_input("Gmail Address:", value=os.getenv('GMAIL_EMAIL', ''))
    gmail_password = st.sidebar.text_input("App Password:", type="password", value=os.getenv('GMAIL_APP_PASSWORD', ''))
    
    if st.sidebar.button("Connect to Gmail"):
        if gmail_email and gmail_password:
            with st.spinner("Connecting to Gmail..."):
                mailbox = connect_gmail(gmail_email, gmail_password)
                if mailbox:
                    st.session_state.gmail_mailbox = mailbox
                    st.success("Connected to Gmail!")
        else:
            st.error("Please enter Gmail credentials.")
    
    # Fetch emails section
    st.sidebar.header("📥 Fetch Emails")
    
    if st.sidebar.button("Refresh Now"):
        fetch_emails(ai_mode)
    
    # Check for automatic refresh
    if should_refresh_automatically():
        st.info("🔄 Automatic refresh triggered. Fetching latest emails...")
        fetch_emails(ai_mode)
    
    # Load and display data
    df = load_email_history()
    
    if not df.empty:
        create_dashboard(df)
    else:
        st.info("No email data available. Please connect to your email provider and fetch emails.")

def fetch_emails(ai_mode: str):
    """
    Fetch and classify emails from Gmail.
    
    Args:
        ai_mode: AI classification mode
    """
    emails = []
    
    try:
        if hasattr(st.session_state, 'gmail_mailbox'):
            with st.spinner("Fetching emails from Gmail..."):
                emails = fetch_emails_gmail(st.session_state.gmail_mailbox)
        
        if emails:
            # Load existing data
            df_existing = load_email_history()
            
            # Classify new emails
            new_emails = []
            for email in emails:
                # Check if email already exists
                if not df_existing.empty and email['id'] in df_existing['id'].values:
                    continue
                
                # Classify email
                if ai_mode == "OpenAI":
                    status = classify_email_ai(email['body'], 'openai')
                elif ai_mode == "Hugging Face":
                    status = classify_email_ai(email['body'], 'huggingface')
                else:
                    status = classify_email_keywords(email['body'])
                
                new_email = {
                    'id': email['id'],
                    'date': email['date'],
                    'sender': email['sender'],
                    'subject': email['subject'],
                    'status': status,
                    'provider': email['provider']
                }
                new_emails.append(new_email)
            
            if new_emails:
                # Add new emails to existing data
                df_new = pd.DataFrame(new_emails)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                
                # Save updated data
                save_email_history(df_combined)
                update_last_fetch()
                
                st.success(f"✅ Fetched and classified {len(new_emails)} new emails!")
                st.rerun()
            else:
                st.info("No new emails found.")
        else:
            st.warning("No emails fetched. Please check your connection.")
    
    except Exception as e:
        st.error(f"Error fetching emails: {str(e)}")

if __name__ == "__main__":
    main()
