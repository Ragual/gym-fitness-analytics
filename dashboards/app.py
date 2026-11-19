from pathlib import Path
import json
import os
import sys
import urllib.error
import urllib.request

import pandas as pd
import streamlit as st


# ============================================================
# APPLICATION SETUP
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
ARTIFACTS = ROOT / "artifacts"
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


st.set_page_config(
    page_title="Gym Report",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM (same look, larger and easier-to-read text)
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #080d13;
        --surface: #101923;
        --border: #263746;
        --accent: #b9f36b;
        --text: #edf3f8;
        --muted: #9fb0be;
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background:
            radial-gradient(ellipse at 78% -12%, rgba(52, 91, 105, .30), transparent 36%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] { background: transparent; }

    .main .block-container {
        max-width: 1480px;
        padding: 2rem 2.5rem 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -.6px;
    }

    p, label, li { color: #c0ccd6; font-size: 15px; }

    [data-testid="stSidebar"] {
        background: #0c141d;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
    [data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif; }

    /* Clean chevron for the sidebar open/close button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        width: 2.5rem !important; min-width: 2.5rem !important; height: 2.5rem !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapsedControl"] span {
        font-size: 0 !important; line-height: 0 !important;
        width: 1.5rem !important; height: 1.5rem !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    [data-testid="stSidebarCollapseButton"] span::before {
        content: "‹"; color: #c4d0d9; font-family: Arial, sans-serif; font-size: 27px; line-height: 1;
    }
    [data-testid="stSidebarCollapsedControl"] span::before {
        content: "›"; color: #c4d0d9; font-family: Arial, sans-serif; font-size: 27px; line-height: 1;
    }
    [data-testid="stSidebarCollapseButton"]:hover span::before,
    [data-testid="stSidebarCollapsedControl"]:hover span::before { color: #b9f36b; }

    .brand { padding: 12px 8px 25px; }
    .brand-kicker { color: var(--accent); font-size: 11px; font-weight: 800; letter-spacing: 3px; }
    .brand-name {
        color: #f4f7fa; font-family: 'Manrope', sans-serif;
        font-size: 24px; font-weight: 800; letter-spacing: -1px; margin-top: 5px;
    }
    .brand-subtitle { color: #93a4b2; font-size: 12px; letter-spacing: 1.2px; margin-top: 5px; }
    .sidebar-label {
        color: #93a4b2; font-size: 12px; font-weight: 800; letter-spacing: 1.5px;
        margin: 6px 0 10px 8px; text-transform: uppercase;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none; }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap: 5px; }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {
        background: transparent; border: 1px solid transparent; border-radius: 10px;
        padding: 11px 12px; min-height: 46px;
        transition: background .15s ease, border-color .15s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:hover {
        background: #172431; border-color: #2b3e4d;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
        background: rgba(185, 243, 107, .10); border-color: rgba(185, 243, 107, .32);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label p {
        color: #c0ccd6 !important; font-size: 15px; font-weight: 600;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p {
        color: var(--accent) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label > div:first-child { display: none; }
    [data-testid="stSidebar"] hr { border-color: var(--border); margin: 18px 0; }

    .sidebar-status {
        background: #121e28; border: 1px solid #2a3b49; border-radius: 12px;
        padding: 14px; margin-top: 18px;
    }
    .sidebar-status-label { color: var(--accent); font-size: 11px; font-weight: 800; letter-spacing: 1.4px; }
    .sidebar-status-value { color: #e8eff5; font-size: 14px; font-weight: 700; margin-top: 8px; }
    .sidebar-status-note { color: #93a4b2; font-size: 12px; margin-top: 5px; }

    .hero {
        position: relative; overflow: hidden; padding: 30px 32px; margin-bottom: 24px;
        background:
            radial-gradient(circle at 90% 18%, rgba(185, 243, 107, .10), transparent 30%),
            linear-gradient(115deg, #172834, #101923 76%);
        border: 1px solid #304452; border-radius: 18px;
    }
    .hero-kicker { color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
    .hero-title {
        color: #f3f7fa; font-family: 'Manrope', sans-serif;
        font-size: clamp(28px, 3.2vw, 42px); font-weight: 800; line-height: 1.16;
        letter-spacing: -1.5px; margin-top: 13px; max-width: 850px;
    }
    .hero-subtitle { color: #b8c6d1; font-size: 16px; line-height: 1.7; margin-top: 11px; max-width: 760px; }
    .hero-decoration {
        position: absolute; right: 26px; bottom: -50px; color: rgba(185, 243, 107, .035);
        font-family: 'Manrope', sans-serif; font-size: 155px; font-weight: 800;
        pointer-events: none; user-select: none;
    }

    .section-heading {
        color: #e7eef4; font-family: 'Manrope', sans-serif;
        font-size: 21px; font-weight: 800; letter-spacing: -.3px; margin: 29px 0 7px;
    }
    .section-caption { color: var(--muted); font-size: 14px; line-height: 1.7; margin: 0 0 15px; }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #16232e, #101923);
        border: 1px solid var(--border); border-radius: 13px;
        padding: 17px 18px; min-height: 112px;
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 14px !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] {
        color: var(--accent) !important; font-family: 'Manrope', sans-serif !important;
        font-size: 28px !important; font-weight: 800 !important;
    }

    .info-card {
        background: linear-gradient(145deg, #17242f, #111a23);
        border: 1px solid var(--border); border-radius: 13px; padding: 18px; min-height: 130px;
    }
    .info-card-label { color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; }
    .info-card-value {
        color: #f0f5f8; font-family: 'Manrope', sans-serif;
        font-size: 26px; font-weight: 800; margin-top: 11px; overflow-wrap: anywhere;
    }
    .info-card-note { color: var(--muted); font-size: 13px; line-height: 1.5; margin-top: 5px; }

    .assistant-banner {
        background:
            radial-gradient(circle at 92% 0%, rgba(185, 243, 107, .10), transparent 32%),
            linear-gradient(120deg, #172b35, #111c26);
        border: 1px solid #304653; border-radius: 15px; padding: 20px 22px; margin-bottom: 20px;
    }
    .assistant-banner-title { color: #f2f7fa; font-family: 'Manrope', sans-serif; font-size: 20px; font-weight: 800; }
    .assistant-banner-copy { color: #b8c6d1; font-size: 15px; line-height: 1.7; margin-top: 7px; }
    .question-group-title { color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: 1.4px; margin: 18px 0 8px; }

    [data-testid="stChatMessage"] {
        background: #131f29; border: 1px solid #293b49; border-radius: 13px;
        padding: 13px 15px; margin-bottom: 10px;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #e7eef4 !important; font-size: 15px; line-height: 1.7;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong { color: var(--accent) !important; }

    .stButton > button {
        border: 1px solid #304351; border-radius: 10px; background: #15232e; color: #dce6ed;
        min-height: 46px; font-size: 14px; font-weight: 600;
        transition: background .15s ease, border-color .15s ease;
    }
    .stButton > button:hover { background: #1c2e3b; border-color: #718b9a; color: #ffffff; }

    .stTextInput input, .stChatInput textarea {
        background: #111d27 !important; color: var(--text) !important;
        border: 1px solid #304351 !important; border-radius: 10px !important; font-size: 15px !important;
    }
    .stTextInput input:focus, .stChatInput textarea:focus {
        border-color: var(--accent) !important; box-shadow: 0 0 0 1px rgba(185, 243, 107, .45) !important;
    }

    [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 11px; }
    [data-testid="stAlert"] { border-radius: 11px; }
    [data-testid="stVegaLiteChart"], [data-testid="stPlotlyChart"] {
        background: #111a23; border: 1px solid var(--border); border-radius: 12px; padding: 7px;
    }
    [data-testid="stChatInput"] { border-color: #304351; }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    @media (max-width: 800px) {
        .main .block-container { padding: 1rem 1rem 2rem; }
        .hero { padding: 23px 21px; }
        .hero-decoration { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA ACCESS
# ============================================================

@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_json(filename: str) -> dict:
    path = ARTIFACTS / filename
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            result = json.load(file)
        return result if isinstance(result, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


features = load_csv("member_features.csv")
segments = load_csv("member_segments.csv")
recommendations = load_csv("workout_recommendations.csv")
profiles = load_csv("segment_profiles.csv")

metrics = load_json("model_evaluation.json")
insights = load_json("workout_insights.json")


def ask_gym_assistant(question: str) -> dict:
    payload = json.dumps({"question": question}).encode("utf-8")
    request = urllib.request.Request(
        f"{API_BASE_URL}/assistant/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=100) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not isinstance(result, dict):
        raise ValueError("The API returned an invalid response.")

    return result


# ============================================================
# HELPERS
# ============================================================

# Friendly names shown to the user instead of the raw column names.
COLUMN_LABELS = {
    "member_id": "Member ID",
    "attendance_count": "Total visits",
    "active_days": "Days visited",
    "days_since_last_visit": "Days since last visit",
    "failed_payments": "Failed payments",
    "attendance_recent_ratio": "Recent visits vs usual",
    "goal_completion_rate": "Goal completion rate",
    "workout_sessions": "Workout sessions",
    "churned": "Stopped coming (1 = yes)",
    "segment": "Group",
    "cluster": "Group",
    "segment_id": "Group",
    "recommendation_type": "Suggested plan",
    "recommendation": "Suggested plan",
    "recommended_workout": "Suggested plan",
    "workout_recommendation": "Suggested plan",
}


def pretty_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(
        columns=lambda name: COLUMN_LABELS.get(
            name, str(name).replace("_", " ").capitalize()
        )
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">GYM REPORT</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            <div class="hero-decoration">GYM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, caption: str | None = None) -> None:
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.markdown(
            f'<div class="section-caption">{caption}</div>',
            unsafe_allow_html=True,
        )


def info_card(label: str, value, note: str) -> None:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card-label">{label}</div>
            <div class="info-card-value">{value}</div>
            <div class="info-card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def find_column(df: pd.DataFrame, candidates: list[str]):
    return next((name for name in candidates if name in df.columns), None)


def safe_mean(df: pd.DataFrame, column: str) -> float:
    if df.empty or column not in df.columns:
        return 0.0
    values = pd.to_numeric(df[column], errors="coerce")
    result = values.mean()
    return 0.0 if pd.isna(result) else float(result)


def show_table(df: pd.DataFrame, height: int = 420) -> None:
    if df.empty:
        st.info("There is nothing to show here yet.")
        return

    display_df = pretty_columns(df).copy()

    seen = {}
    unique_columns = []

    for column in display_df.columns:
        name = str(column)
        count = seen.get(name, 0) + 1
        seen[name] = count
        unique_columns.append(name if count == 1 else f"{name} ({count})")

    display_df.columns = unique_columns

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=height,
    )

def sort_by_member_id(df: pd.DataFrame) -> pd.DataFrame:
    """Sort 2 before 10 when IDs are numbers (plain text sorting puts 10 first)."""
    if "member_id" not in df.columns:
        return df
    numeric = pd.to_numeric(df["member_id"], errors="coerce")
    if numeric.notna().all():
        return df.assign(_sort_key=numeric).sort_values("_sort_key").drop(columns="_sort_key")
    return df.sort_values("member_id", key=lambda values: values.astype(str))


def format_number(value) -> str:
    try:
        number = float(value)
        if pd.isna(number):
            return "—"
        return f"{number:,.1f}"
    except (TypeError, ValueError):
        return "—"


def format_percent(value) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(value)


# ============================================================
# NAVIGATION
# ============================================================

PAGES = {
    "Overview": "01  Overview",
    "Members": "02  Find a member",
    "Churn Intelligence": "03  Members who stopped coming",
    "Segments": "04  Member groups",
    "Workout Studio": "05  Workout plans",
    "AI Assistant": "06  Ask a question",
    "AI Performance": "07  How reliable is the prediction?",
}

if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview"

if st.session_state.active_page not in PAGES:
    st.session_state.active_page = "Overview"

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-kicker">GYM REPORT</div>
            <div class="brand-name">GYM INTELLIGENCE<span style="color:#b9f36b">.</span></div>
            <div class="brand-subtitle">MEMBERS · VISITS · WORKOUTS</div>
        </div>
        <div class="sidebar-label">Pages</div>
        """,
        unsafe_allow_html=True,
    )

    st.radio(
        "Choose a page",
        options=list(PAGES.keys()),
        format_func=lambda page_name: PAGES[page_name],
        key="active_page",
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        """
        <div class="sidebar-status">
            <div class="sidebar-status-label">STATUS</div>
            <div class="sidebar-status-value">● Report is ready</div>
            <div class="sidebar-status-note">Gym Intelligence · v1.0.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

page = st.session_state.active_page


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":
    hero(
        "Your gym, at a glance.",
        "See how members are doing, spot who has stopped coming and decide what needs attention.",
    )

    total = len(features)

    churn_values = (
        pd.to_numeric(features["churned"], errors="coerce").fillna(0)
        if not features.empty and "churned" in features.columns
        else pd.Series(dtype=float)
    )

    no_visit_count = int(churn_values.sum())
    no_visit_rate = no_visit_count / total * 100 if total else 0
    average_visits = safe_mean(features, "attendance_count")

    columns = st.columns(4)

    with columns[0]:
        st.metric("Members in this report", f"{total:,}")
    with columns[1]:
        st.metric("Members who did not come back", f"{no_visit_count:,}")
    with columns[2]:
        st.metric("Share who did not come back", f"{no_visit_rate:.1f}%")
    with columns[3]:
        st.metric("Average visits per member", format_number(average_visits))

    st.caption(
        f"This report covers {total:,} members. Only members who were signed up for the "
        "whole 30 days after the report date are counted, so other members in the "
        "gym's records are left out."
    )

    section(
        "How is your gym doing?",
        "A simple look at how often members visit.",
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### How often do members visit?")
        if not features.empty and "attendance_count" in features.columns:
            visit_data = (
                pd.to_numeric(features["attendance_count"], errors="coerce")
                .dropna()
                .value_counts()
                .sort_index()
            )
            visit_data.index.name = "Number of visits"
            visit_data.name = "Number of members"
            st.bar_chart(visit_data, color="#b9f36b")
            st.caption("Each bar shows how many members made that number of visits.")
        else:
            st.info("Visit information is not available yet.")

    with right:
        st.markdown("#### Did members come back in the next 30 days?")
        if not churn_values.empty:
            outcomes = churn_values.astype(int).value_counts().reindex(
                [0, 1], fill_value=0
            )
            outcomes.index = ["Came back", "Did not come back"]
            outcomes.name = "Number of members"
            st.bar_chart(outcomes, color="#83bfff")
        else:
            st.info("This information is not available yet.")

    section("What needs your attention?", "A simple next step based on this report.")

    if no_visit_count > 0:
        st.warning(
            f"{no_visit_count:,} members did not visit at all in the next 30 days. "
            "Consider calling or messaging them to check in and invite them back."
        )
    else:
        st.success("Good news: every member in this report visited at least once.")

    st.markdown("#### Explore more")
    a, b, c = st.columns(3)

    with a:
        segment_col = find_column(segments, ["segment", "cluster", "segment_id"])
        segment_count = (
            segments[segment_col].nunique()
            if segment_col and not segments.empty
            else 0
        )
        info_card(
            "Member groups",
            f"{segment_count:,}",
            "Members with similar habits are put in the same group",
        )

    with b:
        info_card(
            "Workout plans",
            f"{len(recommendations):,}",
            "Plans suggested for members",
        )

    with c:
        info_card(
            "Ask a question",
            "Ready",
            "Type a question about your gym in plain English",
        )

    st.caption(
        "This is practice data created for demonstration. These are not real members. "
        "“Did not come back” means no visits were recorded in the 30 days after the report date."
    )


# ============================================================
# MEMBERS
# ============================================================

elif page == "Members":
    hero(
        "Find a member",
        "Look up members and see how often they visit.",
    )

    if features.empty:
        st.warning("The member list is not available. Please set up the data first.")
    else:
        search = st.text_input(
            "Search by member ID",
            placeholder="Type a member ID...",
        )

        filtered = features.copy()
        if search.strip() and "member_id" in filtered.columns:
            filtered = filtered[
                filtered["member_id"].astype(str).str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                )
            ]

        c1, c2, c3 = st.columns(3)
        c1.metric("Members found", f"{len(filtered):,}")
        c2.metric(
            "Average visits",
            format_number(safe_mean(filtered, "attendance_count")),
        )
        c3.metric(
            "Average days visited",
            format_number(safe_mean(filtered, "active_days")),
        )

        filtered = sort_by_member_id(filtered)

        section("Member list", "Sorted by member ID.")
        show_table(filtered, height=480)


# ============================================================
# MEMBERS WHO STOPPED COMING
# ============================================================

elif page == "Churn Intelligence":
    hero(
        "Members who stopped coming",
        "See who has stopped visiting and what they have in common.",
    )

    if features.empty or "churned" not in features.columns:
        st.warning("This information is not available yet.")
    else:
        st.info(
            "How we decide: we checked who visited the gym between October 1 and "
            "October 30, 2026. Anyone with no visits in that time is marked as "
            "“stopped coming”. The member details are as of September 30, 2026. "
            "Only members who were signed up for the whole period are included."
        )

        labels = pd.to_numeric(features["churned"], errors="coerce").fillna(0)
        inactivity = features[labels == 1]
        no_label = features[labels == 0]

        c1, c2, c3 = st.columns(3)
        c1.metric("Members who stopped coming", f"{len(inactivity):,}")
        c2.metric("Members who kept coming", f"{len(no_label):,}")
        c3.metric(
            "Share who stopped coming",
            f"{len(inactivity) / len(features) * 100:.1f}%" if len(features) else "0%",
        )

        section(
            "How the two groups differ",
            "Average numbers for each group. These show patterns, but they do not prove what caused them.",
        )

        comparison_columns = [
            column
            for column in [
                "attendance_count",
                "days_since_last_visit",
                "failed_payments",
                "attendance_recent_ratio",
                "goal_completion_rate",
                "workout_sessions",
            ]
            if column in features.columns
        ]

        if comparison_columns:
            comparison = (
                features.assign(_label=labels)
                .groupby("_label")[comparison_columns]
                .mean()
                .round(2)
            )
            comparison.index = comparison.index.map(
                {0: "Kept coming", 1: "Stopped coming"}
            )
            comparison = comparison.rename_axis("Members who...").reset_index()
            show_table(comparison, height=140)
        else:
            st.info("There are no numbers to compare yet.")

        section(
            "Members who stopped coming: full list",
            "Members with no visits in the 30 days after the report date. The longest-absent members are shown first.",
        )

        columns = [
            column
            for column in [
                "member_id",
                "attendance_count",
                "days_since_last_visit",
                "failed_payments",
                "attendance_recent_ratio",
                "goal_completion_rate",
                "churned",
            ]
            if column in features.columns
        ]

        risk_data = inactivity[columns].copy()
        if "days_since_last_visit" in risk_data.columns:
            risk_data = risk_data.sort_values(
                "days_since_last_visit",
                ascending=False,
            )
        show_table(risk_data, height=400)

        st.caption(
            "This uses practice data. “Stopped coming” here means no visits in 30 days, "
            "which is not the same as a member cancelling their membership."
        )


# ============================================================
# MEMBER GROUPS
# ============================================================

elif page == "Segments":
    hero(
        "Member groups",
        "Members who use the gym in similar ways are put into the same group.",
    )

    if segments.empty:
        st.warning("Member group information is not available yet.")
    else:
        segment_column = find_column(
            segments,
            ["segment", "cluster", "segment_id"],
        )

        if segment_column:
            counts = segments[segment_column].value_counts().sort_index()

            c1, c2 = st.columns(2)
            c1.metric("Members placed in groups", f"{len(segments):,}")
            c2.metric("Number of groups", f"{len(counts):,}")

            section(
                "How big is each group?",
                "The number of members in each group.",
            )
            st.bar_chart(counts, color="#b9f36b")

            cards = st.columns(min(len(counts), 4))
            for card, (name, count) in zip(cards, counts.items()):
                with card:
                    info_card(
                        f"Group {name}",
                        f"{count:,}",
                        "Members in this group",
                    )
        else:
            st.warning("The group information could not be found in the data.")

        section(
            "What each group is like",
            "Average numbers for the members in each group.",
        )
        if not profiles.empty:
            show_table(profiles, height=350)
        else:
            st.info("Group details are not available yet.")

        section("Which group each member is in")
        show_table(segments, height=400)


# ============================================================
# WORKOUT PLANS
# ============================================================

elif page == "Workout Studio":
    hero(
        "Workout plans",
        "See the workout plans suggested for members and how they are spread out.",
    )

    if recommendations.empty:
        st.warning("Workout plan information is not available yet.")
    else:
        recommendation_column = find_column(
            recommendations,
            [
                "recommendation_type",
                "recommendation",
                "recommended_workout",
                "workout_recommendation",
            ],
        )

        if recommendation_column:
            counts = recommendations[recommendation_column].value_counts()

            c1, c2, c3 = st.columns(3)
            c1.metric("Plans suggested", f"{len(recommendations):,}")
            c2.metric("Types of plan", f"{len(counts):,}")
            c3.metric(
                "Members with a plan",
                f"{recommendations['member_id'].nunique():,}"
                if "member_id" in recommendations.columns
                else "—",
            )

            section(
                "Which plans are suggested most?",
                "The number of members given each type of plan.",
            )
            st.bar_chart(counts, color="#b9f36b")

        section("Plan for each member")
        show_table(recommendations, height=450)

    section("Workout highlights")
    if insights:
        useful_insights = {
            key: value
            for key, value in insights.items()
            if isinstance(value, (str, int, float, bool))
        }

        if useful_insights:
            columns = st.columns(min(len(useful_insights), 4))
            for index, (key, value) in enumerate(useful_insights.items()):
                with columns[index % len(columns)]:
                    info_card(
                        key.replace("_", " ").capitalize(),
                        str(value),
                        "Workout fact",
                    )
        else:
            st.info("There are no highlights to show yet.")
    else:
        st.info("Workout highlights are not available yet.")


# ============================================================
# ASK A QUESTION
# ============================================================

elif page == "AI Assistant":
    hero(
        "Ask a question about your gym.",
        "Ask about members, visits, groups, workout plans and goals.",
    )

    st.markdown(
        """
        <div class="assistant-banner">
            <div class="assistant-banner-title">Ask in plain English</div>
            <div class="assistant-banner-copy">
                Tap one of the suggested questions below, or type your own question
                at the bottom of the page. Answers come from the gym data in this report.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Question wording is unchanged on purpose: the answer service may rely on it.
    question_groups = {
        "MEMBERS": [
            "How many members are registered?",
            "What is the average attendance?",
        ],
        "VISITS & RETENTION": [
            "How many members are at risk of inactivity?",
            "How many members are inactive?",
        ],
        "MEMBER GROUPS": [
            "How many members are in each segment?",
        ],
        "WORKOUTS": [
            "How are workout recommendations distributed?",
        ],
        "GOALS & PAYMENTS": [
            "What is the goal completion rate?",
            "How many members have failed payments?",
        ],
    }

    WELCOME_MESSAGE = {
        "role": "assistant",
        "content": (
            "Hello! I can answer questions about your members, their visits, payments, "
            "groups, workout plans and goals. Tap a suggested question or type your own."
        ),
        "source": "Gym report",
    }

    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = [WELCOME_MESSAGE]

    if "pending_assistant_question" not in st.session_state:
        st.session_state.pending_assistant_question = None

    def queue_assistant_question(question: str) -> None:
        st.session_state.pending_assistant_question = question

    for category, questions in question_groups.items():
        st.markdown(
            f'<div class="question-group-title">{category}</div>',
            unsafe_allow_html=True,
        )

        prompt_columns = st.columns(len(questions))
        for index, question_text in enumerate(questions):
            with prompt_columns[index]:
                st.button(
                    question_text,
                    key=f"assistant_prompt_{category}_{index}",
                    use_container_width=True,
                    on_click=queue_assistant_question,
                    args=(question_text,),
                )

    typed_question = st.chat_input("Type your question here...")
    if typed_question:
        st.session_state.pending_assistant_question = typed_question

    pending_question = st.session_state.pending_assistant_question

    if pending_question:
        st.session_state.pending_assistant_question = None
        st.session_state.assistant_messages.append(
            {
                "role": "user",
                "content": pending_question,
                "source": "",
            }
        )

        try:
            with st.spinner("Looking up your answer..."):
                result = ask_gym_assistant(pending_question)

            answer = result.get(
                "answer",
                "Sorry, I could not find an answer to that in the gym data.",
            )
            source = result.get("source", "Gym data")
            mode = result.get("mode", "unknown")
            model = result.get("model")
        except urllib.error.HTTPError as error:
            print(f"Assistant HTTP error: {error.code}", file=sys.stderr)
            answer = (
                "Sorry, something went wrong while getting your answer. "
                "Please try again in a moment."
            )
            source = "Answer service"
            mode = "error"
            model = None
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            print(f"Assistant connection error: {error!r}", file=sys.stderr)
            answer = (
                "Sorry, I can't get answers right now. The answer service may be "
                "switched off. Please try again later or ask the person who manages "
                "this app to check it."
            )
            source = "Answer service"
            mode = "error"
            model = None
        except Exception as error:
            print(f"Assistant error: {error!r}", file=sys.stderr)
            answer = "Sorry, I could not answer that. Please try again."
            source = "Answer service"
            mode = "error"
            model = None

        st.session_state.assistant_messages.append(
            {
                "role": "assistant",
                "content": answer,
                "source": source,
                "mode": mode,
                "model": model,
            }
        )
        st.rerun()

    section(
        "Your conversation",
        "Your questions and the answers appear here.",
    )

    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("source"):
                st.caption(f"Answer based on: {message['source']}")

            if message["role"] == "assistant" and message.get("mode"):
                mode = message["mode"]
                if mode == "gemini":
                    st.caption("Explained by AI (Google Gemini)")
                elif mode == "deterministic_fallback":
                    st.caption("Quick answer straight from the data (AI explanation not available right now)")
                elif mode == "error":
                    st.caption("No answer received")

    clear_col, note_col = st.columns([1, 3])
    with clear_col:
        if st.button("Clear conversation", key="clear_assistant_chat"):
            del st.session_state["assistant_messages"]
            st.rerun()
    with note_col:
        st.caption(
            "Your question is checked against the gym data, and AI (Google Gemini) "
            "explains the result in simple words. If the AI is not available, "
            "you get a shorter answer straight from the data."
        )


# ============================================================
# HOW RELIABLE IS THE PREDICTION
# ============================================================

elif page == "AI Performance":
    hero(
        "How reliable is the prediction?",
        "The computer tries to guess which members may stop coming. "
        "Here is how well those guesses matched what really happened in a test.",
    )

    if not metrics:
        st.warning("The test results are not available yet.")
    else:
        evaluation = metrics.get("test_metrics", metrics)

        if isinstance(evaluation, dict):
            metric_names = [
                (
                    "Overall correct",
                    "accuracy",
                    "Out of 100 members, how many it got right.",
                ),
                (
                    "Right when it warned",
                    "precision",
                    "When it said a member would stop coming, how often it was right.",
                ),
                (
                    "Stopped-members it caught",
                    "recall",
                    "Of the members who really stopped coming, how many it spotted.",
                ),
                (
                    "Balance score",
                    "f1_score",
                    "One score that balances the two numbers above.",
                ),
                (
                    "Ranking skill",
                    "roc_auc",
                    "How well it puts likely-to-stop members first. 50% is a coin toss, 100% is perfect.",
                ),
                (
                    "Warning quality",
                    "pr_auc",
                    "How well it finds members who stopped, without many false alarms.",
                ),
            ]

            available = [
                (label, key, note, evaluation[key])
                for label, key, note in metric_names
                if key in evaluation
            ]

            if available:
                section(
                    "Test results",
                    "How the prediction did on members it had not seen before. Higher is better.",
                )
                columns = st.columns(min(len(available), 3))

                for index, (label, key, note, value) in enumerate(available):
                    with columns[index % len(columns)]:
                        info_card(label, format_percent(value), note)

        with st.expander("Technical details (for developers)"):
            st.json(metrics)

    st.caption(
        "This test used practice data and a small group of members, so treat the "
        "results as a rough guide, not a guarantee."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    """
    <div style="
        text-align:center;
        color:#8a9ba9;
        font-size:11px;
        letter-spacing:1.4px;
        padding:10px 0 4px;">
        GYM INTELLIGENCE · BUILT FOR DATA-DRIVEN FITNESS
    </div>
    """,
    unsafe_allow_html=True,
)