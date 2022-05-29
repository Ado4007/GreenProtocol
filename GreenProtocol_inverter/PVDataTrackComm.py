from dataclasses import dataclass
from quopri import encodestring
from sqlite3 import Timestamp
import pymongo
from dataclasses import dataclass
import time

status2str = {0: "unpaid",
              1: "payment init.",
              2: "paid"}

@dataclass(init=True)
class PVComm:
    url :str = "mongodb://localhost:27017/"
    client : pymongo.MongoClient = None
    db_name = "EU_Energy_DB"
    db = None
    producer_id: int = 0
    kWh_total: float = 0
    kWh_feed: float = 0
    state: str = ""
    zipcode: str = ""
    energy_type : str = ""
    plant_size : float = 0
    wallet_address: str = ""
    timestamp : int = time.time()
    initialized : bool = False
    status : int = 0

    def init_client(self):
        self.client = pymongo.MongoClient(self.url)
        self.db = self.client[self.db_name]["GreenProtocol"]
        self.initialized = True

    def transmit2GOV(self):
        if not( len(self.state) < 1 or len(self.zipcode) < 3 or len(self.energy_type) < 1 or self.plant_size < 1 or  
           len(self.wallet_address) == 0 or self.zipcode == 0 or self.producer_id == 0 or self.kWh_total == 0 or self.timestamp == 0):
            entry = {"producer_id" : self.producer_id,
                     "kWh_total" : self.kWh_total,
                     "kWh_feed" : self.kWh_feed,
                     "state" : self.state,
                     "zipcode" : self.zipcode,
                     "energy_type" : self.energy_type,
                     "plant_size" : self.plant_size,
                     "wallet_address" : self.wallet_address,
                     "timestamp" : self.timestamp,
                     "status": 0}
            self.db.insert_one(entry)

    def updatePaymentStatus(self, objectid):
        result = self.db.update_one({"_id" : objectid}, {"$inc": {"status": 1}}, upsert=True)

    def recvUnpaid(self):
        return self.db.find({"status" : 0}).sort("timestamp")

    def recvLastEntriesFromDB(self, lastXEntries: int = 5):
        return self.db.find({"producer_id" : self.producer_id}).sort({"timestamp":1}).limit(lastXEntries)