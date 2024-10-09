import requests

token=open('env.txt','r').readline()

def getWork(object):
    return object['name']


def getWorkName():
    response=requests.get('http://www.spot-setjetter.kro.kr:8080/api/spot/work',headers={
        "Authorization":token
    })
    workDict={}
    for o in response.json():
        workDict[o['name']]=o['id']
    return workDict

inputName=input('찾으려는 이름')
try:
    print(getWorkName()[inputName])
except:
    print("찾으려는 작품명이 없습니다. (띄어쓰기를 확인해주세요)")