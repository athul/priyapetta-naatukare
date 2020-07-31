from fastapi import FastAPI, Request
from typing import Dict
import yaml
import os
import logging
import requests
import base64
from datetime import date

app = FastAPI()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")

def decodeData(data:Dict) -> str:
    enc = data['content']
    decodedBytes = base64.b64decode(enc)
    decodedStr = str(decodedBytes, "utf-8")
    logging.info("👉    Decoded Content")
    return decodedStr

async def sendTGMessage(message:str) -> str:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    msg_data = {'chat_id':chat_id,'text':message,"parse_mode":"Markdown"}
    resp = requests.post(url, msg_data).json()
    if resp['ok'] is False:
        logging.error("Message Not Send")
    else:
        logging.info("👉    Message Sent")

def getNewPush(sha:str) -> str:
    data = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/commits/{sha}').json()
    today = date.today().strftime("%d/%m/%Y")
    for item in data['files']:
        if ".pdf" in item['raw_url']:
            msg = f"**Date**:\t{today}\n\nNew PDF Uploaded\n\n[Find the File Here]({item['raw_url']})"
            sendTGMessage(msg)
            logging.info("👉    PDF Update Sent")
            return "PDF Update Sent"
        elif ".jpg" or ".jpeg" or ".png" in item['raw_url']:
            msg = f"**Date**:\t{today}\n\nNew File Uploaded\n\n[Download]({item['raw_url']})"
            sendTGMessage(msg)
            logging.info("👉    Image update Sent")
            return "Image update Sent"
        else:
            return None

def getAnnouncements() -> str:
    try:
        data = requests.get("https://api.github.com/repos/infincek/gatsby-site/contents/data/front-page-data/Announcements.yml").json()
    except ValueError:
        return "No Data Received"
    logging.info("👉    Acquired FrontPage Data")
    yaml_data = yaml.load(decodeData(data),Loader=yaml.FullLoader)
    date = yaml_data[0]['date'].strftime("%d/%m/%Y")
    return f"**Date** :\t{date}\n\n**Announcement** : \t{yaml_data[0]['data']}"

async def makeResponse(bd:Dict,pr_num:int) -> str:
    pr_file = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/pulls/{pr_num}/files').json()
    flname = pr_file[0]['filename']
    if "Announcement" in flname:
        resp = getAnnouncements()
        # logging.info(👉    resp)
        await sendTGMessage(resp)
        return "Announcements Found"
    else:
        return "Announcements not Found"
    


@app.post("/pr")
async def getResponse(request:Request):
    try:
        req_data = await request.json()
        logging.info("👉    Data Received")
    except ValueError:
        return "Data Not Received"
    try:
        if req_data['pull_request']['merged'] is True:
            await makeResponse(req_data,req_data['number'])
            return "Received and Processed"
    except KeyError:
        return "Not a merged PR"
        if req_data['pusher']['name'] != "":
            if req_data['deleted'] is True:
                return "PR Is Deleted"
        
    

@app.post("/push")
async def getPushes(request:Request):
    try:
        req_data = await request.json()
        logging.info("👉    Data Received")
    except ValueError:
        return "Data Not Received"
    finally:
        try:
            getNewPush(req_data['after'])
            return "Push Hook is Processed and Will be done"
        except KeyError:
            return "Not Valid Push Data"