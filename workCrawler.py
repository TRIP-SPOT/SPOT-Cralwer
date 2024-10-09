import requests
from bs4 import BeautifulSoup
import csv

cities = [
    "서울", "부산", "광주", "대전", "대구", "세종", "울산", "인천",

    # GYEONGGI
    "수원", "성남", "의정부", "안양", "부천", "광명", "평택", "안산", "고양", 
    "과천", "구리", "남양주", "오산", "시흥", "군포", "의왕", "하남", "용인", 
    "파주", "이천", "안성", "김포", "화성", "광주", "양주", "포천", "여주", 
    "동두천", "연천", "가평", "양평",

    # GANGWON
    "춘천", "원주", "강릉", "동해", "태백", "속초", "삼척", "홍천", "횡성", 
    "영월", "평창", "정선", "철원", "화천", "양구", "인제", "고성", "양양",

    # GYEONGBUK
    "포항", "경주", "김천", "안동", "구미", "영주", "영천", "상주", "문경", 
    "경산", "군위", "의성", "청송", "영양", "영덕", "청도", "고령", "성주", 
    "칠곡", "예천", "봉화", "울진", "울릉",

    # GYEONGNAM
    "창원", "진주", "통영", "사천", "김해", "밀양", "거제", "양산", "의령", 
    "함안", "창녕", "고성", "남해", "하동", "산청", "함양", "거창", "합천",

    # JEJU
    "제주", "서귀포",

    # CHUNGBUK
    "청주", "충주", "제천", "보은", "옥천", "영동", "증평", "진천", "괴산", 
    "음성", "단양",

    # CHUNGNAM
    "천안", "공주", "보령", "아산", "서산", "논산", "계룡", "당진", "금산", 
    "부여", "서천", "청양", "홍성", "예산", "태안",

    # JEONBUK
    "전주", "군산", "익산", "정읍", "남원", "김제", "완주", "진안", "무주", 
    "장수", "임실", "순창", "고창", "부안",

    # JEONNAM
    "목포", "여수", "순천", "나주", "광양", "담양", "곡성", "구례", "고흥", 
    "보성", "화순", "장흥", "강진", "해남", "영암", "무안", "함평", "영광", 
    "장성", "완도", "진도", "신안"
]

regions = [
    "강원특별자치도", "경기도", "경상북도", "경상남도", "전라북도", "전라남도", "충청북도", "충청남도", 
    "서울특별시", "인천광역시", "대구광역시", "대전광역시", "세종특별자치시", "부산광역시", "광주광역시", "울산광역시", "제주특별자치도"
]

region_Mapper={
    "서울특별시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "광주광역시": "광주",
    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",
}

def getWork(object):
    return object['name']

token=open('env.txt','r').readline()
def getWorkName():
    response=requests.get('http://www.spot-setjetter.kro.kr:8080/api/spot/work',headers={
        "Authorization":token
    })

    sorted_data = sorted(response.json(), key=lambda x: x['id'], reverse=True)
    return list(map(getWork,sorted_data))
    

[작품명배열, 촬영지들]=csv.reader(open('input.csv','r'))
workMapper=getWorkName()
작품명=작품명배열[0]



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

def getRegionCity(trList):
     for tr in trList:
        if(tr.find('td').get_text().strip()=='ktop:address'):
            address= tr.find_all('td')[1].get_text().strip()
            region=address.split(' ')[0]
            city=address.split(' ')[1]
            REGION_ENUM=regions.index(region)
            try:
                CITY_ENUM=cities.index(city)
            except:
                CITY_ENUM=cities.index(region_Mapper[region])
            finally:
                return {
                    "region":REGION_ENUM,
                    "city":CITY_ENUM
                }
                


def getSpotInformation(contentId,촬영지):
    response=requests.get('https://data.visitkorea.or.kr/page/'+contentId)
    soup=BeautifulSoup(response.content,'html.parser')
    tbody=soup.find(class_="lodList tableLine").find('tbody').find_all('tr')
    lat=getLatitude(tbody)
    long=getLongitude(tbody)
    enums=getRegionCity(tbody)
    if not lat or not long or not enums:
        raise Exception(촬영지+"에서 정보를 불러오는데 실패했습니다.")
    return {'lat':lat,'long':long, "region":enums['region'], "city":enums['city']}

successList=[]

for 촬영지 in 촬영지들:
    contentId=getSpotContentId(촬영지)
    if(contentId):
        print(촬영지,contentId)
        try:
            spotInfo=getSpotInformation(contentId,촬영지)
            result={"workname":작품명,"workId":workMapper.index(작품명),"lat":spotInfo["lat"], "long":spotInfo["long"], 'contentId':contentId, 'city':spotInfo['city'], 'region':spotInfo["region"]}

            response=requests.post('http://www.spot-setjetter.kro.kr:8080/api/spot',json={
                'contentId':result['contentId'],
                'name':촬영지,
                'region':result['region'],
                'city':result['city'],
                'longitude':result['long'],
                'latitude':result['lat'],
                'workId':result['workId']
            },headers={
                "Authorization":token
            })
            if(response.status_code==200):
                successList.append(촬영지)
            else:
                print("서버 오류가 발생했습니다. 토큰을 확인해주시겠어요?")

        except Exception as err:
            print("실패: ",err)

print(작품명,"에 해당하는",len(successList),"개의 촬영지가 업데이트되었습니다.")
print("아래는 db에 업로드한 촬영지 정보입니다.")
print("==================================")
for 촬영지정보 in successList:
    print(촬영지정보)