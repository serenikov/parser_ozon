import os
import telebot
import pandas as pd
import requests
import regex
from bs4 import BeautifulSoup
import time as tm
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Создание пустого DataFrame для хранения данных
df = pd.DataFrame(columns=['Код товара',
                           'Название товара', 
                           'URL страницы с товаром', 
                           'Цена с учетом скидок без Ozon Карты',
                           'Наименование продавца', 
                           'Ссылка продавца',
                           'ID продавца',
                           'Статус'])


#service = Service(executable_path=r'/usr/lib/chromium-browser/chromedriver')
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("start-maximized")
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--headless") # Runs Chrome in headless mode.
chrome_options.add_argument('--no-sandbox') # # Bypass OS security model
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument("--disable-extensions")
chromedriver_autoinstaller.install()
url = 'https://www.ozon.ru/product/876124103/'
driver = webdriver.Chrome(options=chrome_options)

#driver.get(url)

#driver = webdriver.Chrome()
tm.sleep(2)
driver.implicitly_wait(360)
driver.get(url)
os.system('clear')
tm.sleep(30)
#try: 
#	button1 = driver.find_element(By.CLASS_NAME, "rb")
#	button1.click()
#	print('Нажали "обновить"')
#	tm.sleep(10)
#	print('Подождали 10 сек')
#except:
#	button1 = ''
#	print('не нажали "обновить"')
wait = WebDriverWait(driver, 10)
n = 0
while True:
	try:
		elementOne = wait.until(EC.element_to_be_clickable(By.CLASS_NAME("rb")));
		elementOne.click();
		n = n + 1
		print('Нажали "обновить" ' + str(n) + ' раз')
		tm.sleep(30)
		elementTwo = wait.until(EC.element_to_be_clickable(By.id("stickyHeader")));
		elementTwo.click();
		break;
		#button1 = driver.find_element(By.CLASS_NAME, "rb")
		#wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "rb")))
		#driver.execute_script("arguments[0].click();", button1)
		#print('Нажали "обновить"')
		#button2 = driver.find_element(By.ID, "stickyHeader")
	except WebDriverException as e:
		print('не нажали "обновить"')
		print(e)
    	
#try:
#	button1 = driver.find_element(By.CLASS_NAME, "rb")
#	#WebDriverWait(driver, 20).until(EC.element_to_be_clickable(button1)).click()
#	#actions = ActionChains(driver)
#	wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "rb")))
#	#actions.move_to_element(button1).click().perform()
#	driver.execute_script("arguments[0].click();", button1)
#	print('Нажали "обновить"')
#except WebDriverException as e:
#	print('не нажали "обновить"')
#	print('failed')
#	print(e)
tm.sleep(10)
#print('Подождали 30 сек')

body = driver.find_element(By.TAG_NAME, 'body')
body.send_keys(Keys.PAGE_DOWN)	
tm.sleep(4)
page_source = str(driver.page_source)
# Создание объекта BeautifulSoup для парсинга HTML-кода
soup = BeautifulSoup(page_source, 'html.parser')
#работа с html
code = 876124103
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
print('Ссылка на товар: ' + str(url))
print('Цена товара: ' + str(d_price))
print('ID продавца: ' + str(id_seller))
print('Наименование продавца: ' + str(seller))	
print('Ссылка продавца: ' + str(href_seller))
print('Статус товара: ' + str(status))
df = pd.concat([
		df, pd.DataFrame({
		'Код товара': [int(code)],
		'Название товара': [name],
		'URL страницы с товаром': [url],
		'Цена с учетом скидок без Ozon Карты': [int(d_price)],
		'Ссылка продавца': [href_seller],
		'Наименование продавца': [seller],
		'ID продавца': [int(id_seller)],
		'Статус': [status]
		})
	], ignore_index=True)
driver.quit()




