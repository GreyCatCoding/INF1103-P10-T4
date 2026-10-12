import io_manager
import ai_manager
import Logic_Manager
import data_manager
import logging
import time


from dotenv import load_dotenv

# Load API keys from .env so ai_manager can read them with os.getenv
load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    # IO (input)
    # user input for the csv file
    rows = io_manager.run_input_workflow().to_dict("records") # Convert the io manager output to a list of dictionaries (records)
    records_for_logic_manager = [] # to store records that passed AI analysis

    # AI 
    for record in rows: # for each record in the list of dictionaries
        result = ai_manager.analyse_record(record) # ai manager to analyze record
        if result:
            records_for_logic_manager.append(result)  # AI succeeded: append the analyzed record to the records_for_logic_manager list
        else:
            records_for_logic_manager.append(record)  # AI failed: append the original record to the records_for_logic_manager list

        time.sleep(60) #prevent overloading of ai_manager API
    # LOGIC 
    reports = Logic_Manager.process_reports(records_for_logic_manager) # process all records for logic manager

    # DATA
    df = data_manager.to_dataframe(reports)   # logic manager sends processed reports to data manager
    data_manager.save_reports(df, "moderation_results.csv")   # persistent storage for data manager outputs

    # IO (output)
    io_manager.run_output_workflow(df)        # data manager sends back processed csv to io manager for output  

if __name__ == "__main__":
    main()