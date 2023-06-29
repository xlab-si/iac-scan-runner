import uuid
from datetime import datetime
from typing import Dict, Any, List

from pymongo import MongoClient

from iac_scan_runner.utils import parse_json


class ScanProject:
    """Scan Project object."""

    def __init__(self, connection_string: str) -> None:
        """Initialize new user config result database, collection and client."""
        try:
            self.my_client: MongoClient[Dict[str, Any]] = MongoClient(connection_string)
            self.mydb = self.my_client["scandb"]
            self.mycol = self.mydb["projects"]
            self.connection_problem = False
        except Exception as e:
            print(f"Configuration persistence not available, error: {e}")

    def insert_project(self, result: dict[str, Any]) -> None:
        """
        Insert new project into database.

        :param result: Dictionary holding the project info
        """
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(result))

    def new_project(self, creator_id: str, active_config: str = "", check_list: List[str] = []) -> str:
        """
        Insert new project into database.

        :param creator_id: Identifier of project creator
        :param active_config: Identifier of currently active project configuration
        :param check_list: list of enabled checks
        """
        project_id = str(uuid.uuid4())
        project_json = {"project_id": project_id,
                        "creator_id": creator_id,
                        "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "active_config": active_config,
                        "checklist": check_list}

        if self.mycol is not None:
            self.mycol.insert_one(parse_json(project_json))
        return project_id

    def load_project(self, project_id: str) -> Dict[str, Any]:
        """
        Show scan project with given id.

        :param project_id: Identifier of a scan project
        :return: JSON object of project
        """
        if self.mycol is not None:
            myquery = {"project_id": project_id}
            data = self.mycol.find_one(myquery)
            if data is None:
                raise Exception("Project id does not exist")
        return data

    def add_check(self, project_id: str, check: str) -> None:
        """
        Add a new check to the list of enabled checks for particular project.

        :param project_id: Identifier of a scan project
        :param check: Name of the enabled check
        """
        if self.mycol is not None:
            current_project = self.load_project(project_id)
            current_list = current_project["checklist"]

            new = False

            if check not in current_list:
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

    def remove_check(self, project_id: str, check: str) -> None:
        """
        Remove the given check from the list of enabled checks for particular project.

        :param project_id: Identifier of a scan project
        :param check: Name of the disabled check
        """
        if self.mycol is not None:
            current_project = self.load_project(project_id)
            current_list = current_project["checklist"]
            current_list.remove(check) if check in current_list else None  # pylint: disable= expression-not-assigned
            myquery = {"project_id": project_id}
            new_value = {"$set": {"checklist": current_list}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))

    def get_project_check_list(self, project_id):
        """
        Get project check list.

        :param project_id: Identifier of a scan project
        """
        query = {"project_id": project_id}
        result = self.mycol.find_one(query, {"checklist": 1, "_id": 0})
        if result is None:
            raise Exception("Project id does not exist")
        return result["checklist"]
