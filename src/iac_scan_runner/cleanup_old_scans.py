import pymongo
import bson.json_util as json_util
from bson.json_util import dumps
import json
from datetime import datetime

import schedule
import time
from results_persistence import ResultsPersistence
                
def periodic_clean_job():
    persistence_manager = ResultsPersistence()
    
    cursor = persistence_manager.mycol.find({})
    scan_ts = ""
    for doc in cursor:
        print(doc["time"])
        doc_uuid = doc["uuid"]                
        age = persistence_manager.result_age(doc_uuid)
        if(age>14):
            print("delete")
        else:
            print("not_delete")
                                                                            
#schedule.every().day.at("08:54").do(periodic_clean_job)
schedule.every().second.do(periodic_clean_job)
while True:
    schedule.run_pending()
    time.sleep(1)                                      
