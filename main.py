from fastapi import FastAPI, Request
from typing import Dict
import yaml
import requests
import base64

app = FastAPI()

def decodeData(data:Dict) -> str:
    enc = data['content']
    decodedBytes = base64.b64decode(enc)
    decodedStr = str(decodedBytes, "utf-8")
    return decodedStr

def sendTGMessage(message):
    
def getAnnouncements() -> Dict:
    data = requests.get("https://api.github.com/repos/infincek/gatsby-site/contents/data/front-page-data/Announcements.yml").json()
    yaml_data = yaml.load(decodeData(data),Loader=yaml.FullLoader)
    return yaml_data[0]['data']

async def makeResponse(bd:Dict,pr_num:int) -> str: 
    pr_file = requests.get(f'https://api.github.com/repos/infincek/gatsby-site/pulls/{pr_num}/files').json()
    flname = pr_file[0]['filename']
    if "Announcement" in flname:
        resp = getAnnouncements()
    else:
        pass
    
    
@app.post("/point")
async def getResponse(request:Request):
    req_data = await request.json()
    if bd['merged'] == "true":
        await makeResponse(req_data,req_data['number'])
    return "Cool"