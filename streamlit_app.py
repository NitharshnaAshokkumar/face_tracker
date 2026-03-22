import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from pathlib import Path
from PIL import Image
from src.ui_helpers import UIHelper

# Page Config
st.set_page_config(
    page_title="Intelligent Face Tracker Dashboard",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize UI Helper
CONFIG_PATH = "config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
else:
    config = {}

ui = UIHelper(
    db_path=config.get("db_path", "data/db/visitor_counter.db"),
    log_root=config.get("log_root", "logs")
)

# Sidebar Branding
st.sidebar.title("👤 Face Tracker")
st.sidebar.markdown("---")
st.sidebar.info(
    "**Project**: Intelligent Face Tracker\n\n"
    "**Version**: 1.0.0\n\n"
    "**Status**: Online"
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "👥 Visitor Gallery", "📜 Event Logs", "📈 Analytics", "⚙️ Configuration"]
)

# --- A. Dashboard Home ---
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard Summary")
    
    stats = ui.get_summary_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Unique Visitors", stats["unique_visitors"])
    with col2:
        st.metric("Total Entries", stats["total_entries"])
    with col3:
        st.metric("Total Exits", stats["total_exits"])
    with col4:
        st.metric("Last Seen", stats["last_timestamp"][:19] if stats["last_timestamp"] != "No data" else "No data")

    st.markdown("---")
    
    # Source Info
    st.subheader("📡 Current Monitoring Status")
    source_type = config.get("source_type", "video")
    source_path = config.get("video_source", "Unknown")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Mode**: {source_type.upper()}")
    with col_b:
        st.write(f"**Source**: {source_path}")

    st.markdown("---")
    
    # Recent Events Preview
    st.subheader("🆕 Recent Activity")
    df_recent = ui.get_recent_events(limit=10)
    if not df_recent.empty:
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.warning("No events found in database yet.")

# --- B. Visitor Gallery ---
elif page == "👥 Visitor Gallery":
    st.title("👥 Registered Identities")
    
    df_gallery = ui.get_visitor_gallery()
    
    if df_gallery.empty:
        st.info("No visitors registered yet. Start the tracker to see data.")
    else:
        search = st.text_input("Search by Identity ID", "")
        if search:
            df_gallery = df_gallery[df_gallery['identity_id'].str.contains(search, case=False)]
            
        # Display as cards
        for idx, row in df_gallery.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([1, 4, 1])
                
                thumb = ui.find_thumbnail(row['identity_id'])
                with c1:
                    if thumb and os.path.exists(thumb):
                        img = Image.open(thumb)
                        st.image(img, width=120)
                    else:
                        st.image("https://via.placeholder.com/120?text=No+Photo", width=120)
                
                with c2:
                    st.subheader(f"ID: {row['identity_id']}")
                    st.write(f"**First Seen**: {row['first_seen']}")
                    st.write(f"**Last Seen**: {row['last_seen']}")
                    st.write(f"**Source**: {row['source']}")
                
                with c3:
                    st.metric("Events", row['event_count'])
                st.markdown("---")

# --- C. Event Logs ---
elif page == "📜 Event Logs":
    st.title("📜 Full Event History")
    
    df_events = ui.get_recent_events(limit=500)
    
    if df_events.empty:
        st.warning("No events logged yet.")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            e_type = st.multiselect("Event Type", options=["ENTRY", "EXIT"], default=["ENTRY", "EXIT"])
        with col2:
            id_filter = st.text_input("Filter by Face ID")
            
        filtered_df = df_events[df_events['event_type'].isin(e_type)]
        if id_filter:
            filtered_df = filtered_df[filtered_df['identity_id'].str.contains(id_filter, case=False)]
            
        st.dataframe(filtered_df, use_container_width=True)
        
        # CSV Export
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export CSV", csv, "face_events.csv", "text/csv")

# --- D. Analytics ---
elif page == "📈 Analytics":
    st.title("📈 Recognition Trends")
    
    df_analytics = ui.get_analytics_data()
    
    if df_analytics.empty:
        st.info("Gathering data... Run the tracker to see charts.")
    else:
        # Simple Chart: Entries vs Exits over time
        fig = px.bar(df_analytics, x='date', y='count', color='event_type', 
                     title="Daily Activity Summary", barmode='group',
                     template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Unique visits over time logic (approximated)
        unique_over_time = df_analytics[df_analytics['event_type'] == 'ENTRY']
        fig2 = px.line(unique_over_time, x='date', y='count', 
                       title="Unique Visitors Trend",
                       markers=True)
        st.plotly_chart(fig2, use_container_width=True)

# --- E. Configuration ---
elif page == "⚙️ Configuration":
    st.title("⚙️ System Configuration")
    
    # Load current config
    with open("config.json", "r") as f:
        curr_conf = json.load(f)
        
    st.markdown("Review and update system parameters below.")
    
    # 1. Video Source
    st.subheader("🎥 Video Input")
    new_source = st.text_input("Source View (Path or RTSP URL or 0)", str(curr_conf["video_source"]))
    source_type = st.selectbox("Source Type", ["video", "rtsp"], index=0 if curr_conf["source_type"] == "video" else 1)
    
    # 2. Thresholds
    st.subheader("🎯 Detection Thresholds")
    conf_thresh = st.slider("Face Conf Threshold", 0.0, 1.0, float(curr_conf["detector"]["conf_threshold"]))
    rec_thresh = st.slider("Recognition Match Threshold", 0.0, 1.0, float(curr_conf["recognizer"]["recognition_threshold"]))
    
    if st.button("💾 Save Configuration"):
        curr_conf["video_source"] = new_source
        curr_conf["source_type"] = source_type
        curr_conf["detector"]["conf_threshold"] = conf_thresh
        curr_conf["recognizer"]["recognition_threshold"] = rec_thresh
        
        with open("config.json", "w") as f:
            json.dump(curr_conf, f, indent=2)
        st.success("Configuration updated successfully!")

    st.markdown("---")
    st.subheader("🚀 Control")
    st.markdown("To start the processing pipeline, run the following command in your terminal:")
    st.code("python app.py --config config.json")
