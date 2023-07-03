from typing import Dict, Any, Optional

from pymongo import MongoClient

from iac_scan_runner.utils import parse_json, days_passed


class ResultsPersistence:
    """Result persistance class object."""

    def __init__(self, connection_string: str) -> None:
        """Initialize new user config result database, collection and client."""
        try:
            self.my_client: MongoClient[Dict[str, Any]] = MongoClient(connection_string)
            self.mydb = self.my_client["scandb"]
            self.mycol = self.mydb["results"]
            self.connection_problem = False
        except Exception as e:
            print(f"Configuration persistence not available, error: {e}")

    def insert_result(self, result: Dict[str, Any]) -> None:
        """
        Insert new scan result into database.

        :param result: Dictionary holding the scan summary
        """
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(result))

    def show_result(self, uuid4: str) -> Optional[Dict[str, Any]]:
        """
        Show scan result with given id.

        :param uuid4: Identifier of a scan result
        :return: String representing the scan result record
        """
        data = None
        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            data = self.mycol.find_one(myquery)
            if data is None:
                raise Exception("Project id does not exist or there are no scan results")
        return data

    def delete_result(self, uuid4: str) -> None:
        """
        Delete the scan result with given id from database.

        :param uuid4: Identifier of a scan result which is about to be deleted
        """
        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            self.mycol.delete_one(myquery)

    def show_all(self) -> str:
        """
        Show all the scan records from the database.

        :return: String of all database records concatenated
        """
        output = ""
        if self.mycol is not None:
            cursor = self.mycol.find({})
            for doc in cursor:
                output = output + str(doc)
        return output

    def result_age(self, uuid4: str) -> int:
        """
        Calculate how long a scan result resides in database since its insertion.

        :param uuid4: Identifier of a scan result
        :return: Integer denoting scan result age
        """
        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            mydoc = self.mycol.find(myquery)
            for time in mydoc:
                scan_ts = time["time"]

        return days_passed(scan_ts)

    def periodic_clean_job(self):
        """Calculate how long a scan result resides in database since its insertion."""
        if self.mycol is not None:
            cursor = self.mycol.find({})
            for doc in cursor:
                doc_uuid = doc["uuid"]
                age = self.result_age(doc_uuid)
                if age > 14:  # TODO: Add environment variable instead of constant
                    self.delete_result(doc_uuid)

    def get_scan_result(self, project_id: str, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Show all the scan results from the database that belong to a particular project given by id.

        :param project_id: Identifier of project where scan results belongs
        :param result_id: Identifier of scan result
        :return: All scan results for given project identifier
        """
        data = None
        if self.mycol is not None:
            myquery = {"project_id": project_id, "uuid": result_id}
            data = self.mycol.find_one(myquery, {"_id": 0})
            if data is None:
                raise Exception("Project id or uuid does not exist or there are no scan results")
        return data
