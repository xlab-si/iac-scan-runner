import os
from datetime import datetime

import pymongo

from iac_scan_runner.utils import parse_json


class ResultsPersistence:
    def __init__(self):
        """
        Initialize new scan result database, collection and client
        """
        self.connect_db()

    def connect_db(self):
        """
        Initialize new scan result database, collection and client
        """

        try:
            connection_string = os.environ['MONGODB_CONNECTION_STRING']

            if connection_string:
                self.my_client = pymongo.MongoClient(connection_string)
                self.mydb = self.my_client["scandb"]
                self.mycol = self.mydb["results"]
                self.connection_problem = False

        # TODO: Consider more specific exceptions     
        except Exception as e:
            print("Scan result persistence not available")
            print(str(e))
            self.my_client = None
            self.mydb = None
            self.mycol = None
            self.connection_problem = True

    def insert_result(self, result: dict):
        """Inserts new scan result into database
        :param result: Dictionary holding the scan summary
        """
        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(result))

    def show_result(self, uuid4: str) -> str:
        """Shows scan result with given id
        :param uuid4: Identifier of a scan result
        :return: String representing the scan result record
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            mydoc = self.mycol.find(myquery)
            for x in mydoc:
                return str(x)

    def delete_result(self, uuid4: str):
        """Deletes the scan result with given id from database
        :param uuid4: Identifier of a scan result which is about to be deleted
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            self.mycol.delete_one(myquery)

    def show_all(self) -> str:
        """Shows all the scan records from the database
        :return: String of all database records concatenated
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            cursor = self.mycol.find({})
            output = ""
            for doc in cursor:
                output = output + str(doc)
            return output

    def days_passed(self, time_stamp: str) -> int:
        """Calculates how many days have passed between today and given timestamp
        :param time_stamp: Timestamp in format %m/%d/%Y, %H:%M:%S given as string
        :return: Integer which denotes the number of days passed
        """
        time1 = datetime.strptime(time_stamp, "%m/%d/%Y, %H:%M:%S")
        time2 = datetime.now()  # current date and time
        delta = time2 - time1
        string_delta = str(delta)

        if string_delta.find("days") > -1:
            days = string_delta.split(" ")
            days = days[0]
            return int(days)
        else:
            return 0

    def result_age(self, uuid4: str) -> int:
        """Calculates how long a scan result resides in database since its insertion
        :param uuid4: Identifier of a scan result
        :return: Integer denoting scan result age
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"uuid": uuid4}
            mydoc = self.mycol.find(myquery)
            for x in mydoc:
                scan_ts = x["time"]

            return self.days_passed(scan_ts)

    def periodic_clean_job(self):
        """Calculates how long a scan result resides in database since its insertion"""
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            cursor = self.mycol.find({})
            for doc in cursor:
                doc_uuid = doc["uuid"]
                age = self.result_age(doc_uuid)
                # TODO: Add environment variable instead of constant	                     
                if age > 14:
                    self.delete_result(doc_uuid)

    def all_scans_by_project(self, project_id: str) -> str:
        """Shows all the scan results from the database that belong to a particular project given by id
        :param project_id: Identifier of project where scan results belongs
        :return: All scan results for given project identifier
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"project_id": project_id}
            data = self.mycol.find_one(myquery)
            if data is None:
                raise Exception("Project id does not exist or there are no scan results")
            return data

