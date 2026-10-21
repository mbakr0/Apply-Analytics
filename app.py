import html
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from imap_tools import AND, MailBox

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import openai
except ImportError:
    openai = None

load_dotenv()

st.set_page_config(
    page_title="Apply Analytics",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CATEGORIES = ["Rejected", "Interview", "Offer", "Other"]
DB_FILE = Path(os.getenv("DATA_FILE", "applications.db"))
LEGACY_CSV = Path("email_history.csv")

# A small, explainable classifier is kept as the zero-config default. The score
# based approach is more reliable than returning the first matching keyword.
KEYWORDS = {
    "Rejected": {
        "unfortunately": 4,
        "not selected": 5,
        "not chosen": 5,
        "other candidates": 4,
        "better qualified": 4,
        "position has been filled": 5,
        "position filled": 5,
        "not moving forward": 5,
        "we regret": 4,
        "rejection": 4,
        "reject": 3,
    },
    "Interview": {
        "interview": 5,
        "schedule an interview": 6,
        "next steps": 4,
        "technical interview": 6,
        "behavioral interview": 6,
        "phone screen": 5,
        "screening call": 5,
        "availability": 2,
        "calendar invite": 4,
        "meet with": 3,
    },
    "Offer": {
        "job offer": 7,
        "offer letter": 7,
        "pleased to offer": 7,
        "excited to offer": 7,
        "congratulations": 4,
        "salary": 3,
        "compensation": 3,
        "benefits": 3,
        "start date": 4,
        "joining our team": 5,
        "employment agreement": 5,
    },
}


def normalize_text(value: object) -> str:
    """Return clean, searchable text without failing on null values."""
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def init_db() -> None:
    """Create the local database and migrate the old CSV format once."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'Gmail',
                date TEXT,
                sender TEXT,
                subject TEXT,
                status TEXT NOT NULL DEFAULT 'Other',
                confidence REAL NOT NULL DEFAULT 0,
                snippet TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                PRIMARY KEY (id, provider)
            )
            """
        )
        conn.commit()

    if LEGACY_CSV.exists():
        try:
            old = pd.read_csv(LEGACY_CSV)
            if not old.empty:
                migrate = pd.DataFrame({
                    "id": old.get("id", pd.Series(dtype=str)).astype(str),
                    "provider": old.get("provider", pd.Series("Gmail", index=old.index)).fillna("Gmail").astype(str),
                    "date": old.get("date", pd.Series(index=old.index)).astype(str),
                    "sender": old.get("sender", pd.Series(index=old.index)).fillna("").astype(str),
                    "subject": old.get("subject", pd.Series(index=old.index)).fillna("").astype(str),
                    "status": old.get("status", pd.Series("Other", index=old.index)).fillna("Other").astype(str),
                    "confidence": 0.0,
                    "snippet": old.get("body", old.get("subject", pd.Series("", index=old.index))).fillna("").astype(str).str[:500],
                })
                save_applications(migrate)
                LEGACY_CSV.rename(LEGACY_CSV.with_suffix(".csv.migrated"))
        except Exception as exc:
            st.warning(f"Legacy CSV migration was skipped: {exc}")


