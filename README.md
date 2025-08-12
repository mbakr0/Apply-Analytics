# 📧 Job Application Analytics Dashboard

A comprehensive Streamlit dashboard that connects to your email inbox and uses AI to classify job application responses. Supports Gmail (IMAP) and Outlook (Microsoft Graph API) with multiple AI classification modes.

## 🚀 Features

### Email Connection
- **Gmail**: IMAP connection using email + app password
- **Outlook**: Microsoft Graph API using OAuth 2.0
- Modular architecture for easy addition of other providers

### AI-Powered Classification
- **OpenAI GPT-4o-mini**: Cloud-based classification with high accuracy
- **Hugging Face Transformers**: Local/offline inference using pre-trained models
- **Keyword Matching**: Fallback classification using predefined keywords
- Categories: Rejected, Interview, Offer, Other

### Dashboard Analytics
- 📊 **Pie Chart**: Status distribution percentages
- 📈 **Bar Chart**: Email counts over time
- 📋 **Summary Statistics**: Key metrics at a glance
- 🔍 **Interactive Table**: Search and filter capabilities

### Automation
- ⏰ **Automatic Refresh**: Configurable refresh intervals
- 🔄 **Manual Refresh**: On-demand email fetching
- 📝 **Data Persistence**: CSV storage with duplicate prevention

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Apply-Analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Copy the environment example file and configure your settings:
```bash
cp env_example.txt .env
```

Edit `.env` with your credentials:
```env
# Email Configuration
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Outlook Configuration
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret
OUTLOOK_REDIRECT_URI=http://localhost:8501

# AI Configuration
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_MODEL=facebook/bart-large-mnli

# App Configuration
REFRESH_INTERVAL_HOURS=24
```

## 🔧 Configuration

### Gmail Setup
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password (not your regular password)

### Outlook Setup
1. Register an application in Azure AD:
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Create new registration
   - Set redirect URI to `http://localhost:8501`
   - Note the Client ID and Client Secret
2. Grant Mail.Read permission to your app

### OpenAI Setup
1. Create an account at [OpenAI](https://openai.com)
2. Generate an API key
3. Add to `.env` file

### Hugging Face Setup
- No API key required for basic models
- Models are downloaded automatically on first use
- GPU acceleration available if CUDA is installed

## 🚀 Usage

### Start the Application
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### Step-by-Step Guide

1. **Select Email Provider**
   - Choose between Gmail or Outlook in the sidebar

2. **Configure AI Mode**
   - **Keywords**: Fast, no API required
   - **OpenAI**: High accuracy, requires API key
   - **Hugging Face**: Good accuracy, works offline

3. **Connect to Email**
   - **Gmail**: Enter email and app password
   - **Outlook**: Click "Connect to Outlook" and follow OAuth flow

4. **Fetch Emails**
   - Click "Refresh Now" to fetch latest emails
   - Automatic refresh occurs based on configured interval

5. **View Analytics**
   - Dashboard shows visualizations and statistics
   - Use search and filters to explore data
   - Export data via the interactive table

## 📊 Data Structure

The application stores email data in `email_history.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `id` | Unique email identifier |
| `date` | Email received date/time |
| `sender` | Email sender address |
| `subject` | Email subject line |
| `status` | AI classification (Rejected/Interview/Offer/Other) |
| `provider` | Email provider (Gmail/Outlook) |

## 🔍 AI Classification Details

### Keyword Classification
- **Rejected**: "reject", "unfortunately", "not selected", etc.
- **Interview**: "interview", "schedule", "meeting", "call", etc.
- **Offer**: "offer", "congratulations", "salary", "welcome", etc.
- **Other**: Default category for unclassified emails

### OpenAI Classification
- Uses GPT-4o-mini model
- Prompt: "You are an assistant classifying job application responses..."
- Returns one of four categories
- Falls back to keyword classification if API fails

### Hugging Face Classification
- Uses zero-shot classification pipeline
- Default model: `facebook/bart-large-mnli`
- Configurable via environment variable
- Works offline after initial model download

## 🔒 Security Features

- **Gmail**: App passwords only (no regular passwords)
- **Outlook**: OAuth 2.0 with refresh token management
- **Environment Variables**: All secrets stored in `.env`
- **Session State**: Tokens cached in Streamlit session
- **Data Local**: All data stored locally, no cloud storage

## 🛠️ Troubleshooting

### Common Issues

1. **Gmail Connection Failed**
   - Ensure 2FA is enabled
   - Use app password, not regular password
   - Check if "Less secure app access" is disabled

2. **Outlook Authentication Issues**
   - Verify redirect URI matches Azure app registration
   - Check client ID and secret are correct
   - Ensure Mail.Read permission is granted

3. **AI Classification Not Working**
   - Check API keys in `.env` file
   - Verify internet connection for OpenAI
   - Ensure sufficient disk space for Hugging Face models

4. **No Emails Found**
   - Check email provider connection
   - Verify inbox has emails
   - Check date range (fetches last 200 emails)

### Performance Tips

- Use keyword classification for faster processing
- Limit email fetch to smaller batches if needed
- Use GPU for Hugging Face models if available
- Adjust refresh interval based on email volume

## 📈 Future Enhancements

- [ ] Support for additional email providers (Yahoo, ProtonMail)
- [ ] Advanced filtering and search capabilities
- [ ] Email sentiment analysis
- [ ] Response time tracking
- [ ] Integration with job application tracking systems
- [ ] Export to various formats (Excel, PDF)
- [ ] Email templates and response suggestions
- [ ] Multi-user support with authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub
4. Contact the maintainers

---

**Note**: This application processes email data locally. Ensure compliance with your organization's data handling policies and email service terms of use.
