import sqlite3
import time
from pymongo import MongoClient

__connection = sqlite3.connect('karma.db')
__c = __connection.cursor()
__client = MongoClient('localhost', 27017)

__c.execute('SELECT * FROM karma')
results = __c.fetchall()

for r in results:
    __client.aesthetics.users.update({'_id': str(r[0])},
            {'$set':
                {
                    'karma_timestamp': 1,
                    'karma': r[2]
                }
            }, upsert=True)

    print(r)

__connection.commit()
__connection.close()
__client.close()

