import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import streamlit_mermaid as stmd
from langchain_litellm import ChatLiteLLM

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Autonomous Incident Commander",
    page_icon="🚨",
    layout="wide"
)

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Agent Chat", "RCA Report"])

# -------------------------------
# SAMPLE BACKEND DATA
# -------------------------------
backend_data = {
    "events": [
        {"id": 1, "name": "Alpha", "value": 12.5, "status": "ok", "category": "A",
         "timestamp": "2026-02-01T10:00:00", "log": "Service started successfully.",
         "cpu_usage": 35.2, "memory_usage": 512, "p99_latency_ms": 120, "db_connections": 5},
        {"id": 2, "name": "Beta", "value": 9.2, "status": "ok", "category": "B",
         "timestamp": "2026-02-02T11:15:00", "log": "Processed request successfully.",
         "cpu_usage": 40.5, "memory_usage": 610, "p99_latency_ms": 95, "db_connections": 3},
        {"id": 3, "name": "Gamma", "value": 14.7, "status": "fail", "category": "A",
         "timestamp": "2026-02-03T09:30:00", "log": "Database connection timeout error.",
         "cpu_usage": 78.0, "memory_usage": 1024, "p99_latency_ms": 2000, "db_connections": 15},
        {"id": 4, "name": "Delta", "value": 7.1, "status": "ok", "category": "C",
         "timestamp": "2026-02-04T14:45:00", "log": "Service heartbeat normal.",
         "cpu_usage": 33.1, "memory_usage": 480, "p99_latency_ms": 110, "db_connections": 4},
        {"id": 5, "name": "Epsilon", "value": 11.0, "status": "warn", "category": "B",
         "timestamp": "2026-02-05T16:20:00", "log": "High memory usage detected.",
         "cpu_usage": 65.4, "memory_usage": 950, "p99_latency_ms": 450, "db_connections": 8}
    ],
    "agent_chat": [],
    "report": {
        "markdown": """
# Root Cause Analysis Report

## Summary
- Gamma service failed due to DB timeout.
- Epsilon service warning due to high memory.

## Metrics Observed
- Max CPU usage: 78%
- Max Memory usage: 1024 MB
- Max p99 latency: 2000 ms
- Critical incidents: 1
- Warnings: 1

## Recommendations
- Investigate DB connection pool limits for Gamma.
- Optimize memory usage for Epsilon.
- Monitor p99 latency and CPU spikes.

## Timeline
- 2026-02-03 09:30 - Gamma failed
- 2026-02-05 16:20 - Epsilon warning

## Timeline Diagram
```mermaid
graph TD
    A --> B
```
"""
    }
}

# -------------------------------
# HELPER FUNCTION TO RENDER MERMAID
# -------------------------------
def render_markdown_with_mermaid(content):
    """
    Render markdown and Mermaid diagrams from the same content.
    """
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)
    modified_content = re.sub(mermaid_pattern, '', content, flags=re.DOTALL)
    st.markdown(modified_content)
    for mermaid_code in mermaid_blocks:
        stmd.st_mermaid(mermaid_code)

# -------------------------------
# PAGE 1: DASHBOARD
# -------------------------------
if page == "Dashboard":
    st.title("🚨 Autonomous Incident Dashboard")
    st.caption("Fully dynamic JSON-driven KPIs and Table")

    df = pd.DataFrame(backend_data["events"])

    # Dynamic KPIs
    st.subheader("📊 Key Metrics (Dynamic)")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    kpi_cols = st.columns(max(1, len(numeric_cols)))
    for i, col in enumerate(numeric_cols):
        max_val = df[col].max()
        mean_val = df[col].mean()
        kpi_cols[i % len(kpi_cols)].metric(label=f"{col} (Max)", value=f"{max_val}")
        kpi_cols[i % len(kpi_cols)].metric(label=f"{col} (Mean)", value=f"{round(mean_val,2)}")

    if categorical_cols:
        st.subheader("📊 Categorical Metrics")
        for col in categorical_cols:
            st.markdown(f"**{col} counts:**")
            counts = df[col].value_counts().to_dict()
            counts_df = pd.DataFrame(list(counts.items()), columns=[col, "Count"])
            st.table(counts_df)

    st.divider()

    # Dynamic Table
    st.subheader("📋 Incident Events Table")
    columns = df.columns.tolist()
    selected_columns = st.sidebar.multiselect("Select fields to display", columns, default=columns)
    search_text = st.sidebar.text_input("Search table (any field)")
    rows_per_page = st.sidebar.slider("Rows per page", 5, 50, 10)

    display_df = df[selected_columns].copy() if selected_columns else df.copy()
    if search_text:
        mask = display_df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)
        display_df = display_df[mask]

    total_rows = len(display_df)
    page_number = st.number_input(
        "Page", min_value=1, max_value=max(1, (total_rows-1)//rows_per_page +1), value=1
    )
    start = (page_number-1)*rows_per_page
    end = start + rows_per_page
    page_df = display_df.iloc[start:end]

    st.dataframe(page_df, use_container_width=True, hide_index=True)
    st.caption(f"Showing rows {start+1} to {min(end, total_rows)} of {total_rows}")

# -------------------------------
# PAGE 2: AGENT CHAT
# -------------------------------
elif page == "Agent Chat":
    st.title("🤖 Agent Chat (LLM Powered)")
    st.caption("Ask questions and get answers from the LLM backend")

    os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY_HERE"

    # Initialize LLM
    llm = ChatLiteLLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.1,
        litellm_params={"num_retries": 3}
    )

    if "messages" not in st.session_state:
        st.session_state.messages = backend_data.get("agent_chat", [])

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_markdown_with_mermaid(message["content"])
            else:
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Typing…")
            try:
                response = llm.invoke([
                    {"role": "system", "content": "You are an autonomous incident commander agent."},
                    {"role": "user", "content": prompt}
                ])
                agent_reply = response.content if hasattr(response, "content") else str(response)
            except Exception as e:
                agent_reply = f"Error calling LLM: {e}"
            placeholder.empty()
            render_markdown_with_mermaid(agent_reply)

        st.session_state.messages.append({"role": "assistant", "content": agent_reply})

# -------------------------------
# PAGE 3: RCA REPORT
# -------------------------------
elif page == "RCA Report":
    st.title("📄 Root Cause Analysis Report")
    st.caption("Dynamic report loaded from backend Markdown")
    
    report_md = backend_data["report"]["markdown"]
    render_markdown_with_mermaid(report_md)

    st.download_button(
        "Download Report as TXT",
        data=report_md,
        file_name="RCA_report.txt",
        mime="text/plain"
    )
