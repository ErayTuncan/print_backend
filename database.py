import pymongo
from datetime import datetime

myClient = pymongo.MongoClient("mongodb://localhost:27017/")
printDB = myClient["print"]
fileRecordsCOL = printDB["file_records"]


def db_create_file_record(record):
    record['datetime'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    id = str(fileRecordsCOL.insert_one(record))
    return id


def db_query_file_record(fileuuid):
    record = fileRecordsCOL.find_one({'fileuuid': fileuuid})
    return record