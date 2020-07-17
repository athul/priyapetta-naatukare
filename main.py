from fastapi import FastAPI, Request
from typing import Dict
import yaml
import os
import logging
import requests
import base64

app = FastAPI()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")

def decodeData(data:Dict) -> str:
    enc = data['content']
    decodedBytes = base64.b64decode(enc)
    decodedStr = str(decodedBytes, "utf-8")
    logging.info("Decoded Content")
    return decodedStr

def sendTGMessage(message:str) -> str:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    msg_data = {'chat_id':chat_id,'text':message,"parse_mode":"Markdown"}
    resp = requests.post(url, msg_data).json()
    if resp['ok'] is False:
        logging.info("Message Not Send")
    else:
        logging.error("Message Sent")

def getNewPush(sha:str) -> str:
    data = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/commits/{sha}').json()
    for item in data['files']:
        if "pdf" in item['raw_url']:
            msg = f"New PDF Uploaded\n\n{item['raw_url'])}"
            sendTGMessage(msg)
            logging.info("File Update Sent")
        else:
            return None

def getAnnouncements() -> str:
    try:
        data = requests.get("https://api.github.com/repos/infincek/gatsby-site/contents/data/front-page-data/Announcements.yml").json()
    except ValueError:
        return "No Data Received"
    logging.info("Acquired FrontPage Data")
    yaml_data = yaml.load(decodeData(data),Loader=yaml.FullLoader)
    date = yaml_data[0]['date'].strftime("%d/%m/%Y")
    return f"**Date** :\t{date}\n\n**Announcement** : \t{yaml_data[0]['data']}"

def makeResponse(bd:Dict,pr_num:int) -> str: 
    pr_file = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/pulls/{pr_num}/files').json()
    flname = pr_file[0]['filename']
    if "Announcement" in flname:
        resp = getAnnouncements()
        logging.info("Announcements Found")
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
        if req_data['pull_request']['merged'] is True:
           makeResponse(req_data,req_data['number'])
        elif req_data['pusher']['name'] != "": 
            if req_data['deleted'] is True:
                return "PR Is Deleted"
            else:
                getNewPush(req_data['after'])
    except KeyError:
        return "Merge Key not found, Not a PR Merge Hook"
    else:
        return "Not Found"