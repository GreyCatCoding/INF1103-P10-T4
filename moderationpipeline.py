import time

from csvreportstore import CsvReportStore
from data_manager import DataManager
import logic_manager
from ai_manager import AIManager


class ModerationPipeline:
    """Connects AIManager -> logic_manager -> data_manager."""

    def __init__(self, ai_manager: AIManager, data_manager: DataManager = None, delay_seconds: int = 45):
        
        self.__ai_manager = ai_manager
        self.__data_manager = data_manager or DataManager(CsvReportStore()) # Fallback to default CsvReportStore if not explicitly injected
        self.__delay_seconds = delay_seconds  # Stay under the free-tier rate limit

    def process(self, cleaned_df, csv_path):
        """Moderates every row of cleaned_df, saves the reports to csv_path and returns them."""
        rows = cleaned_df.to_dict("records")
        records_for_logic_manager = []

        # AI Analysis
        for record in rows:
            result = self.__ai_manager.analyse_record(record)
            if result:
                records_for_logic_manager.append(result)
            else:
                records_for_logic_manager.append(record)

            time.sleep(self.__delay_seconds)  # Prevent overloading AI API rate limits

        # LOGIC Processing
        reports = logic_manager.process_reports(records_for_logic_manager)

        # DATA Persistence
        df = self.__data_manager.build_table(reports)
        self.__data_manager.save_report(df, csv_path)

        return df