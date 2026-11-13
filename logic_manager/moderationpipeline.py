from data_manager.csvreportstore import CsvReportStore
from data_manager.data_manager import DataManager
from ai_manager.ai_manager import AIManager
from logic_manager.logic_manager_oop import LogicManager
from logic_manager.weightedriskscorer import WeightedRiskScorer
from logic_manager.moderation_policy import ModerationPolicy
from ai_manager.progresstracker import ProgressTracker


class ModerationPipeline:
    """Connects AIManager -> logic_manager -> data_manager."""


    def __init__(
        self,
        ai_manager: AIManager,
        data_manager: DataManager = None,
        delay_seconds: int = 45,
        logic_manager_instance: LogicManager = None
    ):

        self.__ai_manager = ai_manager
        self.__data_manager = data_manager or DataManager(CsvReportStore()) # Fallback to default CsvReportStore if not explicitly injected
        self.__delay_seconds = delay_seconds  # Stay under the free-tier rate limit
        self.__logic_manager = logic_manager_instance or LogicManager(
            scorer=WeightedRiskScorer(),
            policy=ModerationPolicy()
        )


    def process(self, cleaned_df, csv_path, progress: ProgressTracker | None = None):
        """Moderates every row of cleaned_df, saves the reports to csv_path and returns them.
        Runs in the worker thread and checks `progress` between comments so it can stop early."""
        progress = progress or ProgressTracker()

        rows = cleaned_df.to_dict("records")
        progress.start(len(rows))
        records_for_logic_manager = []

        # AI Analysis
        for index, record in enumerate(rows):
            if progress.stop_requested: # check if user pressed Ctrl+C
                break

            result = self.__ai_manager.analyse_record(record)
            if result:
                records_for_logic_manager.append(result)
            else:
                records_for_logic_manager.append(record)
            progress.record_done() # update progress

            is_last = index == len(rows) - 1
            # Wait for the rate limit, pause() returns True if the CTRL+C is pressed
            if not is_last and progress.pause(self.__delay_seconds):
                break

        # LOGIC Processing
        reports = self.__logic_manager.process_records(records_for_logic_manager)

        # DATA Persistence
        df = self.__data_manager.build_table(reports)
        self.__data_manager.save_report(df, csv_path)

        return df