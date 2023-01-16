import os
import uuid

import pymongo

from iac_scan_runner.utils import parse_json


class ProjectConfig:
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

                # TODO: Extract these names in a separate object or variable
                self.mydb = self.my_client["scandb"]
                self.mycol = self.mydb["configs"]
                self.connection_problem = False

        # TODO: Consider more specific exceptions     
        except Exception as e:
            print("Configuration persistence not available, error: {e}")
            self.my_client = None
            self.mydb = None
            self.mycol = None
            self.connection_problem = True

    def insert_config(self, result: dict):
        """Inserts new config into database
        :param result: Dictionary holding the project info
        """
        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(result))

    def new_config(self, creator_id: str, parameters: dict) -> str:
        """Inserts new project config into database
        :param creator_id: Identifier of project creator
        :param parameters: project configuration parameters
        :return: configuration identifier
        """
        config_json = dict()

        # TODO: 	Add this names into object
        config_json["config_id"] = str(uuid.uuid4())
        config_json["creator_id"] = creator_id

        if parameters:
            config_json["parameters"] = dict()
            config_json["parameters"] = parameters
        else:
            config_json["parameters"] = dict()

        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(parse_json(config_json))
            return config_json["config_id"]

    def load_config(self, config_id: str) -> dict:
        """Shows scan project with given id
        :param config_id: Identifier of a configuration
        :return: JSON object of project
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"config_id": config_id}
            mydoc = self.mycol.find(myquery)
            for x in mydoc:
                return x

    def set_parameters(self, config_id: str, parameters: dict):
        """Changes an active configuration of a given scan project
        :param config_id: Identifier of currently active project configuration that we want to assign
        :param parameters:
        :return: JSON object of user
        """

        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"config_id": config_id}
            new_value = {"$set": {"parameters": parameters}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(f"Could not update project configuration {config_id} error: {e}")

    def delete_config(self, config_id: str):
        """Deletes the configuration with given id from database
        :param config_id: Identifier of a project configuration which is about to be deleted
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:
            myquery = {"config_id": config_id}
            self.mycol.delete_one(myquery)

    def all_configs(self) -> str:
        """Shows all the scan project configurations from the database
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
