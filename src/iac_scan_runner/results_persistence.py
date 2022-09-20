import pymongo
import bson.json_util as json_util
from bson.json_util import dumps
import json
from datetime import datetime
import os
class ResultsPersistence:
    def __init__(self):
    
        """
        Initialize new scan result database, collection and client
        """        
        
        try:
            connection_string = os.environ['MONGO_STRING']  
            print(connection_string)  
            self.myclient = pymongo.MongoClient(connection_string)
            self.mydb = self.myclient["scandb"]
            self.mycol = self.mydb["results"]
            self.connection_problem = False
            
        except Exception as e:
            print("Scan result persistence not available")
            self.connection_problem = True


    def parse_json(self, data):
        return json.loads(json_util.dumps(data))

    def insert_result(self, result: dict):
    
        """Inserts new scan result into database
        :param result: Dictionary holding the scan summary
        """         
        self.mycol.insert_one(self.parse_json(result))

    def show_result(self, uuid4: str) -> str:
    
        """Shows scan result with given id
        :param uuid4: Identifier of a scan result
        :return: String representing the scan result record
        """
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.find(myquery)
        for x in mydoc:
            return str(x)      

    def delete_result(self, uuid4: str):
    
        """Deletes the scan result with given id from database
        :param uuid4: Identifier of a scan result which is about to be deleted
        """
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.delete_one(myquery)


    def show_all(self) -> str:
    
        """Shows all the scan records from the database
        :return: String of all database records concatenated
        """
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
        time2 = datetime.now() # current date and time
        delta = time2 - time1
        string_delta = str(delta)
        if(string_delta.find("days")>-1):
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
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.find(myquery)
        for x in mydoc:
            scan_ts = x["time"]

        return self.days_passed(scan_ts)            
        
    def periodic_clean_job(self):
    
        """Calculates how long a scan result resides in database since its insertion
        :param uuid4: Identifier of a scan result
        """    
        cursor = self.mycol.find({})
        scan_ts = ""
        for doc in cursor:
            doc_uuid = doc["uuid"]                
            age = self.result_age(doc_uuid)
            if(age>14):
                self.delete_result(doc_uuid)                                      
