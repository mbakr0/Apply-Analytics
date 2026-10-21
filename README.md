# 📬 Apply Analytics

A modern Streamlit dashboard for turning job-search emails into a useful application pipeline. Connect Gmail through IMAP, classify responses locally or with OpenAI, review the results, correct classifications, and export your data.

## What changed

The application was rebuilt around a simpler, more reliable workflow:

- **SQLite storage** replaces the fragile CSV-only history and provides safe upserts.
- **Automatic legacy migration** imports the existing `email_history.csv` the first time the new version runs.
- **Weighted keyword classification** replaces first-match keyword logic and reports a confidence score.
- **OpenAI classification** is optional and automatically falls back to local classification if unavailable or if the API fails.
- **Gmail sync** safely re-processes existing messages without creating duplicates.
- **Modern dashboard** with KPI cards, outcome distribution, activity timeline, filters, and insights.
- **Editable classifications** through the Applications table.
- **CSV export** for the currently filtered dataset.
- **Demo mode** lets you explore the application without connecting an email account.
- **Improved search** covers sender, subject, and a privacy-conscious email snippet.
- Removed the previously advertised but unimplemented Outlook/Hugging Face paths from the main application.

## Features

### 📊 Dashboard
- Total applications
- Interview count
- Offer count
- Rejection count
- Positive response rate
- Outcome distribution
- Application activity over time
- Recent activity table

### 🔎 Search and filtering
Filter the complete history by:

- Sender
- Subject
- Email snippet
- Status
- Date range

### 🧠 Classification
**Keywords** is the default and requires no external AI service. It uses weighted phrases so a message containing both interview and offer language is handled more intelligently.

**OpenAI** is available when `OPENAI_API_KEY` is configured. The model can be selected through `OPENAI_MODEL`, and failures fall back to local classification.

Categories:

- `Rejected`
- `Interview`
- `Offer`
- `Other`

### 📥 Gmail
Gmail is connected with IMAP using an **App Password**. The application does not ask for or store your normal Gmail password.

### ✏️ Manual corrections
The Applications tab contains an editable status column. This is useful when an email is ambiguous or the classifier gets something wrong. Corrections are persisted in SQLite.

### 🧪 Demo mode
Click **Load demo data** in the sidebar to populate the dashboard with realistic sample applications. This is useful for testing the UI before configuring Gmail.

## Installation

```bash
git clone https://github.com/mbakr0/Apply-Analytics.git
cd Apply-Analytics
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

The default local URL is `http://localhost:8501`.

## Configuration

Create a `.env` file. You can start from `env_example.txt`.

```env
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# Optional
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Optional local database path
DATA_FILE=applications.db
```

### Gmail App Password

1. Enable 2-Step Verification on your Google account.
2. Open Google Account security settings.
3. Create an App Password for mail access.
4. Put that generated password in `GMAIL_APP_PASSWORD`.

Do not commit `.env` or real credentials to GitHub.

## Data storage

The current version stores application history in `applications.db` using SQLite. The database contains:

| Field | Purpose |
|---|---|
| `id` | Provider message ID |
| `provider` | Email provider |
| `date` | Received date/time |
| `sender` | Sender address |
| `subject` | Subject line |
| `status` | Classification |
| `confidence` | Classifier confidence estimate |
| `snippet` | Short searchable email excerpt |
| `created_at` | Local record timestamp |

The old `email_history.csv` format is migrated automatically when possible and renamed to `email_history.csv.migrated` after a successful import.

## Security and privacy

- Gmail access uses an App Password rather than your normal account password.
- Credentials are read from environment variables or the Streamlit form and are not written into the application database.
- Email content is not stored in full; only a short snippet is retained for search and classification context.
- All application data is stored locally by default.
- Review your organization's policies before processing work-related or confidential email.

## Project structure

```text
Apply-Analytics/
├── app.py
├── requirements.txt
├── env_example.txt
├── test_app.py
├── quick_start.py
├── debug_app.py
└── start_dashboard.bat
```

## Testing

Run the smoke tests with:

```bash
python test_app.py
```

The tests cover the core classifier and verify that the main dashboard components are present.

## Roadmap

Good next additions for the project include:

- Job/company entities and application grouping
- Follow-up reminders
- Interview scheduling and calendar integration
- Response-time analytics
- More email providers
- Authentication for hosted deployments
- Automated tests against mocked Gmail messages

## License

This project is licensed under the MIT License.
