import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from datetime import datetime
import json

class  Client:
    def __init__(self, username, password, host):
        self.user = username
        self.passw = password
        self.host = host
        self.requesttoken = ''
    async def login(self, s):
        try:
            async with s.get(self.host+'index.php/login', ssl=False) as resp:
                soup = BeautifulSoup(await resp.text(),'html.parser')
                self.requesttoken = soup.find('head')['data-requesttoken']
                timezone = 'America/Mexico_City'
                timezone_offset = '-5'
                data = {
                    'user':self.user,
                    'password':self.passw,
                    'timezone':timezone,
                    'timezone_offset':timezone_offset,
                    'requesttoken':self.requesttoken
                }
                async with s.post(self.host+'index.php/login', data=data, ssl=False) as resp:
                    soup = BeautifulSoup(await resp.text(),'html.parser')
                    title = soup.find('div', attrs={'id':'settings'})
                    if title:
                        return True
                    else:
                        return False
        except:
            return False
    async def upload_file(self, file, s):
        print("comenzando subida")
        try:
            files = self.host+'index.php/apps/files/'
            print("files ",files)
            filepath = str(file).split('/')[-1]
            print("filepath ",filepath)
            uploadUrl = self.host+'remote.php/webdav/'+filepath
            print("uploadurl ",uploadUrl)
            async with s.get(files, ssl=False) as resp:
                soup = BeautifulSoup(await resp.text(),'html.parser')
                print("ok soup")
                f  = open(file, 'rb')
                print("f")
                self.requesttoken = soup.find('head')['data-requesttoken']
                print("self.request")
                async with s.put(uploadUrl, data=f, headers={'requesttoken': self.requesttoken}, ssl=False) as resp:
                    f.close()
                    print(await resp.text())
                    return f'{self.host}remote.php/webdav/{file}'
        except Exception as ex:
            print(ex)
            return 'error'
            
    async def direct_link(self,file,url,session):
            try:
                name = url.split("/")[-1]
                update = datetime.now()
                year = update.year
                month = update.month
                day = update.day + 6
                if day > 30:
                    month = month + 1
                    day = day - 30
                    if day < 10:
                        day = '0' + str(day)
                    else:pass
                else:
                    pass
                expire = f"{year}-{month}-{day}"
                data = {"attributes":"[]","expireDate":expire,"path":"/"+file,"shareType":"3"}
                api = self.host + "ocs/v2.php/apps/files_sharing/api/v1/shares"
                resp = await session.post(api,data=data,headers={"requesttoken":self.requesttoken})
                soup = BeautifulSoup(await resp.text(),"html.parser")
                f = soup.find('url').contents[0]
                token = str(f).split('/s/')[1]
                url = self.host + 's/' + token + '/download/' + name
                return url
            except Exception as ex:
                print(ex)
                return "error"
    
    async def delete_nexc(self,url,session):
                try:
                    files = self.host + 'index.php/apps/files/'
                    resp = await session.get(files)
                    soup = BeautifulSoup(await resp.text(),'html.parser')
                    requesttoken = soup.find('head')['data-requesttoken']
                    files = self.host + 'apps/files/'
                    name = url.split("/")[-1]
                    resp = await session.get(files)
                    soup = BeautifulSoup(await resp.text(),"html.parser")
                    value_acces = soup.find("div",attrs={"id":"avatardiv-menu"})["data-user"]
                    url_delete = self.host + "remote.php/dav/files/" + str(value_acces) + "/" + name
                    resp = await session.delete(url_delete,headers={"requesttoken":requesttoken})
                    print(await resp.text())
                    return True
                except Exception as ex:
                    print(ex)
                    return "error"
                    
                
                
                
                
                
            
            
            