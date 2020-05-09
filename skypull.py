import requests
import datetime
import json


with open("skybox_secrets.json", "r+") as f:
    secrets = json.load(f)["SKYBOX_SECRETS"]

#Default Authorizations, Should be passed in CLI Args
auths = {"X-Account": secrets["X-Account"], #Account ID
    "X-Api-Token": secrets["X-Api-Token"], #Internal API Key
    "X-Application-Token" : secrets["X-Application-Token"], #Registered App Token
    "Content-Type": secrets["Content-Type"]}


class SkyGrab:
    
    base = "https://skybox.vividseats.com/services"
    today = datetime.datetime.now() #Grab Date through DateTime Library
    vendors = {}

    def __init__(self, keys = auths):
        self.auths = keys

    def get_sold_inventory(self, payload = None): #Sends GET request for sold inventory
        default_payload = {"zoneSeating": "true",
        "invoiceDateFrom": SkyGrab.today.isoformat()[:-15] + "05:00:00.000",
        "invoiceDateTo": datetime.datetime.utcnow().isoformat(),
        "state": "NY",
        "fulfillmentStatus" : "PENDING"}
        payload = default_payload if payload == None else payload

        r = requests.get(SkyGrab.base +"/inventory/sold", params = payload, headers = self.auths)
        return SkyGrab.format_data(r.json())
    
    #s['rows'][0]['event']['venue']

    def get_inventory(self, payload = None): #Sends GET request for unsold inventory
        if payload == None:
            raise Exception("No filters provided.")
        
        r = requests.get(SkyGrab.base + "/inventory", params = payload, headers = self.auths)
        try:
            return r.json()
        except:
            print(r.status_code)
            return r.status_code

    @staticmethod
    def format_data(invoices_json): #Cleans up the data into an array of strings as needed for the buying sheet. Most error-prone part of the code
        events = []
        for i in invoices_json['rows']:
            event = [i["invoiceId"], i["event"]["name"], i["event"]["date"], i["event"]["venue"]["name"], i["section"],i["row"],i["seatNumbers"],i["quantity"]]
            event = [str(field) for field in event]
            events.append(event)
        return events

    def change_inventory(self,payload):
         r = requests.put(SkyGrab.base + "/inventory/bulk-update", data = json.dumps(payload), headers=self.auths)

         return r.json()
    
    
    def get_vendors(self,payload=None):
        r = requests.get(SkyGrab.base + "/vendors", params = {}, headers=self.auths)
        r = r.json()['rows']
        vendors = {}
        for i in r:
            vendors[i['displayName']] = {
                "venue" : i['displayName'],
                "id" : i['id'],
                'type' : i['type'],
                'city' : i['address']['city'],
                'state' : i['address']['state']}
        with open("skybox_vendors.json","w") as f:
            json.dump(vendors,f)
        return 1

    def get_vendorID(self,vendor):
        if SkyGrab.vendors == {}:
            with open("skybox_vendors.json") as f:
                SkyGrab.vendors = json.load(f)
        
        if vendor in SkyGrab.vendors:
            return SkyGrab.vendors[vendor]['id']
        else:
            return None

    def get_eventID(self, event_info):
        payload = { "eventDateFrom": event_info["event_date"].isoformat(),
                    "eventDateTo": (event_info['event_date'] + datetime.timedelta(minutes = 15)).isoformat(),
                    "keywords": event_info["event_name"],
                    "limit": 100,
                    "excludeParking": 'True',
                    'venue': event_info['venue']}
        r = requests.get(SkyGrab.base + "/events", params = payload, headers=self.auths)

        if r.json()['rowCount'] == 1:
            return r.json()['rows'][0]['id']
        else:
            print(">1 Event Found")
            return r

    def post_purchase(self,purchase_info):
        data = json.dumps(purchase_info)
        print(data)
        r = requests.post(url = SkyGrab.base + "/purchases", data = data, headers=self.auths)

        return r



""" dict_keys(['inHandDate', 'id', 
'accountId', 'eventId', 'quantity', 'notes', 'section', 'row', 'secondRow', 'lowSeat', 'highSeat', 'cost', 'faceValue',
 'tickets', 'ticketIds', 'stockType', 'splitType', 'customSplit', 'listPrice', 'expectedValue', 'publicNotes', 'attributes', 
 'status', 'inHandDaysBeforeEvent', 'lastPriceUpdate', 'createdBy', 'lastUpdateBy', 'version', 'tags', 'seatType', 
 'eventMapping', 'mappingId', 'exchangePosId', 'broadcast', 'zoneSeating', 'electronicTransfer', 'optOutAutoPrice',
  'hideSeatNumbers', 'vsrOption', 'replenishmentGroupId', 'replenishmentGroup', 'shownQuantity', 'ticketsMerged', 
  'ticketsSplit', 'filesUploaded', 'barCodesEntered', 'seatNumbers', 'listed', 'consignmentStatus', 'cooperative', 'holdId', 
'hold', 'unitCostAverage', 'faceValueAverage', 'currencies', 'received', 'vendorId', 'inHand', 'daysOld', 'event']) """