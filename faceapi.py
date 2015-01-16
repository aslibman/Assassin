import json
import os
from urllib2 import Request, urlopen
import base64


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
    print response_body

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

    response_body = urlopen(request).read()
    print response_body

def kairosapiREMOVESUBJECT(id):
    values= """
    {"gallery_name":"Assassin",
    "subject_id":%s"
    }
    """%(id)
    
    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/remove_subject', data=values, headers=headers)

    response_body = urlopen(request).read()
    print response_body

def kairosapiDETECT(facepath):
    values= """
    {
    "image":%s,
    "selector":"SETPOSE"
    }
    """%(facepath)
    
    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/detect', data=values, headers=headers)

    response_body = urlopen(request).read()
    print response_body
