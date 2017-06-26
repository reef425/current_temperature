'''
Created on Jun 22, 2017

@author: reef425
'''
import threading
import curses
import time
import re
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup



class View:
    
    def __init__(self, controller):
        self.controller = controller
        self.model = self.controller.getModel()
        self.errorMsg = ""
        self.url = "https://www.bashkirenergo.ru/consumers/online-ufa"
        # controller.updateData()
    
    def __drawCity(self, index):
        self.myScreen.erase()
        self.myScreen.addstr(1, 5, "Temperature in the city:")
        city = self.model.temperCity[index]
        self.myScreen.addstr(2, 5, city)
        self.myScreen.addstr(3, 5, self.model.getData().get(city))
        self.myScreen.addstr(4, 5, "Update time:" + str(self.model.getTime()))
        self.myScreen.addstr(5, 5, "Press \"m\" to back to main menu")
        self.myScreen.addstr(5, 5, "Press \"r\" to update")
        self.myScreen.refresh()
   
    def __drawMainMenu(self, index, citys=[]):
        self.myScreen.erase()
        self.myScreen.addstr(1, 5, "Menu:")
        for i in range(26):
            if i < 15:
                if index != i:
                    self.myScreen.addstr(i + 2, 2, citys[i])
                else:
                    self.myScreen.addstr(i + 2, 2, citys[i], curses.A_STANDOUT)
            else:
                if index != i:
                    self.myScreen.addstr(i + 2 - 15, 20, citys[i])
                else:
                    self.myScreen.addstr(i + 2 - 15, 20, citys[i], curses.A_STANDOUT)
        self.myScreen.addstr(18, 5, self.errorMsg)
        self.myScreen.addstr(19, 5, str(index))
        self.myScreen.addstr(19, 5, "Press \"enter\" to get information about city")
        self.myScreen.addstr(20, 5, "Press \"q\" or \"ctrl+\"c for quit")
        self.myScreen.addstr(21, 5, "Information from the site:%s" % self.url)
        self.myScreen.refresh()
       
    def __cityMenu(self, index):
        key = 'X'
        self.myScreen.nodelay(1)
        while key != ord('m') and self.model.urlError:
            self.__drawCity(index)
            if key == ord('r'):
                self.controller.updateData()
            key = self.myScreen.getch()
        self.myScreen.nodelay(0)
    
    def __mainMenu(self):
        key = 'X'
        count = len(self.model.temperCity)
        index = 0
        while key != ord('q'):
            if not self.model.urlError:
                self.errorMsg = "Error opening Url"
            if key == curses.KEY_UP:
                index -= 1
            if index == -1:
                index = count
            if key == curses.KEY_DOWN:
                index += 1
            if index > count:
                index = 0
            if key == curses.KEY_ENTER or key == 10: 
                if self.model.urlError:
                    self.__cityMenu(index)
            self.__drawMainMenu(index, self.model.temperCity)    
            key = self.myScreen.getch()
        self.controller.stop()
        pass
        
    def run(self):
        try:
            self.myScreen = curses.initscr()
            curses.curs_set(0)
            curses.noecho()
            curses.cbreak()
            self.myScreen.keypad(True)
            self.__mainMenu()
        finally:
            curses.endwin()
    
class Controller:
    
    def __init__(self, model):
        self.model = model
        self.update = False
        self.task = Task(self.model)
        self.task.start()
    
    def getModel(self):
        return self.model
    
    def updateData(self):
        self.model.setRawData(self.task.getRawData())
        self.model.setTime(time.ctime())
    
    def stop(self):
        self.task.setState(False)
        self.task.join()
        
    
class Task(threading.Thread):
    
    def __init__(self, model):
        threading.Thread.__init__(self)
        self.trLock = threading.Lock()
        self.__urlState = True
        self.__state = True
        self.model = model
        self.__setData()
        self.model.setRawData(self.rawData)
        
    url = "https://www.bashkirenergo.ru/consumers/online-ufa"

    def getBsObject(self, url=""):
        try:
            htmlObj = urlopen(url)
            bsObj = BeautifulSoup(htmlObj.read(), "html.parser")
            return bsObj.findAll("script", {"type":"text/javascript"})  
        except URLError:
            self.__urlState = False    
    
    def getUrlState(self):
        return self.__urlState
            
    def __getData(self):
        bsObjects = self.getBsObject(self.url)
        patternJS = "ymaps"
        if not bsObjects:
            self.model.urlError = False
            return "error"
        else:
            self.model.urlError = True
        for bsObj in bsObjects:
            if re.search(patternJS, bsObj.text):
                return bsObj.text
                break

        
    def __setData(self):
        self.rawData = self.__getData()
    
    
    def getRawData(self):
        return self.rawData
    
    def setState(self, state):
        self.__state = state
    
    def run(self):
        while self.__state:
            self.trLock.acquire()
            self.model.setRawData(self.__getData())
            self.model.setTime(time.ctime())
            self.trLock.release()
            self.timer(30)
            
    def timer(self, seconds=5):
        for i in range(seconds):
            time.sleep(1)
            if not self.__state:
                break
                           
class Model:
    
    temperCity = ["Западная ЦЭС",
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
        self.urlError = True
        self.data = {}
    
    def __getPatterns(self, txt=""):
        result1 = re.findall(r'(iconContent: \")([0-9\+\-\.]+)', txt, 0)
        result2 = re.findall(r'(balloonContent: \")([а-яА-Я\ \-\(\)|.0-9]+)', txt, 0)
        return result1, result2
    
    def setRawData(self, rawData):
        patterns = self.__getPatterns(rawData)
        values = []
        keys = []
        for i, item in enumerate(patterns[0]):
            values.append(item[1])
            keys.append(patterns[1][i][1])
        self.data = dict(zip(keys, values))
        
    def getData(self):
        return self.data
    
    def setTime(self, updateTime):
        self.updateTime = updateTime
    
    def getTime(self):
        return self.updateTime


if __name__ == '__main__':
    model = Model()
    controller = Controller(model)
    view = View(controller)
    view.run()
