import os
import telebot
import pandas as pd
import requests
import regex
from bs4 import BeautifulSoup
import time as tm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from gspread import Client, Spreadsheet, Worksheet, service_account, exceptions
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

start_time = tm.time()  # время начала выполнения

# Загрузка кодов товаров из файла
with open('D:\Python\Python38\Projects\codes.txt', 'r') as f:
    codes = f.read().splitlines()

# Создание пустого DataFrame для хранения данных
df = pd.DataFrame(columns=['Код товара',
                           'Название товара', 
                           'URL страницы с товаром', 
                           'Цена с учетом скидок без Ozon Карты',
                           'Наименование продавца', 
                           'Ссылка продавца',
                           'ID продавца',
                           'Статус'])

# Загрузка учетных данных для загрузки в Гугл таблицу
file_path = 'D:\Python\Python38\Projects\ozon\gspread.json'
with open(file_path, 'r') as f:
    credentials_info = json.loads(f.read())
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])

# Авторизация и открытие гугл таблицы
client = gspread.authorize(credentials)
sheet = client.open('скобы конкуренты (цены)').worksheet("список озон")

#тест заполнения ячейки таблицы
#sheet.update_acell('A1', 'Hello, World!')

#цикл по списку артикулов в codes.txt     
url_1 = 'https://www.ozon.ru/product/'
#url = 'https://app.mayak.bz/ozon/products/1597476647'
#driver = webdriver.Chrome()
#driver.get(url)
#apikey = os.getenv('ZENROW_API_KEY')
maxitems = len(codes)
steps = maxitems
os.system('cls||clear')
for code in codes:
	start_code_time = tm.time()  # время начала выполнения
	page_url = url_1 + code
	#params = {
    #	'url': page_url,
    #	'apikey': apikey,
    #	'js_render': 'true',
	#'premium_proxy': 'true',
	#}
	#response = requests.get('https://api.zenrows.com/v1/', params=params)
	driver = webdriver.Chrome()
	driver.implicitly_wait(10)
	#----чистим экран
	#os.system('cls||clear') 

	steps = steps - 1
	driver.get(page_url)
	tm.sleep(2)
	try: 
		button1 = driver.find_element(By.CLASS_NAME, "rb")
		button1.click()
		tm.sleep(3)
	except:
		button1 = ''	
	
	body = driver.find_element(By.TAG_NAME, 'body')
	body.send_keys(Keys.PAGE_DOWN)	
	tm.sleep(4)
	page_source = str(driver.page_source)
	# Создание объекта BeautifulSoup для парсинга HTML-кода
	soup = BeautifulSoup(page_source, 'html.parser')
	#работа с html
 
 	# Получение названия товара
	try:
		name_element = soup.find('h1')
		name = name_element.text.strip().replace('"', "&quot;")
	except:
		name = ''
	# Получение цены со скидкой без Ozon Карты
	try:
		price_element = soup.find('span', string="без Ozon Карты").parent.parent.find('div').findAll('span')
		discount_price = price_element[0].text.strip() if price_element[0] else ''
		#<span class="mn6_27 m6n_27 mo_27">1 542 ₽</span>
		discount_price = discount_price.replace("₽","")
		d_price = discount_price.split()
		d_price = ''.join(d_price)
	except:
		d_price = 0
	# Получение цены базовая
	#try:
		#base_price = price_element[1].text.strip() if price_element[1] is not None else ''
		#base_price = base_price.replace("₽","")
		#base_price = int(base_price.replace(" ",""))
	#except:
		#base_price = 0
	#try:
		#ozon_card_price_element = soup.find('span', string="c Ozon Картой").parent.find('div').find('span')
		#ozon_card_price = ozon_card_price_element.text.strip() if ozon_card_price_element else ''
		#ozon_card_price = ozon_card_price.replace("₽","")
		#ozon_card_price = int(ozon_card_price.replace(" ",""))
	#except:
		#ozon_card_price = 0
	OutOfStock = ''
	Oerror = ''
	status = ''
	#Пробуем найти виджет продавца и определить id, ссылку и наименование продавца
	try:
		seller_element = soup.find('div', {"data-widget":"webCurrentSeller"}).select('a[href*="ozon.ru/seller"]' )
		seller = seller_element[-1].get('title').strip() if seller_element else ''
		#--- ссылка продавца
		href_seller_find = seller_element[-1].get('href').strip() if seller_element else ''
		href_seller = href_seller_find + 'skoby-9786/?type=123733'
		#--- id продавца
		id_seller = 0  ##https://www.ozon.ru/seller/makita-servis-429330/ 
		#print(href_seller)
		match = regex.search(r'-(\d+)/$', href_seller_find)
		if match:
			id_seller = match.group(1)
			#print(id_seller)
		else:
			id_seller = 0
			#print("ID не найден.")
	# если нет виджета то проверим на что "товара сейчас нет в продаже" ищем виджет webOutOfStock	
	except:
		id_seller = 0
		href_seller = ''
		seller = ''
		try:
			webOutOfStock = soup.find('div', {"data-widget":"webOutOfStock"}).select('h2' ) ##('//*[@id="layoutPage"]/div[1]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/div/div/div[2]/div/p[1]')
			OutOfStock = webOutOfStock[-1].text.strip()
			OutStockNext = soup.find_all('p' )
			name = OutStockNext[0].text
			nameOutStock = OutStockNext[1].text
			seller_element = soup.find('div', {"data-widget":"webOutOfStock"}).select('a[href*="/seller/"]' )
			href_seller_find = seller_element[-1].get('href').strip() if seller_element else ''
			match = regex.search(r'/seller/(\d+)/$', href_seller_find)
			if match:
				id_seller = match.group(1)
			else:
				id_seller = 0
			href_seller = 'https://www.ozon.ru' + str(href_seller_find[:-1]) + '/skoby-9786/?type=123733' if seller_element else ''
			seller = seller_element[-1].text
		except:
			OutOfStock = ''
			try:
				error = soup.find('div', {"data-widget":"error"}).select('h2' ) ##('//*[@id="layoutPage"]/div[1]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/div/div/div[2]/div/p[1]')
				Oerror = error[-1].text.strip()
				print(Oerror)
			except:
				Oerror = ''
	if OutOfStock != '':
		status = OutOfStock
	if Oerror != '':
		status = Oerror
	if status == '':
		status = 'В продаже'

