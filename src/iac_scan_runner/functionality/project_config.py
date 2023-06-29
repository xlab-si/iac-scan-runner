import uuid
from typing import Dict, Any, Optional

from pymongo import MongoClient

from iac_scan_runner.utils import parse_json


class ProjectConfig:
    """Project config class object."""

    def __init__(self, connection_string: str) -> None:
        """Initialize new user config result database, collection and client."""
        try:
            self.my_client: MongoClient[Dict[str, Any]] = MongoClient(connection_string)
            self.mydb = self.my_client["scandb"]
            self.mycol = self.mydb["configs"]
            self.connection_problem = False
        except Exception as e:
            print(f"Configuration persistence not available, error: {e}")

    def insert_config(self, result: Dict[Any, Any]) -> None:
        """
        Insert new config into database.

        :param result: Dictionary holding the project information
        """
        self.mycol.insert_one(parse_json(result))

    def new_config(self, creator_id: str, parameters: Dict[Any, Any]) -> str:
        """
        Insert new project config into database.

        :param creator_id: Identifier of project creator
        :param parameters: project configuration parameters
        :return: configuration identifier
        """
        config_id = str(uuid.uuid4())
        config_json = {"config_id": config_id, "creator_id": creator_id, "parameters": {}}
        if parameters:
            config_json["parameters"] = parameters
        self.mycol.insert_one(parse_json(config_json))
        return config_id

    def load_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Show scan project with given id.

        :param config_id: Identifier of a configuration
        :return: JSON object of project
        """
        if self.mycol is not None:
            myquery = {"config_id": config_id}
            return self.mycol.find_one(myquery)
        return None

    def set_parameters(self, config_id: str, parameters: Dict[Any, Any]) -> None:
        """
        Change an active configuration of a given scan project.

        :param config_id: Identifier of currently active project configuration that we want to assign
        :param parameters:
        :return: JSON object of user
        """
        if self.mycol is not None:
            myquery = {"config_id": config_id}
            new_value = {"$set": {"parameters": parameters}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(f"Could not update project configuration {config_id} error: {e}")

    def delete_config(self, config_id: str) -> None:
        """
        Delete the configuration with given id from database.

        :param config_id: Identifier of a project configuration which is about to be deleted
        """
        if self.mycol is not None:
            myquery = {"config_id": config_id}
            self.mycol.delete_one(myquery)

    def all_configs(self) -> str:
        """
        Show all the scan project configurations from the database.

        :return: String of all database records concatenated
        """
        output = ""
        if self.mycol is not None:
            cursor = self.mycol.find({})
            for doc in cursor:
                output = output + str(doc)
        return output
