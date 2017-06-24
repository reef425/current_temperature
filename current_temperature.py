'''
Created on Jun 22, 2017

@author: klondaik
'''
import threading
import curses
import time
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup


class View:
    
    def __init__(self,controller):
        self.controller=controller
        #controller.updateData()
    
    def __drawCity(self,index):
        self.myScreen.erase()
        self.myScreen.addstr(1,5,"City:")
        city=self.controller.getData().temperCity[index]
        self.myScreen.addstr(2,5,city)
        self.myScreen.addstr(3,5,self.controller.getData().getData().get(city))
        self.myScreen.addstr(4,5,"update time:"+str(model.getTime()))
        self.myScreen.refresh()
        
    def __drawMainMenu(self,index):
        self.myScreen.erase()
        self.myScreen.addstr(1,5,"Menu:")
        for i in range(15):
            if index!= i:
                self.myScreen.addstr(i+2,5,self.controller.getData().temperCity[i])
            else:
                self.myScreen.addstr(i+2,5,self.controller.getData().temperCity[i],curses.A_STANDOUT)
        self.myScreen.refresh()
       
    def __getCity(self,index):
        key='X'
        self.myScreen.nodelay(1)
        while key!= ord('m'):
            time.sleep(0.1)
            self.__drawCity(index)
            if key == ord('r'):
                controller.updateData()
            key=self.myScreen.getch()
        self.myScreen.nodelay(0)
    
    def __mainMenu(self):
        key = 'X'
        count=len(self.controller.getData().temperCity)
        index=0
        while key != ord('q'):
            if key == curses.KEY_UP:
                index-=1
            if index == -1:
                index=count
            if key == curses.KEY_DOWN:
                index += 1
            if index > count:
                index = 0
            if key == curses.KEY_ENTER or key == 10: 
                self.__getCity(index)
            else:
                self.__drawMainMenu(index)    
            key=self.myScreen.getch()
        self.controller.stop()
        pass
        
    def run(self):
        try:
            self.myScreen = curses.initscr()
            curses.curs_set(0)
            self.myScreen.keypad(True)
            self.__mainMenu()
        finally:
            curses.endwin()
    
class Controller:
    
    def __init__(self,model):
        self.model=model
        self.update=False
        self.task=Task(self.model)
        self.task.start()
    
    def getData(self):
        return self.model
    
    def updateData(self):
        self.model.setRawData(self.task.getRawData())
        self.model.setTime(time.ctime())
    
    def stop(self):
        self.task.setState(False)
        self.task.join()
    
class Task(threading.Thread):
    
    def __init__(self,model):
        threading.Thread.__init__(self)
        self.trLock = threading.Lock()
        self.model=model
        self.__state = True
        self.__setData()
     
    url="https://www.bashkirenergo.ru/consumers/online-ufa"

    def getUrl(self,url=""):
        htmlObj=urlopen(url)
        bsObj=BeautifulSoup(htmlObj.read())
        return bsObj.findAll("script",{"type":"text/javascript"})  
            
    def __getData(self):
        for txt in self.getUrl(self.url):
            patternJS='function fid_135530034264435666603(ymaps)'
            if txt.find(patternJS,1,100)!=-1:
                return txt
        #with open("/home/klondaik/txt","r") as txtFile:
         #   return txtFile.read()
    
    def __setData(self):
        self.rawData=self.__getData()
    
    
    def getRawData(self):
        return self.rawData
    
    def setState(self,state):
        self.__state=state
    
    def run(self):
        while self.__state:
            self.trLock.acquire()
            self.model.setRawData(self.__getData())
            self.model.setTime(time.ctime())
            self.trLock.release()
            time.sleep(30)
                
    
class Model:
    
    citys=["Уфа",
       "Уфа ПС Ибрагимовская",
       "Аэропорт",
       "Аксаково",
       "Бекетово",
       "Бурибай",
       "Дюртюли",
       "Караидель",
       "Кушнаренково",
       "Кумертау",
       "Инсягулово",
       "Ишимбай",
       "Мелеуз",
       "Мраково",
       "Нефтекамск",
       "Павловка",
       "Салават",
       "Стерлитамак",
       "Мишкино"
       "Туймазы",
       "Тюльди",
       "Федоровка",
       "Учалы (Иремель)",
       "Янаул"]

    temperCity=["Западная ЦЭС",
          "Аксаково",
          "Бурибай",
          "Учалы (Иремель)",
          "Туймазы",
          "Дюртюли",
          "Ишимбай",
          "Федоровка",
          "Караидель",
          "Инсягулово",
          "Мраково",
          "Кумертау",
          "Мелеуз",
          "Нефтекамск",
          "Янаул",
          "Тюльди",
          "Уфа ПС Ибрагимовская",
          "Стерлитамак",
          "Салават",
          "Аэропорт",
          "Бекетово",
          "Павловка",
          "Кушнаренково",
          "Мишкино",
          "ТЭЦ-4",
          "РТС-2 Трамвайная"]
    
    def __init__(self):
        self.data={}
        pass
    
    def __getPatterns(self,txt=""):
        result1=re.findall(r'(iconContent: \")([0-9\+\-\.]+)', txt,0)
        result2=re.findall(r'(balloonContent: \")([а-яА-Я\ \-\(\)|.0-9]+)', txt,0)
        return result1,result2
    
    def setRawData(self,rawData):
        patterns=self.__getPatterns(rawData)
        values=[]
        keys=[]
        for i, item in enumerate(patterns[0]):
            values.append(item[1])
            keys.append(patterns[1][i][1])
        self.data=dict(zip(keys,values))
        
    def getData(self):
        return self.data
    
    def setTime(self,updateTime):
        self.updateTime=updateTime
    
    def getTime(self):
        return self.updateTime

if __name__ == '__main__':
    model=Model()
    controller=Controller(model)
    view=View(controller)
    view.run()
    