# Заполнение DataFrame
	print('ID товара: ' + str(code))
	print('Наименование товара: ' + str(name))
	print('Ссылка на товар: ' + str(page_url))
	print('Цена товара: ' + str(d_price))
	print('ID продавца: ' + str(id_seller))
	print('Наименование продавца: ' + str(seller))	
	print('Ссылка продавца: ' + str(href_seller))
	print('Статус товара: ' + str(status))
	df = pd.concat([
		    df, pd.DataFrame({
			'Код товара': [int(code)],
			'Название товара': [name],
			'URL страницы с товаром': [page_url],
			'Цена с учетом скидок без Ozon Карты': [int(d_price)],
			'Ссылка продавца': [href_seller],
			'Наименование продавца': [seller],
			'ID продавца': [int(id_seller)],
			'Статус': [status]
		    })
	        ], ignore_index=True)
	driver.quit()
	# Вычисляем прошедшее время
	time_f = tm.time()
	elapsed_time = time_f - start_time
	# Получаем минуты и секунды
	minutes = int(elapsed_time // 60)
	seconds = int(elapsed_time % 60)
 
	elapsed_code_time = time_f - start_code_time 
	seconds_code = int(elapsed_code_time % 60)
	#print('seconds_code' + str(seconds_code))
	lost_seconds = int(steps * seconds_code)
	#print('lost_seconds' + str(lost_seconds))
	lost_minutes = int(lost_seconds // 60)
	if lost_minutes != 0:
		lost_seconds = 0
	lost_hour = int(lost_minutes // 60)
	if lost_hour != 0:
		lost_minutes = int(lost_minutes % 60)
	
	#print('lost_minutes' + str(lost_minutes))
	# выводим время
	print(f"Прошло времени: {minutes} минут(ы) и {seconds} секунд(ы)")
	
	print(f"Осталось времени: {lost_hour} час(-а,-ов) {lost_minutes} минут(ы) и {lost_seconds} секунд(ы)")
	print('Осталось ' + str(steps) + ' из ' + str(maxitems) + ' артикулов')
	#dfjs = df.to_json()
	#sheet.append_row(dfjs)
##Выгружаем в гугл таблицу
sheet.update([df.columns.values.tolist()] + df.values.tolist()) 

#print(df.to_string())


#print(name)
#print('Цена без Озон-карты: ' + str(discount_price))
#print('Базовая цена: ' + str(base_price))
#print('Цена с Озон-карты: ' + str(ozon_card_price))
#print('Продавец: ' + seller)

# Загрузка кодов товаров из файла
#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#TELEGRAM_ID = os.getenv('TELEGRAM_ID')
#bot = telebot.TeleBot(TELEGRAM_TOKEN)

#bot.send_message(TELEGRAM_ID, status_code)