def load_applications() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query("SELECT * FROM applications ORDER BY date DESC", conn)
    if df.empty:
        return pd.DataFrame(columns=["id", "provider", "date", "sender", "subject", "status", "confidence", "snippet", "created_at"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["status"] = df["status"].where(df["status"].isin(CATEGORIES), "Other")
    return df


def save_applications(df: pd.DataFrame) -> None:
    """Upsert application records while preserving the local history."""
    if df.empty:
        return
    init_db()
    columns = ["id", "provider", "date", "sender", "subject", "status", "confidence", "snippet"]
    work = df.copy()
    for column in columns:
        if column not in work:
            work[column] = "" if column not in {"confidence"} else 0.0
    work["created_at"] = datetime.now(timezone.utc).isoformat()
    work["id"] = work["id"].astype(str)
    work["provider"] = work["provider"].fillna("Gmail").astype(str)
    work["status"] = work["status"].where(work["status"].isin(CATEGORIES), "Other")
    work["confidence"] = pd.to_numeric(work["confidence"], errors="coerce").fillna(0.0)
    work["snippet"] = work["snippet"].fillna("").astype(str).str[:500]

    with sqlite3.connect(DB_FILE) as conn:
        for _, row in work.iterrows():
            conn.execute(
                """
                INSERT INTO applications
                (id, provider, date, sender, subject, status, confidence, snippet, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id, provider) DO UPDATE SET
                    date=excluded.date,
                    sender=excluded.sender,
                    subject=excluded.subject,
                    status=excluded.status,
                    confidence=excluded.confidence,
                    snippet=excluded.snippet
                """,
                (
                    row["id"], row["provider"], str(row["date"]), normalize_text(row["sender"]),
                    normalize_text(row["subject"]), row["status"], float(row["confidence"]),
                    normalize_text(row["snippet"]), row["created_at"],
                ),
            )
        conn.commit()


def clear_database() -> None:
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM applications")
        conn.commit()


def classify_keywords(text: str) -> Tuple[str, float]:
    """Classify using weighted, explainable keywords and return confidence."""
    text = normalize_text(text).lower()
    if not text:
        return "Other", 0.0

    scores = {category: 0 for category in CATEGORIES}
    for category, terms in KEYWORDS.items():
        for term, weight in terms.items():
            if term in text:
                scores[category] += weight

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    winner, score = ranked[0]
    if score == 0:
        return "Other", 0.25

    second = ranked[1][1]
    confidence = min(0.99, 0.55 + (score - second) / max(score * 2, 1))
    return winner, round(confidence, 2)


def classify_openai(text: str) -> Tuple[str, float]:
    """Use OpenAI when configured; fall back cleanly to local classification."""
    if openai is None or not os.getenv("OPENAI_API_KEY"):
        return classify_keywords(text)
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify job application emails. Return exactly one label: "
                        "Rejected, Interview, Offer, or Other. "
                        "Choose Offer over Interview when the message is a job offer."
                    ),
                },
                {"role": "user", "content": normalize_text(text)[:6000]},
            ],
            temperature=0,
            max_tokens=8,
        )
        label = normalize_text(response.choices[0].message.content)
        for category in CATEGORIES:
            if label.lower() == category.lower():
                return category, 0.95
    except Exception as exc:
        st.warning(f"OpenAI classification failed; using local classification instead. ({exc})")
    return classify_keywords(text)


def classify_email(text: str, mode: str) -> Tuple[str, float]:
    if mode == "OpenAI":
        return classify_openai(text)
    return classify_keywords(text)


def clean_email_body(msg) -> str:
    raw = msg.text or msg.html or ""
    if msg.html and BeautifulSoup is not None:
        raw = BeautifulSoup(msg.html, "html.parser").get_text(" ")
    elif msg.html:
        raw = re.sub(r"<[^>]+>", " ", msg.html)
    return normalize_text(raw)


def connect_gmail(email: str, password: str) -> MailBox:
    if not email or not password:
        raise ValueError("Enter a Gmail address and an App Password.")
    mailbox = MailBox("imap.gmail.com")
    mailbox.login(email, password)
    return mailbox


def fetch_gmail(mailbox: MailBox, limit: int = 200) -> List[Dict]:
    emails: List[Dict] = []
    for msg in mailbox.fetch(AND(all=True), limit=limit, reverse=True):
        body = clean_email_body(msg)
        emails.append({
            "id": str(msg.uid),
            "provider": "Gmail",
            "date": msg.date,
            "sender": normalize_text(msg.from_),
            "subject": normalize_text(msg.subject),
            "body": body,
        })
    return emails


def demo_data() -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    samples = [
        ("demo-1", 1, "recruiting@company.com", "Interview invitation — Software Engineer", "We would like to schedule an interview and discuss next steps."),
        ("demo-2", 2, "talent@startup.com", "Application update", "Unfortunately, we will not be moving forward with your application."),
        ("demo-3", 4, "hr@product.io", "Congratulations — Job Offer", "We are pleased to offer you the Software Engineer position. Salary and start date are attached."),
        ("demo-4", 6, "jobs@company.com", "Application received", "Thank you for applying. We have received your application."),
        ("demo-5", 8, "recruiting@company.com", "Technical interview next steps", "Please share your availability for a technical interview next week."),
    ]
    rows = []
    for ident, days, sender, subject, body in samples:
        status, confidence = classify_keywords(f"{subject} {body}")
        rows.append({"id": ident, "provider": "Demo", "date": now - timedelta(days=days), "sender": sender, "subject": subject, "status": status, "confidence": confidence, "snippet": body})
    return pd.DataFrame(rows)


