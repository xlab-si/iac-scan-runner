import pymongo
import bson.json_util as json_util
from bson.json_util import dumps
import json
from datetime import datetime

class ResultsPersistence:
    def __init__(self):
        """
        Initialize new scan result database, collection and client
        """        
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.mydb = self.myclient["scandb"]
        self.mycol = self.mydb["results"]

    def parse_json(self, data):
        return json.loads(json_util.dumps(data))

    def insert_result(self, result: dict):
        """Inserts new scan result into database
        :param result: Dictionary holding the scan summary
        """         
        self.mycol.insert_one(self.parse_json(result))


    def show_result(self, uuid4: str):
        """Shows scan result with given id
        :param uuid4: Identifier of a scan result
        """
        print('RESULT----------------------------------------------')
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.find(myquery)
        for x in mydoc:
            print(x)         

    def delete_result(self, uuid4: str):
        """Deletes the scan result with given id from database
        :param uuid4: Identifier of a scan result which is about to be deleted
        """
        print('DELETE RESULT------------------------------------')
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.delete_one(myquery)
                   

    def show_all(self):
        """Shows all the scan records from the database
        """
        print('RESULTS SHOW ALL------------------------------------------')
        cursor = self.mycol.find({})
        for doc in cursor:
            print(doc)
                           

    def days_passed(self, time_stamp: str):
        time1 = datetime.strptime(time_stamp, "%m/%d/%Y, %H:%M:%S") 
        time2 = datetime.now() # current date and time
        print(time2)
        delta = time2 - time1
        string_delta = str(delta)
        print(string_delta)
        if(string_delta.find("days")>-1):
            days = string_delta.split(" ")
            days = days[0]
            print(days)
            return int(days)
        else:
            print("0 days")	
            return 0    
   

    def result_age(self, uuid4: str):
        """Calculates how long a scan result resides in database since its insertion
        :param uuid4: Identifier of a scan result
        """
        print('AGE-------------------------------------------------------------------')
        myquery = { "uuid": uuid4 }
        mydoc = self.mycol.find(myquery)
        for x in mydoc:
            print(x["time"])
            scan_ts = x["time"]

        return self.days_passed(scan_ts)            
        
    def periodic_clean_job(self):
        cursor = self.mycol.find({})
        scan_ts = ""
        for doc in cursor:
            print(doc["time"])
            doc_uuid = doc["uuid"]                
            age = self.result_age(doc_uuid)
            if(age>14):
                print("delete")
            else:
                print("not_delete")
                                      
