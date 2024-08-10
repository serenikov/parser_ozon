import os
import telebot
import pandas as pd
import requests

from bs4 import BeautifulSoup
import time as tm
#from selenium import webdriver
from seleniumbase import Driver


driver = Driver(uc=True, headless=True)
# Initialize Chrome WebDriver with the specified options         
url = 'https://www.ozon.ru/product/skoba-stroitelnaya-200-mm-x-8-mm-50-sht-876124103'

apikey = os.getenv('ZENROW_API_KEY')
params = {
    'url': url,
    'apikey': apikey,
#'autoparse': 'true',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
#print(response.text)

        # Создание объекта BeautifulSoup для парсинга HTML-кода
soup = BeautifulSoup(response.text, 'html.parser')
        # работа с html
        # Получение названия товара
 #print(soup)

name_element = soup.find('h1')
name = name_element.text.strip().replace('"', "&quot;")

# Получение цены со скидкой без Ozon Карты
try:
    price_element = soup.find('span', string="без Ozon Карты").parent.parent.find('div').findAll('span')
    discount_price = price_element[0].text.strip() if price_element[0] else ''
except:
    discount_price = 0

# Получение цены базовая
try:
    base_price = price_element[1].text.strip() if price_element[1] is not None else ''
except:
    base_price = 0

# Получение цены по Ozon Карте
try:
    ozon_card_price_element = soup.find('span', string="c Ozon Картой").parent.find('div').find('span')
    ozon_card_price = ozon_card_price_element.text.strip() if ozon_card_price_element else ''
except:
    ozon_card_price = 0

 # Получение продавца
#seller_element = soup.find('div', {"data-widget":"webCurrentSeller"}).select('a[href*="ozon.ru/seller"]' )
#seller = seller_element[-1].get('title').strip() if seller_element else ''

print(name)
print('Цена без Озон-карты: ' + str(discount_price))
print('Базовая цена: ' + str(base_price))
print('Цена с Озон-карты: ' + str(ozon_card_price))
#print('Продавец: ' + seller)

# Загрузка кодов товаров из файла
#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#TELEGRAM_ID = os.getenv('TELEGRAM_ID')
#bot = telebot.TeleBot(TELEGRAM_TOKEN)

#bot.send_message(TELEGRAM_ID, status_code)





