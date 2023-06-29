import os
import time

import schedule  # type: ignore

from iac_scan_runner.functionality.results_persistence import ResultsPersistence


def periodic_clean_job():
    """Periodic cleanup of scan results."""
    connection_string = os.environ["MONGODB_CONNECTION_STRING"]
    persistence_manager = ResultsPersistence(connection_string)
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
