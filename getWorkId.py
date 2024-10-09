import requests

token=open('env.txt','r').readline()

def getWork(object):
    return object['name']

def getWorkName():
    response=requests.get('http://www.spot-setjetter.kro.kr:8080/api/spot/work',headers={
        "Authorization":token
    })

    sorted_data = sorted(response.json(), key=lambda x: x['id'])
    return list(map(getWork,sorted_data))

inputName=input('찾으려는 이름')
try:
    print(getWorkName().index(inputName))
except:
    print("찾으려는 작품명이 없습니다. (띄어쓰기를 확인해주세요)")