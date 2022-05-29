from PVDataTrackComm import PVComm
import time, random

pvDataObj = PVComm(producer_id=1052, zipcode="1230", state="Austria", plant_size=6.2, energy_type="PV", wallet_address="austria1.testnet")
pvDataObj.init_client()

while(1):
    
    pvDataObj.kWh_total = random.randrange(int(pvDataObj.plant_size*40), int(pvDataObj.plant_size*70), 10)/100
    pvDataObj.kWh_feed = pvDataObj.kWh_total * 0.2
    print(f"Producer: {pvDataObj.producer_id} - Total kWh: {pvDataObj.kWh_total} - Feed KWh {pvDataObj.kWh_feed} | Country: {pvDataObj.state} - ZIP Code: {pvDataObj.zipcode}")
    pvDataObj.timestamp = time.time()
    pvDataObj.transmit2GOV()
    time.sleep(5)