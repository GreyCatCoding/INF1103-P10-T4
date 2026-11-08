"""Stores moderation reports as documents in a MongoDB collection."""
from pathlib import Path

import pandas as pd
from pymongo.collection import Collection # allows type hinting in python for MongoDB collections
from reportstore import ReportStore


class MongoReportStore(ReportStore):
    """Saves and loads reports in one MongoDB collection.

     Each row of a report is one document, tagged with a 'report_name' field
    (e.g. 'sample.csv') so all rows of the same report can be found together.
    """

    def __init__(self, collection: Collection):
        self.__collection = collection  

    def list_reports(self) -> list[str]:
        """Returns each saved report name once, sorted alphabetically."""
        names = self.__collection.distinct("report_name")
        return sorted(names)

    def save(self, df: pd.DataFrame, name: str | Path) -> None:
        """Saves df under the given name, replacing any report with that name."""

        # Convert the name to a proper report name (filename with .csv)
        report_name = self.__name_for(name)

        #turns each dataframe row into a dict 
        documents = df.to_dict("records")
        for document in documents:
            #adds a report_name field to each document to indicate which report it belongs to eg 'sample.csv'
            document["report_name"] = report_name

        self.__collection.delete_many({"report_name": report_name})

        if documents:
            self.__collection.insert_many(documents)

    def load(self, name: str | Path) -> pd.DataFrame:
        """Returns the named report as a DataFrame, with blank cells as "".

        Raises FileNotFoundError if no report has that name.
        """

        report_name = self.__name_for(name)

        hidden_fields = {"_id": 0, "report_name": 0} # dont return the MongoDB internal _id or the report_name field
        cursor = self.__collection.find({"report_name": report_name}, hidden_fields) #find document using the report name but exclude hidden fields
        documents = list(cursor.sort("_id", 1))

        # exception handling if no documents are found for the given report name
        if not documents:
            raise FileNotFoundError(f"Report '{report_name}' does not exist.")

        # loads the documents from mongodb into a DataFrame
        df = pd.DataFrame(documents)
        return df.fillna("")

    def __name_for(self, name: str | Path) -> str:
        """Returns just the filename drops folders and paths, ending in .csv, so names match CsvReportStore."""
        filename = Path(name).name
        if not filename.endswith(".csv"):
            filename += ".csv"
        return filename
