import pymongo
import bson.json_util as json_util
from bson.json_util import dumps
import json
from datetime import datetime
import os
import uuid


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
            
            if(connection_string):
                self.myclient = pymongo.MongoClient(connection_string)
                self.mydb = self.myclient["scandb"]
                self.mycol = self.mydb["configs"]
                self.connection_problem = False
        
        # TODO: Consider more specific exceptions     
        except Exception as e:
            print("Configuration persistence not available")
            print(str(e))
            self.myclient = None
            self.mydb = None
            self.mycol = None
            self.connection_problem = True


    def parse_json(self, data):
        return json.loads(json_util.dumps(data))

    def insert_config(self, result: dict):
    
        """Inserts new config into database
        :param result: Dictionary holding the project info
        """     
        if(self.connection_problem == True):
            self.connect_db()
        if(self.mycol != None):
            self.mycol.insert_one(self.parse_json(result))

    def new_config(self, creatorid: str, parameters: dict):
    
        """Inserts new project config into database
        :param creatorid: Identifier of project creator
        :param result: Identifier of a new configuration
        """     
        config_json = dict()
        config_json["configid"] = str(uuid.uuid4())
        config_json["creatorid"] = creatorid
                      
        if(parameters):
            config_json["parameters"] = dict()
            config_json["parameters"] = parameters            
        else:
            config_json["parameters"] = dict()
            
        if(self.connection_problem == True):
            self.connect_db()
        if(self.mycol != None):
            self.mycol.insert_one(self.parse_json(config_json))
            return config_json["configid"]
         
    def load_config(self, configid: str):
    
        """Shows scan project with given id
        :param projectid: Identifier of a scan project
        :return: JSON object of project
        """
        if(self.connection_problem==True):
            self.connect_db()
            
        if(self.mycol != None):                
            myquery = { "configid": configid }
            mydoc = self.mycol.find(myquery)
            for x in mydoc:
                return x

    def set_parameters(self, configid: str, parameters: dict):
    
        """Changes an active configuration of a given scan project
        :param projectid: Identifier of a scan project
        :param configid: Identifier of currently active project configuration that we want to assign     
        :return: JSON object of user
        """

        if(self.connection_problem == True):
            self.connect_db()

        if(self.mycol != None):           

            myquery = { "configid": configid }
            new_value = { "$set": { "parameters": parameters } }
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))   
    
    def delete_config(self, configid: str):
    
        """Deletes the configuration with given id from database
        :param configid: Identifier of a project configuration which is about to be deleted
        """
        if(self.connection_problem==True):
            self.connect_db()
            
        if(self.mycol != None):          
            myquery = { "configid": configid }
            mydoc = self.mycol.delete_one(myquery)

    def all_configs(self) -> str:
    
        """Shows all the scan project configurations from the database
        :return: String of all database records concatenated
        """
        if(self.connection_problem==True):
            self.connect_db()
            
        if(self.mycol != None):        
            cursor = self.mycol.find({})
            output = ""
            for doc in cursor:
                output = output + str(doc)
            return output	                                                       
