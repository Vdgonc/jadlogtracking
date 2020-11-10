import logging
import requests
from time import sleep
from bs4 import BeautifulSoup
from json import dumps, loads, dump
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


class Bot:
    def __init__(self, trackid: str, telegramToken: str ,executable_path: str = './geckodriver'):
        self.trackID = trackid
        self.trackURL = "https://www.jadlog.com.br/tracking"
        self.execPath = executable_path

        self.searchBox = '//*[@id="termo"]'
        self.detailsSpan = '/html/body/div[4]/div/form/div[1]/div[2]/table/tbody/tr[2]/td/div/a/h4/span'
        self.table = '/html/body/div[4]/div/form/div[1]/div[2]/table/tbody/tr[2]/td/div/div[2]/div/div[2]/table'

        self.token = telegramToken
    
    def parseData(self):
        options = Options()
        options.add_argument('--headless')

        logging.info(f'Accessing jadlog')
        driver = webdriver.Firefox(executable_path=self.execPath, options=options)
        driver.get(self.trackURL)

        logging.warning('Waiting 30 seconds after access jadlog')
        sleep(30)

        logging.info(f'Sending track id {self.trackID}')
        searchInput = driver.find_element_by_xpath(self.searchBox)
        searchInput.send_keys(self.trackID)
        searchInput.send_keys(Keys.RETURN)

        logging.warning('Waiting 15 seconds after sent trackid')
        sleep(15)

        logging.info('Opening details')
        detailSpan = driver.find_element_by_xpath(self.detailsSpan)
        detailSpan.click()

        logging.warning('Waiting 15 seconds after open details')
        sleep(15)

        table = driver.find_element_by_xpath(self.table)
        table = table.get_attribute('innerHTML')
        
        tableData = [[cell.text for cell in row("td")] for row in BeautifulSoup(table, 'html.parser')("tr")]

        parsedData = []
        logging.info('Parsing Table')
        for data in tableData:
            if len(data) != 0:
                for item in data:
                    if item.find('Data/ Hora') != -1:
                        date = item.split('Data/ Hora')[1]
                    elif item.find('Ponto Origem') != -1:
                        origin = item.split('Ponto Origem')[1]
                    elif item.find('Ponto Destino') != -1:
                        dest = item.split('Ponto Destino')[1]
                    elif item.find('Status') != -1:
                        status = item.split('Status')[1]
                    else:   
                        ...
                    
                rowDict = {"date": date,"origin": origin, "dest": dest, "status": status}
                parsedData.append(rowDict)
        
        logging.warning(f'Table parsed: {parsedData}')

        logging.warning('Closing driver')
        driver.close()
        return dict(status=parsedData)

    def sendMessage(self, lastStatus: dict, chatID: str):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        txt = f"""
            \tAtualização do Pacote:
            Data: {lastStatus['date']}
            Origem: {lastStatus['origin']}
            Dest: {lastStatus['dest']}
            Status: {lastStatus['status']}
        """

        msg = {"chat_id": chatID, "text": txt, "disable_notification": False}
        data = dumps(msg)

        req = requests.post(url=url, data=data, headers={'content-type': 'application/json'})

        if req.status_code == 200:
            logging.warning('Message sent')

    def compare(self, statusfile: str, chatID: str):
        try:
            with open(statusfile, 'r') as file:
                status = loads(file.read())
                file.close()
        except Exception as err:
            logging.error(f'Unable to load status json: {err}')
            return None

        data = self.parseData()
        
        if data["status"] != status["status"]:
            self.sendMessage(lastStatus=data["status"][-1], chatID=chatID)
        
        try:
            with open(statusfile, 'w') as outputfile:
                json = dumps(data)
                outputfile.write(json)
        except Exception as err:
            logging.error(f'Unable to rewrite status json: {err}')
            return None

        return data