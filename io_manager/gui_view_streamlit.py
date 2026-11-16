import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

import streamlit as st

from ai_manager.progresstracker import ProgressTracker
from io_manager.commentfileprocessor import CommentFileProcessor


class StreamlitGUI:
    """Streamlit web presentation layer for the Content Moderation System."""

    DEFAULT_ACTIONS = [
        "Immediate removal & ban",
        "Remove comment & warn user",
        "Flag for human review",
        "Monitor user",
        "No action required",
    ]

    def __init__(self, data_manager, pipeline):
        self.data_manager = data_manager
        self.pipeline = pipeline
        self.processor = CommentFileProcessor()

    def render(self):
        """Main entry point to configure and render the Streamlit dashboard."""
        st.set_page_config(page_title="Content Moderation System", layout="wide")
        st.title("Content Moderation System - Group P10-T4")

        self._init_session_state()
        self._render_sidebar()
        self._render_main_area()

    def _init_session_state(self):
        """Initializes persistent state variables across Streamlit reruns."""
        if "current_df" not in st.session_state:
            st.session_state.current_df = None
        if "current_report_name" not in st.session_state:
            st.session_state.current_report_name = None

    # ==========================================
    # SIDEBAR: NAVIGATION & FILE LOADING
    # ==========================================
    def _render_sidebar(self):
        with st.sidebar:
            st.header("Navigation")

            st.subheader("1. Cleanse New File")
            uploaded_file = st.file_uploader("Upload Uncleaned CSV", type=["csv"])

            if st.button("Process File") and uploaded_file:
                self._handle_file_upload(uploaded_file)

            st.divider()

            st.subheader("2. Load Existing Report")
            self._render_report_loader()

    def _handle_file_upload(self, uploaded_file):
        """Saves the upload with its original filename in a temp folder, cleans it, and runs AI moderation."""
        original_filename = Path(uploaded_file.name).name

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = os.path.join(tmp_dir, original_filename)
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                with st.spinner("Cleaning file..."):
                    cleaned_df, csv_path, json_path = self.processor.process(tmp_path)
                    st.session_state.current_report_name = Path(csv_path).name

                if self.pipeline:
                    st.session_state.current_df = self._run_moderation_pipeline(cleaned_df, csv_path)
                else:
                    st.session_state.current_df = cleaned_df

            st.success(f"File processed and saved as {st.session_state.current_report_name}!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def _run_moderation_pipeline(self, cleaned_df, csv_path):
        """Runs AI moderation in a background thread while updating the progress bar."""
        progress = ProgressTracker()
        bar = st.progress(0.0, text="Starting AI moderation...")
        start = time.monotonic()

        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="moderation") as pool:
            future = pool.submit(self.pipeline.process, cleaned_df, csv_path, progress)

            while not future.done():
                done, total = progress.snapshot()
                fraction = done / total if total else 0.0
                elapsed = int(time.monotonic() - start)
                bar.progress(
                    fraction,
                    text=f"{done} of {total} comments | {elapsed // 60:02d}:{elapsed % 60:02d}",
                )
                wait([future], timeout=0.5)

            result_df = future.result()

        done, total = progress.snapshot()
        elapsed = int(time.monotonic() - start)
        bar.progress(
            1.0,
            text=f"{done} of {total} comments | {elapsed // 60:02d}:{elapsed % 60:02d} | Done",
        )
        return result_df

    def _render_report_loader(self):
        """Renders the dropdown and button to load previously saved reports."""
        report_names = self.data_manager.list_reports()
        if report_names:
            selected_report = st.selectbox("Saved reports:", report_names)
            if st.button("Load Report"):
                try:
                    df = self.data_manager.load_report(selected_report)
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
    def _render_main_area(self):
        if st.session_state.current_df is None:
            st.info("Awaiting Data... Upload a new file or load an existing report from the sidebar.")
            return

        df = st.session_state.current_df
        self._render_summary(df)
        display_df = self._render_filters(df)
        self._render_data_table(display_df)
        self._render_crud_controls(display_df)

    def _render_summary(self, df):
        """Displays high-level metrics and category/priority counts."""
        summary = self.data_manager.get_summary(df)
        st.write("### Report Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Comments", summary.get("total_records", 0))
        col2.metric("Pending Human Review", summary.get("human_review_count", 0))

        st.caption(
            f"**Categories:** {dict(summary.get('category_counts', {}))} | "
            f"**Priorities:** {dict(summary.get('priority_counts', {}))}"
        )
        st.divider()

    def _render_filters(self, df):
        """Renders category and priority text filters and returns the filtered DataFrame."""
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
            display_df = self.data_manager.filter_reports(df, category=cat, action=act)

        return display_df

    def _render_data_table(self, display_df):
        """Renders the active report's DataFrame."""
        st.write(f"### Data View: {st.session_state.current_report_name}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.divider()

    def _render_crud_controls(self, display_df):
        """Renders controls to update priority/recommended action or delete records by User ID."""
        st.write("### Manage Records")
        c_col1, c_col2 = st.columns(2)

        # Assuming User ID is the first column
        user_ids = display_df.iloc[:, 0].astype(str).tolist() if not display_df.empty else []
        action_col = "recommended_action" if "recommended_action" in display_df.columns else "action"

        existing_actions = (
            display_df[action_col].dropna().astype(str).unique().tolist()
            if action_col in display_df.columns
            else []
        )
        action_options = list(dict.fromkeys(existing_actions + self.DEFAULT_ACTIONS))
        priority_options = ["P1", "P2", "P3", "P4"]

        with c_col1:
            st.markdown("**Update Record**")
            update_user = st.selectbox("Select User ID to Update", user_ids, key="update_uid")

            # Pre-select the selected user's current priority and action if available
            default_prio_idx = 0
            default_act_idx = 0
            if update_user and not display_df.empty:
                matching_rows = display_df[display_df.iloc[:, 0].astype(str) == update_user]
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    if "priority" in display_df.columns and str(row["priority"]) in priority_options:
                        default_prio_idx = priority_options.index(str(row["priority"]))
                    if action_col in display_df.columns and str(row[action_col]) in action_options:
                        default_act_idx = action_options.index(str(row[action_col]))

            new_priority = st.selectbox(
                "Select new priority",
                priority_options,
                index=default_prio_idx,
                key="new_prio",
            )
            new_action = st.selectbox(
                "Select recommended action",
                action_options,
                index=default_act_idx,
                key="new_action",
            )

            if st.button("Edit Row"):
                try:
                    self.data_manager.update_record(
                        st.session_state.current_report_name,
                        update_user,
                        {
                            "priority": new_priority,
                            action_col: new_action,
                        },
                    )
                    st.session_state.current_df = self.data_manager.load_report(
                        st.session_state.current_report_name
                    )
                    st.success(f"Updated User {update_user} ({new_priority} - {new_action})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

        with c_col2:
            st.markdown("**Delete Record**")
            delete_user = st.selectbox("Select User ID to Delete", user_ids, key="del_uid")

            if st.button("Delete Row", type="primary"):
                try:
                    self.data_manager.delete_record(
                        st.session_state.current_report_name,
                        delete_user,
                    )
                    st.session_state.current_df = self.data_manager.load_report(
                        st.session_state.current_report_name
                    )
                    st.success(f"Deleted User {delete_user}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")