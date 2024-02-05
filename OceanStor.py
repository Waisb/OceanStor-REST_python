import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#Все методы описаны тут.
#https://support.huawei.com/enterprise/en/doc/EDOC1100144155/f5087536/restful-apis
#

class OceanStor:
    def __init__(self, username, password, host, port = 8088,scope = 1):
        self.username = username
        self.password = password
        self.host = str(host)
        self.port = str(port)
        self.scope = str(scope)
        self.deviceid = None 
        self.iBaseToken = None
        self.cookies = None
        self.headers = None

    def __str__(self): #Прикол
        hidepass = len(self.password)*"*"
        if self.scope == "1":
            scope = "LDAP"
        else:
            scope = "LOCAL"
        return f"HOST: {self.host}:{self.port}\nAUTH: {self.username}:{hidepass}:{scope}\n"

    def start_session(self):
        '''
        СТАРТУЕТ СЕССИЮ. Обязательно начинать именно с этого!
        '''
        REST_Access_Auth = "deviceManager/rest/xxxxx/sessions"
        url = f"https://{self.host}:{self.port}/{REST_Access_Auth}"
        data = json.dumps({'scope': self.scope, 'username': self.username, 'password': self.password})
        headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Accept': 'application/json'}
        connect = requests.post(url, verify=False, data = data, headers = headers, timeout=3)
        connect_info = (json.loads(connect.content.decode('utf8')),connect.cookies)

        self.deviceid = connect_info[0]['data']['deviceid']
        self.iBaseToken = connect_info[0]['data']['iBaseToken']
        self.cookies = connect_info[1]
        self.headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Accept': 'application/json', 'iBaseToken':self.iBaseToken}
        print (f"Started session: {self.deviceid}\n{self.iBaseToken}")
    def metod(self, metod):
        '''
        Универсальный post (get) возврат в сыром виде
        Передавать строго видом deviceManager/rest/${deviceId}/МЕТОД"
        '''

        "deviceManager/rest/${deviceId}/system/"
        
        REST = metod.split('/')
        metod = REST[3]
        SanitasedREST = f"https://{self.host}:{self.port}/deviceManager/rest/{self.deviceid}/{metod}"
        data = requests.get(SanitasedREST, verify=False, cookies = self.cookies, headers = self.headers)
        return data.json()

    def get_lunCount(self):
        '''
        Получает количество лунов
        '''
        REST = f"deviceManager/rest/{self.deviceid}/lun/count"
        url = f"https://{self.host}:{self.port}/{REST}"
        lunCount = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return lunCount.json()['data']["COUNT"]
    def get_diskpoolCount(self):
        '''
        Получает количество пулов диска? 
        '''
        REST = f"/deviceManager/rest/{self.deviceid}/diskpool/count"
        url = f"https://{self.host}:{self.port}/{REST}"
        diskCount = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return diskCount.json()['data']["COUNT"]
    def get_diskInfo(self, id):
        '''
        Получает информацию о диске по его id
        '''
        REST = f"/deviceManager/rest/{self.deviceid}/disk/{str(id)}"
        url = f"https://{self.host}:{self.port}/{REST}"
        diskInfo = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return diskInfo.json()['data']

    def get_allDisks(self):
        '''
        Возвращает массив с инфрмацией всех дисков 
        '''
        REST = f"/deviceManager/rest/{self.deviceid}/disk"
        url = f"https://{self.host}:{self.port}/{REST}"
        disk = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return disk.json()['data']
    def get_DisksCount(self):
        '''
        Возвращает количество дисков. Оно равно и id. Все диски идут с 0 id.
        
        Тяжелый метод!
        '''
        REST = f"/deviceManager/rest/{self.deviceid}/disk"
        url = f"https://{self.host}:{self.port}/{REST}"
        disk = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return len(disk.json()['data'])

    def search_by_serial(self, serial):
        '''
        Возвращает информацию о диске по его серийнику

        Тяжелый метод!
        '''
        Disks = self.get_allDisks()['data']
        Founded = []
        for Disk in Disks:
            if Disk['SERIALNUMBER'] == serial.upper():
                Founded.append(Disk)
        return Founded
    def search_by_barcode(self, barcode):
        '''
        Возвращает информацию о диске по его серийнику

        Тяжелый метод!
        '''
        Disks = self.get_allDisks()['data']
        Founded = []
        for Disk in Disks:
            if Disk['barcode'] == barcode.upper():
                Founded.append(Disk)
        return Founded
    def get_bbu(self):
        REST = f"/deviceManager/rest/{self.deviceid}/backup_power"
        url = f"https://{self.host}:{self.port}/{REST}"
        bbu = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return bbu.json()['data']
    def get_system(self):
        REST = f"/deviceManager/rest/{self.deviceid}/system/"
        url = f"https://{self.host}:{self.port}/{REST}"
        system = requests.get(url, verify=False, cookies = self.cookies, headers = self.headers)
        return system.json()['data']

test = OceanStor ("USERNAME", "PASSWORD","IP") #Передача данных о сессии
test.start_session()                            #Старт сессии. 
#print("LUN COUNT: " + test.get_lunCount())            Пример запроса количества лунов
#print("DISKPOOL COUNT: " + test.get_diskpoolCount())   Пример запроса количества дисков (не луны)
#print(test.get_diskInfo(32))                           Пример запроса получения информации о диске по его id
#All_disks = test.get_disk()                            Пример запроса получения ВСЕХ дисков
#print(test.search_by_serial('A04403a0'))               пример запроса поиска диска по серийнику
#print (test.get_system())                              Пример запроса для получения информации о системе (мейн страница дашборда)
#print(test.metod("deviceManager/rest/${deviceId}/system_utc_time")) Пример запроса универсального метода REST