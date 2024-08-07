import os
import telebot
import pandas as pd
import requests
import webdriver_manager

from bs4 import BeautifulSoup
import time as tm
#from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

options = uc.ChromeOptions()
options.add_argument("--headless")
 
# Initialize Chrome WebDriver with the specified options

#caps = DesiredCapabilities.CHROME
#caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
#options = Options()
options.add_argument('--deny-permission-prompts')
options.add_argument("--disable-notifications")  
options.add_argument('--blink-settings=imagesEnabled=false')

driver = uc.Chrome(headless=True, use_subprocess=False, service=Service(ChromeDriverManager().install()), options=options, version_main=127)

driver.implicitly_wait(5)

#driver = uc.Chrome(options=options)

#def status_code_first_request(performance_log):
#    for line in performance_log:     
#        try:
#            print(line)
#            json_log = json.loads(line['message'])
#            if json_log['message']['method'] == 'Network.responseReceived':
#                print('есть лог, статус: ' + json_log['message']['params']['response']['status'])
#                return json_log['message']['params']['response']['status']
#        except:
#            pass
         
url = 'https://www.ozon.ru/product/skoba-stroitelnaya-200-mm-x-8-mm-50-sht-876124103/'

# Загрузка страницы товара с помощью веб-драйвера
driver.get(url)
tm.sleep(2)
#logs = driver.get_log('performance')
#status_code = status_code_first_request(logs)

find_goods = driver.find_element_by_css_selector('div.webPrice')

find_goods.click()
tm.sleep(6)

page_source = str(driver.page_source)
print(page_source) 
print(find_goods) 

# Загрузка кодов товаров из файла
#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#TELEGRAM_ID = os.getenv('TELEGRAM_ID')
#bot = telebot.TeleBot(TELEGRAM_TOKEN)

#bot.send_message(TELEGRAM_ID, status_code)





