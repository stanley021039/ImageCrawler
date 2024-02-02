#coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import os
import time
import hashlib


class unsplashCrawler():
    def __init__(self, query, sessionToken):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        web_url = f'https://unsplash.com/s/photos/{query}'
        self.save_dir = f'pic/{sessionToken}'
        self.mkdir(self.save_dir)
        chrome_opt = Options()
        chrome_opt.add_argument('--headless')
        chrome_opt.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_opt)
        print('Start sending the get requeset...')
        self.driver.get(web_url)
        self.load_count = 0

    def mkdir(self, path):
        path = path.strip()
        if not os.path.exists(path):
            os.mkdir(path)
            print(f'Creat folder {path} seccessfully')
    
    def save_pic(self, url, pic_name):
        img = requests.get(url, headers=self.header)
        f = open(pic_name, 'ab')
        f.write(img.content)
        f.close()

    def scroll_down(self, height):
        self.driver.execute_script("window.scrollTo(0,%d);" % height)
        time.sleep(3)
    
    def click_load_more_btn(self):
        load_more_button = self.driver.find_element(By.XPATH, "//button[text()='Load more']")
        self.driver.execute_script("arguments[0].click();", load_more_button)
        time.sleep(3)

    def trans_md5(self, img_url):
        m = hashlib.md5()
        m.update(img_url.encode("utf8"))
        return m.hexdigest()
    
    def get_img_urls(self, soup):
        all_img_urls = []
        mItv1_div = soup.find('div', class_='mItv1')
        for row in mItv1_div:
            for figure in row:
                if figure.name == 'div':
                    continue
                img_elements = figure.find_all('img', class_='a5VGX')
                all_img_urls.append(img_elements[0]['src'])
        return all_img_urls

    def get_pic(self, amount=None):
        all_img_urls = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        all_img_urls = self.get_img_urls(soup)
        print(f'Get {len(all_img_urls)} urls successfully')

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1500);")
        # click 'load more' btn at first time
        if self.load_count == 0:
            self.load_count =+ 1
            time.sleep(2)
            self.click_load_more_btn()
        buffer_time = 3
        start_timg = time.time()
        
        new_images_name = []
        for img_url in all_img_urls:
            img_name = self.trans_md5(img_url) + '.jpg'
            if img_name not in os.listdir(self.save_dir):
                img_path = os.path.join(self.save_dir, img_name)
                self.save_pic(img_url, img_path)
                new_images_name.append(img_name)
            if amount is not None and len(new_images_name) >= amount:
                break
        print(f'Save pictures successfully')
        time.sleep(max(0, buffer_time - (time.time()-start_timg)))
        return new_images_name

    def quit(self):
        self.driver.quit()
