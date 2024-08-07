import os
import telebot
import pandas as pd

import requests
import webdriver_manager


from bs4 import BeautifulSoup
import time as tm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc



#my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
options = uc.ChromeOptions()
options.add_argument("--headless")
#options.add_argument(f"user-agent={my_user_agent}")
 
# Initialize Chrome WebDriver with the specified options
#uc.TARGET_VERSION = 126
driver = uc.Chrome(options=options)


# Загрузка кодов товаров из файла
with open('codes.txt', 'r') as f:
    codes = f.read().splitlines()

# Создание пустого DataFrame для хранения данных
# df = pd.DataFrame(columns=['Код товара', 'Название товара', 'URL страницы с товаром', 'URL первой картинки', 'Цена базовая', 'Цена с учетом скидок без Ozon Карты', 'Цена по Ozon Карте', 'Продавец', 'Количество отзывов', 'Количество видео', 'Количество вопросов', 'Рейтинг товара', 'Все доступные характеристики товара', 'Информация о доставке в Москве'])
df = pd.DataFrame()

driver.implicitly_wait(10)

# Парсинг каждого товара
for code in codes:
     try:
        print(code)
        #получение ссылки на товар через костыли
        #ссылка на главную страницу озон
        url = 'https://www.ozon.ru/'

        # Загрузка страницы товара с помощью веб-драйвера
        driver.get(url)
        print(driver.status_code)
        tm.sleep(10)
        #WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "a4da_32 tsBody400Small"), "Везде"))     
        #find_goods = driver.find_element(By.CSS_SELECTOR, "input[name='text']")
        #find_goods = driver.find_element(By.NAME, "text")
 
        #find_goods = driver.find_element(By.placeholder, "Искать на Ozon")
        
        find_goods.clear()
        find_goods.send_keys(code)
        tm.sleep(2)

        find_goods.send_keys(Keys.ENTER)
        tm.sleep(2)

        try:
            find_goods = driver.find_element(By.XPATH, '//*[@id="paginatorContent"]/div/div/div/a')
        except:
            continue
        find_goods.click()

        tm.sleep(6)

        # Получение HTML-кода страницы
        page_source = str(driver.page_source)

        # Создание объекта BeautifulSoup для парсинга HTML-кода
        soup = BeautifulSoup(page_source, 'html.parser')
        # работа с html
        # Получение названия товара
        name_element = soup.find('h1')
        name = name_element.text.strip().replace('"', "&quot;") if name_element else 'No name'
        
        # Получение URL первой картинки если первое видео
        if soup.find('div', {"data-widget": "webGallery"}).find('video-player') or soup.find('div', {"data-widget": "webGallery"}).find('video'):
            print('video')
            find_img = driver.find_element(By.XPATH, '//*[@data-index="1"]').find_element(By.TAG_NAME, 'img')
            find_img.click()
            tm.sleep(2)
            page_source = str(driver.page_source)
            soup = BeautifulSoup(page_source, 'html.parser')
            image_element = soup.select(f'img[alt*="{name[:30]}"]')
            print(image_element)
            image_url = image_element[0].get('src') if image_element else ''
        else:
            # Получение URL первой картинки
            print('photo')
            image_element = soup.select(f'img[alt*="{name[:30]}"]')
            image_url = image_element[0].get('src') if image_element else ''

        # Получение информации о доставке в Москве
        driver.execute_script("window.scrollBy(0, 7200)")
        tm.sleep(3)
        page_source = str(driver.page_source)
        soup = BeautifulSoup(page_source, 'html.parser')
        try:
            delivery_info_element = soup.find('h2', string="Информация о доставке").parent
            delivery_info = delivery_info_element.text.strip() if delivery_info_element else ''
        except:
            delivery_info = ''

        # Получение URL страницы с товаром
        page_url = url + '/product/' + code

        # Получение цены со скидкой без Ozon Карты
        try:
            price_element = soup.find('span', string="без Ozon Карты").parent.parent.find('div').findAll('span')
            discount_price = price_element[0].text.strip() if price_element[0] else ''
        except:
            discount_price = 0
            print(discount_price)
        # Получение цены базовая
        try:
            base_price = price_element[1].text.strip() if price_element[1] is not None else ''
        except:
            base_price = 0
            print(base_price)

        # Получение цены по Ozon Карте
        try:
            ozon_card_price_element = soup.find('span', string="c Ozon Картой").parent.find('div').find('span')
            ozon_card_price = ozon_card_price_element.text.strip() if ozon_card_price_element else ''
        except:
            ozon_card_price = 0
            print(ozon_card_price)

        # Заполнение DataFrame
        df = pd.concat([
            df, pd.DataFrame({
                'Код товара': [code],
                'Название товара': [name],
                'URL страницы с товаром': [page_url],
                'URL первой картинки': [image_url],
                'Цена базовая': [base_price],
                'Цена с учетом скидок без Ozon Карты': [discount_price],
                'Цена по Ozon Карте': [ozon_card_price],
                'Продавец': [seller],
                'Количество отзывов': [reviews_count],
                'Количество видео': video_count,
                'Количество вопросов': questions_count,
                'Рейтинг товара': rate_info,
                'Все доступные характеристики товара': [characteristics],
                'Информация о доставке в Москве': [delivery_info],
                **dict(characteristics_zip)
            })
        ], ignore_index=True)
    # except:
    #     continue

# Закрытие веб-драйвера
driver.close()
driver.quit()

print(df.to_string())

# Сохранение DataFrame в файл
df.to_excel('products.xlsx', index=False)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ID = os.getenv('TELEGRAM_ID')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

bot.send_message(TELEGRAM_ID, df.to_string())







