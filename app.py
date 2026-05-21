import io
import json
import os
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from prediction_logic import StudentDropoutRiskLogic


DATASET_PATH = "updated_nigerian_student_dropout_dataset_5000.csv"
PROFILE_PATH = "dataset_profile.json"

REQUIRED_COLUMNS = [
    "Student_ID",
    "Matric_No",
    "Full_Name",
    "Gender",
    "Age",
    "State_of_Origin",
    "Programme",
    "Entry_Year",
    "Level",
    "Semester_GPA",
    "Cumulative_GPA",
    "Courses_Attempted",
    "Courses_Passed",
    "Attendance_Percentage",
    "Failed_Courses",
    "Carryovers",
    "Scholarship_Holder",
    "Tuition_Status",
    "Financial_Stress_Score",
    "LMS_Login_Frequency",
    "Assignment_Submission_Rate",
    "Medical_Challenges",
]

NUMERIC_COLUMNS = [
    "Age",
    "Entry_Year",
    "Level",
    "Semester_GPA",
    "Cumulative_GPA",
    "Courses_Attempted",
    "Courses_Passed",
    "Attendance_Percentage",
    "Failed_Courses",
    "Carryovers",
    "Financial_Stress_Score",
    "LMS_Login_Frequency",
    "Assignment_Submission_Rate",
]

DISPLAY_COLUMNS = [
    "Full_Name",
    "Matric_No",
    "Programme",
    "Level",
    "Cumulative_GPA",
    "Attendance_Percentage",
    "Failed_Courses",
    "Carryovers",
    "Tuition_Status",
    "Financial_Stress_Score",
    "Risk_Index",
    "Risk_Band",
]


