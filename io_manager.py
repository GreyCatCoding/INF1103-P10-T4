# =============================================================
# MAIN WORKFLOW EXECUTION (OOP)
# =============================================================
from pathlib import Path
import pandas as pd
import data_manager
from commentfileprocessor import CommentFileProcessor
from console_view import ConsoleView
#from file_selector import UncleanedFileSelector, CleanedFileSelector

BASE_DIR = Path(__file__).resolve().parent
UNCLEANED_DIR = BASE_DIR / "uncleaned"
CLEANED_DIR = BASE_DIR / "cleaned"
class IOManager:
    """Main workflow controller. Coordinates views, selectors, and processors."""
    
    def __init__(self):
        # Composition: IOManager manages the lifecycles of these instances
        self.__view = ConsoleView()
        self.__processor = CommentFileProcessor()
        #self.__uncleaned_selector = UncleanedFileSelector(UNCLEANED_DIR)
        #self.__cleaned_selector = CleanedFileSelector(CLEANED_DIR)

    def main_menu(self, process_callback=None) -> None:
        """Displays the main options menu and routes user selections."""
        while True:
            print("\n" + "=" * 40)
            print("      DATA CLEANING & MANAGEMENT MENU      ")
            print("=" * 40)
            print("1.) Cleanse New File")
            print("2.) Display Existing Cleaned File")
            print("3.) Exit")

            choice = input("\nSelect an option (1-3): ").strip()

            if choice == "1":
                cleaned_df, csv_path = self.__run_input_workflow()
                if cleaned_df is not None:
                    if process_callback: 
                        try:
                            final_df = process_callback(cleaned_df, csv_path)
                            self.__run_output_workflow(final_df)
                        except PermissionError:
                            print(f"\n[Error] Could not save results: '{csv_path.name}' is open in another program.")
                            continue
                    else:
                        self.__run_output_workflow(cleaned_df)

            elif choice == "2":
                result = self.__cleaned_selector.select_file()
                if result:
                    cleaned_df, csv_path = result
                    self.__run_output_workflow(cleaned_df)

            elif choice == "3":
                print("\nExiting program. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 1, 2, or 3.")

    def __run_input_workflow(self) -> tuple[pd.DataFrame | None, Path | None]:
        """Coordinates uncleaned file selection, processing, and outputting previews."""
        input_file = self.__uncleaned_selector.select_file()
        
        if input_file is None:
            return None, None

        print(f"\nProcessing {input_file.name}...")
        raw_df = pd.read_csv(input_file)
        
        # Processor transforms the data
        cleaned_df, csv_path, json_path = self.__processor.process(input_file)

        print("\n--- Uncleaned Data Preview (Top 5) ---")
        self.__view.print_table(raw_df.head(5))
        
        print(f"\nSaved CSV to: {csv_path}")
        print(f"Saved JSON to: {json_path}")
        
        print("\n--- Cleaned Data Preview (Top 5) ---")
        self.__view.print_table(cleaned_df.head(5))

        return cleaned_df, csv_path

    def __run_output_workflow(self, df: pd.DataFrame) -> None:
        """Generates statistical summaries and triggers the filter loop."""
        print("\nModerated DataFrame:")
        self.__view.print_detailed_records(df)
        
        # Association: Utilizing data_manager without owning it
        summary_dict = data_manager.get_summary_metrics(df)
        self.__view.print_summary(summary_dict)
        self.__run_filter(df)

    def __run_filter(self, df: pd.DataFrame) -> None:
        """Handles the interactive filtering query loop."""
        while True:
            print("\n=== Filter Moderated Data ===")
            print("1.) Start Filtering")
            print("2.) Exit to Main Menu")

            choice = input("\nSelect an option (1-2): ").strip()

            if choice == "2":
                print("Exiting filter system...")
                break
            elif choice != "1":
                print("\n[Error] Invalid choice.")
                continue
                
            while True:
                print("\n--- Filter Options ---")
                category = input("Enter Category (e.g., harassment, sexual, hate) or leave blank: ").strip() or None
                action = input("Enter Action/Priority (e.g., P1, P2, P3, P4) or leave blank: ").strip() or None
                
                if category is None and action is None:
                    print("\n[Error] You must provide either a Category or an Action to filter.")
                    continue
                    
                results = data_manager.query(df, category=category, action=action)

                print("\n--- Filter Results ---")
                if results.empty:
                    print("No matching records found.")
                else:
                    self.__view.print_detailed_records(results)
                break