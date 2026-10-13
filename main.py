import io_manager
import ai_manager
import logic_manager
import data_manager
import logging
import time
from dotenv import load_dotenv

"""Load API keys from .env so ai_manager can read them with os.getenv"""
load_dotenv()
logging.basicConfig(level=logging.INFO)


def process_ai_and_logic(cleaned_df, csv_path):
    """Handles the AI analysis, Logic Manager, and Data Manager pipeline."""
    rows = cleaned_df.to_dict("records")
    records_for_logic_manager = []

    # AI Analysis
    for record in rows:
        result = ai_manager.analyse_record(record)
        if result:
            records_for_logic_manager.append(result)
        else:
            records_for_logic_manager.append(record)

        time.sleep(60)  # Prevent overloading AI API rate limits

    # LOGIC Processing
    reports = logic_manager.process_reports(records_for_logic_manager)

    # DATA Persistence
    df = data_manager.to_dataframe(reports)
    data_manager.save_reports(df, csv_path)

    return df


def main():
    # Launches the main menu from io_manager and hooks in the AI/Logic pipeline
    io_manager.main_menu(process_callback=process_ai_and_logic)


if __name__ == "__main__":
    main()