
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="JourneyIQ | Customer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');
:root{--navy:#17366f;--blue:#1769e8;--ink:#15264a;--muted:#71809a;--line:#e4ebf6;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:#f5f8fd;color:var(--ink);}

/* Remove Streamlit's fixed top toolbar so it cannot cover the app header.
   The dashboard keeps its own JourneyIQ header and controls. */
header[data-testid="stHeader"],
[data-testid="stHeader"]{display:none !important;height:0 !important;min-height:0 !important;}
[data-testid="stToolbar"]{display:none !important;height:0 !important;}
[data-testid="stAppViewBlockContainer"],
section.main > div.block-container,
.block-container{max-width:1600px !important;padding:1.1rem 1.15rem 2rem !important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102c62 0%,#1d438c 72%,#3e82e8 100%);border-right:0;}
[data-testid="stSidebar"] *{color:#f4f7ff !important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#d5e2ff !important;}
[data-testid="stSidebar"] div[role="radiogroup"] label{padding:8px 10px;margin:4px 0;border:0;border-radius:9px;background:transparent;}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(255,255,255,.12);}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:#1260c9;box-shadow:0 3px 10px #0b255b55;}
[data-testid="stSidebar"] [data-testid="stRadio"]>label{font-weight:700;color:#fff!important;}
.main-title{font-family:'Manrope',sans-serif;font-size:27px;font-weight:800;color:#172b55;}
.subtitle{color:#71809a;font-size:13px;}
.section-title{font-family:'Manrope',sans-serif;font-size:18px;font-weight:800;color:#172b55;}
div[data-testid="stMetric"]{background:#fff;border:1px solid #e0e8f5;border-radius:12px;padding:12px 15px;box-shadow:0 3px 10px #193a7010;}
div[data-testid="stMetricLabel"]{color:#6c7890;font-weight:600;}
div[data-testid="stMetricValue"]{color:#17264b;font-family:'Manrope',sans-serif;font-weight:800;}
div[data-testid="stPlotlyChart"]{background:#fff;border:1px solid #e1e9f5;border-radius:12px;padding:5px 8px;box-shadow:0 3px 10px #193a7009;}
.journey-table{width:100%;border-collapse:separate;border-spacing:0;margin-bottom:12px;background:white;border:1px solid #e2eaf6;border-radius:10px;overflow:hidden;font-size:12px;}
.journey-table th{background:#edf3fc;color:#23385f;padding:9px;text-align:left;font-weight:700;}
.journey-table td{padding:8px 9px;border-bottom:1px solid #edf1f7;color:#43516d;}
.journey-table tr:last-child td{border-bottom:0;}
.journey-table tr:hover{background:#f5f9ff;}
.stButton button,.stDownloadButton button{border-radius:8px;border:1px solid #d8e3f5;background:#fff;color:#145bc3;font-weight:700;}
.stButton button:hover,.stDownloadButton button:hover{background:#edf5ff;color:#145bc3;border-color:#9fc2f5;}
div[data-testid="stAlert"]{border-radius:10px;}
hr{border-color:#e6edf7;}
.footer{color:#96a1b5;font-size:11px;text-align:center;padding:16px 0 0;}
.hero-title{font-family:'Manrope',sans-serif;font-size:25px;font-weight:800;color:#172b55;margin:0;}
.hero-sub{font-size:12px;color:#71809a;margin-top:2px;}
.kpi{background:#fff;border:1px solid #dfe8f5;border-radius:12px;padding:13px 14px;min-height:78px;box-shadow:0 4px 12px #193a7010;display:flex;gap:12px;align-items:center;}
.kpi-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:19px;}
.kpi-label{font-size:11px;color:#6c7890;font-weight:600;}
.kpi-value{font-family:'Manrope',sans-serif;font-size:23px;font-weight:800;color:#17264b;line-height:1.25;}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

RAW_DIR = Path("data/raw/starter")
PROCESSED_DIR = Path("data/processed")

METRICS_FILE = PROCESSED_DIR / "session_metrics.csv"
FUNNEL_FILE = PROCESSED_DIR / "funnel_metrics.csv"
CHANNEL_FILE = PROCESSED_DIR / "channel_performance.csv"

ANOMALY_FILE = PROCESSED_DIR / "detected_anomalies.csv"
IDENTITY_ANOMALY_FILE = PROCESSED_DIR / "identity_anomalies.csv"
BENCHMARK_FILE = PROCESSED_DIR / "benchmark_results.csv"

SESSIONS_FILE = RAW_DIR / "sessions.csv"
EVENTS_FILE = RAW_DIR / "journey_events.csv"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def show_table(data):

    if data.empty:
        st.info("No data available.")
        return

    html = data.to_html(
        index=False,
        border=0,
        classes="journey-table",
        escape=True
    )

    st.markdown(html, unsafe_allow_html=True)


def load_csv(path):

    if path.exists():
        return pd.read_csv(path)

    return pd.DataFrame()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

required_files = [
    METRICS_FILE,
    FUNNEL_FILE
]

missing_files = [
    str(file)
    for file in required_files
    if not file.exists()
]

if missing_files:

    st.error("Required analytics files are missing:")

    for file in missing_files:
        st.write(f"- {file}")

    st.info(
        "Run the analytics pipeline before opening the dashboard."
    )

    st.stop()


metrics = load_csv(METRICS_FILE)
funnel = load_csv(FUNNEL_FILE)
channel = load_csv(CHANNEL_FILE)

sessions = load_csv(SESSIONS_FILE)
raw_events = load_csv(EVENTS_FILE)


# Load both types of anomalies

anomaly_parts = []

for path in [
    ANOMALY_FILE,
    IDENTITY_ANOMALY_FILE
]:

    current = load_csv(path)

    if not current.empty:

        current["source"] = (
            "Identity stitching"
            if path == IDENTITY_ANOMALY_FILE
            else "Journey monitoring"
        )

        anomaly_parts.append(current)


if anomaly_parts:

    issues = pd.concat(
        anomaly_parts,
        ignore_index=True
    )

else:

    issues = pd.DataFrame()


# --------------------------------------------------
# PREPARE SESSION DATA
# --------------------------------------------------

if not metrics.empty and not sessions.empty:

    session_details = sessions[
        [
            "session_id",
            "channel",
            "is_bot",
            "lifecycle_state"
        ]
    ].drop_duplicates(
        subset=["session_id"]
    )

    explorer_data = metrics.merge(
        session_details,
        on="session_id",
        how="left"
    )

else:

    explorer_data = metrics.copy()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

head_left, head_right = st.columns([5, 2])
with head_left:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;padding:3px 0 8px;">'
        '<div style="font-size:27px;color:#1674e8;">▥</div>'
        '<div><div style="font-family:Manrope,sans-serif;font-size:22px;font-weight:800;color:#17366f;">JourneyIQ</div>'
        '<div style="font-size:10px;color:#71809a;">Cross-channel customer journey analytics and friction detection</div></div></div>',
        unsafe_allow_html=True
    )
with head_right:
    top_a, top_b, top_c = st.columns([2.1, 0.8, 1.1])
    with top_a:
        st.selectbox(" ", ["All Periods"], label_visibility="collapsed", key="period_selector")
    with top_b:
        if st.button("↻", help="Refresh dashboard", use_container_width=True):
            st.rerun()
    with top_c:
        st.download_button(
            "⬇ Export",
            data=metrics.to_csv(index=False),
            file_name="journeyiq_session_metrics.csv",
            mime="text/csv",
            key="export_metrics_top",
            use_container_width=True
        )

st.markdown("---")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding:10px 2px 20px;">
      <div style="display:flex;align-items:center;gap:9px;">
        <div style="font-size:25px;color:#53a6ff;">▥</div>
        <div style="font-family:Manrope,sans-serif;font-size:21px;font-weight:800;color:white;">JourneyIQ</div>
      </div>
    </div>
    """, unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Funnel Analytics",
        "Channel Performance",
        "Anomaly Detection",
        "Session Explorer",
        "Performance Benchmark"
    ]
)

st.sidebar.divider()

st.sidebar.caption("JourneyIQ Analytics Platform")

st.sidebar.caption("Customer journey intelligence")


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.markdown('<div class="hero-title">Business Overview</div><div class="hero-sub">Monitor customer journeys and identify conversion friction.</div>', unsafe_allow_html=True)

    total_sessions = len(metrics)

    conversions = (
        int(metrics["converted"].fillna(False).sum())
        if "converted" in metrics.columns
        else 0
    )

    abandoned = total_sessions - conversions

    conversion_rate = (
        conversions / total_sessions * 100
        if total_sessions
        else 0
    )

    abandonment_rate = (
        abandoned / total_sessions * 100
        if total_sessions
        else 0
    )

    total_issues = len(issues)

    # KPI Cards

    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("👥", "#e4f3ff", "Eligible Sessions", f"{total_sessions:,}"),
        ("🛒", "#eeeaff", "Converted Sessions", f"{conversions:,}"),
        ("◎", "#e2fbef", "Conversion Rate", f"{conversion_rate:.2f}%"),
        ("⚠", "#ffedf0", "Detected Issues", f"{total_issues:,}")
    ]
    for col, (symbol, tint, label, value) in zip([col1,col2,col3,col4], cards):
        with col:
            st.markdown(
                f'<div class="kpi"><div class="kpi-icon" style="background:{tint};">{symbol}</div>'
                f'<div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div></div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:

        st.subheader("Customer Journey Funnel")

        if not funnel.empty:

            fig = px.funnel(
                funnel,
                x="sessions",
                y="stage",
                title="Conversion Funnel"
            )

            fig.update_layout(
                template="plotly_white", height=300, margin=dict(l=10,r=10,t=25,b=10),
                font=dict(family="DM Sans", color="#24365f"),
                paper_bgcolor="white", plot_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("Funnel data unavailable.")

    with right:

        st.subheader("Conversion vs Abandonment")

        conversion_data = pd.DataFrame({
            "Status": [
                "Converted",
                "Abandoned"
            ],
            "Sessions": [
                conversions,
                abandoned
            ]
        })

        fig = px.pie(
            conversion_data,
            names="Status",
            values="Sessions",
            hole=0.55,
            title="Session Outcomes"
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Channel Performance Snapshot")

    if not channel.empty:

        show_table(channel)

    else:

        st.info(
            "Channel performance file not available."
        )

    st.subheader("Recent Detected Issues")

    if not issues.empty:

        show_table(issues.head(10))

    else:

        st.success("No anomalies detected.")


# --------------------------------------------------
# FUNNEL ANALYTICS PAGE
# --------------------------------------------------

elif page == "Funnel Analytics":

    st.subheader("Customer Journey Funnel")

    if funnel.empty:

        st.warning("No funnel data available.")

    else:

        fig = px.funnel(
            funnel,
            x="sessions",
            y="stage",
            title="Customer Conversion Journey"
        )

        fig.update_layout(
            template="plotly_white",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Stage-wise Drop-off")

        show_table(funnel)

        if len(funnel) > 1:

            dropoff = funnel.iloc[1:].copy()

            fig = px.bar(
                dropoff,
                x="stage",
                y="dropoff_from_previous_pct",
                title="Drop-off Percentage by Stage",
                text="dropoff_from_previous_pct"
            )

            fig.update_layout(
                template="plotly_white",
                yaxis_title="Drop-off (%)",
                xaxis_title="Journey Stage"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# --------------------------------------------------
# CHANNEL PERFORMANCE PAGE
# --------------------------------------------------

elif page == "Channel Performance":

    st.subheader("Channel Performance Analytics")

    if channel.empty:

        st.warning(
            "Channel performance data not found. "
            "Run python -m src.analytics first."
        )

    else:

        st.caption(
            "Compare conversion and abandonment across customer channels."
        )

        required_columns = [
            "channel",
            "total_sessions",
            "converted_sessions",
            "abandoned_sessions",
            "conversion_rate_pct",
            "abandonment_rate_pct"
        ]

        if all(
            col in channel.columns
            for col in required_columns
        ):

            best_channel = channel.sort_values(
                "conversion_rate_pct",
                ascending=False
            ).iloc[0]

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Total Channels",
                len(channel)
            )

            c2.metric(
                "Best Conversion Channel",
                str(best_channel["channel"])
            )

            c3.metric(
                "Highest Conversion Rate",
                f'{best_channel["conversion_rate_pct"]:.2f}%'
            )

            st.divider()

            st.subheader("Channel Conversion Rate")

            fig = px.bar(
                channel,
                x="channel",
                y="conversion_rate_pct",
                color="channel",
                text="conversion_rate_pct",
                title="Conversion Rate by Channel"
            )

            fig.update_layout(
                template="plotly_white",
                yaxis_title="Conversion Rate (%)",
                xaxis_title="Channel",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Sessions by Channel")

            fig = px.bar(
                channel,
                x="channel",
                y=[
                    "converted_sessions",
                    "abandoned_sessions"
                ],
                barmode="group",
                title="Converted vs Abandoned Sessions"
            )

            fig.update_layout(
                template="plotly_white",
                yaxis_title="Number of Sessions"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Detailed Channel Metrics")

            show_table(channel)

        else:

            st.error(
                "The channel performance CSV does not contain "
                "all expected columns."
            )


# --------------------------------------------------
# ANOMALY DETECTION PAGE
# --------------------------------------------------

elif page == "Anomaly Detection":

    st.subheader("Friction and Anomaly Detection")

    if issues.empty:

        st.success("No anomalies detected.")

    else:

        total = len(issues)

        high = (
            issues["severity"].astype(str).str.lower()
            == "high"
        ).sum()

        medium = (
            issues["severity"].astype(str).str.lower()
            == "medium"
        ).sum()

        low = (
            issues["severity"].astype(str).str.lower()
            == "low"
        ).sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Issues", total)

        c2.metric("High Severity", int(high))

        c3.metric("Medium Severity", int(medium))

        c4.metric("Low Severity", int(low))

        st.divider()

        st.subheader("Anomalies by Type")

        issue_summary = (
            issues.groupby("issue_type")
            .size()
            .reset_index(name="count")
        )

        fig = px.bar(
            issue_summary,
            x="issue_type",
            y="count",
            color="issue_type",
            title="Detected Anomalies"
        )

        fig.update_layout(
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Anomaly Details")

        show_table(issues)


# --------------------------------------------------
# SESSION EXPLORER PAGE
# --------------------------------------------------

elif page == "Session Explorer":

    st.subheader("Customer Session Explorer")

    if explorer_data.empty:

        st.info("No session data available.")

    else:

        filtered = explorer_data.copy()

        # Channel filter

        if "channel" in filtered.columns:

            channels = sorted(
                filtered["channel"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_channels = st.multiselect(
                "Filter by channel",
                channels,
                default=channels
            )

            filtered = filtered[
                filtered["channel"].isin(selected_channels)
            ]

        # Conversion filter

        conversion_filter = st.selectbox(
            "Conversion status",
            [
                "All",
                "Converted",
                "Not Converted"
            ]
        )

        if conversion_filter == "Converted":

            filtered = filtered[
                filtered["converted"] == True
            ]

        elif conversion_filter == "Not Converted":

            filtered = filtered[
                filtered["converted"] == False
            ]

        st.write(
            f"Showing {len(filtered)} sessions"
        )

        show_table(filtered.head(100))

        # Individual session details

        st.divider()

        st.subheader("View Individual Journey")

        if not filtered.empty:

            selected_session = st.selectbox(
                "Select Session ID",
                filtered["session_id"].tolist()
            )

            if not raw_events.empty:

                view = raw_events[
                    raw_events["session_id"] == selected_session
                ].copy()

                if not view.empty:

                    if "event_timestamp" in view.columns:

                        view["event_timestamp"] = pd.to_datetime(
                            view["event_timestamp"],
                            utc=True
                        )

                        view = view.sort_values(
                            "event_timestamp"
                        )

                    st.write("Customer Journey Events")

                    show_table(view)

                else:

                    st.info(
                        "No events found for this session."
                    )

            else:

                st.warning(
                    "Journey events file not found."
                )

        else:

            st.info(
                "No sessions match the selected filters."
            )


# --------------------------------------------------
# PERFORMANCE BENCHMARK PAGE
# --------------------------------------------------

elif page == "Performance Benchmark":

    st.subheader("Pipeline Performance Benchmark")

    st.caption(
        "Compare execution time and Python memory usage "
        "for each JourneyIQ module."
    )

    benchmark = load_csv(BENCHMARK_FILE)

    if benchmark.empty:

        st.warning(
            "Benchmark results are not available yet."
        )

        st.code(
            "python -m src.benchmark",
            language="powershell"
        )

        st.info(
            "Run the benchmark command from your project folder, "
            "then refresh this dashboard."
        )

    else:

        required_benchmark_columns = [
            "module",
            "execution_time_seconds",
            "peak_memory_mb",
            "status"
        ]

        missing_benchmark_columns = [
            column
            for column in required_benchmark_columns
            if column not in benchmark.columns
        ]

        if missing_benchmark_columns:

            st.error(
                "The benchmark CSV is missing required columns: "
                + ", ".join(missing_benchmark_columns)
            )

        else:

            benchmark["execution_time_seconds"] = pd.to_numeric(
                benchmark["execution_time_seconds"],
                errors="coerce"
            )

            benchmark["peak_memory_mb"] = pd.to_numeric(
                benchmark["peak_memory_mb"],
                errors="coerce"
            )

            benchmark["status"] = (
                benchmark["status"]
                .astype(str)
                .str.upper()
            )

            successful = int(
                (benchmark["status"] == "SUCCESS").sum()
            )

            failed = int(
                (benchmark["status"] == "FAILED").sum()
            )

            total_execution_time = (
                benchmark["execution_time_seconds"].sum()
            )

            k1, k2, k3, k4 = st.columns(4)

            k1.metric(
                "Modules Benchmarked",
                len(benchmark)
            )

            k2.metric(
                "Successful Modules",
                successful
            )

            k3.metric(
                "Failed Modules",
                failed
            )

            k4.metric(
                "Summed Execution Time",
                f"{total_execution_time:.2f} sec"
            )

            st.caption(
                f"Sum of measured module execution times: "
                f"{total_execution_time:.4f} seconds. "
                "Peak memory values are measured separately "
                "for each module and should not be added together."
            )

            st.divider()

            left, right = st.columns(2)

            # Execution time chart

            with left:

                st.subheader("Execution Time by Module")

                time_data = benchmark.dropna(
                    subset=["execution_time_seconds"]
                )

                if not time_data.empty:

                    fig = px.bar(
                        time_data,
                        x="module",
                        y="execution_time_seconds",
                        color="status",
                        text="execution_time_seconds",
                        title="Execution Time (seconds)"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        xaxis_title="Module",
                        yaxis_title="Seconds"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Execution-time measurements are unavailable."
                    )

            # Memory usage chart

            with right:

                st.subheader("Peak Python Memory by Module")

                memory_data = benchmark.dropna(
                    subset=["peak_memory_mb"]
                )

                if not memory_data.empty:

                    fig = px.bar(
                        memory_data,
                        x="module",
                        y="peak_memory_mb",
                        color="status",
                        text="peak_memory_mb",
                        title="Peak Python Memory (MB)"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        xaxis_title="Module",
                        yaxis_title="Megabytes"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Memory measurements are unavailable."
                    )

            # Benchmark details

            st.subheader("Module Benchmark Details")

            show_table(benchmark)

            # Failed module details

            if "error" in benchmark.columns:

                failed_rows = benchmark[
                    (benchmark["status"] == "FAILED")
                    & benchmark["error"]
                    .fillna("")
                    .astype(str)
                    .ne("")
                ]

                if not failed_rows.empty:

                    st.subheader("Failure Details")

                    show_table(
                        failed_rows[
                            ["module", "error"]
                        ]
                    )

            st.caption(
                "Memory values represent Python-tracked allocations "
                "from tracemalloc; they are not total "
                "operating-system process memory."
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "JourneyIQ | Cross-channel Customer Journey Analytics"
)
