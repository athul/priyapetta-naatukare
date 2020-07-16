from fastapi import FastAPI, Request
from typing import Dict
import yaml
import os
import requests
import base64

app = FastAPI()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")

def decodeData(data:Dict) -> str:
    enc = data['content']
    decodedBytes = base64.b64decode(enc)
    decodedStr = str(decodedBytes, "utf-8")
    print("Decoded Content")
    return decodedStr

def sendTGMessage(message:str) -> str:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    msg_data = {'chat_id':chat_id,'text':message,"parse_mode":"Markdown"}
    resp = requests.post(url, msg_data).json()
    if resp['ok'] is False:
        print("Message Not Send")
    else:
        print("Message Sent")


def getAnnouncements() -> str:
    try:
        data = requests.get("https://api.github.com/repos/infincek/gatsby-site/contents/data/front-page-data/Announcements.yml").json()
    except ValueError:
        return "No Data Received"
    print("Acquired FrontPage Data")
    yaml_data = yaml.load(decodeData(data),Loader=yaml.FullLoader)
    date = yaml_data[0]['date'].strftime("%d/%m/%Y")
    return f"**Date** :\t{date}\n\n**Announcement** : \t{yaml_data[0]['data']}"

def makeResponse(bd:Dict,pr_num:int) -> str: 
    pr_file = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/pulls/{pr_num}/files').json()
    flname = pr_file[0]['filename']
    if "Announcement" in flname:
        resp = getAnnouncements()
        print("Announcements Found")
    else:
        return "Announcements not Found"
    sendTGMessage(resp)
    
    
@app.post("/point")
async def getResponse(request:Request):
    try:
        req_data = await request.json()
    except ValueError:
        return "Data Not Received"
    try:
        if req_data['pull_request']['merged'] == "true":
           makeResponse(req_data,req_data['number'])
    except KeyError:
        return "Merge Key not found, Not a PR Merge ßHook"
    else:
        return "Not Found"