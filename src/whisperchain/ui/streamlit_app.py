# Run this file to test the Streamlit UI
#
# $ streamlit run tests/test_streamlit_demo.py
#
# If you get an error about the config file, run the following command to kill all running Streamlit processes:
#
# $ lsof -ti :8501 | xargs kill -9

import time
from datetime import datetime

import requests
import streamlit as st

from whisperchain.core.config import config


def main():
    # Set page config
    st.set_page_config(
        page_title=config.ui_config.title,
        page_icon=config.ui_config.page_icon,
        layout=config.ui_config.layout,
    )

    st.title("WhisperChain Dashboard")

    # Initialize session state
    if "last_history" not in st.session_state:
        st.session_state.last_history = []
        st.session_state.last_check_time = time.time()
        st.session_state.server_online = False  # Initialize server status

    # Server status check - only check every 5 seconds
    current_time = time.time()
    if current_time - st.session_state.last_check_time >= 5:
        try:
            response = requests.get(config.ui_config.server_url)
            st.session_state.server_online = response.status_code == 200
            st.session_state.last_check_time = current_time
        except:
            st.session_state.server_online = False

    # Display server status
    st.sidebar.header("Server Status")
    if st.session_state.server_online:
        st.sidebar.success("🟢 Server Online")
    else:
        st.sidebar.error("🔴 Server Offline")
        st.header(
            "Once the server is online, the UI will automatically refresh and display the transcription history."
        )
        time.sleep(5)  # Longer delay when server is offline
        st.rerun()

    # Transcription History
    st.header("Transcription History")

    # Clear history button
    if st.button("Clear History"):
        requests.delete(config.ui_config.server_url + "/history")
        st.session_state.last_history = []
        st.rerun()

    try:
        # Fetch history from server
        response = requests.get(config.ui_config.server_url + "/history")
        history = response.json()

        # Check if history has changed
        history_changed = len(history) != len(st.session_state.last_history)
        st.session_state.last_history = history

        # Display transcriptions
        for idx, entry in enumerate(reversed(history)):
            with st.expander(f"Transcription {len(history) - idx}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Raw Transcription")
                    st.text(entry.get("transcription", ""))
                    st.caption(f"Processed bytes: {entry.get('processed_bytes', 0)}")
                with col2:
                    st.subheader("Cleaned Transcription")
                    st.text(entry.get("cleaned_transcription", ""))
                    st.caption(f"Timestamp: {entry.get('timestamp', '')}")

        # Only rerun if history has changed
        if history_changed:
            print("History changed, rerunning...")
            time.sleep(config.ui_config.quick_refresh)
            st.rerun()
        else:
            time.sleep(config.ui_config.refresh_interval)
            st.rerun()

    except Exception as e:
        st.error(f"Error fetching history: {str(e)}")
        st.rerun()


if __name__ == "__main__":
    # Ensure Streamlit config is up to date
    config.generate_streamlit_config()
    main()
