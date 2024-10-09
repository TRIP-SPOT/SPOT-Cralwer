import requests
from bs4 import BeautifulSoup
import csv

f=open('work.csv','r')
rdr=csv.reader(f)
[작품명배열, 촬영지들]=csv.reader(open('test.csv','r'))

workMapper=[]
작품명=작품명배열[0]

for line in rdr:
    workMapper.append(line[3])


def getSpotContentId(촬영지):
    response=requests.get('https://data.visitkorea.or.kr/search.do?keyword='+촬영지)
    soup=BeautifulSoup(response.content,'html.parser')
    try:
        content=soup.find(id="_searchList").find('tr').find('td').find('dl').find('dd').find('a').get_text()
        contentId=content.split('resource/')[1]
        return contentId
    except:
        return None

def getLatitude(trList):
    for tr in trList:
        if(tr.find('td').get_text().strip()=='geo-pos:lat'):
            return tr.find_all('td')[1].get_text().strip().split('(xsd:double)')[0]

def getLongitude(trList):
    for tr in trList:
        if(tr.find('td').get_text().strip()=='geo-pos:long'):
            return tr.find_all('td')[1].get_text().strip().split('(xsd:double)')[0]

def getSpotInformation(contentId):
    response=requests.get('https://data.visitkorea.or.kr/page/'+contentId)
    soup=BeautifulSoup(response.content,'html.parser')
    tbody=soup.find(class_="lodList tableLine").find('tbody').find_all('tr')
    lat=getLatitude(tbody)
    long=getLongitude(tbody)
    return {'lat':lat,'long':long}


for 촬영지 in 촬영지들:
    contentId=getSpotContentId(촬영지)
    if(contentId):
        pos=getSpotInformation(contentId)
        result={"workname":작품명,"workId":workMapper.index(작품명),"lat":pos["lat"], "long":pos["long"], 'contentId':contentId}
        print(result)