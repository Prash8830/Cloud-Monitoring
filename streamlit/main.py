import streamlit as st
import pandas as pd
import json
import os
import re
from pathlib import Path
from datetime import datetime

# Try to import mermaid, but make it optional
try:
    import streamlit_mermaid as stmd
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="🚨 Incident Commander Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
    }
    .status-high { color: #ff4b4b; font-weight: bold; }
    .status-medium { color: #ffa600; font-weight: bold; }
    .status-low { color: #00cc66; font-weight: bold; }
    .finding-card {
        background: #f8f9fa;
        padding: 10px;
        border-left: 4px solid #667eea;
        margin: 5px 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# DATA PATHS
# -------------------------------
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# -------------------------------
# DATA LOADING FUNCTIONS
# -------------------------------
@st.cache_data(ttl=60)
def load_json_file(filepath):
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
        return None

@st.cache_data(ttl=60)
def load_logs():
    """Load logs data."""
    return load_json_file(DATA_DIR / "logs.json")

@st.cache_data(ttl=60)
def load_metrics():
    """Load metrics data."""
    return load_json_file(DATA_DIR / "metrics.json")

@st.cache_data(ttl=60)
def load_deployments():
    """Load deployments data."""
    return load_json_file(DATA_DIR / "deployments.json")

def get_report_files():
    """Get list of report files."""
    if REPORTS_DIR.exists():
        return sorted(REPORTS_DIR.glob("*.txt"), reverse=True)
    return []

def parse_report(filepath):
    """Parse a report file and extract sections."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading report: {e}"

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def render_markdown_with_mermaid(content):
    """Render markdown and Mermaid diagrams."""
    if MERMAID_AVAILABLE:
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)
        modified_content = re.sub(mermaid_pattern, '', content, flags=re.DOTALL)
        st.markdown(modified_content)
        for mermaid_code in mermaid_blocks:
            stmd.st_mermaid(mermaid_code)
    else:
        st.markdown(content)

def severity_color(level):
    """Return color based on severity level."""
    colors = {
        'CRITICAL': '🔴',
        'ERROR': '🔴',
        'WARN': '🟡',
        'WARNING': '🟡',
        'INFO': '🟢',
        'DEBUG': '⚪'
    }
    return colors.get(level.upper(), '⚪')

def risk_badge(risk_level):
    """Return styled risk badge."""
    if 'high' in risk_level.lower():
        return f"🔴 **{risk_level.upper()}**"
    elif 'medium' in risk_level.lower():
        return f"🟡 **{risk_level.upper()}**"
    else:
        return f"🟢 **{risk_level.upper()}**"

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("🚨 Incident Commander")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📜 Logs Explorer", "📈 Metrics", "🚀 Deployments", "📄 Reports", "🏗️ Architecture"]
)

# -------------------------------
# PAGE 1: DASHBOARD
# -------------------------------
if page == "📊 Dashboard":
    st.title("🚨 Incident Commander Dashboard")
    st.markdown("*Real-time incident analysis and root cause detection*")
    
    # Load all data
    logs = load_logs() or []
    metrics = load_metrics() or {}
    deployments = load_deployments() or []
    
    # KPI Row
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate KPIs from data
    error_count = sum(1 for log in logs if log.get('level') in ['ERROR', 'CRITICAL']) if logs else 0
    warn_count = sum(1 for log in logs if log.get('level') == 'WARN') if logs else 0
    
    metrics_data = metrics.get('metrics', {})
    error_rate = metrics_data.get('error_rate', {}).get('during_incident', 0)
    latency = metrics_data.get('latency_p95', {}).get('during_incident', 0)
    cpu_max = metrics_data.get('cpu_usage', {}).get('max', 0)
    
    col1.metric("🔴 Errors", error_count, delta=f"+{error_count}" if error_count > 0 else None, delta_color="inverse")
    col2.metric("🟡 Warnings", warn_count)
    col3.metric("📈 Error Rate", f"{error_rate}%", delta=f"+{error_rate-0.1:.1f}%" if error_rate > 0.1 else None, delta_color="inverse")
    col4.metric("⏱️ P95 Latency", f"{latency}ms")
    col5.metric("💻 CPU Max", f"{cpu_max}%")
    
    st.markdown("---")
    
    # Two column layout
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("📜 Recent Error Logs")
        if logs:
            error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL', 'WARN']]
            for log in error_logs[:5]:
                severity = severity_color(log.get('level', 'INFO'))
                st.markdown(f"""
                <div class="finding-card">
                    {severity} <strong>{log.get('level', 'INFO')}</strong> | {log.get('timestamp', 'N/A')}<br/>
                    <em>{log.get('service', 'unknown')}</em>: {log.get('message', 'No message')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No logs available")
    
    with right_col:
        st.subheader("🚀 Recent Deployments")
        if deployments:
            for deploy in deployments[:3]:
                status_icon = "✅" if deploy.get('status') == 'success' else "❌"
                st.markdown(f"""
                <div class="finding-card">
                    {status_icon} <strong>{deploy.get('deployment_id', 'N/A')}</strong> | {deploy.get('deployed_at', 'N/A')}<br/>
                    <em>{deploy.get('service', 'unknown')}</em> v{deploy.get('version', '?')}<br/>
                    Changes: {', '.join(deploy.get('changes', [])[:2])}...
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No deployments available")
    
    st.markdown("---")
    
    # Latest Report Summary
    st.subheader("📄 Latest Incident Report")
    report_files = get_report_files()
    if report_files:
        latest_report = parse_report(report_files[0])
        with st.expander(f"📋 {report_files[0].name}", expanded=True):
            st.text(latest_report[:2000] + "..." if len(latest_report) > 2000 else latest_report)

# -------------------------------
# PAGE 2: LOGS EXPLORER
# -------------------------------
elif page == "📜 Logs Explorer":
    st.title("📜 Logs Explorer")
    st.markdown("*Analyze and filter application logs*")
    
    logs = load_logs()
    
    if logs:
        df = pd.DataFrame(logs)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            level_filter = st.multiselect("Filter by Level", df['level'].unique(), default=df['level'].unique())
        with col2:
            service_filter = st.multiselect("Filter by Service", df['service'].unique(), default=df['service'].unique())
        with col3:
            search_text = st.text_input("🔍 Search messages")
        
        # Apply filters
        filtered_df = df[df['level'].isin(level_filter) & df['service'].isin(service_filter)]
        if search_text:
            filtered_df = filtered_df[filtered_df['message'].str.contains(search_text, case=False, na=False)]
        
        # Stats row
        st.markdown("---")
        stat_cols = st.columns(4)
        stat_cols[0].metric("Total Logs", len(filtered_df))
        stat_cols[1].metric("Errors", len(filtered_df[filtered_df['level'].isin(['ERROR', 'CRITICAL'])]))
        stat_cols[2].metric("Warnings", len(filtered_df[filtered_df['level'] == 'WARN']))
        stat_cols[3].metric("Services", filtered_df['service'].nunique())
        
        st.markdown("---")
        
        # Display table
        st.subheader("📋 Log Entries")
        
        # Add severity emoji column
        filtered_df['Severity'] = filtered_df['level'].apply(severity_color)
        display_cols = ['Severity', 'timestamp', 'level', 'service', 'message']
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_cols],
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Error details
        st.subheader("🔍 Error Details")
        for _, log in filtered_df[filtered_df['level'].isin(['ERROR', 'CRITICAL'])].iterrows():
            with st.expander(f"{severity_color(log['level'])} {log['timestamp']} - {log['message'][:50]}..."):
                st.json(log.to_dict())
    else:
        st.warning("No logs data available. Check if data/logs.json exists.")

# -------------------------------
# PAGE 3: METRICS
# -------------------------------
elif page == "📈 Metrics":
    st.title("📈 System Metrics")
    st.markdown("*Telemetry and performance metrics analysis*")
    
    metrics = load_metrics()
    
    if metrics:
        st.subheader(f"📊 Service: {metrics.get('service', 'Unknown')}")
        st.caption(f"Time Range: {metrics.get('time_range', 'N/A')}")
        
        metrics_data = metrics.get('metrics', {})
        
        # Overview metrics
        st.markdown("---")
        st.subheader("📉 Performance Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Latency
        latency = metrics_data.get('latency_p95', {})
        col1.metric(
            "P95 Latency",
            f"{latency.get('during_incident', 0)}ms",
            delta=f"+{latency.get('during_incident', 0) - latency.get('before_incident', 0)}ms",
            delta_color="inverse"
        )
        
        # Error Rate
        error_rate = metrics_data.get('error_rate', {})
        col2.metric(
            "Error Rate",
            f"{error_rate.get('during_incident', 0)}%",
            delta=f"+{error_rate.get('during_incident', 0) - error_rate.get('before_incident', 0):.1f}%",
            delta_color="inverse"
        )
        
        # CPU
        cpu = metrics_data.get('cpu_usage', {})
        col3.metric("CPU Max", f"{cpu.get('max', 0)}%")
        
        # Memory
        memory = metrics_data.get('memory_usage', {})
        col4.metric("Memory Max", f"{memory.get('max', 0)}%")
        
        st.markdown("---")
        
        # Detailed tables
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("💾 Database Connections")
            db = metrics_data.get('database_connections', {})
            if db:
                db_df = pd.DataFrame([
                    {"Metric": "Pool Size", "Value": db.get('pool_size', 0)},
                    {"Metric": "Active Connections", "Value": db.get('active', 0)},
                    {"Metric": "Waiting Requests", "Value": db.get('waiting', 0)},
                    {"Metric": "Timeout Count", "Value": db.get('timeout_count', 0)},
                    {"Metric": "Avg Query Time (ms)", "Value": db.get('avg_query_time_ms', 0)},
                ])
                st.dataframe(db_df, use_container_width=True, hide_index=True)
            else:
                st.info("No database metrics available")
        
        with col_right:
            st.subheader("🧵 Thread Pool")
            thread = metrics_data.get('thread_pool', {})
            if thread:
                thread_df = pd.DataFrame([
                    {"Metric": "Active Threads", "Value": thread.get('active_threads', 0)},
                    {"Metric": "Max Threads", "Value": thread.get('max_threads', 0)},
                    {"Metric": "Queue Size", "Value": thread.get('queue_size', 0)},
                    {"Metric": "Rejected Requests", "Value": thread.get('rejected_requests', 0)},
                ])
                st.dataframe(thread_df, use_container_width=True, hide_index=True)
            else:
                st.info("No thread pool metrics available")
        
        st.markdown("---")
        
        # Timeline data
        st.subheader("📊 Metric Timelines")
        
        # CPU Timeline
        cpu_timeline = cpu.get('timeline', [])
        if cpu_timeline:
            cpu_df = pd.DataFrame(cpu_timeline)
            st.markdown("**CPU Usage Over Time**")
            st.bar_chart(cpu_df.set_index('time')['value'])
        
        # Request Rate Timeline
        request_rate = metrics_data.get('request_rate', {})
        req_timeline = request_rate.get('timeline', [])
        if req_timeline:
            req_df = pd.DataFrame(req_timeline)
            st.markdown("**Request Rate Over Time**")
            st.bar_chart(req_df.set_index('time')['value'])
    else:
        st.warning("No metrics data available. Check if data/metrics.json exists.")

# -------------------------------
# PAGE 4: DEPLOYMENTS
# -------------------------------
elif page == "🚀 Deployments":
    st.title("🚀 Deployment History")
    st.markdown("*Track deployments and configuration changes*")
    
    deployments = load_deployments()
    
    if deployments:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deployments", len(deployments))
        col2.metric("Successful", sum(1 for d in deployments if d.get('status') == 'success'))
        col3.metric("Services", len(set(d.get('service', '') for d in deployments)))
        
        st.markdown("---")
        
        # Deployments table
        st.subheader("📋 Deployment List")
        
        df = pd.DataFrame(deployments)
        
        # Add status icon
        df['Status Icon'] = df['status'].apply(lambda x: '✅' if x == 'success' else '❌')
        
        # Flatten changes column for display
        df['Changes Summary'] = df['changes'].apply(lambda x: ', '.join(x[:2]) + ('...' if len(x) > 2 else '') if isinstance(x, list) else str(x))
        
        display_cols = ['Status Icon', 'deployment_id', 'service', 'version', 'deployed_at', 'Changes Summary']
        available_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Detailed deployment view
        st.subheader("🔍 Deployment Details")
        
        for deploy in deployments:
            status_icon = "✅" if deploy.get('status') == 'success' else "❌"
            rollback = "🔄 Rollback Available" if deploy.get('rollback_available') else ""
            
            with st.expander(f"{status_icon} {deploy.get('deployment_id', 'N/A')} - {deploy.get('service', 'unknown')} v{deploy.get('version', '?')} {rollback}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Deployed At:** {deploy.get('deployed_at', 'N/A')}")
                    st.markdown(f"**Deployed By:** {deploy.get('deployed_by', 'N/A')}")
                    if deploy.get('commit_hash'):
                        st.markdown(f"**Commit:** `{deploy.get('commit_hash')}`")
                
                with col2:
                    st.markdown("**Changes:**")
                    for change in deploy.get('changes', []):
                        # Highlight risky changes
                        if any(word in change.lower() for word in ['pool', 'connection', 'timeout', 'reduced', 'limit']):
                            st.markdown(f"- ⚠️ {change}")
                        else:
                            st.markdown(f"- {change}")
    else:
        st.warning("No deployment data available. Check if data/deployments.json exists.")

# -------------------------------
# PAGE 5: REPORTS
# -------------------------------
elif page == "📄 Reports":
    st.title("📄 Incident Reports")
    st.markdown("*View and analyze generated incident reports*")
    
    report_files = get_report_files()
    
    if report_files:
        # Report selector
        selected_report = st.selectbox(
            "Select Report",
            report_files,
            format_func=lambda x: f"📋 {x.name} ({x.stat().st_mtime})"
        )
        
        if selected_report:
            content = parse_report(selected_report)
            
            # Report metadata
            col1, col2, col3 = st.columns(3)
            col1.metric("File Size", f"{selected_report.stat().st_size} bytes")
            col2.metric("Created", datetime.fromtimestamp(selected_report.stat().st_mtime).strftime("%Y-%m-%d %H:%M"))
            col3.metric("Lines", len(content.split('\n')))
            
            st.markdown("---")
            
            # Report content
            st.subheader("📋 Report Content")
            st.text_area("", content, height=600, label_visibility="collapsed")
            
            # Download button
            st.download_button(
                "⬇️ Download Report",
                data=content,
                file_name=selected_report.name,
                mime="text/plain"
            )
    else:
        st.warning("No reports found. Run the incident investigation first to generate reports.")
        st.info("Reports are saved in the `reports/` directory.")

# -------------------------------
# PAGE 6: ARCHITECTURE
# -------------------------------
elif page == "🏗️ Architecture":
    st.title("🏗️ Agent Architecture")
    st.markdown("*Understanding the Incident Commander agent workflow*")
    
    # Architecture diagram
    st.subheader("📊 Agent Workflow")
    
    mermaid_diagram = """
    flowchart TB
        subgraph Input["📥 Input"]
            incident["🚨 Incident Input"]
        end

        subgraph Orchestration["📋 Orchestration"]
            orchestrator["OrchestratorAgent"]
        end

        subgraph Analysis["🔍 Data Analysis"]
            logs["📜 LogsAgent"]
            telemetry["📊 TelemetryAgent"]
            deployment["🚀 DeploymentAgent"]
        end

        subgraph Correlation["🧠 Reasoning"]
            reasoning["ReasoningAgent"]
        end

        subgraph Output["📤 Output"]
            report["ReportAgent"]
            final["📄 Incident Report"]
        end

        incident --> orchestrator
        orchestrator --> logs
        orchestrator --> telemetry
        orchestrator --> deployment
        logs --> reasoning
        telemetry --> reasoning
        deployment --> reasoning
        reasoning --> report
        report --> final
    """
    
    if MERMAID_AVAILABLE:
        stmd.st_mermaid(mermaid_diagram)
    else:
        st.code(mermaid_diagram, language="mermaid")
        st.info("Install streamlit-mermaid for diagram rendering: `pip install streamlit-mermaid`")
    
    st.markdown("---")
    
    # Agent descriptions
    st.subheader("🤖 Agent Descriptions")
    
    agents = [
        {"name": "OrchestratorAgent", "icon": "📋", "desc": "Creates the investigation plan and coordinates the workflow"},
        {"name": "LogsAgent", "icon": "📜", "desc": "Analyzes log files for error patterns, cascading failures, and timeline"},
        {"name": "TelemetryAgent", "icon": "📊", "desc": "Analyzes metrics like CPU, memory, latency, and connection pools"},
        {"name": "DeploymentAgent", "icon": "🚀", "desc": "Reviews recent deployments and identifies risky configuration changes"},
        {"name": "ReasoningAgent", "icon": "🧠", "desc": "Correlates all evidence to determine root cause with confidence score"},
        {"name": "ReportAgent", "icon": "📝", "desc": "Generates prioritized mitigation actions and recommendations"},
    ]
    
    for agent in agents:
        st.markdown(f"**{agent['icon']} {agent['name']}**")
        st.markdown(f"> {agent['desc']}")
        st.markdown("")

# -------------------------------
# FOOTER
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("**🚨 Incident Commander**")
st.sidebar.markdown("*AI-Powered Root Cause Analysis*")
st.sidebar.caption("Built with LangGraph + Streamlit")
