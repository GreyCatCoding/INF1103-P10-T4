import io_manager
import ai_manager
import logging
import time

from dotenv import load_dotenv

# Load API keys from .env so ai_manager can read them with os.getenv
load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    # user input for the csv file
    rows = io_manager.run_input_workflow().to_dict("records") # Convert the io manager output to a list of dictionaries (records)

    for record in rows: # for each record in the list of dictionaries
        record["comment"] = record["processed_comments"] # save processed comment into comment field
        ai_manager.analyse_record(record) # ai manager to analyze record
        time.sleep(60) #prevent overloading of ai_manager API


    
    

if __name__ == "__main__":
    main()