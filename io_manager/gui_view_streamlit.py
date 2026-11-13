import os
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st

from io_manager.commentfileprocessor import CommentFileProcessor

def render_streamlit_ui(data_manager, pipeline):
    st.set_page_config(page_title="Content Moderation System", layout="wide")
    st.title("Content Moderation System - Group P10-T4")

    # Initialize persistent state variables across reruns
    if "current_df" not in st.session_state:
        st.session_state.current_df = None
    if "current_report_name" not in st.session_state:
        st.session_state.current_report_name = None

    processor = CommentFileProcessor()

    # ==========================================
    # SIDEBAR: NAVIGATION & FILE LOADING
    # ==========================================
    with st.sidebar:
        st.header("Navigation")
        
        st.subheader("1. Cleanse New File")
        uploaded_file = st.file_uploader("Upload Uncleaned CSV", type=["csv"])
        
        if st.button("Process File") and uploaded_file:
            # Streamlit keeps files in memory; write to a temp file for the processor
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                # Spinner replaces the QThread - it automatically handles the loading state
                with st.spinner("Processing file with AI... This will take a while due to rate limits."):
                    cleaned_df, csv_path, json_path = processor.process(tmp_path)
                    st.session_state.current_report_name = Path(csv_path).name
                    
                    if pipeline:
                        final_df = pipeline.process(cleaned_df, csv_path)
                        st.session_state.current_df = final_df
                    else:
                        st.session_state.current_df = cleaned_df
                        
                st.success("File processed successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                os.remove(tmp_path)
                
        st.divider()
        
        st.subheader("2. Load Existing Report")
        report_names = data_manager.list_reports()
        if report_names:
            selected_report = st.selectbox("Saved reports:", report_names)
            if st.button("Load Report"):
                try:
                    df = data_manager.load_report(selected_report)
                    st.session_state.current_df = df
                    st.session_state.current_report_name = selected_report
                    st.success(f"Loaded {selected_report}")
                except Exception as e:
                    st.error(f"Failed to load report: {e}")
        else:
            st.info("No saved reports found. Cleanse a file first.")

    # ==========================================
    # MAIN AREA: DISPLAY & CRUD
    # ==========================================
    if st.session_state.current_df is not None:
        df = st.session_state.current_df
        
        # Summary Metrics
        summary = data_manager.get_summary(df)
        st.write("### Report Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Comments", summary.get("total_records", 0))
        col2.metric("Pending Human Review", summary.get("human_review_count", 0))
        
        st.caption(f"**Categories:** {dict(summary.get('category_counts', {}))} | **Priorities:** {dict(summary.get('priority_counts', {}))}")
        st.divider()

        # Filtering Section
        st.write("### Filter Data")
        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        with f_col1:
            cat_filter = st.text_input("Filter by Category (e.g. spam, hate)")
        with f_col2:
            act_filter = st.text_input("Filter by Priority (e.g. P1, P2)")
        
        display_df = df
        cat = cat_filter.strip() if cat_filter.strip() else None
        act = act_filter.strip() if act_filter.strip() else None
        
        if cat or act:
            display_df = data_manager.filter_reports(df, category=cat, action=act)

        # Table Display
        st.write(f"### Data View: {st.session_state.current_report_name}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.divider()

        # CRUD Operations
        st.write("### Manage Records")
        c_col1, c_col2 = st.columns(2)
        
        # Assuming User ID is the first column
        user_ids = display_df.iloc[:, 0].astype(str).tolist() if not display_df.empty else []

        with c_col1:
            st.markdown("**Update Priority**")
            update_user = st.selectbox("Select User ID to Update", user_ids, key="update_uid")
            new_priority = st.selectbox("Select new priority", ["P1", "P2", "P3", "P4"])
            
            if st.button("Edit Row"):
                try:
                    data_manager.update_record(st.session_state.current_report_name, update_user, {"priority": new_priority})
                    st.session_state.current_df = data_manager.load_report(st.session_state.current_report_name)
                    st.success(f"Updated User {update_user} to {new_priority}")
                    st.rerun()  # Instantly refresh the UI
                except Exception as e:
                    st.error(f"Update failed: {e}")

        with c_col2:
            st.markdown("**Delete Record**")
            delete_user = st.selectbox("Select User ID to Delete", user_ids, key="del_uid")
            
            if st.button("Delete Row", type="primary"):
                try:
                    data_manager.delete_record(st.session_state.current_report_name, delete_user)
                    st.session_state.current_df = data_manager.load_report(st.session_state.current_report_name)
                    st.success(f"Deleted User {delete_user}")
                    st.rerun()  # Instantly refresh the UI
                except Exception as e:
                    st.error(f"Delete failed: {e}")
    else:
        st.info("Awaiting Data... Upload a new file or load an existing report from the sidebar.")