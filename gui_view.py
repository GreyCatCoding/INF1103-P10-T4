import pandas as pd
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                               QWidget, QFileDialog, QTableWidget, QTableWidgetItem, 
                               QLabel, QLineEdit, QMessageBox)
from PySide6.QtCore import QThread, Signal

from commentfileprocessor import CommentFileProcessor
from data_manager import DataManager

# ==========================================
# THREADING WORKER (to prevent GUI freezing during long-running AI moderation)
# ==========================================
class ModerationWorker(QThread):
    """Runs the AI moderation pipeline in the background to prevent GUI freezing."""
    
    # Signals to communicate back to the main GUI thread
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
            # This runs pipeline.process(cleaned_df, csv_path)
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
        self.worker = None  # Holds the background thread
        
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

        # --- Summary Label ---
        self.summary_label = QLabel("Awaiting Data...\n")
        #self.summary_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0;") #Catered for better light theme visibility
        self.summary_label.setStyleSheet(
            "font-weight: bold; "
            "padding: 10px; "
            "background-color: #2d2d2d; "
            "color: #ffffff; "
            "border: 1px solid #555555; "
            "border-radius: 5px;") # Catered for better dark theme visibility
        main_layout.addWidget(self.summary_label)

        # --- Table Display ---
        self.table = QTableWidget()
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
            # Fast operation: Clean the file
            cleaned_df, csv_path, json_path = self.processor.process(file_path)
            
            # Slow operation: Pass to AI Moderation Pipeline via Thread
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
        """Starts the background thread and disables the UI temporarily."""
        self.summary_label.setText("Processing with AI... This will take a while due to rate limits. Please wait.")
        self.set_ui_enabled(False)

        # Create and connect the worker thread
        self.worker = ModerationWorker(self.process_callback, cleaned_df, csv_path)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, final_df):
        """Re-enables the UI when the thread finishes and displays the results."""
        self.current_df = final_df
        self.display_data(self.current_df)
        self.set_ui_enabled(True)

    def on_processing_error(self, error_message):
        """Handles any errors that occurred inside the background thread."""
        QMessageBox.critical(self, "AI Processing Error", error_message)
        self.summary_label.setText("Processing failed.")
        self.set_ui_enabled(True)

    def set_ui_enabled(self, enabled: bool):
        """Toggles interface buttons to prevent users from clicking while AI is processing."""
        self.btn_clean_file.setEnabled(enabled)
        self.btn_load_cleaned.setEnabled(enabled)
        self.btn_apply_filter.setEnabled(enabled)
        self.btn_clear_filter.setEnabled(enabled)

    def handle_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cleaned CSV", "cleaned", "CSV Files (*.csv)")
        if file_path:
            try:
                filename = Path(file_path).name
                df = self.data_manager.load_report(filename)
                self.current_df = df
                self.display_data(self.current_df)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

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