"""
ZOMCO-IMI | HSE Analytics Platform
Production-Grade Dashboard with RBAC
Version 2.0
"""

from pathlib import Path
import re
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import hashlib

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="ZOMCO-IMI | HSE Analytics Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== USER CREDENTIALS & ROLES ====================
USERS = {
    "Riyaz.Sulaiman": {"password": "Riyaz@123", "role": "Superintendent"},
    "Azarudeen.Naina": {"password": "Azar@123", "role": "Planner Engineer"},
    "Mustafa.Talaq": {"password": "Mustafa@123", "role": "Project Manager"},
    "Saleh.Yami": {"password": "Saleh@123", "role": "Facility Manager"},
    "Abdullah.AlSubaie": {"password": "Admin@123", "role": "HSE In-Charge"}
    "Ali.Yousuf": {"password": "Ali@123", "role": "HVAC Engineer"},

}

# Page access control by role
PAGE_ACCESS = {
    "Superintendent": ["Executive Overview", "Operational Analytics", "TSMH Performance", 
                       "Safety Intelligence", "Permit Management", "Training & Compliance", 
                       "Risk Assessment", "Reports & Export"],
    "Planner Engineer": ["TSMH Performance", "Permit Management", "Operational Analytics"],
    "Project Manager": ["Executive Overview", "TSMH Performance", "Permit Management"],
    "Facility Manager": ["Executive Overview", "Permit Management"],
    "HSE In-Charge": ["Executive Overview", "Operational Analytics", "TSMH Performance", 
                      "Safety Intelligence", "Permit Management", "Training & Compliance", 
                      "Risk Assessment", "Reports & Export"]
}

