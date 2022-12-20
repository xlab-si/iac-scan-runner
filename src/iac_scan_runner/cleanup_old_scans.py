import time

import schedule

from results_persistence import ResultsPersistence


def periodic_clean_job():
    persistence_manager = ResultsPersistence()

    cursor = persistence_manager.mycol.find({})
    for doc in cursor:
        doc_uuid = doc["uuid"]
        age = persistence_manager.result_age(doc_uuid)
        if age > 14:
            persistence_manager.delete_result(doc_uuid)


schedule.every().day.at("00:00").do(periodic_clean_job)
while True:
    schedule.run_pending()
    time.sleep(1)