def filtered_data(df: pd.DataFrame, search: str, statuses: List[str], start_date, end_date) -> pd.DataFrame:
    work = df.copy()
    if work.empty:
        return work
    work["date"] = pd.to_datetime(work["date"], errors="coerce", utc=True)
    work = work.dropna(subset=["date"])
    if search:
        q = re.escape(search.strip())
        mask = (
            work["sender"].fillna("").str.contains(q, case=False, regex=True) |
            work["subject"].fillna("").str.contains(q, case=False, regex=True) |
            work["snippet"].fillna("").str.contains(q, case=False, regex=True)
        )
        work = work[mask]
    if statuses:
        work = work[work["status"].isin(statuses)]
    start = pd.Timestamp(start_date, tz="UTC")
    end = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
    return work[(work["date"] >= start) & (work["date"] < end)]


def render_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1450px; padding-top: 2rem; padding-bottom: 3rem;}
        [data-testid="stMetric"] {background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); padding: 1rem; border-radius: 16px;}
        .hero {padding: 1.4rem 1.6rem; border: 1px solid rgba(100,180,255,.18); border-radius: 22px; background: linear-gradient(135deg, rgba(30,70,110,.35), rgba(20,25,40,.7)); margin-bottom: 1.5rem;}
        .hero h1 {margin: 0; font-size: 2.2rem;}
        .muted {color: #94a3b8; margin-top: .4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(df: pd.DataFrame) -> None:
    total = len(df)
    interviews = int((df["status"] == "Interview").sum())
    offers = int((df["status"] == "Offer").sum())
    rejected = int((df["status"] == "Rejected").sum())
    response_rate = ((interviews + offers) / total * 100) if total else 0
    cols = st.columns(5)
    cols[0].metric("Applications", total)
    cols[1].metric("Interviews", interviews)
    cols[2].metric("Offers", offers)
    cols[3].metric("Rejected", rejected)
    cols[4].metric("Positive response", f"{response_rate:.1f}%")


def render_overview(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No applications match the current filters.")
        return
    render_kpis(df)
    st.divider()

    left, right = st.columns(2)
    with left:
        counts = df["status"].value_counts().reindex(CATEGORIES, fill_value=0).reset_index()
        counts.columns = ["status", "count"]
        fig = px.pie(counts, values="count", names="status", hole=.58, title="Application outcomes")
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        daily = df.assign(day=df["date"].dt.date).groupby(["day", "status"]).size().reset_index(name="count")
        fig = px.bar(daily, x="day", y="count", color="status", title="Activity over time")
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent activity")
    recent = df.sort_values("date", ascending=False).head(8).copy()
    recent["date"] = recent["date"].dt.strftime("%b %d, %Y %H:%M")
    recent["confidence"] = (recent["confidence"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(
        recent[["date", "sender", "subject", "status", "confidence"]],
        use_container_width=True,
        hide_index=True,
        column_config={"subject": st.column_config.TextColumn("Subject", width="large")},
    )


def render_applications(df: pd.DataFrame) -> None:
    st.subheader("Applications")
    st.caption("Edit a status below to correct classification. Changes are saved locally.")
    if df.empty:
        st.info("Nothing to show.")
        return

    editable = df.sort_values("date", ascending=False).copy()
    editable["date"] = editable["date"].dt.strftime("%Y-%m-%d %H:%M")
    editable["confidence"] = (editable["confidence"] * 100).round(0).astype(int)
    editable = editable[["id", "date", "sender", "subject", "status", "confidence", "provider"]]
    edited = st.data_editor(
        editable,
        use_container_width=True,
        hide_index=True,
        disabled=["id", "date", "sender", "subject", "confidence", "provider"],
        column_config={
            "id": None,
            "status": st.column_config.SelectboxColumn("Status", options=CATEGORIES, required=True),
            "confidence": st.column_config.NumberColumn("Confidence", format="%d%%"),
            "subject": st.column_config.TextColumn("Subject", width="large"),
        },
        key="application_editor",
    )
    if st.button("💾 Save status changes", type="primary"):
        changed = edited[edited["status"].values != editable["status"].values]
        if changed.empty:
            st.info("No status changes detected.")
        else:
            updates = changed[["id", "status"]]
            with sqlite3.connect(DB_FILE) as conn:
                for _, row in updates.iterrows():
                    conn.execute("UPDATE applications SET status=? WHERE id=?", (row["status"], row["id"]))
                conn.commit()
            st.success(f"Saved {len(changed)} status change(s).")
            st.rerun()

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export filtered data as CSV", csv, "apply-analytics.csv", "text/csv")


def render_insights(df: pd.DataFrame) -> None:
    st.subheader("Insights")
    if df.empty:
        st.info("Fetch some applications to generate insights.")
        return
    positives = df[df["status"].isin(["Interview", "Offer"])]
    response_rate = len(positives) / len(df) * 100
    st.markdown(f"**Positive response rate:** {response_rate:.1f}% ({len(positives)} of {len(df)})")

    sender_stats = df.groupby("sender", dropna=False).agg(
        Applications=("id", "count"),
        Positive=("status", lambda s: s.isin(["Interview", "Offer"]).sum()),
    ).reset_index()
    sender_stats["Response rate"] = (sender_stats["Positive"] / sender_stats["Applications"] * 100).round(1)
    st.dataframe(sender_stats.sort_values("Applications", ascending=False).head(20), use_container_width=True, hide_index=True)

    st.info("Tip: use the Applications tab to correct classifications. The corrected status is stored in the local SQLite database and is preserved across restarts.")


def render_sidebar() -> Tuple[str, int]:
    st.sidebar.title("Apply Analytics")
    st.sidebar.caption("Job application intelligence, locally stored.")
    st.sidebar.divider()

    mode = st.sidebar.selectbox("Classification", ["Keywords"] + (["OpenAI"] if openai and os.getenv("OPENAI_API_KEY") else []))
    limit = st.sidebar.slider("Emails per sync", 25, 500, 200, 25)

    st.sidebar.subheader("Gmail")
    email = st.sidebar.text_input("Gmail address", value=os.getenv("GMAIL_EMAIL", ""))
    password = st.sidebar.text_input("App Password", type="password", value=os.getenv("GMAIL_APP_PASSWORD", ""))

    if "gmail_mailbox" not in st.session_state:
        st.session_state.gmail_mailbox = None

    if st.sidebar.button("Connect to Gmail", use_container_width=True):
        try:
            with st.spinner("Connecting to Gmail..."):
                st.session_state.gmail_mailbox = connect_gmail(email, password)
            st.sidebar.success("Connected")
        except Exception as exc:
            st.session_state.gmail_mailbox = None
            st.sidebar.error(f"Connection failed: {exc}")

    if st.session_state.gmail_mailbox is not None:
        if st.sidebar.button("↻ Sync inbox", type="primary", use_container_width=True):
            sync_inbox(mode, limit)

    st.sidebar.divider()
    st.sidebar.subheader("Demo & data")
    if st.sidebar.button("Load demo data", use_container_width=True):
        save_applications(demo_data())
        st.rerun()
    if st.sidebar.button("Clear local data", use_container_width=True):
        clear_database()
        st.session_state.gmail_mailbox = None
        st.rerun()
    return mode, limit


def sync_inbox(mode: str, limit: int) -> None:
    mailbox = st.session_state.get("gmail_mailbox")
    if mailbox is None:
        st.error("Connect to Gmail first.")
        return
    try:
        with st.spinner("Syncing and classifying emails..."):
            emails = fetch_gmail(mailbox, limit)
            rows = []
            for email in emails:
                label, confidence = classify_email(
                    f"{email['subject']}\n{email['body']}", mode
                )
                rows.append({
                    "id": email["id"],
                    "provider": email["provider"],
                    "date": email["date"],
                    "sender": email["sender"],
                    "subject": email["subject"],
                    "status": label,
                    "confidence": confidence,
                    "snippet": email["body"][:500],
                })
            save_applications(pd.DataFrame(rows))
        st.success(f"Synced {len(rows)} email(s). Existing messages were safely upserted.")
        st.rerun()
    except Exception as exc:
        st.error(f"Sync failed: {exc}")


def main() -> None:
    render_styles()
    init_db()
    mode, _ = render_sidebar()

    st.markdown(
        '<div class="hero"><h1>📬 Apply Analytics</h1><div class="muted">Track job application responses, spot patterns, and keep your search organized.</div></div>',
        unsafe_allow_html=True,
    )

    df = load_applications()
    if df.empty:
        st.info("Your dashboard is ready. Connect Gmail to sync real emails, or load demo data to explore the interface.")

    with st.expander("🔎 Filters", expanded=not df.empty):
        c1, c2, c3 = st.columns([2, 1, 1])
        search = c1.text_input("Search sender, subject, or email snippet", placeholder="e.g. interview, company.com")
        statuses = c2.multiselect("Status", CATEGORIES, default=CATEGORIES)
        if not df.empty:
            min_date = df["date"].min().date()
            max_date = df["date"].max().date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()
        date_range = c3.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    view = st.tabs(["📊 Overview", "📋 Applications", "💡 Insights"])
    filtered = filtered_data(df, search, statuses, start_date, end_date)
    with view[0]:
        render_overview(filtered)
    with view[1]:
        render_applications(filtered)
    with view[2]:
        render_insights(filtered)

    st.caption(f"Classification mode: {mode} · Storage: SQLite · Records: {len(df)}")


if __name__ == "__main__":
    main()