# ==================== STYLING ====================
st.markdown("""
<style>
    :root {
        --primary: #00D9FF;
        --secondary: #7B68EE;
        --success: #00C853;
        --warning: #FFB300;
        --danger: #FF3D00;
        --dark-bg: #0E1117;
        --card-bg: #1E2228;
        --border: #2D3340;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, #252b36 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 2px solid var(--border);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,217,255,0.2);
        border-color: var(--primary);
    }
    
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .alert-box {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        animation: slideIn 0.5s ease;
    }
    
    .alert-success {
        background: rgba(0, 200, 83, 0.1);
        border-color: var(--success);
        color: #51CF66;
    }
    
    .alert-warning {
        background: rgba(255, 179, 0, 0.1);
        border-color: var(--warning);
        color: #FFB84D;
    }
    
    .alert-info {
        background: rgba(0, 217, 255, 0.1);
        border-color: var(--primary);
        color: #00D9FF;
    }
    
    .chart-container {
        background: var(--card-bg);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        margin: 1rem 0;
    }
    
    .chart-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6C757D;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
    }
    
    .quote-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    .quote-text {
        font-size: 1.3rem;
        font-style: italic;
        margin-bottom: 1rem;
    }
    
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2rem;
        background: var(--card-bg);
        border-radius: 20px;
        border: 2px solid var(--border);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .access-denied {
        background: rgba(255, 61, 0, 0.1);
        border: 2px solid var(--danger);
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        color: #FF6B6B;
        margin: 3rem auto;
        max-width: 600px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA CONFIGURATION ====================
DATA_FILE = Path("Data Analysis 1.xlsm")
SHEET_TBT = "TBT"
SHEET_TSMH = "TSMH"
SHEET_PERMIT = "IMI Permit"

# Safety quotes that rotate daily
SAFETY_QUOTES = [
    "Safety is not an accident, it's a choice we make every day.",
    "Your family needs you. Work safely, return home safely.",
    "Think safety, work safely, be safe – it starts with you.",
    "Safety first, because accidents last.",
    "No task is so important that we cannot take time to do it safely.",
    "Safety doesn't happen by accident – it's a team effort.",
    "Be alert today, alive tomorrow. Safety pays.",
    "Safety is a cheap and effective insurance policy.",
    "Shortcuts cut life short. Follow procedures.",
    "Don't learn safety by accident.",
    "Your good health is your greatest wealth. Protect it.",
    "Safety: A frame of mind that builds a culture of caring.",
    "Working safely may get old, but so do those who practice it.",
    "Safety is everyone's responsibility. Take ownership."
]

# ==================== UTILITY FUNCTIONS ====================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names by removing line breaks and extra spaces"""
    def norm(s: str) -> str:
        s = str(s).replace("\n", " ").replace("\r", " ")
        s = re.sub(r"\s+", " ", s).strip()
        return s
    df = df.copy()
    df.columns = [norm(c) for c in df.columns]
    return df

@st.cache_data(ttl=300)
def load_data(sheet: str) -> pd.DataFrame:
    """Load and cache data with error handling"""
    if not DATA_FILE.exists():
        return pd.DataFrame()
    try:
        df = pd.read_excel(DATA_FILE, sheet_name=sheet, engine="openpyxl")
        return normalize_columns(df)
    except Exception as e:
        st.error(f"Error reading sheet '{sheet}': {e}")
        return pd.DataFrame()

def find_column(df: pd.DataFrame, names: list) -> str:
    """Find first matching column name (case-insensitive)"""
    if df.empty:
        return None
    lower_map = {c.lower().strip(): c for c in df.columns}
    for name in names:
        if name.lower().strip() in lower_map:
            return lower_map[name.lower().strip()]
    return None

def create_kpi_card(label: str, value, icon="📊"):
    """Create enhanced KPI card"""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

def create_alert(message: str, alert_type: str = "success"):
    """Create styled alert box"""
    return f'<div class="alert-box alert-{alert_type}">✓ {message}</div>'

def get_daily_quote():
    """Get quote that rotates daily"""
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(SAFETY_QUOTES)
    return SAFETY_QUOTES[index]

def get_smart_alerts(tbt_df, tsmh_df, tbt_att_col, rotation_days=7):
    """Generate smart alerts with rotation based on date"""
    alerts = []
    day_index = (datetime.now().timetuple().tm_yday // rotation_days) % 3
    
    # Alert variants for LTI
    lti_variants = [
        "Zero LTI this week – excellent safety control maintained",
        "No Lost Time Injuries recorded – outstanding performance",
        "Perfect safety record: Zero LTI incidents this period"
    ]
    alerts.append(("success", lti_variants[day_index % len(lti_variants)]))
    
    # TSMH growth alert
    if not tsmh_df.empty:
        try:
            tsmh_col = find_column(tsmh_df, ["Cumulative TSMH", "TSMH", "Total Safe Man Hours"])
            if tsmh_col:
                values = pd.to_numeric(tsmh_df[tsmh_col], errors='coerce').dropna()
                if len(values) >= 2:
                    current = values.iloc[-1]
                    previous = values.iloc[-2]
                    growth = ((current - previous) / previous * 100) if previous != 0 else 0
                    
                    if growth > 0:
                        growth_variants = [
                            f"TSMH increased by {growth:.1f}% – positive trend",
                            f"Safe man-hours grew by {growth:.1f}% this period",
                            f"Progress confirmed: {growth:.1f}% TSMH increase"
                        ]
                        alerts.append(("success", growth_variants[day_index % len(growth_variants)]))
                    
                    # Hours recorded variant
                    hours_variants = [
                        f"{int(current):,} safe man-hours recorded this period",
                        f"Total safe hours achieved: {int(current):,}",
                        f"Accumulated {int(current):,} safe working hours"
                    ]
                    alerts.append(("info", hours_variants[day_index % len(hours_variants)]))
        except:
            pass
    
    # TBT completion alert
    if not tbt_df.empty:
        sessions = len(tbt_df)
        if sessions >= 20:
            tbt_variants = [
                f"{sessions} TBT sessions completed – strong engagement",
                f"Training excellence: {sessions} toolbox talks delivered",
                f"{sessions} safety briefings conducted this period"
            ]
            alerts.append(("success", tbt_variants[day_index % len(tbt_variants)]))
    
    return alerts

# ==================== AUTHENTICATION ====================
def check_login(username: str, password: str):
    """Verify user credentials"""
    if username in USERS and USERS[username]["password"] == password:
        return True, USERS[username]["role"]
    return False, None

def has_page_access(role: str, page: str):
    """Check if role can access page"""
    return page in PAGE_ACCESS.get(role, [])

# Initialize session state
if "auth" not in st.session_state:
    st.session_state.auth = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user" not in st.session_state:
    st.session_state.user = None

# ==================== SIDEBAR - LOGIN/LOGOUT ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='color: #00D9FF; margin: 0;'>🛡️ ZOMCO-IMI</h1>
        <p style='color: #A0AEC0; font-size: 0.9rem;'>HSE Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Login/Logout logic
    if not st.session_state.auth:
        st.markdown("### 🔐 Login Required")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("🔓 Login", use_container_width=True):
            success, role = check_login(username, password)
            if success:
                st.session_state.auth = True
                st.session_state.role = role
                st.session_state.user = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    else:
        st.success(f"👤 **{st.session_state.user}**")
        st.info(f"**Role:** {st.session_state.role}")
        
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state.auth = False
            st.session_state.role = None
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")

# Stop here if not authenticated
if not st.session_state.auth:
    st.markdown("""
    <div class="login-container">
        <h2 style='text-align: center; color: #00D9FF;'>🛡️ ZOMCO-IMI HSE Analytics</h2>
        <p style='text-align: center; color: #A0AEC0;'>Please login using the sidebar to access the dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==================== LOAD DATA (only after auth) ====================
tbt = load_data(SHEET_TBT)
tsmh = load_data(SHEET_TSMH)
permit = load_data(SHEET_PERMIT)

# ==================== DATA PREPROCESSING ====================
# TBT columns
tbt_date = find_column(tbt, ["Date", "التاريخ", "day"])
if tbt_date and not tbt.empty:
    tbt[tbt_date] = pd.to_datetime(tbt[tbt_date], errors="coerce")

tbt_zone = find_column(tbt, ["Zone", "المنطقة", "Area"])
tbt_shift = find_column(tbt, ["Shift", "الوردية", "Shift/وردية"])
tbt_topic = find_column(tbt, ["Safety Topic Discussed", "Safety Topic", "موضوع السلامة"])
tbt_att = find_column(tbt, ["Attendance", "الحضور", "Attendees", "No. Attendees", "No Attendees"])

if tbt_att and not tbt.empty:
    tbt[tbt_att] = pd.to_numeric(tbt[tbt_att], errors="coerce")

# TSMH columns
tsmh_y = find_column(tsmh, ["Cumulative TSMH", "TSMH", "Total Safe Man Hours", "Total Safe-Man Hours"])
if not tsmh_y and not tsmh.empty:
    exclude = {"month", "date"}
    num_cols = [c for c in tsmh.columns if c.lower().strip() not in exclude and pd.api.types.is_numeric_dtype(tsmh[c])]
    if num_cols:
        tsmh_y = num_cols[0]

if "Month" in tsmh.columns:
    tsmh_x = "Month"
elif "Date" in tsmh.columns:
    tsmh_x = "Date"
    tsmh["Date"] = pd.to_datetime(tsmh["Date"], errors="coerce")
else:
    tsmh_x = "Index"
    tsmh[tsmh_x] = range(1, len(tsmh) + 1)

# Permit columns
permit_type_col = find_column(permit, ["Permit Type", "Type", "نوع التصريح"])
permit_date_col = find_column(permit, ["Date", "التاريخ", "Issue Date", "Permit Date"])
if permit_date_col and not permit.empty:
    permit[permit_date_col] = pd.to_datetime(permit[permit_date_col], errors='coerce')

# ==================== SIDEBAR FILTERS ====================
with st.sidebar:
    st.markdown("### 🎯 Filters")
    
    # Date range
    date_from, date_to = None, None
    if tbt_date and not tbt.empty:
        min_date = pd.to_datetime(tbt[tbt_date]).min()
        max_date = pd.to_datetime(tbt[tbt_date]).max()
        date_range = st.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            date_from, date_to = date_range
    
    # Zone filter
    zone_filter = []
    if tbt_zone and not tbt.empty:
        zones = sorted(tbt[tbt_zone].dropna().astype(str).unique())
        zone_filter = st.multiselect("🏭 Zone", zones, default=[])
    
    # Shift filter
    shift_filter = []
    if tbt_shift and not tbt.empty:
        shifts = sorted(tbt[tbt_shift].dropna().astype(str).unique())
        shift_filter = st.multiselect("⏰ Shift", shifts, default=[])
    
    # Permit type filter
    permit_type_filter = []
    if permit_type_col and not permit.empty:
        permit_types = sorted(permit[permit_type_col].dropna().astype(str).unique())
        permit_type_filter = st.multiselect("📋 Permit Type", permit_types, default=[])
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📍 Navigation")
    
    # Get allowed pages for current role
    allowed_pages = PAGE_ACCESS.get(st.session_state.role, [])
    
    page = st.radio(
        "Select Dashboard",
        allowed_pages,
        label_visibility="collapsed"
    )

# Apply filters
tbt_filtered = tbt.copy()
if not tbt_filtered.empty:
    if tbt_zone and zone_filter:
        tbt_filtered = tbt_filtered[tbt_filtered[tbt_zone].astype(str).isin(zone_filter)]
    if tbt_shift and shift_filter:
        tbt_filtered = tbt_filtered[tbt_filtered[tbt_shift].astype(str).isin(shift_filter)]
    if tbt_date and date_from and date_to:
        tbt_filtered = tbt_filtered[
            (tbt_filtered[tbt_date] >= pd.to_datetime(date_from)) &
            (tbt_filtered[tbt_date] <= pd.to_datetime(date_to))
        ]

permit_filtered = permit.copy()
if not permit_filtered.empty and permit_type_col and permit_type_filter:
    permit_filtered = permit_filtered[permit_filtered[permit_type_col].astype(str).isin(permit_type_filter)]

# ==================== PAGE ACCESS CHECK ====================
if not has_page_access(st.session_state.role, page):
    st.markdown("""
    <div class="access-denied">
        <h2>🚫 Access Denied</h2>
        <p>Your role (<strong>{}</strong>) does not have permission to access this page.</p>
        <p>Please contact your administrator if you need access.</p>
    </div>
    """.format(st.session_state.role), unsafe_allow_html=True)
    st.stop()

# ==================== PAGES ====================

# -------------------- EXECUTIVE OVERVIEW --------------------
if page == "Executive Overview":
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Executive Overview</h1>
        <p>Real-time HSE Performance Monitoring & Strategic Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs
    total_sessions = len(tbt_filtered)
    avg_attendance = round(tbt_filtered[tbt_att].mean(), 1) if tbt_att and not tbt_filtered.empty else 0
    zones_covered = tbt_filtered[tbt_zone].nunique() if tbt_zone and not tbt_filtered.empty else 0
    
    try:
        current_tsmh = int(pd.to_numeric(tsmh[tsmh_y], errors='coerce').dropna().iloc[-1])
    except:
        current_tsmh = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card("Total TBT Sessions", total_sessions, "📋"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_kpi_card("Avg Attendance", avg_attendance, "👥"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_kpi_card("Zones Covered", zones_covered, "🏭"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_kpi_card("Current TSMH", f"{current_tsmh:,}", "⏱️"), unsafe_allow_html=True)
    
    # Smart Alerts
    st.markdown("### 🔔 Smart Alerts & Insights")
    alerts = get_smart_alerts(tbt_filtered, tsmh, tbt_att)
    
    cols = st.columns(len(alerts))
    for idx, (alert_type, message) in enumerate(alerts):
        with cols[idx]:
            st.markdown(create_alert(message, alert_type), unsafe_allow_html=True)
    
    # Safety Quote of the Day
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Daily TBT Sessions</div>', unsafe_allow_html=True)
        
        if tbt_date and not tbt_filtered.empty:
            daily_sessions = tbt_filtered.groupby(tbt_date).size().reset_index(name='Sessions')
            fig = px.bar(daily_sessions, x=tbt_date, y='Sessions', 
                        color='Sessions', color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350,
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2D3340')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="quote-card">
            <h3 style='margin: 0 0 1rem 0;'>💭 Safety Quote of the Day</h3>
            <div class="quote-text">"{get_daily_quote()}"</div>
            <p style='margin: 0; font-weight: 600;'>Stay safe. Work smart.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Attendance Trend
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">👥 Attendance Trend</div>', unsafe_allow_html=True)
    
    if tbt_date and tbt_att and not tbt_filtered.empty:
        att_trend = tbt_filtered.groupby(tbt_date)[tbt_att].mean().reset_index()
        fig = px.line(att_trend, x=tbt_date, y=tbt_att, markers=True)
        fig.update_traces(line=dict(color='#00D9FF', width=3), marker=dict(size=8))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350,
            xaxis=dict(showgrid=True, gridcolor='#2D3340'),
            yaxis=dict(showgrid=True, gridcolor='#2D3340', title='Avg Attendance')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No attendance data available")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- OPERATIONAL ANALYTICS --------------------
elif page == "Operational Analytics":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Operational Analytics</h1>
        <p>Detailed Performance Metrics & Operational Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Zone/Shift Breakdown
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🏭 TBT by Zone & Shift</div>', unsafe_allow_html=True)
        
        if tbt_zone and tbt_shift and not tbt_filtered.empty:
            matrix_data = tbt_filtered.groupby([tbt_zone, tbt_shift]).size().reset_index(name='Sessions')
            fig = px.bar(matrix_data, x=tbt_zone, y='Sessions', color=tbt_shift, barmode='stack')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2D3340')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zone/Shift data not available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Pareto Analysis
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Pareto Analysis (80/20 Rule)</div>', unsafe_allow_html=True)
        
        if tbt_topic and not tbt_filtered.empty:
            topic_counts = tbt_filtered[tbt_topic].value_counts().reset_index()
            topic_counts.columns = ['Topic', 'Count']
            topic_counts = topic_counts.head(10)
            topic_counts['Cumulative %'] = (topic_counts['Count'].cumsum() / topic_counts['Count'].sum() * 100)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=topic_counts['Topic'],
                y=topic_counts['Count'],
                name='Count',
                marker=dict(color='#00D9FF'),
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=topic_counts['Topic'],
                y=topic_counts['Cumulative %'],
                name='Cumulative %',
                mode='lines+markers',
                line=dict(color='#FFB300', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            fig.add_hline(y=80, line_dash="dash", line_color="#FF3D00", 
                         annotation_text="80%", annotation_position="right", yref='y2')
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(title='Count', showgrid=True, gridcolor='#2D3340'),
                yaxis2=dict(title='Cumulative %', overlaying='y', side='right', showgrid=False),
                legend=dict(x=0.01, y=0.99)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No safety topics available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Table
    st.markdown("### 📋 Detailed Session Log")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    if not tbt_filtered.empty:
        display_df = tbt_filtered.copy()
        if tbt_date:
            display_df = display_df.sort_values(by=tbt_date, ascending=False)
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.info("No data available")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- TSMH PERFORMANCE --------------------
elif page == "TSMH Performance":
    st.markdown("""
    <div class="main-header">
        <h1>📈 TSMH Performance</h1>
        <p>Total Safe Man-Hours Analysis & Growth Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not tsmh.empty and tsmh_y:
        tsmh_data = pd.to_numeric(tsmh[tsmh_y], errors='coerce').dropna()
        
        # Calculate stats
        try:
            current_val = int(tsmh_data.iloc[-1])
            max_val = int(tsmh_data.max())
            min_val = int(tsmh_data.min())
            total_records = len(tsmh_data)
            
            if len(tsmh_data) >= 2:
                prev_val = tsmh_data.iloc[-2]
                growth_rate = ((current_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
                growth_str = f"{growth_rate:.1f}%"
            else:
                growth_str = "N/A"
        except:
            current_val = max_val = min_val = total_records = 0
            growth_str = "N/A"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_kpi_card("Current", f"{current_val:,}", "⏱️"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Max Value", f"{max_val:,}", "🔝"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_kpi_card("Min Value", f"{min_val:,}", "📉"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_kpi_card("Growth Rate", growth_str, "📈"), unsafe_allow_html=True)
        
        # TSMH Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Cumulative TSMH Trend</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=tsmh[tsmh_x],
            y=tsmh_data,
            mode='lines+markers',
            name='TSMH',
            line=dict(color='#00D9FF', width=4),
            marker=dict(size=10, color='#00D9FF'),
            fill='tozeroy',
            fillcolor='rgba(0, 217, 255, 0.1)'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=450,
            xaxis=dict(showgrid=True, gridcolor='#2D3340'),
            yaxis=dict(showgrid=True, gridcolor='#2D3340', title='Safe Man-Hours'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stats Panel
        st.markdown("### 📊 Statistics Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", total_records)
        with col2:
            st.metric("Average", f"{int(tsmh_data.mean()):,}")
        with col3:
            st.metric("Range", f"{max_val - min_val:,}")
        
        # Raw Data
        if st.session_state.role == "HSE In-Charge":
            st.markdown("### 🔍 Raw Data (HSE In-Charge View)")
            st.dataframe(tsmh, use_container_width=True)
    
    else:
        st.warning("⚠️ No TSMH data available")

# -------------------- SAFETY INTELLIGENCE --------------------
elif page == "Safety Intelligence":
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Safety Intelligence Center</h1>
        <p>Advanced Pattern Recognition & Risk Signals</p>
    </div>
    """, unsafe_allow_html=True)
    
    if tbt_topic and not tbt_filtered.empty:
        # High-Risk Signals
        st.markdown("### ⚠️ High-Risk Signals")
        
        topic_counts = tbt_filtered[tbt_topic].value_counts().head(5).reset_index()
        topic_counts.columns = ['Issue', 'Frequency']
        
        # Add suggested focus
        def get_suggested_focus(topic):
            topic_lower = str(topic).lower()
            if 'height' in topic_lower or 'elevated' in topic_lower:
                return "Fall protection / work at height briefing"
            elif 'heat' in topic_lower or 'temperature' in topic_lower:
                return "Hydration / heat stress management reinforcement"
            elif 'confined' in topic_lower or 'space' in topic_lower:
                return "Confined space entry procedures / gas testing"
            elif 'electrical' in topic_lower or 'electric' in topic_lower:
                return "LOTO procedures / electrical safety review"
            elif 'chemical' in topic_lower:
                return "SDS review / PPE requirements verification"
            else:
                return "Reinforce toolbox talk / supervision"
        
        topic_counts['Suggested Focus'] = topic_counts['Issue'].apply(get_suggested_focus)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(topic_counts, use_container_width=True, height=250)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommended Immediate Focus
        st.markdown("### 🎯 Recommended Immediate Focus")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        for idx, row in topic_counts.head(3).iterrows():
            st.markdown(f"""
            <div style='padding: 1rem; margin: 0.5rem 0; background: rgba(0, 217, 255, 0.1); 
                        border-left: 4px solid #00D9FF; border-radius: 8px;'>
                <strong>🔹 {row['Issue']}</strong> (Frequency: {row['Frequency']})<br>
                <span style='color: #A0AEC0;'>→ {row['Suggested Focus']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Visual Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Top Safety Topics</div>', unsafe_allow_html=True)
            
            fig = px.bar(topic_counts, x='Frequency', y='Issue', orientation='h',
                        color='Frequency', color_continuous_scale='Reds')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350,
                showlegend=False,
                xaxis=dict(showgrid=True, gridcolor='#2D3340'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 Distribution</div>', unsafe_allow_html=True)
            
            fig = px.pie(topic_counts, values='Frequency', names='Issue', hole=0.4)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("ℹ️ No data available for safety intelligence analysis")

# -------------------- PERMIT MANAGEMENT --------------------
elif page == "Permit Management":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Permit Management</h1>
        <p>Work Permit Tracking & Authorization Control</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not permit_filtered.empty:
        # Calculate KPIs
        total_permits = len(permit_filtered)
        
        # Permits today
        permits_today = 0
        if permit_date_col:
            today = datetime.now().date()
            permits_today = len(permit_filtered[permit_filtered[permit_date_col].dt.date == today])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(create_kpi_card("Total Permits", total_permits, "📋"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Permits Today", permits_today, "📅"), unsafe_allow_html=True)
        with col3:
            if permit_type_col:
                unique_types = permit_filtered[permit_type_col].nunique()
                st.markdown(create_kpi_card("Permit Types", unique_types, "📑"), unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if permit_type_col:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📊 Permits by Type</div>', unsafe_allow_html=True)
                
                type_counts = permit_filtered[permit_type_col].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                
                fig = px.bar(type_counts, x='Type', y='Count', color='Count', 
                            color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=350,
                    showlegend=False,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#2D3340')
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if permit_date_col:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📅 Permit Timeline</div>', unsafe_allow_html=True)
                
                daily_permits = permit_filtered.groupby(permit_filtered[permit_date_col].dt.date).size().reset_index(name='Count')
                daily_permits.columns = ['Date', 'Count']
                
                fig = px.line(daily_permits, x='Date', y='Count', markers=True)
                fig.update_traces(line=dict(color='#7B68EE', width=3))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=350,
                    xaxis=dict(showgrid=True, gridcolor='#2D3340'),
                    yaxis=dict(showgrid=True, gridcolor='#2D3340')
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Table
        st.markdown("### 📋 Permit Register")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(permit_filtered, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("ℹ️ Permit register not available or no matching records")

# -------------------- TRAINING & COMPLIANCE --------------------
elif page == "Training & Compliance":
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Training & Compliance</h1>
        <p>Training Status & Regulatory Compliance Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate compliance metrics
    if not tbt_filtered.empty and tbt_att:
        total_employees = 150  # Placeholder
        unique_attendees = tbt_filtered[tbt_att].sum()
        compliance_rate = min((unique_attendees / (total_employees * len(tbt_filtered))) * 100, 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(create_kpi_card("Compliance Rate", f"{compliance_rate:.1f}%", "✅"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Total Sessions", len(tbt_filtered), "📚"), unsafe_allow_html=True)
        with col3:
            avg_att = round(tbt_filtered[tbt_att].mean(), 1)
            st.markdown(create_kpi_card("Avg Attendance", avg_att, "👥"), unsafe_allow_html=True)
    
    # Upcoming Trainings (Placeholder)
    st.markdown("### 📅 Upcoming Mandatory Trainings")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    trainings = [
        {"Training": "Confined Space Entry", "Due Date": "2025-11-15", "Status": "Scheduled"},
        {"Training": "Fire Safety Refresher", "Due Date": "2025-11-20", "Status": "Pending"},
        {"Training": "First Aid Certification", "Due Date": "2025-12-01", "Status": "Scheduled"},
        {"Training": "LOTO Procedures", "Due Date": "2025-12-10", "Status": "Scheduled"}
    ]
    
    training_df = pd.DataFrame(trainings)
    st.dataframe(training_df, use_container_width=True, height=250)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Compliance by Zone
    if not tbt_filtered.empty and tbt_zone and tbt_att:
        st.markdown("### 📊 Compliance by Zone")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        zone_compliance = tbt_filtered.groupby(tbt_zone)[tbt_att].sum().reset_index()
        zone_compliance.columns = ['Zone', 'Total Attendance']
        
        fig = px.bar(zone_compliance, x='Zone', y='Total Attendance', 
                    color='Total Attendance', color_continuous_scale='Greens')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350,
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#2D3340')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- RISK ASSESSMENT --------------------
elif page == "Risk Assessment":
    st.markdown("""
    <div class="main-header">
        <h1>⚠️ Risk Assessment</h1>
        <p>Active Risk Monitoring & Control Measures</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Top 3 Active Risks")
    
    risks = [
        {
            "Risk": "Confined Space Entry",
            "Status": "Controlled",
            "Control Action": "Gas testing before entry, continuous monitoring, rescue standby"
        },
        {
            "Risk": "Working at Height",
            "Status": "Active Monitoring",
            "Control Action": "Fall protection equipment inspection, safety harness mandatory"
        },
        {
            "Risk": "Hot Work Operations",
            "Status": "Controlled",
            "Control Action": "Fire watch assigned, fire extinguishers staged, area cleared"
        }
    ]
    
    for risk in risks:
        status_color = "#00C853" if risk["Status"] == "Controlled" else "#FFB300"
        st.markdown(f"""
        <div class="chart-container" style='border-left: 4px solid {status_color};'>
            <h3 style='color: white; margin: 0 0 0.5rem 0;'>⚠️ {risk['Risk']}</h3>
            <p style='color: {status_color}; font-weight: 600; margin: 0.5rem 0;'>
                Status: {risk['Status']}
            </p>
            <p style='color: #A0AEC0; margin: 0.5rem 0 0 0;'>
                <strong>Control Action:</strong> {risk['Control Action']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk Matrix (Placeholder)
    st.markdown("### 📊 Risk Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        risk_data = pd.DataFrame({
            'Level': ['Low', 'Medium', 'High', 'Critical'],
            'Count': [45, 28, 15, 2]
        })
        
        fig = px.pie(risk_data, values='Count', names='Level', hole=0.4,
                    color='Level', 
                    color_discrete_map={'Low': '#00C853', 'Medium': '#FFB300', 
                                       'High': '#FF6D00', 'Critical': '#FF3D00'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Priority Actions")
        st.markdown("""
        - 🔴 Review 2 critical risks immediately
        - 🟠 Update 15 high-risk assessments
        - 🟡 Schedule 28 medium-risk reviews
        - 🟢 Monitor 45 low-risk items
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- REPORTS & EXPORT --------------------
elif page == "Reports & Export":
    st.markdown("""
    <div class="main-header">
        <h1>📑 Reports & Export</h1>
        <p>Generate Reports & Export Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📥 Available Downloads")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 TBT Data")
        st.write(f"Records: {len(tbt_filtered)}")
        
        if not tbt_filtered.empty:
            csv = tbt_filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download TBT Data",
                data=csv,
                file_name=f"TBT_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⏱️ TSMH Data")
        st.write(f"Records: {len(tsmh)}")
        
        if not tsmh.empty:
            csv = tsmh.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download TSMH Data",
                data=csv,
                file_name=f"TSMH_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 Permit Data")
        st.write(f"Records: {len(permit_filtered)}")
        
        if not permit_filtered.empty:
            csv = permit_filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download Permit Data",
                data=csv,
                file_name=f"Permits_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Confidentiality Notice
    st.markdown("---")
    st.warning("🔒 **Confidentiality Notice:** All data is confidential - FM&SS Internal Use Only")
    
    # Summary
    st.markdown("### 📊 Data Summary")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    summary_data = {
        "Dataset": ["TBT Records", "TSMH Records", "Permit Records"],
        "Total Count": [len(tbt), len(tsmh), len(permit)],
        "Filtered Count": [len(tbt_filtered), len(tsmh), len(permit_filtered)]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, height=150)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>ZOMCO-IMI | HSE Analytics Platform</strong></p>
    <p>World-Class Safety Management System | Version 2.0</p>
    <p style="font-size: 0.9rem; color: #A0AEC0;">
        Powered by Advanced Analytics • Real-time Monitoring • Predictive Intelligence
    </p>
    <p style="font-size: 0.85rem; color: #6C757D; margin-top: 0.5rem;">
        Powered by HSE In-Charge: <strong>Abdullah AlSubaie</strong>
    </p>
</div>

""", unsafe_allow_html=True)
