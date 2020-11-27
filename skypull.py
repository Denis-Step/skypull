import requests
import datetime
import json


with open("skybox_secrets.json", "r+") as f:
    secrets = json.load(f)["SKYBOX_SECRETS"]

# Default Authorizations, Should be passed in CLI Args, Fix this later when environment permits
auths = {"X-Account": secrets["X-Account"],  # Account ID
         "X-Api-Token": secrets["X-Api-Token"],  # Internal API Key
         # Registered App Token
         "X-Application-Token": secrets["X-Application-Token"],
         "Content-Type": secrets["Content-Type"]}


class SkyGrab:

    base = "https://skybox.vividseats.com/services"
    today = datetime.datetime.now()
    vendors = {}

    def __init__(self, keys=auths):
        self.auths = keys

    def get_events(self, params=None):
        if params == None:
            raise Exception("No parameters specified")
        r = requests.get(SkyGrab.base + "/events",
                         params=params, headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    def get_invoices(self, params=None):
        default_params = {"createdDateFrom": (SkyGrab.today - datetime.timedelta(days=365)).isoformat(),
                          "createdDateTo": datetime.datetime.utcnow().isoformat(),
                          }
        params = default_params if params == None else params
        r = requests.get(SkyGrab.base + "/invoices",
                         params=params, headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    def get_sold_inventory(self, params=None):  # Sends request for sold inventory
        default_params = {"zoneSeating": "true",
                          "invoiceDateFrom": (SkyGrab.today - datetime.timedelta(days=30)).isoformat(),
                          "invoiceDateTo": datetime.datetime.utcnow().isoformat(),
                          "state": "NY",
                          "fulfillmentStatus": "PENDING"}
        params = default_params if params == None else params
        r = requests.get(SkyGrab.base + "/inventory/sold",
                         params=params, headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    # s['rows'][0]['event']['venue']

    def get_inventory(self, params=None):  # Sendsrequest for unsold inventory
        default_params = {
            "createdDateFrom": (SkyGrab.today - datetime.timedelta(days=1)).isoformat(),
            "createdDateTo": datetime.datetime.utcnow().isoformat()}
        params = default_params if params is None else params

        r = requests.get(SkyGrab.base + "/inventory",
                         params=params, headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    @staticmethod
    # Cleans up the data into an array of strings as needed for the buying sheet. Brittle
    def format_data(invoices_json):
        events = []
        for i in invoices_json['rows']:
            event = [i["invoiceId"], i["event"]["name"], i["event"]["date"], i["event"]
                     ["venue"]["name"], i["section"], i["row"], i["seatNumbers"], i["quantity"]]
            event = [str(field) for field in event]
            events.append(event)
        return events

    def change_inventory(self, payload):
        r = requests.put(SkyGrab.base + "/inventory/bulk-update",
                         data=json.dumps(payload), headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    def get_vendors(self, payload=None):  # Update master vendors file
        r = requests.get(SkyGrab.base + "/vendors",
                         params={}, headers=self.auths)
        try:
            return r.json()['rows']
        except Exception:
            return r.status_code

    # Bad Name & Usage, Fix this!!
    def get_eventID(self, event_info):
        params = {"eventDateFrom": event_info["event_date"].isoformat(),
                  "eventDateTo": (event_info['event_date'] + datetime.timedelta(minutes=15)).isoformat(),
                  "keywords": event_info["event_name"],
                  "limit": 100,
                  "excludeParking": 'True',
                  'venue': event_info['venue']}
        r = requests.get(SkyGrab.base + "/events",
                         params=params, headers=self.auths)

        if r.json()['rowCount'] == 1:
            return r.json()['rows'][0]['id']
        else:
            print(">1 Event Found")
            return r

    def post_purchase(self, purchase_info):
        data = json.dumps(purchase_info)
        r = requests.post(url=SkyGrab.base + "/purchases",
                          data=data, headers=self.auths)
        return r.status_code

# Schema below:


""" dict_keys(['inHandDate', 'id', 
'accountId', 'eventId', 'quantity', 'notes', 'section', 'row', 'secondRow', 'lowSeat', 'highSeat', 'cost', 'faceValue',
 'tickets', 'ticketIds', 'stockType', 'splitType', 'customSplit', 'listPrice', 'expectedValue', 'publicNotes', 'attributes', 
 'status', 'inHandDaysBeforeEvent', 'lastPriceUpdate', 'createdBy', 'lastUpdateBy', 'version', 'tags', 'seatType', 
 'eventMapping', 'mappingId', 'exchangePosId', 'broadcast', 'zoneSeating', 'electronicTransfer', 'optOutAutoPrice',
  'hideSeatNumbers', 'vsrOption', 'replenishmentGroupId', 'replenishmentGroup', 'shownQuantity', 'ticketsMerged', 
  'ticketsSplit', 'filesUploaded', 'barCodesEntered', 'seatNumbers', 'listed', 'consignmentStatus', 'cooperative', 'holdId', 
'hold', 'unitCostAverage', 'faceValueAverage', 'currencies', 'received', 'vendorId', 'inHand', 'daysOld', 'event']) """
