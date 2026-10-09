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


    
    

if __name__ == "__main__":
    main()