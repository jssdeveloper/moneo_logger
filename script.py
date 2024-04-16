import requests, time

test_api_key = "GEmAGPsdz6Rgad9SE2qesg"
test_comp_id = "53f98a26-041ecdf6-4cf71dcd-0474b2b3-b7c42fd6"
test_server = "https://ossa.moneo.lv:15000"

class MoneoApi:
    def __init__(self, api_key, comp_id, server):
        self.api_key = api_key
        self.comp_id = comp_id
        self.server = server
        self.headers = {"Authorization": api_key}
        self.default_body = {
            "request": {
                "compuid": comp_id
            }
        }

    def create_invoice(self):
        body = self.default_body
        body["data"] = {
            "sales.invoices":{
                "fieldlist":["sernr","custcode"],
                "data":[["240014","1036"]]
            }}
        
        res = requests.post(self.server + "/api/v2/sales.invoices/create/", json=body, headers=self.headers)
        
        message = res.json()["result"][0][1][0]
        if message == None:
            message = "VAT code created successfully"
        return message

    
    def create_vatcode(self):
        body = self.default_body
        body["data"] = {
            "finance.taxes":{
                "fieldlist":["code","taxtype"],
                "data":[["78","945-"]]
            }}
        
        res = requests.post(self.server + "/api/v2/finance.taxes/create/", json=body, headers=self.headers)
        

        message = res.json()["result"][0][1][0]
        if message == None:
            message = "VAT code created successfully"
        return message
    

mon = MoneoApi(test_api_key, test_comp_id, test_server)

# create sqlite connection
import sqlite3
conn = sqlite3.connect("logger.db")
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS moneo_log
             (id INTEGER PRIMARY KEY, invoices TEXT, vatcodes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')


while True:
    invoices = mon.create_invoice()
    vatcodes = mon.create_vatcode()

    # Fetch last record by timestamp, select invoices, vatcodes
    c.execute("SELECT invoices, vatcodes FROM moneo_log ORDER BY created_at DESC LIMIT 1")
    result = c.fetchone()

    try:
        last_db_invoice, last_db_vatcode = result
    except TypeError:
        last_db_invoice, last_db_vatcode = None, None

    if invoices != last_db_invoice or vatcodes != last_db_vatcode:
        # Insert new record
        c.execute("INSERT INTO moneo_log (invoices, vatcodes) VALUES (?, ?)", (invoices, vatcodes))
        conn.commit()
        print("New record inserted")
    else:
        print("No new records to insert")

    time.sleep(5)