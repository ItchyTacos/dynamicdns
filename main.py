import requests
from dotenv import load_dotenv
import os
import json

#load all keys and ids needed
load_dotenv(".env")
ZONE_ID = os.environ.get("ZONE_ID")
CLOUDFLARE_EMAIL = os.environ.get("CLOUDFLARE_EMAIL")
API_KEY = os.environ.get("API_KEY")
#RECORD ID NOT ZONE ID
HOME_ID = os.environ.get("HOME_ID")

#get current public ip
pub_ip = requests.get("https://ifconfig.me").text.strip()


#setup to avoid unnecicary calls
if os.path.exists("prev.txt"):
    with open("prev.txt") as file:
        prev = file.readline().strip()
else:
    prev = ""

if pub_ip != prev:

    #get cloudflare ip record for zone ID
    response = requests.request(method="GET", url=f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{HOME_ID}", headers={"X-Auth-Email": f"{CLOUDFLARE_EMAIL}","X-Auth-Key": f"{API_KEY}", "content-type": "application/json"})

    resp = response.json()

    if not resp.get("success"):
        print("Cloudflare API error:", json.dumps(resp, indent=2))
        exit(1)

    cf_ip = resp["result"]["content"]
    with open("prev.txt","w") as file:
        file.write(pub_ip.strip())

    #if there's any mismatch correct it
    if (pub_ip != cf_ip):

        #write json to send
        update_json = {
            "type": resp["result"]["type"],
            "name": resp["result"]["name"],
            "content": pub_ip
        }
        #update cloudflare record
        response = requests.request(method="PATCH", url=f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{HOME_ID}",
                                     headers={"X-Auth-Email": f"{CLOUDFLARE_EMAIL}","X-Auth-Key": f"{API_KEY}", "content-type": "application/json"},
                                     json=update_json)
        resp = response.json()
        if not resp.get("success"):
            print("Cloudflare API error:", json.dumps(resp, indent=2))
            exit(1)

        