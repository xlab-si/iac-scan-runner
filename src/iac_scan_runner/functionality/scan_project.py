import os
import uuid
from datetime import datetime

import pymongo

from iac_scan_runner.utils import parse_json


class ScanProject:
    def __init__(self):
        """
        Initialize new user config result database, collection and client
        """
        self.connect_db()

    def connect_db(self):
        """
        Initialize new project collection connection into scan result database
        """

        try:
            connection_string = os.environ['MONGODB_CONNECTION_STRING']

            if connection_string:
                self.my_client = pymongo.MongoClient(connection_string)
                self.mydb = self.my_client["scandb"]
                self.mycol = self.mydb["projects"]
                self.connection_problem = False

        # TODO: Consider more specific exceptions     
        except Exception as e:
            print("Project persistence not available")
            print(str(e))
            self.my_client = None
            self.mydb = None
            self.mycol = None
            self.connection_problem = True

    def insert_project(self, result: dict):
        """Inserts new project into database
        :param result: Dictionary holding the project info
        """
        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(result))

    def new_project(self, creator_id: str, active_config: str, check_list: list = []):

        """Inserts new project into database
        :param creator_id: Identifier of project creator
        :param active_config: Identifier of currently active project configuration
        :param check_list: list of enabled checks
        """
        project_json = dict()
        project_json["project_id"] = str(uuid.uuid4())
        project_json["creator_id"] = creator_id

        project_json["time"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        if active_config:
            project_json["active_config"] = active_config
        else:
            project_json["active_config"] = ""

        project_json["checklist"] = check_list

        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(project_json))
            return project_json["project_id"]

    def load_project(self, project_id: str):

        """Shows scan project with given id
        :param project_id: Identifier of a scan project
        :return: JSON object of project
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"project_id": project_id}
            mydoc = self.mycol.find_one(myquery)
            if mydoc is None:
                raise Exception("Project id does not exist")
            return mydoc

    def set_config(self, project_id: str, config_id: str):

        """Changes an active configuration of a given scan project
        :param project_id: Identifier of a scan project
        :param config_id: Identifier of currently active project configuration that we want to assign     
        :return: JSON object of user
        """

        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:

            myquery = {"project_id": project_id}
            new_value = {"$set": {"active_config": config_id}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))

    def delete_project(self, project_id: str):

        """Deletes the project with given id from database
        :param project_id: Identifier of a project which is about to be deleted
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"project_id": project_id}
            self.mycol.delete_one(myquery)

    def all_projects(self) -> str:

        """Shows all the scan projects from the database
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

    def all_projects_by_user(self, creator_id: str) -> str:

        """Shows all the scan projects from the database created by guven user
        :param creator_id: Identifier of project creator        
        :return: String of all database records concatenated for given user creator
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"creator_id": creator_id}
            cursor = self.mycol.find(myquery)
            output = ""
            for doc in cursor:
                output = output + str(doc)
            return output

    def add_check(self, project_id: str, check: str):

        """Adds a new check to the list of enabled checks for particular project
        :param project_id: Identifier of a scan project
        :param check: Name of the enabled check     
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            current_project = self.load_project(project_id)
            current_list = current_project["checklist"]

            new = False

            if not (check in current_list):
                current_list.append(check)
                new = True
            try:
                if new:
                    myquery = {"project_id": project_id}
                    new_value = {"$set": {"checklist": current_list}}
                    self.mycol.find_one_and_update(myquery, new_value, upsert=True)
                else:
                    raise Exception(f"Check: {check} is already enabled.")
            except Exception as e:
                print(str(e))

    def remove_check(self, project_id: str, check: str):

        """Removes the given check from the list of enabled checks for particular project
        :param project_id: Identifier of a scan project
        :param check: Name of the disabled check     
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            current_project = self.load_project(project_id)
            current_list = current_project["checklist"]
            current_list.remove(check) if check in current_list else None
            myquery = {"project_id": project_id}
            new_value = {"$set": {"checklist": current_list}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))

    def get_project_check_list(self, project_id):
        """Get project check list

        :param project_id: Identifier of a scan project
        """
        query = {"project_id": project_id}
        result = self.mycol.find_one(query, {"checklist": 1, "_id": 0})
        if result is None:
            raise Exception("Project id does not exist")
        return result["checklist"]