st.set_page_config(
    page_title="Student Retention Intelligence",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4f1ea;
            --bg-soft: #faf8f3;
            --surface: #fffdf8;
            --surface-strong: #ffffff;
            --ink: #191713;
            --ink-soft: #514b43;
            --muted: #7b7266;
            --line: #e5ded0;
            --line-strong: #d6c8b2;
            --gold: #a77a2d;
            --gold-soft: #f2e4c6;
            --green: #145a3a;
            --green-soft: #e4efe8;
            --teal: #0f6f68;
            --plum: #5b324f;
            --red: #a2342c;
            --red-soft: #f7dedb;
            --amber: #b26d15;
            --amber-soft: #f5e1c4;
            --shadow: 0 24px 70px rgba(25, 23, 19, 0.10);
            --soft-shadow: 0 14px 34px rgba(25, 23, 19, 0.07);
        }

        html,
        body,
        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(135deg, rgba(250,248,243,0.98), rgba(244,241,234,0.96)),
                radial-gradient(circle at 12% 8%, rgba(167,122,45,0.12), transparent 26%),
                radial-gradient(circle at 88% 4%, rgba(20,90,58,0.10), transparent 24%);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: rgba(250, 248, 243, 0.82);
            border-bottom: 1px solid rgba(229, 222, 208, 0.82);
            backdrop-filter: blur(18px);
        }

        .main .block-container {
            max-width: min(96vw, 1560px);
            padding: 1.15rem 1.35rem 2.4rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.82rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.85rem;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(255,253,248,0.96), rgba(240,235,224,0.96));
            border-right: 1px solid var(--line);
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] label {
            color: var(--ink-soft);
        }

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }

        h1, h2, h3, h4, h5 {
            color: var(--ink);
            letter-spacing: 0;
        }

        h1 {
            line-height: 1.04;
        }

        hr {
            border-color: var(--line);
            margin: 1.1rem 0;
        }

        .lux-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: clamp(1rem, 2.2vw, 1.65rem);
            background:
                linear-gradient(135deg, rgba(25,23,19,0.96), rgba(20,90,58,0.92)),
                linear-gradient(135deg, rgba(167,122,45,0.14), transparent);
            box-shadow: var(--shadow);
            color: #fffdf8;
            margin-bottom: 0.9rem;
        }

        .lux-hero::after {
            content: "";
            position: absolute;
            inset: auto -6rem -8rem auto;
            width: 22rem;
            height: 22rem;
            border: 1px solid rgba(242, 228, 198, 0.28);
            border-radius: 50%;
        }

        .hero-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.75fr);
            gap: clamp(0.9rem, 2vw, 1.5rem);
            align-items: end;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #f2e4c6;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.48rem;
        }

        .hero-title {
            margin: 0;
            max-width: 980px;
            color: #fffdf8;
            font-size: clamp(1.85rem, 4vw, 3.75rem);
            font-weight: 900;
            letter-spacing: 0;
        }

        .hero-copy {
            max-width: 880px;
            color: rgba(255,253,248,0.78);
            margin: 0.65rem 0 0;
            font-size: clamp(0.92rem, 1.4vw, 1.02rem);
            line-height: 1.55;
        }

        .hero-stats {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.62rem;
        }

        .hero-stat {
            border: 1px solid rgba(242, 228, 198, 0.24);
            background: rgba(255, 253, 248, 0.08);
            border-radius: 14px;
            padding: 0.78rem;
            backdrop-filter: blur(18px);
            min-height: 82px;
        }

        .hero-stat span {
            display: block;
            color: rgba(255,253,248,0.62);
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .hero-stat strong {
            display: block;
            margin-top: 0.3rem;
            color: #fffdf8;
            font-size: clamp(1.18rem, 2.4vw, 1.72rem);
            line-height: 1.05;
        }

        .metric-grid,
        .insight-grid,
        .driver-grid,
        .student-profile-grid,
        .micro-grid {
            display: grid;
            gap: 0.72rem;
        }

        .metric-grid {
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        }

        .insight-grid {
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        }

        .driver-grid {
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        }

        .student-profile-grid {
            grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
        }

        .micro-grid {
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        }

        .metric-card,
        .insight-card,
        .profile-card,
        .driver-card,
        .result-card,
        .panel-card {
            background: rgba(255,253,248,0.94);
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--soft-shadow);
        }

        .metric-card {
            padding: 0.82rem;
            min-height: 112px;
        }

        .metric-card span,
        .profile-card span,
        .driver-card span {
            display: block;
            color: var(--muted);
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metric-card strong {
            display: block;
            margin-top: 0.32rem;
            color: var(--ink);
            font-size: clamp(1.22rem, 2.3vw, 1.86rem);
            line-height: 1.06;
        }

        .metric-card small,
        .profile-card small,
        .driver-card small {
            display: block;
            margin-top: 0.36rem;
            color: var(--ink-soft);
            font-size: 0.8rem;
            line-height: 1.34;
        }

        .accent-green { border-top: 4px solid var(--green); }
        .accent-gold { border-top: 4px solid var(--gold); }
        .accent-red { border-top: 4px solid var(--red); }
        .accent-plum { border-top: 4px solid var(--plum); }

        .section-head {
            margin: 1.25rem 0 0.62rem;
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
        }

        .section-head .eyebrow {
            color: var(--gold);
            margin-bottom: 0.18rem;
        }

        .section-head h2 {
            margin: 0;
            font-size: clamp(1.18rem, 2.2vw, 1.72rem);
        }

        .section-head p {
            max-width: 720px;
            margin: 0;
            color: var(--muted);
            line-height: 1.45;
            font-size: 0.92rem;
        }

        .panel-card {
            padding: clamp(0.82rem, 1.6vw, 1rem);
        }

        .insight-card {
            padding: 0.86rem;
            min-height: 124px;
        }

        .insight-card strong {
            display: block;
            color: var(--ink);
            font-size: 1rem;
            margin-bottom: 0.35rem;
        }

        .insight-card p {
            color: var(--muted);
            margin: 0;
            line-height: 1.42;
            font-size: 0.86rem;
        }

        .profile-card,
        .driver-card {
            padding: 0.78rem;
        }

        .profile-card strong,
        .driver-card strong {
            display: block;
            margin-top: 0.35rem;
            color: var(--ink);
            font-size: 0.96rem;
        }

        .result-card {
            padding: clamp(0.85rem, 1.8vw, 1.1rem);
            border-left: 7px solid var(--green);
            margin: 0.72rem 0;
        }

        .result-card.high {
            border-left-color: var(--red);
            background: linear-gradient(135deg, rgba(247,222,219,0.78), rgba(255,253,248,0.96));
        }

        .result-card.watch {
            border-left-color: var(--amber);
            background: linear-gradient(135deg, rgba(245,225,196,0.80), rgba(255,253,248,0.96));
        }

        .result-card.low {
            border-left-color: var(--green);
            background: linear-gradient(135deg, rgba(228,239,232,0.90), rgba(255,253,248,0.96));
        }

        .result-card h3 {
            margin: 0;
            font-size: clamp(1.15rem, 2.4vw, 1.6rem);
        }

        .result-card p {
            margin: 0.4rem 0 0;
            color: var(--ink-soft);
            line-height: 1.45;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px;
            min-height: 2.55rem;
            font-weight: 850;
            letter-spacing: 0;
            border: 1px solid var(--green);
            background: linear-gradient(135deg, var(--green), #0f6f68);
            color: #fffdf8;
            box-shadow: 0 14px 24px rgba(20, 90, 58, 0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: var(--gold);
            color: #fffdf8;
            transform: translateY(-1px);
        }

        div[data-testid="stRadio"] [role="radiogroup"] {
            gap: 0.5rem;
            background: rgba(255,253,248,0.78);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.45rem;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea,
        input {
            border-radius: 12px !important;
            min-height: 2.35rem !important;
        }

        label,
        div[data-testid="stWidgetLabel"] {
            font-size: 0.88rem !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.38rem;
            background: rgba(255,253,248,0.72);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.45rem 0.75rem;
            height: auto;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--soft-shadow);
            padding: 1rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--soft-shadow);
        }

        .compact-kpi {
            background: linear-gradient(135deg, rgba(255,253,248,0.96), rgba(250,248,243,0.84));
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.72rem 0.8rem;
            min-height: 92px;
            box-shadow: var(--soft-shadow);
        }

        .compact-kpi span {
            display: block;
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .compact-kpi strong {
            display: block;
            margin-top: 0.24rem;
            color: var(--ink);
            font-size: clamp(1.05rem, 2vw, 1.5rem);
            word-break: break-word;
            overflow-wrap: break-word;
        }

        .compact-kpi small {
            display: block;
            margin-top: 0.22rem;
            color: var(--ink-soft);
            font-size: 0.76rem;
            line-height: 1.3;
        }

        @media (min-width: 1280px) {
            .metric-grid {
                grid-template-columns: repeat(6, minmax(0, 1fr));
            }

            .insight-grid {
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }

            .student-profile-grid {
                grid-template-columns: repeat(6, minmax(0, 1fr));
            }
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(255,253,248,0.90);
            box-shadow: var(--soft-shadow);
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
            border: 1px solid var(--line);
        }

        .mobile-safe-table {
            overflow-x: auto;
        }

        @media (max-width: 980px) {
            .main .block-container {
                max-width: 100vw;
                padding: 0.85rem 0.85rem 2rem;
            }

            .hero-grid {
                grid-template-columns: 1fr;
            }

            .hero-stats {
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }

            .section-head {
                display: block;
            }

            .section-head p {
                margin-top: 0.35rem;
                max-width: none;
            }
        }

        @media (max-width: 640px) {
            .lux-hero {
                border-radius: 14px;
                padding: 0.9rem;
            }

            .hero-copy {
                font-size: 0.9rem;
                line-height: 1.45;
            }

            .hero-stats,
            .metric-grid,
            .insight-grid,
            .driver-grid,
            .student-profile-grid {
                grid-template-columns: 1fr;
            }

            .hero-title {
                font-size: 1.88rem;
            }

            .metric-card,
            .insight-card,
            .profile-card,
            .driver-card,
            .compact-kpi {
                min-height: auto;
            }

            div[data-testid="stDataFrame"] {
                font-size: 0.78rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def clean_dataset(df: pd.DataFrame, ensure_required: bool = True) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]
    valid_columns = [
        column
        for column in df.columns
        if column and not column.lower().startswith("unnamed")
    ]
    df = df[valid_columns]

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if ensure_required:
        for column in REQUIRED_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA

    return df


@st.cache_data
def load_historical_data() -> pd.DataFrame | None:
    if not os.path.exists(DATASET_PATH):
        return None

    try:
        return clean_dataset(pd.read_csv(DATASET_PATH, encoding="utf-8-sig"))
    except Exception:
        return None


@st.cache_data
def load_profile() -> dict:
    if not os.path.exists(PROFILE_PATH):
        return {"Programme": [], "State_of_Origin": [], "Medical_Challenges": []}

    with open(PROFILE_PATH, "r", encoding="utf-8") as profile_file:
        return json.load(profile_file)


def enrich_with_risk(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty:
        return df

    enriched = df.copy()
    cgpa = enriched["Cumulative_GPA"].fillna(5.0)
    attendance = enriched["Attendance_Percentage"].fillna(100.0)
    carryovers = enriched["Carryovers"].fillna(0)
    failed = enriched["Failed_Courses"].fillna(0)
    stress = enriched["Financial_Stress_Score"].fillna(1)
    tuition = enriched["Tuition_Status"].fillna("Paid").astype(str).str.strip().str.lower()

    risk = pd.Series(0.0, index=enriched.index)
    risk += cgpa.lt(1.5) * 30
    risk += cgpa.ge(1.5).mul(cgpa.lt(2.5)) * 15

    backlog = carryovers + failed
    risk += backlog.gt(4) * 25
    risk += backlog.gt(1).mul(backlog.le(4)) * 10

    risk += attendance.lt(70.0) * 25
    risk += attendance.ge(70.0).mul(attendance.lt(80.0)) * 10

    risk += (tuition.eq("pending") | stress.gt(7)) * 20
    risk += tuition.ne("pending").mul(stress.gt(4)).mul(stress.le(7)) * 10

    enriched["Risk_Index"] = risk.round(0).astype(int)
    enriched["Backlog_Load"] = backlog.fillna(0).astype(int)
    enriched["Risk_Band"] = enriched["Risk_Index"].map(risk_band)
    enriched["Support_Priority"] = enriched["Risk_Index"].map(support_priority)
    return enriched


def risk_band(score: float | int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Watch"
    return "Stable"


def support_priority(score: float | int) -> str:
    if score >= 75:
        return "Same-day intervention"
    if score >= 50:
        return "Advisor escalation"
    if score >= 25:
        return "Guided monitoring"
    return "Routine follow-up"


def pct(part: float, whole: float) -> float:
    if not whole:
        return 0.0
    return round((part / whole) * 100, 1)


def fmt_number(value: float | int | None, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}{suffix}"
    return f"{value:,.0f}{suffix}"


def html_value(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return escape(str(value))


def render_section(title: str, note: str, kicker: str) -> None:
    st.markdown(
        f'<div class="section-head">'
        f'<div><div class="eyebrow">{escape(kicker)}</div>'
        f'<h2>{escape(title)}</h2></div>'
        f'<p>{escape(note)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_hero(df: pd.DataFrame | None) -> None:
    total = 0 if df is None else len(df)
    risk_queue = 0 if df is None else int((df["Risk_Index"] >= 50).sum())
    watch_list = 0 if df is None else int((df["Risk_Index"] >= 25).sum())
    avg_cgpa = None if df is None or df.empty else df["Cumulative_GPA"].mean()

    st.markdown(
        f"""
        <div class="lux-hero">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">Student success intelligence</div>
                    <h1 class="hero-title">Retention decisions with the calm of an executive cockpit.</h1>
                    <p class="hero-copy">
                        This console converts academic performance, attendance, curriculum backlog,
                        tuition exposure, and financial stress into a practical support queue for the institution.
                    </p>
                </div>
                <div class="hero-stats">
                    <div class="hero-stat"><span>Cohort size</span><strong>{total:,}</strong></div>
                    <div class="hero-stat"><span>Risk queue</span><strong>{risk_queue:,}</strong></div>
                    <div class="hero-stat"><span>Watch list</span><strong>{watch_list:,}</strong></div>
                    <div class="hero-stat"><span>Mean CGPA</span><strong>{fmt_number(avg_cgpa)}</strong></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(df: pd.DataFrame) -> None:
    total = len(df)
    high_risk = int((df["Risk_Index"] >= 50).sum())
    critical = int((df["Risk_Band"] == "Critical").sum())
    pending_tuition = int(df["Tuition_Status"].fillna("").astype(str).str.lower().eq("pending").sum())
    low_attendance = int((df["Attendance_Percentage"] < 70).sum())
    avg_attendance = df["Attendance_Percentage"].mean()
    avg_cgpa = df["Cumulative_GPA"].mean()

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card accent-green">
                <span>Tracked cohort</span>
                <strong>{total:,}</strong>
                <small>Complete student records currently available for analysis.</small>
            </div>
            <div class="metric-card accent-red">
                <span>High-risk queue</span>
                <strong>{high_risk:,}</strong>
                <small>{pct(high_risk, total)}% of the selected cohort needs advisor attention.</small>
            </div>
            <div class="metric-card accent-gold">
                <span>Critical interventions</span>
                <strong>{critical:,}</strong>
                <small>Same-day support candidates based on combined risk indicators.</small>
            </div>
            <div class="metric-card accent-plum">
                <span>Tuition exposure</span>
                <strong>{pending_tuition:,}</strong>
                <small>{pct(pending_tuition, total)}% of records show pending tuition status.</small>
            </div>
            <div class="metric-card accent-green">
                <span>Mean CGPA</span>
                <strong>{fmt_number(avg_cgpa)}</strong>
                <small>Academic center of gravity across the filtered population.</small>
            </div>
            <div class="metric-card accent-red">
                <span>Attendance default</span>
                <strong>{low_attendance:,}</strong>
                <small>{fmt_number(avg_attendance, "%")} average attendance in this view.</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_kpis(df: pd.DataFrame) -> None:
    total = len(df)
    top_programme = df["Programme"].mode().iloc[0] if not df["Programme"].mode().empty else "N/A"
    top_state = df["State_of_Origin"].mode().iloc[0] if not df["State_of_Origin"].mode().empty else "N/A"
    avg_stress = df["Financial_Stress_Score"].mean()
    assignment_avg = df["Assignment_Submission_Rate"].mean()
    backlog_sum = df["Backlog_Load"].sum()
    stable_count = int((df["Risk_Band"] == "Stable").sum())

    st.markdown(
        f"""
        <div class="micro-grid">
            <div class="compact-kpi">
                <span>Leading programme</span>
                <strong>{escape(str(top_programme))}</strong>
                <small>Largest share in the current filter.</small>
            </div>
            <div class="compact-kpi">
                <span>Top origin</span>
                <strong>{escape(str(top_state))}</strong>
                <small>Most represented state in view.</small>
            </div>
            <div class="compact-kpi">
                <span>Average stress</span>
                <strong>{fmt_number(avg_stress)} / 10</strong>
                <small>Financial pressure baseline.</small>
            </div>
            <div class="compact-kpi">
                <span>Assignment health</span>
                <strong>{fmt_number(assignment_avg, "%")}</strong>
                <small>Mean submission performance.</small>
            </div>
            <div class="compact-kpi">
                <span>Total backlog</span>
                <strong>{backlog_sum:,}</strong>
                <small>Failed and carryover load.</small>
            </div>
            <div class="compact-kpi">
                <span>Stable students</span>
                <strong>{stable_count:,}</strong>
                <small>{pct(stable_count, total)}% routine follow-up.</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_cards(df: pd.DataFrame) -> None:
    total = len(df)
    academic_pressure = int((df["Cumulative_GPA"] < 2.5).sum())
    backlog_pressure = int((df["Backlog_Load"] > 4).sum())
    engagement_pressure = int((df["Attendance_Percentage"] < 70).sum())
    financial_pressure = int(
        (
            df["Tuition_Status"].fillna("").astype(str).str.lower().eq("pending")
            | (df["Financial_Stress_Score"] > 7)
        ).sum()
    )

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <strong>Academic pressure</strong>
                <p>{academic_pressure:,} students ({pct(academic_pressure, total)}%) sit below a 2.50 CGPA and should be checked for learning support or progression barriers.</p>
            </div>
            <div class="insight-card">
                <strong>Curriculum backlog</strong>
                <p>{backlog_pressure:,} students carry a heavy failed-course or carryover load, which can quietly delay graduation even when attendance is acceptable.</p>
            </div>
            <div class="insight-card">
                <strong>Engagement pressure</strong>
                <p>{engagement_pressure:,} students are below the 70% attendance threshold. This is the fastest signal to convert into an outreach workflow.</p>
            </div>
            <div class="insight-card">
                <strong>Financial pressure</strong>
                <p>{financial_pressure:,} students show tuition or severe stress exposure. Pair academic advising with finance-office intervention.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_bar(data: pd.DataFrame, x: str, y: str, title: str, color: str = "#145a3a"):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7, color=color)
        .encode(
            x=alt.X(x, title=None),
            y=alt.Y(y, title=None),
            tooltip=list(data.columns),
        )
        .properties(height=285, title=title)
        .configure_title(anchor="start", color="#191713", fontSize=16, fontWeight=700)
        .configure_axis(labelColor="#514b43", titleColor="#514b43", gridColor="#eee7da")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def chart_horizontal(data: pd.DataFrame, x: str, y: str, title: str, color: str = "#a77a2d"):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopRight=7, cornerRadiusBottomRight=7, color=color)
        .encode(
            x=alt.X(x, title=None),
            y=alt.Y(y, title=None, sort="-x"),
            tooltip=list(data.columns),
        )
        .properties(height=285, title=title)
        .configure_title(anchor="start", color="#191713", fontSize=16, fontWeight=700)
        .configure_axis(labelColor="#514b43", titleColor="#514b43", gridColor="#eee7da")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def chart_scatter(df: pd.DataFrame) -> None:
    source = df.dropna(subset=["Cumulative_GPA", "Attendance_Percentage", "Risk_Index"])
    if source.empty:
        st.info("Not enough complete records for the risk matrix.")
        return

    chart = (
        alt.Chart(source)
        .mark_circle(opacity=0.72)
        .encode(
            x=alt.X("Cumulative_GPA:Q", title="CGPA", scale=alt.Scale(domain=[0, 5])),
            y=alt.Y("Attendance_Percentage:Q", title="Attendance", scale=alt.Scale(domain=[0, 100])),
            size=alt.Size("Risk_Index:Q", title="Risk index", scale=alt.Scale(range=[40, 420])),
            color=alt.Color(
                "Risk_Band:N",
                title="Risk band",
                scale=alt.Scale(
                    domain=["Stable", "Watch", "High", "Critical"],
                    range=["#145a3a", "#b26d15", "#a2342c", "#5b324f"],
                ),
            ),
            tooltip=[
                "Full_Name",
                "Matric_No",
                "Programme",
                "Cumulative_GPA",
                "Attendance_Percentage",
                "Risk_Index",
                "Risk_Band",
            ],
        )
        .properties(height=335, title="Risk matrix: attendance by CGPA")
        .interactive()
        .configure_title(anchor="start", color="#191713", fontSize=16, fontWeight=700)
        .configure_axis(labelColor="#514b43", titleColor="#514b43", gridColor="#eee7da")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def row_to_payload(row: pd.Series) -> dict:
    payload = {}
    for column in REQUIRED_COLUMNS:
        value = row.get(column)
        if pd.isna(value):
            value = 0 if column in NUMERIC_COLUMNS else ""
        payload[column] = value
    return payload


def risk_reasons(data: dict) -> list[tuple[str, str, str]]:
    reasons = []
    cgpa = float(data.get("Cumulative_GPA", 5.0) or 0)
    attendance = float(data.get("Attendance_Percentage", 100.0) or 0)
    carryovers = int(data.get("Carryovers", 0) or 0)
    failed = int(data.get("Failed_Courses", 0) or 0)
    assignment_rate = float(data.get("Assignment_Submission_Rate", 100.0) or 0)
    tuition = str(data.get("Tuition_Status", "Paid")).strip().lower()
    stress = int(data.get("Financial_Stress_Score", 1) or 1)

    if cgpa < 1.5:
        reasons.append(("Critical academic standing", f"CGPA is {cgpa:.2f}, which sits in the probation zone.", "Critical"))
    elif cgpa < 2.5:
        reasons.append(("Academic support needed", f"CGPA is {cgpa:.2f}; this student needs structured academic recovery.", "Watch"))

    backlog = carryovers + failed
    if backlog > 4:
        reasons.append(("Heavy curriculum backlog", f"{backlog} failed or carryover courses are active.", "Critical"))
    elif backlog > 0:
        reasons.append(("Course backlog present", f"{backlog} failed or carryover courses may slow progression.", "Watch"))

    if attendance < 70:
        reasons.append(("Attendance default", f"Attendance is {attendance:.1f}%, below the exam-entry threshold.", "Critical"))
    elif attendance < 80:
        reasons.append(("Attendance drift", f"Attendance is {attendance:.1f}%, close to the danger zone.", "Watch"))

    if assignment_rate < 75:
        reasons.append(("Low assignment delivery", f"Assignment submission is {assignment_rate:.1f}%.", "Watch"))

    if tuition == "pending":
        reasons.append(("Tuition block risk", "Tuition status is pending and may restrict registration.", "Critical"))

    if stress > 7:
        reasons.append(("Severe financial stress", f"Financial stress is {stress}/10.", "Critical"))
    elif stress > 4:
        reasons.append(("Moderate financial stress", f"Financial stress is {stress}/10.", "Watch"))

    if not reasons:
        reasons.append(("No significant red flags", "The available indicators align with stable retention baselines.", "Stable"))

    return reasons


def render_result(payload: dict, display_name: str = "Selected student") -> None:
    result = StudentDropoutRiskLogic.evaluate_risk(payload)
    if not result["success"]:
        st.error(f"Prediction pipeline failure: {result['error_message']}")
        return

    probability = result["dropout_probability"] * 100
    band = risk_band(probability)
    card_class = "high" if probability >= 50 else "watch" if probability >= 25 else "low"
    verdict = "High-risk support case" if probability >= 50 else "Watch-list profile" if probability >= 25 else "Stable retention profile"

    st.markdown(
        f"""
        <div class="result-card {card_class}">
            <h3>{escape(verdict)}</h3>
            <p>{escape(display_name)} has a calculated institutional risk index of <strong>{probability:.2f}%</strong>.
            Recommended handling: <strong>{escape(support_priority(probability))}</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(max(int(probability), 0), 100), text=f"Risk index: {probability:.2f}%")

    reasons = risk_reasons(payload)
    reason_html = "".join(
        f'<div class="driver-card"><span>{escape(level)}</span>'
        f'<strong>{escape(title)}</strong>'
        f'<small>{escape(detail)}</small></div>'
        for title, detail, level in reasons
    )
    st.markdown(f'<div class="driver-grid">{reason_html}</div>', unsafe_allow_html=True)


def render_student_profile(row: pd.Series) -> None:
    profile = [
        ("Student", row.get("Full_Name"), row.get("Matric_No")),
        ("Programme", row.get("Programme"), f"{html_value(row.get('Level'))} Level"),
        ("Academic pulse", f"{fmt_number(row.get('Cumulative_GPA'))} CGPA", f"{fmt_number(row.get('Semester_GPA'))} semester GPA"),
        ("Engagement", f"{fmt_number(row.get('Attendance_Percentage'), '%')} attendance", f"{fmt_number(row.get('LMS_Login_Frequency'))} LMS logins/month"),
        ("Backlog", f"{fmt_number(row.get('Backlog_Load'))} active load", f"{fmt_number(row.get('Failed_Courses'))} failed, {fmt_number(row.get('Carryovers'))} carryovers"),
        ("Finance", row.get("Tuition_Status"), f"Stress score {html_value(row.get('Financial_Stress_Score'))}/10"),
    ]

    cards = "".join(
        f'<div class="profile-card"><span>{escape(label)}</span>'
        f'<strong>{html_value(primary)}</strong>'
        f'<small>{html_value(secondary)}</small></div>'
        for label, primary, secondary in profile
    )
    st.markdown(f'<div class="student-profile-grid">{cards}</div>', unsafe_allow_html=True)


def apply_sidebar_filters(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    st.sidebar.markdown("### Portfolio filters")

    programmes = sorted(df["Programme"].dropna().astype(str).unique().tolist()) or profile.get("Programme", [])
    selected_programmes = st.sidebar.multiselect("Programme", programmes, default=programmes)

    levels = sorted(df["Level"].dropna().astype(int).unique().tolist())
    selected_levels = st.sidebar.multiselect("Level", levels, default=levels)

    bands = ["Stable", "Watch", "High", "Critical"]
    selected_bands = st.sidebar.multiselect("Risk band", bands, default=bands)

    filtered = df.copy()
    if selected_programmes:
        filtered = filtered[filtered["Programme"].astype(str).isin(selected_programmes)]
    if selected_levels:
        filtered = filtered[filtered["Level"].isin(selected_levels)]
    if selected_bands:
        filtered = filtered[filtered["Risk_Band"].isin(selected_bands)]

    st.sidebar.markdown("---")
    st.sidebar.caption("Filters affect overview, intelligence, and queue views. Student search still uses the full registry.")
    return filtered


def render_overview(df: pd.DataFrame) -> None:
    render_section(
        "Executive overview",
        "A high-level command view of cohort health, intervention pressure, and institutional exposure.",
        "Cohort command",
    )
    render_metric_cards(df)
    render_compact_kpis(df)

    render_section(
        "Signal interpretation",
        "The system groups risk into practical operating lenses so academic units know what to do next.",
        "Intelligence layer",
    )
    render_insight_cards(df)

    render_section(
        "Distribution intelligence",
        "Responsive charts resize across desktop and mobile while preserving the decision-making hierarchy.",
        "Visual analytics",
    )
    chart_col1, chart_col2, chart_col3 = st.columns([0.85, 1.25, 0.9])
    with chart_col1:
        risk_counts = df["Risk_Band"].value_counts().rename_axis("Risk_Band").reset_index(name="Students")
        risk_counts["Risk_Band"] = pd.Categorical(
            risk_counts["Risk_Band"],
            categories=["Stable", "Watch", "High", "Critical"],
            ordered=True,
        )
        risk_counts = risk_counts.sort_values("Risk_Band")
        chart_bar(risk_counts, "Risk_Band:N", "Students:Q", "Risk band distribution", "#145a3a")

    with chart_col2:
        programme_counts = df["Programme"].value_counts().head(10).rename_axis("Programme").reset_index(name="Students")
        chart_horizontal(programme_counts, "Students:Q", "Programme:N", "Programme population", "#a77a2d")

    with chart_col3:
        tuition_counts = df["Tuition_Status"].fillna("Unknown").value_counts().rename_axis("Tuition_Status").reset_index(name="Students")
        chart_bar(tuition_counts, "Tuition_Status:N", "Students:Q", "Tuition status", "#0f6f68")

    chart_scatter(df)

    render_section(
        "Latest cohort records",
        "A compact operational table for fast scanning after filters have been applied.",
        "Registry stream",
    )
    st.dataframe(
        df[DISPLAY_COLUMNS].head(60),
        width="stretch",
        hide_index=True,
        column_config={
            "Risk_Index": st.column_config.ProgressColumn("Risk Index", min_value=0, max_value=100, format="%d"),
            "Cumulative_GPA": st.column_config.NumberColumn("CGPA", format="%.2f"),
            "Attendance_Percentage": st.column_config.NumberColumn("Attendance", format="%.1f%%"),
        },
    )

    csv_buffer = io.StringIO()
    df[DISPLAY_COLUMNS].to_csv(csv_buffer, index=False)
    st.download_button(
        "⬇ Export filtered cohort (CSV)",
        data=csv_buffer.getvalue(),
        file_name="filtered_cohort_export.csv",
        mime="text/csv",
    )


def render_risk_intelligence(df: pd.DataFrame) -> None:
    render_section(
        "Risk intelligence desk",
        "Prioritize the students most likely to need intervention and identify which risk drivers are dominating the cohort.",
        "Support queue",
    )

    driver_data = pd.DataFrame(
        [
            {"Driver": "CGPA below 2.50", "Students": int((df["Cumulative_GPA"] < 2.5).sum())},
            {"Driver": "Attendance below 70%", "Students": int((df["Attendance_Percentage"] < 70).sum())},
            {"Driver": "Backlog above 4", "Students": int((df["Backlog_Load"] > 4).sum())},
            {"Driver": "Tuition pending", "Students": int(df["Tuition_Status"].fillna("").astype(str).str.lower().eq("pending").sum())},
            {"Driver": "Stress above 7", "Students": int((df["Financial_Stress_Score"] > 7).sum())},
        ]
    )

    queue = df.sort_values(["Risk_Index", "Backlog_Load"], ascending=False)
    queue = queue[queue["Risk_Index"] >= 25]
    queue_col, driver_col = st.columns([1.35, 0.75])

    with queue_col:
        if queue.empty:
            st.success("No watch-list or high-risk students match the current filters.")
        else:
            st.dataframe(
                queue[DISPLAY_COLUMNS + ["Support_Priority"]].head(120),
                width="stretch",
                hide_index=True,
                column_config={
                    "Risk_Index": st.column_config.ProgressColumn("Risk Index", min_value=0, max_value=100, format="%d"),
                    "Cumulative_GPA": st.column_config.NumberColumn("CGPA", format="%.2f"),
                    "Attendance_Percentage": st.column_config.NumberColumn("Attendance", format="%.1f%%"),
                },
            )

    with driver_col:
        chart_horizontal(driver_data, "Students:Q", "Driver:N", "Driver pressure ranking", "#a2342c")

    render_section(
        "Dominant risk drivers",
        "Use these counts to decide whether the next institutional move is academic remediation, attendance outreach, or finance-office support.",
        "Root-cause lens",
    )
    driver_cards = "".join(
        f'<div class="compact-kpi"><span>{escape(row.Driver)}</span>'
        f'<strong>{row.Students:,}</strong>'
        f'<small>{pct(row.Students, len(df))}% of filtered records.</small></div>'
        for row in driver_data.itertuples(index=False)
    )
    st.markdown(f'<div class="micro-grid">{driver_cards}</div>', unsafe_allow_html=True)

    csv_buffer = io.StringIO()
    queue_export = df[df["Risk_Index"] >= 25][DISPLAY_COLUMNS + ["Support_Priority"]]
    queue_export.to_csv(csv_buffer, index=False)
    st.download_button(
        "⬇ Export risk queue (CSV)",
        data=csv_buffer.getvalue(),
        file_name="risk_queue_export.csv",
        mime="text/csv",
    )


def render_student_console(df: pd.DataFrame, profile: dict) -> None:
    render_section(
        "Student console",
        "Search a live record or simulate a new profile. The console turns the rule engine into a support conversation.",
        "Individual triage",
    )

    lookup_tab, sandbox_tab = st.tabs(["Registry lookup", "Sandbox simulation"])

    with lookup_tab:
        query = st.text_input(
            "Search by name, matric number, or programme",
            placeholder="Example: Adeola, CSC/20/00001, Data Science",
        )
        if query:
            query_mask = (
                df["Full_Name"].fillna("").astype(str).str.contains(query, case=False, na=False)
                | df["Matric_No"].fillna("").astype(str).str.contains(query, case=False, na=False)
                | df["Programme"].fillna("").astype(str).str.contains(query, case=False, na=False)
            )
            matches = df[query_mask].copy()
        else:
            matches = df.sort_values("Risk_Index", ascending=False).head(25).copy()

        if matches.empty:
            st.warning("No student records match that search.")
            return

        option_map = {
            f"{row.Full_Name} | {row.Matric_No} | {row.Programme} | Risk {row.Risk_Index}%": idx
            for idx, row in matches.iterrows()
        }
        selected_label = st.selectbox("Select student", list(option_map.keys()))
        selected_row = df.loc[option_map[selected_label]]

        profile_col, result_col = st.columns([1.05, 0.95])
        with profile_col:
            render_student_profile(selected_row)
        with result_col:
            render_result(row_to_payload(selected_row), str(selected_row.get("Full_Name", "Selected student")))

    with sandbox_tab:
        with st.form("sandbox_form"):
            form_col1, form_col2, form_col3 = st.columns(3)

            with form_col1:
                st.markdown("#### Academic")
                level = st.selectbox("Current level", [100, 200, 300, 400, 500])
                semester_gpa = st.slider("Latest semester GPA", 0.0, 5.0, 3.5, 0.01)
                cumulative_gpa = st.slider("Cumulative GPA", 0.0, 5.0, 3.4, 0.01)
                courses_attempted = st.number_input("Courses attempted", min_value=1, max_value=24, value=8)
                courses_passed = st.number_input("Courses passed", min_value=0, max_value=24, value=7)

            with form_col2:
                st.markdown("#### Engagement")
                attendance = st.slider("Attendance percentage", 0.0, 100.0, 85.0, 0.1)
                failed_courses = st.number_input("Failed courses", min_value=0, max_value=24, value=1)
                carryovers = st.number_input("Active carryovers", min_value=0, max_value=30, value=1)
                assignment_rate = st.slider("Assignment submission rate", 0.0, 100.0, 88.5, 0.1)
                lms_login = st.number_input("LMS logins per month", min_value=0, max_value=250, value=15)

            with form_col3:
                st.markdown("#### Context")
                gender = st.selectbox("Gender", ["Male", "Female"])
                age = st.number_input("Age", min_value=15, max_value=60, value=20)
                state = st.selectbox("State of origin", profile.get("State_of_Origin", []))
                programme = st.selectbox("Programme", profile.get("Programme", []))
                entry_year = st.number_input("Entry year", min_value=2018, max_value=2026, value=2025)
                scholarship = st.selectbox("Scholarship holder", ["No", "Yes"])
                tuition = st.selectbox("Tuition status", ["Paid", "Pending"])
                stress = st.slider("Financial stress score", 1, 10, 4)
                medical = st.selectbox("Medical challenges", profile.get("Medical_Challenges", []))

            submitted = st.form_submit_button("Run diagnostic assessment", width="stretch")

        if submitted:
            payload = {
                "Student_ID": "SIMULATION",
                "Matric_No": "SIMULATION",
                "Full_Name": "Sandbox Student",
                "Gender": gender,
                "Age": age,
                "State_of_Origin": state,
                "Programme": programme,
                "Entry_Year": entry_year,
                "Level": level,
                "Semester_GPA": semester_gpa,
                "Cumulative_GPA": cumulative_gpa,
                "Courses_Attempted": courses_attempted,
                "Courses_Passed": courses_passed,
                "Attendance_Percentage": attendance,
                "Failed_Courses": failed_courses,
                "Carryovers": carryovers,
                "Scholarship_Holder": scholarship,
                "Tuition_Status": tuition,
                "Financial_Stress_Score": stress,
                "LMS_Login_Frequency": lms_login,
                "Assignment_Submission_Rate": assignment_rate,
                "Medical_Challenges": medical,
            }
            render_result(payload, "Sandbox Student")


def render_data_intake(df: pd.DataFrame | None) -> None:
    render_section(
        "Data intake studio",
        "Download the official template, validate incoming records, and update the CSV-backed registry without losing column discipline.",
        "Controlled ingestion",
    )

    left, right = st.columns([0.9, 1.1])
    with left:
        template_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        csv_buffer = io.StringIO()
        template_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download intake template",
            data=csv_buffer.getvalue(),
            file_name="student_ingestion_template.csv",
            mime="text/csv",
            width="stretch",
        )
        st.markdown(
            """
            <div class="panel-card">
                <strong>Validation standard</strong>
                <p style="color:#7b7266; line-height:1.6; margin-bottom:0;">
                The upload must include all official fields. Extra blank or unnamed spreadsheet columns
                are cleaned automatically, but missing core fields are blocked.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        uploaded_file = st.file_uploader("Upload completed student CSV", type=["csv"])
        if uploaded_file is None:
            return

        try:
            uploaded_df = clean_dataset(pd.read_csv(uploaded_file), ensure_required=False)
        except Exception as exc:
            st.error(f"Unable to read uploaded CSV: {exc}")
            return

        missing = [column for column in REQUIRED_COLUMNS if column not in uploaded_df.columns]
        if missing:
            st.error("Upload blocked. Missing required columns: " + ", ".join(missing))
            return

        st.success(f"Validated {len(uploaded_df):,} incoming student records.")

        preview_enriched = enrich_with_risk(clean_dataset(uploaded_df))
        if preview_enriched is not None and not preview_enriched.empty:
            p_total = len(preview_enriched)
            p_high = int((preview_enriched["Risk_Index"] >= 50).sum())
            p_watch = int((preview_enriched["Risk_Index"] >= 25).sum()) - p_high
            p_stable = p_total - p_high - p_watch
            st.markdown(
                f'<div class="micro-grid">'
                f'<div class="compact-kpi"><span>Incoming records</span><strong>{p_total:,}</strong><small>Total validated rows.</small></div>'
                f'<div class="compact-kpi" style="border-top:4px solid var(--red)"><span>High risk</span><strong>{p_high:,}</strong><small>{pct(p_high, p_total)}% need immediate attention.</small></div>'
                f'<div class="compact-kpi" style="border-top:4px solid var(--amber)"><span>Watch list</span><strong>{p_watch:,}</strong><small>{pct(p_watch, p_total)}% require monitoring.</small></div>'
                f'<div class="compact-kpi" style="border-top:4px solid var(--green)"><span>Stable</span><strong>{p_stable:,}</strong><small>{pct(p_stable, p_total)}% routine follow-up.</small></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.dataframe(uploaded_df[REQUIRED_COLUMNS].head(20), width="stretch", hide_index=True)

        if st.button("Commit records to registry", type="primary", width="stretch"):
            if df is not None and not df.empty:
                combined = pd.concat([df[REQUIRED_COLUMNS], uploaded_df[REQUIRED_COLUMNS]], ignore_index=True)
                combined = combined.drop_duplicates(subset=["Student_ID", "Matric_No"], keep="last")
            else:
                combined = uploaded_df[REQUIRED_COLUMNS]

            combined.to_csv(DATASET_PATH, index=False)
            st.cache_data.clear()
            st.success("Registry updated. Refreshing the workspace now.")
            st.rerun()


def main() -> None:
    inject_theme()

    profile = load_profile()
    raw_df = load_historical_data()
    if raw_df is None or raw_df.empty:
        render_hero(None)
        st.error("Historical dataset is missing or empty. Use the Data Intake Studio to initialize the registry.")
        render_data_intake(raw_df)
        return

    df = enrich_with_risk(raw_df)
    render_hero(df)

    st.sidebar.markdown("## SR Intelligence")
    workspace = st.sidebar.radio(
        "Workspace",
        ["Executive Overview", "Risk Intelligence", "Student Console", "Data Intake Studio"],
    )

    filtered_df = apply_sidebar_filters(df, profile)
    if filtered_df.empty:
        st.warning("No records match the current sidebar filters.")
        return

    if workspace == "Executive Overview":
        render_overview(filtered_df)
    elif workspace == "Risk Intelligence":
        render_risk_intelligence(filtered_df)
    elif workspace == "Student Console":
        render_student_console(df, profile)
    else:
        render_data_intake(df)


if __name__ == "__main__":
    main()
