from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import requests
import math
import time
import json
from PyQt5 import QtCore, QtWidgets, QtGui,uic
from PyQt5.QtWidgets import QApplication
import sys


chrome_options = Options()
#chrome_options.add_argument("--headless")
number_threads = 2
parser_ses = []
my_accdct = {}
my_acclst = []
acc_psn = []
acc_xbox = []
acc_xperc = {}
acc_psnperc = {}
acc_troph = {}
url_log = 'https://id.sonyentertainmentnetwork.com/signin/?response_type=token&scope=capone%3Areport_submission%2Ckamaji%3Agame_list%2Ckamaji%3Aget_account_hash%2Cuser%3Aaccount.get%2Cuser%3Aaccount.profile.get%2Ckamaji%3Asocial_get_graph%2Ckamaji%3Augc%3Adistributor%2Cuser%3Aaccount.identityMapper%2Ckamaji%3Amusic_views%2Ckamaji%3Aactivity_feed_get_feed_privacy%2Ckamaji%3Aactivity_feed_get_news_feed%2Ckamaji%3Aactivity_feed_submit_feed_story%2Ckamaji%3Aactivity_feed_internal_feed_submit_story%2Ckamaji%3Aaccount_link_token_web%2Ckamaji%3Augc%3Adistributor_web%2Ckamaji%3Aurl_preview&client_id=656ace0b-d627-47e6-915c-13b259cd06b2&redirect_uri=https%3A%2F%2Fmy.playstation.com%2Fauth%2Fresponse.html%3FrequestID%3Dexternal_request_fc54694f-fdfe-4a9e-9dea-bae1d2d15c29%26baseUrl%3D%2F%26returnRoute%3D%2F%26targetOrigin%3Dhttps%3A%2F%2Fmy.playstation.com%26excludeQueryParams%3Dtrue&prompt=login&tp_console=true&ui=pr&error=login_required&error_code=4165&error_description=User+is+not+authenticated&no_captcha=false#/signin?entry=%2Fsignin'
url_xbox = 'https://www.xboxgamertag.com/search/'
e = {}
acc_data_x = {}
acc_data_psn = {}
dir_firefox = '\\geckodriver.exe'
with open('myacc.txt', 'r') as f:
    my_accdct = json.load(f)
    for a,b in my_accdct.items():
        my_acclst.append(a)
    print(my_acclst)

with open('acc.txt', 'r', encoding='cp1251') as f:
    acctxt = f.read()
acctxt = acctxt.replace('====================[ Информация об аккаунте ]========================','').replace('=====================================================================', ',')
acctxt = acctxt.split(',')
for a in acctxt:
    for b in a.split('\n'):
        if b.find('Данные для входа - ') != -1:
            tt = b.replace('Данные для входа - ', '')
        if b.find('Playstation Network - Подключен') != -1:
            b = b.replace('Playstation Network - Подключен','').replace('[','').replace(']','')
            acc_psn.append(b)
            acc_data_psn[b] = tt
            #print(acc_psn)
        if b.find('Xbox - Подключен') != -1:
            b = b.replace('Xbox - Подключен','').replace('[','').replace(']','')
            acc_xbox.append(b)
            acc_data_x[b] = tt
            #print(acc_xbox)
print(acc_psn)

def dict_add_keep_last(a, b):
    d = a.copy()
    d.update(b)
    return d

