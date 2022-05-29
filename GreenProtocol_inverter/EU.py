from PVDataTrackComm import PVComm
import time, random

pvDataObj = PVComm()
pvDataObj.init_client()
import requests
import threading

def request_task(url, txinfo):
    try:
        requests.post(url, data = txinfo, timeout=1)
    except:
        pass

def fire_and_forget(url, txinfo):
    threading.Thread(target=request_task, args=(url, txinfo)).start()

url = 'http://192.168.236.67:3000/gcp'
#myobj = {'somekey': 'somevalue'}

#x = requests.post(url, data = myobj)
ratiokwhCreditFeed = 20
ratiokwhCreditConsumed = 5

while(1):
    for el in pvDataObj.recvUnpaid():
        kwh_consumed = el["kWh_total"] - el["kWh_feed"]
        total_credits = int(el["kWh_feed"]*ratiokwhCreditFeed + kwh_consumed * ratiokwhCreditConsumed)
        tokentype = 2 if el["state"] == "spain" else 1
        txinfo = {'receiver': el["wallet_address"], "t_type": tokentype, "amount" : total_credits}
        print(f"Received Info from producer: {el['producer_id']} -> issuing {total_credits} Credits ")
        try:
            if total_credits > 0:
                fire_and_forget(url, txinfo)
                pvDataObj.updatePaymentStatus(el["_id"])
        except:
            pass
    time.sleep(1)