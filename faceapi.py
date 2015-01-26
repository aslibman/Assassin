import json
import os
from urllib2 import Request, urlopen
import base64
import os.path, time
import datetime

def kairosapiENROLL(facepath,id):
    with open(facepath,'rb') as img:
        data=img.read()
        encoded_img = data.encode("base64")
    values = """{
    "image": "%s",
    "subject_id": "%s",
    "gallery_name": "Assassin",
    "selector": "SETPOSE",
    "symmetricFill": "true"
    }"""% (encoded_img,id)
    

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/enroll', data=values, headers=headers)

    response_body = urlopen(request).read()
    d=json.loads(response_body)
    try:
        if d['images'][0]['transaction']['status']=='success':
            print True
            return True
        elif d['images'][0]['transation']['status']=='failure':
            print False
            return False
    except:
        return False

def kairosapiRECOGNIZE(facepath):
    with open(facepath,'rb') as img:
        data=img.read()
        encoded_img = data.encode("base64")
    values = """
    {
    "image": "%s",
    "gallery_name": "Assassin"
    }
    """%(encoded_img)

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/recognize', data=values, headers=headers)
    response_body= urlopen(request).read()
    d=json.loads(response_body)
    try:
        if d['images'][0]['transaction']['status']=='failure':
            return False
        elif d['images'][0]['transaction']['status']=='success':
            d=d['images'][0]['candidates']
            l=[]
            for x in d:
                for b in x:
                    if b!="enrollment_timestamp":
                        l.append(b)
            return l 
            
    except:
        return False

def kairosapiREMOVESUBJECT(id):
    values= """
    {"gallery_name":"Assassin",
    "subject_id":"%s"
    }
    """%(id)
    
    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/gallery/remove_subject', data=values, headers=headers)

    response_body = urlopen(request).read()
    d=json.loads(response_body)
    print d

def kairosapiDETECT(facepath):
    with open(facepath,'rb') as img:
        data=img.read()
        encoded_img = data.encode("base64")
    values = """
    {
    "image": "%s",
    "selector":"FACE"
    }
    """%(encoded_img)

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/detect', data=values, headers=headers)

    response_body = urlopen(request).read()
    d=json.loads(response_body)
    try:
        if d['images'][0]['status']=='Complete':
            print True
            return True
    except:
        if d['Errors'][0]['Message']=='no faces found in the image':
            print False
            return False
    return False

def kairosapiVIEW(galleryid):
    values = """
    {
    "gallery_name":"%s"
    }
    """%(galleryid)

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/gallery/view', data=values, headers=headers)

    response_body = urlopen(request).read()
    d=json.loads(response_body)
    print d
    
def timecheck(filesave):
    x= os.path.getctime(filesave)
    x=datetime.datetime.fromtimestamp(x)
    y=datetime.datetime.now()-datetime.timedelta(seconds=30)
    print x
    print y
    if x > y:
        print True
        return True
    else:
        print False
        return False