class XBOX(QtCore.QThread):
    s_save = QtCore.pyqtSignal()
    s_csv = QtCore.pyqtSignal()
    s_startPSN = QtCore.pyqtSignal()
    def __init__(self,acc_xbox,url_xbox, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.acc_xbox = acc_xbox
        self.url_xbox = url_xbox
        self.acc_perc = {}
        self.stop_check = False
    def run(self):
        self.headers = {"Referer": 'https://www.xboxgamertag.com',
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
                        }
        for self.a in self.acc_xbox:
            if self.stop_check != True:
                try:
                    QtWidgets.qApp.processEvents()
                    self.url = self.url_xbox + self.a + '/'
                    self.bs_xbox = BeautifulSoup(requests.get(self.url, headers=self.headers).text)
                    #print(self.bs_xbox)
                    if self.bs_xbox.find(text="EA SPORTS™ FIFA 20") != None:
                        self.acc_perc[self.a] = str(self.bs_xbox.find(text="EA SPORTS™ FIFA 20").find_parent('td').find_parent('tr').find('div', {"class":"percentage-container"}).get_text().split('/')[0]).replace('\n','')
                        print(self.a, " - ", self.acc_perc[self.a])
                    self.s_save.emit()
                except Exception as err:
                    print(err)
            else:
                break
        self.s_csv.emit()

def startParseX():
    global acc_xperc
    cc = True
    onex = []
    twox = []
    for a in acc_xbox:
        if cc == True:
            onex.append(a)
            cc = False
        else:
            twox.append(a)
            cc = True

    def stop_x():
        print('Остановка потока')
        Xa.stop_check = True
        Xb.stop_check = True
        window.start_btn.setDisabled(True)
        window.stop_btn.setDisabled(True)
    def save_csv():
        with open('XBOX.csv', 'wt') as f:
            csv_writer = csv.writer(f, delimiter=';', lineterminator="\n")
            for _key, _val in acc_xperc.items():
                csv_writer.writerow([_key, _val, acc_data_x[_key]])
    def sav():
        global acc_xperc
        print('Сохранение промежуточное')
        acc_xperc = dict_add_keep_last(Xa.acc_perc, Xb.acc_perc)
    Xa = XBOX(onex, url_xbox)
    Xb = XBOX(twox, url_xbox)
    window.stop_btn.clicked.connect(stop_x)
    Xa.s_save.connect(sav)
    Xa.s_csv.connect(save_csv)
    #Xb.s_save.connect(save_csv)
    Xa.start()
    Xb.start()
    window.stop_btn.setDisabled(False)

class SelenPSN(QtCore.QThread):
    def __init__(self, acc, psw, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.account = acc
        self.password = psw
    def Start_Selen(self):
        print('Start_Selen')
        self.caps = DesiredCapabilities().FIREFOX
        self.caps["pageLoadStrategy"] = "none"
        self.driver = webdriver.Firefox(capabilities=self.caps,options=chrome_options)
        self.driver.set_window_size(400, 900)
        self.driver.get(url_log)
        WebDriverWait(self.driver, 400).until(EC.presence_of_element_located((By.ID, "ember17")))
        self.driver.find_element_by_xpath("//input[@type='email']").send_keys(self.account)
        self.driver.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        return
    def driverWait(self):
        print("driverWait")
        WebDriverWait(self.driver, 2900).until(EC.presence_of_element_located((By.ID, "profile")))
        print('Пользователь зашел. Приступаем к парсингу')
        #self.driver.set_window_position(-2000, 0)
        self.parse_acc = {}
        self.troph = {}
        return
    def ld_pg(self,acc):
        #self.driver.set_page_load_timeout(0.1)
        print('ld_pg')
        self.a = acc
        try:
            self.driver.get('https://my.playstation.com/profile/'+self.a+'/trophies/details/NPWR17768_00/default')
        except:
            print('load error')
        return
    def checkban(self):
        print('Checkban')
        WebDriverWait(self.driver, 400).until(EC.presence_of_element_located((By.ID, "profile")))
        try:
            self.BS = BeautifulSoup(self.driver.page_source).find('h2', {'class': 'error-state-indicator__header'}).get_text() == 'Что-то не так.'
            print("Ожидание завершения блокировки ") # пауза
            for self.i in range(1,3600):
                time.sleep(0.25)
                QtWidgets.qApp.processEvents()
            return True
        except :
            return False
    def parsing(self):
        print('parsing')
        try:
            self.procent = BeautifulSoup(self.driver.page_source).find('div',{'class':'progress-bar__progress-percentage'}).get_text()
            print(self.a,' - ',self.procent)
            self.parse_acc[self.a] = self.procent
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.find_elements_by_xpath("//li[@class='game-trophies-page__tile-container']")[17].click()
            if BeautifulSoup(self.driver.page_source).find('div',{'class':'trophy-info-modal__earned-text'}) != None:
                print('Troph YES')
                self.troph[self.a] = 'Troph YES'
            else:
                print('Troph NO')
                self.troph[self.a] = 'Troph NO'
        except Exception as err:
            print(err,'Нет FIFA 20 - ', self.a)
        return
def tasked():
    global completed_bar
    global acc_psnperc
    global acc_troph
    print('Предварительное сохранение в переменных')
    for f in sessionSelen:
        print(f.parse_acc)
        print(f.troph)
        acc_psnperc.update(f.parse_acc)
        acc_troph.update(f.troph)
    print(acc_psnperc)
    print(acc_troph)

    completed_bar += iter_bar
    window.progressBar.setValue(completed_bar)
    sti_parse.clear()
    sti_parse.setHorizontalHeaderLabels(['Аккаунт', 'Проценты', 'Трофей', 'Данные'])
    for _key, _val in acc_psnperc.items():
        sti_parse.appendRow([QtGui.QStandardItem(_key), QtGui.QStandardItem(_val), QtGui.QStandardItem(acc_troph[_key]), QtGui.QStandardItem(acc_data_psn[_key])])
    window.table_progress.setModel(sti_parse)
    return
def PSN_csv():
    print('Сохраняем в csv')
    with open('PSN.csv', 'wt') as f:
        csv_writer = csv.writer(f, delimiter=';',lineterminator="\n")
        for _key, _val in acc_psnperc.items():
            try:
                csv_writer.writerow([_key,_val,acc_troph[_key],acc_data_psn[_key]])
            except Exception as err:
                print('Ошибка ключа. Из-за экстренной остановки', err)
    return
def StartPSN():
    global sessionSelen
    global completed_bar
    global iter_bar
    global pre_count
    completed_bar = 0
    sessionSelen = []
    global check_stop
    check_stop = False
    iter_bar = (math.ceil((100/len(acc_psn))*100))/100
    print(iter_bar)
    for acc, psw in my_accdct.items(): # создаем экземпляры классов
        sessionSelen.append(SelenPSN(acc, psw))

    def f_stopbtn():
        global check_stop
        print("Пользователь нажал кнопку стоп")
        check_stop = True
        window.stop_btn.setDisabled(True)

    window.stop_btn.clicked.connect(f_stopbtn)
    for a in sessionSelen:
        a.Start_Selen()
    for a in sessionSelen:
        a.driverWait()
    iter_acc = 0
    while iter_acc < len(acc_psn) and check_stop != True:
        for a in sessionSelen:
            a.ld_pg(acc_psn[iter_acc])
            iter_acc +=1
        for r in range(0,50): #пауза
            QtWidgets.qApp.processEvents()
            time.sleep(0.1)

        for a in sessionSelen:
            if a.checkban() == True:
                for b in sessionSelen:
                    b.ld_pg(b.a)
                for r in range(0, 50):  # пауза
                    QtWidgets.qApp.processEvents()
                    time.sleep(0.1)

        for a in sessionSelen:
            a.parsing()
            tasked()
        PSN_csv()




    QtWidgets.qApp.processEvents()
    print('ffff')
def StartAll():
    save_allHUI()
    window.start_btn.setDisabled(True)
    window.stop_btn.setDisabled(False)
    window.file_btn.setDisabled(True)
    QtWidgets.QMessageBox.information(window, "Создаются потоки",
                                      "Внимание! Сейчас будут создаваться окна браузера Firefox!Решите капчи , и после этого НЕ НАЖИМАЙТЕ на окна браузера Firefox",
                                      buttons = QtWidgets.QMessageBox.Close,
                                      defaultButton = QtWidgets.QMessageBox.Close)
    StartPSN()
    if check_stop != True:
        startParseX()

def save_allHUI():
    global my_accdct
    global my_acclst
    my_acclst = []
    my_accdct = {}
    i = 0
    while i < sti_acc.rowCount():
        if sti_acc.index(i, 0).data() != None and sti_acc.index(i, 0).data() != "":
            my_accdct[sti_acc.index(i, 0).data()] = sti_acc.index(i, 1).data()
            my_acclst.append(sti_acc.index(i, 0).data())
        i += 1
    print(my_acclst)
    print(my_accdct)
    with open("myacc.txt", "w") as f:
        f.write(json.dumps(my_accdct))

def add_file():
    global acc_psn
    global acc_data_psn
    global acc_xbox
    global acc_data_x

    acc_xbox = []
    acc_data_psn = {}
    acc_psn = []
    acc_data_x = {}
    file = QtWidgets.QFileDialog.getOpenFileName(parent=window, caption="Список аккаунтов", directory="c:\\", filter="txt(*.txt)", initialFilter="txt (*.txt)")
    fileName = file[0]
    print(fileName)

    with open(fileName, 'r', encoding='cp1251') as f:
        acctxt = f.read()
    acctxt = acctxt.replace('====================[ Информация об аккаунте ]========================', '').replace(
        '=====================================================================', ',')
    acctxt = acctxt.split(',')
    for a in acctxt:
        for b in a.split('\n'):
            if b.find('Данные для входа - ') != -1:
                tt = b.replace('Данные для входа - ', '')
            if b.find('Playstation Network - Подключен') != -1:
                b = b.replace('Playstation Network - Подключен', '').replace('[', '').replace(']', '')
                acc_psn.append(b)
                acc_data_psn[b] = tt
                # print(acc_psn)
            if b.find('Xbox - Подключен') != -1:
                b = b.replace('Xbox - Подключен', '').replace('[', '').replace(']', '')
                acc_xbox.append(b)
                acc_data_x[b] = tt
                # print(acc_xbox)
    print(acc_psn)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = uic.loadUi("mainUI.ui")
    window.start_btn.clicked.connect(StartAll)
    window.stop_btn.setDisabled(True)
    window.progressBar.setValue(0)
    window.file_btn.clicked.connect(add_file)
    sti_acc = QtGui.QStandardItemModel(parent=window)
    sti_parse = QtGui.QStandardItemModel(parent=window)
    for z,k in my_accdct.items():
        sti_acc.appendRow([QtGui.QStandardItem(z), QtGui.QStandardItem(k)])
    sti_acc.setHorizontalHeaderLabels(['Аккаунт', 'Пароль'])
    window.table_acc.setModel(sti_acc)
    sti_parse.setHorizontalHeaderLabels(['Аккаунт', 'Проценты', 'Трофей', 'Данные'])
    sti_acc.insertRows(len(my_acclst), 10)
    window.table_acc.setItemDelegate(QtWidgets.QItemDelegate())
    window.show()

    sys.exit(app.exec_())




