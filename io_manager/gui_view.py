import pandas as pd
from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                               QWidget, QFileDialog, QTableWidget, QTableWidgetItem, 
                               QLabel, QLineEdit, QMessageBox, QInputDialog)
from PySide6.QtCore import QThread, Signal

from io_manager.commentfileprocessor import CommentFileProcessor
from data_manager.data_manager import DataManager

# ==========================================
# THREADING WORKER (to prevent GUI freezing during long-running AI moderation)
# ==========================================
class ModerationWorker(QThread):
    """Runs the AI moderation pipeline in the background to prevent GUI freezing."""
    
    finished = Signal(object) 
    error = Signal(str)

    def __init__(self, callback, cleaned_df, csv_path):
        super().__init__()
        self.callback = callback
        self.cleaned_df = cleaned_df
        self.csv_path = csv_path

    def run(self):
        """Executes the long-running pipeline process."""
        try:
            final_df = self.callback(self.cleaned_df, self.csv_path)
            self.finished.emit(final_df)
        except Exception as e:
            self.error.emit(str(e))


# ==========================================
# MAIN GUI CONTROLLER
# ==========================================
class GUIView(QMainWindow):
    def __init__(self, data_manager: DataManager, process_callback=None):
        super().__init__()
        self.setWindowTitle("Content Moderation System - Group P10-T4")
        self.resize(1000, 700)
        
        self.data_manager = data_manager
        self.process_callback = process_callback
        self.processor = CommentFileProcessor()
        
        self.current_df = None
        self.current_report_name = None  # Tracks the active report for database updates
        self.worker = None 
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # --- Top Menu Buttons ---
        btn_layout = QHBoxLayout()
        self.btn_clean_file = QPushButton("1. Cleanse New File")
        self.btn_clean_file.clicked.connect(self.handle_cleanse_file)
        btn_layout.addWidget(self.btn_clean_file)
        
        self.btn_load_cleaned = QPushButton("2. Display Existing Cleaned File")
        self.btn_load_cleaned.clicked.connect(self.handle_load_file)
        btn_layout.addWidget(self.btn_load_cleaned)
        
        self.btn_exit = QPushButton("3. Exit Program")
        self.btn_exit.clicked.connect(self.close)
        self.btn_exit.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_exit)
        
        main_layout.addLayout(btn_layout)

        # --- Filtering Section ---
        filter_layout = QHBoxLayout()
        self.filter_category = QLineEdit()
        self.filter_category.setPlaceholderText("Filter by Category (e.g. spam, hate)")
        filter_layout.addWidget(self.filter_category)

        self.filter_action = QLineEdit()
        self.filter_action.setPlaceholderText("Filter by Priority (e.g. P1, P2)")
        filter_layout.addWidget(self.filter_action)

        self.btn_apply_filter = QPushButton("Apply Filter")
        self.btn_apply_filter.clicked.connect(self.handle_filter)
        filter_layout.addWidget(self.btn_apply_filter)
        
        self.btn_clear_filter = QPushButton("Clear Filter")
        self.btn_clear_filter.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.btn_clear_filter)

        main_layout.addLayout(filter_layout)

        # --- CRUD Action Section ---
        crud_layout = QHBoxLayout()
        self.btn_update_row = QPushButton("Edit Selected Row (Priority)")
        self.btn_update_row.clicked.connect(self.handle_update_row)
        crud_layout.addWidget(self.btn_update_row)

        self.btn_delete_row = QPushButton("Delete Selected Row")
        self.btn_delete_row.clicked.connect(self.handle_delete_row)
        self.btn_delete_row.setStyleSheet("background-color: #f0ad4e; font-weight: bold;")
        crud_layout.addWidget(self.btn_delete_row)
        
        main_layout.addLayout(crud_layout)

        # --- Summary Label ---
        self.summary_label = QLabel("Awaiting Data...\n")
        self.summary_label.setStyleSheet(
            "font-weight: bold; "
            "padding: 10px; "
            "background-color: #2d2d2d; "
            "color: #ffffff; "
            "border: 1px solid #555555; "
            "border-radius: 5px;"
        )
        main_layout.addWidget(self.summary_label)

        # --- Table Display ---
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # Select entire rows for safe CRUD targeting
        main_layout.addWidget(self.table)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # ==========================================
    # WORKFLOW EVENT HANDLERS
    # ==========================================
    def handle_cleanse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Uncleaned CSV", "uncleaned", "CSV Files (*.csv)")
        if not file_path:
            return
            
        try:
            cleaned_df, csv_path, json_path = self.processor.process(file_path)
            
            # Store the current report name so CRUD knows what to update in MongoDB
            from pathlib import Path
            self.current_report_name = Path(csv_path).name 

            if self.process_callback:
                self.start_ai_processing(cleaned_df, csv_path)
            else:
                self.current_df = cleaned_df
                self.display_data(self.current_df)
                
        except PermissionError:
            QMessageBox.critical(self, "Error", f"Could not access file. It may be open in Excel.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def start_ai_processing(self, cleaned_df, csv_path):
        self.summary_label.setText("Processing with AI... This will take a while due to rate limits. Please wait.")
        self.set_ui_enabled(False)

        self.worker = ModerationWorker(self.process_callback, cleaned_df, csv_path)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, final_df):
        self.current_df = final_df
        self.display_data(self.current_df)
        self.set_ui_enabled(True)

    def on_processing_error(self, error_message):
        QMessageBox.critical(self, "AI Processing Error", error_message)
        self.summary_label.setText("Processing failed.")
        self.set_ui_enabled(True)

    def set_ui_enabled(self, enabled: bool):
        self.btn_clean_file.setEnabled(enabled)
        self.btn_load_cleaned.setEnabled(enabled)
        self.btn_apply_filter.setEnabled(enabled)
        self.btn_clear_filter.setEnabled(enabled)
        self.btn_update_row.setEnabled(enabled)
        self.btn_delete_row.setEnabled(enabled)

    def handle_load_file(self):
        report_names = self.data_manager.list_reports()
        if not report_names:
            QMessageBox.information(self, "No Reports", "No saved reports found. Cleanse a file first.")
            return

        report_name, chosen = QInputDialog.getItem(
            self, "Select Report", "Saved reports:", report_names, 0, False
        )
        if not chosen:
            return  

        try:
            self.current_report_name = report_name # Track active report for CRUD operations
            df = self.data_manager.load_report(report_name)
            self.current_df = df
            self.display_data(self.current_df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load report: {str(e)}")

    def handle_filter(self):
        if self.current_df is None:
            QMessageBox.warning(self, "Warning", "No data loaded to filter.")
            return

        cat = self.filter_category.text().strip() or None
        act = self.filter_action.text().strip() or None
        
        filtered_df = self.data_manager.filter_reports(self.current_df, category=cat, action=act)
        self.display_dataframe(filtered_df)

    def clear_filter(self):
        if self.current_df is not None:
            self.filter_category.clear()
            self.filter_action.clear()
            self.display_dataframe(self.current_df)

    # ==========================================
    # DATABASE UPDATE & DELETE HANDLERS
    # ==========================================
    def handle_update_row(self):
        if not self.current_report_name or self.current_df is None:
            QMessageBox.warning(self, "Error", "No report loaded. Please load or cleanse a file first.")
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a row from the table to update.")
            return

        user_id = self.table.item(current_row, 0).text()
        current_priority = self.table.item(current_row, 5).text().strip().upper()

        allowed_priorities = ["P1", "P2", "P3", "P4"]
        
        # Set default dropdown index to the row's current priority if valid, otherwise default to P1 (index 0)
        default_index = allowed_priorities.index(current_priority) if current_priority in allowed_priorities else 0

        # Use getItem with editable=False to force selection strictly from the allowed_priorities list
        new_priority, ok = QInputDialog.getItem(
            self, 
            "Update Row", 
            "Select new priority:", 
            allowed_priorities, 
            default_index, 
            False
        )

        if ok and new_priority:
            try:
                # Update backend payload to modify the 'priority' field
                updated_data = {"priority": new_priority}
                self.data_manager.update_record(self.current_report_name, user_id, updated_data)
                
                # Refresh local DataFrame and Table
                self.current_df = self.data_manager.load_report(self.current_report_name)
                self.display_data(self.current_df)
                QMessageBox.information(self, "Success", f"Updated User ID {user_id} to priority: {new_priority}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Update failed: {str(e)}")

    def handle_delete_row(self):
        if not self.current_report_name or self.current_df is None:
            QMessageBox.warning(self, "Error", "No report loaded. Please load or cleanse a file first.")
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a row from the table to delete.")
            return

        user_id = self.table.item(current_row, 0).text()
        username = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete user '{username}' (ID: {user_id})?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Delete from backend
                self.data_manager.delete_record(self.current_report_name, user_id)
                
                # Refresh local DataFrame and Table
                self.current_df = self.data_manager.load_report(self.current_report_name)
                self.display_data(self.current_df)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}")

    # ==========================================
    # DISPLAY HELPERS
    # ==========================================
    def display_data(self, df: pd.DataFrame):
        self.update_summary(df)
        self.display_dataframe(df)

    def update_summary(self, df: pd.DataFrame):
        summary = self.data_manager.get_summary(df)
        
        if summary.get("total_records", 0) == 0:
            self.summary_label.setText("No data available to summarize.")
            return

        text = (f"Total Comments: {summary['total_records']}  |  "
                f"Pending Human Review: {summary['human_review_count']}\n"
                f"Categories: {dict(summary.get('category_counts', {}))}  |  "
                f"Priorities: {dict(summary.get('priority_counts', {}))}")
                
        self.summary_label.setText(text)

    def display_dataframe(self, df: pd.DataFrame):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns.astype(str))
        
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()