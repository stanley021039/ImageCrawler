import os
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class pixabayCrawler():
    def __init__(self, query, sessionToken):
        try:
            with open('external_resource/pixabay_api_key.txt', 'r') as f:
                self.api_key = f.read()
        except Exception as e:
            print("Error: The file containing Pixabay API key was not found.")
            sys.exit()
        self.save_dir = f'pic/{sessionToken}'
        self.mkdir(self.save_dir)
        self.query = query

    def mkdir(self, path):
        path = path.strip()
        if not os.path.exists(path):
            os.mkdir(path)
            print(f'Creat folder {path} seccessfully')

    def fetch_pixabay_images(self, amount=20):
        page = 0
        hits = []
        while amount > 0:
            per_page = max(min(200, amount), 3)  # pixabay not allow per_page < 3
            page += 1
            url = f"https://pixabay.com/api/?key={self.api_key}&q={self.query}&per_page={per_page}&page={page}"
            print('request endpoint:', url)
            response = requests.get(url)
            data = response.json()
            if 'hits' in data:
                print(amount)
                hits.extend(data['hits'][:amount])
            else:
                print("Error fetching data from Pixabay")
                break
            amount -= 200
        return hits
    
    def trans_md5(self, img_url):
        m = hashlib.md5()
        m.update(img_url.encode("utf8"))
        return m.hexdigest()

    def download_image(self, image_info):
        image_url = image_info['largeImageURL']
        img_name = f'{self.trans_md5(image_url)}.jpg'
        save_path = os.path.join(self.save_dir, img_name)
        response = requests.get(image_url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return img_name

    def download_images(self, image_data):
        images_name = []
        with ThreadPoolExecutor(max_workers=10) as executor:  # 設置最大工作線程數
            future_to_url = {executor.submit(self.download_image, image_info): image_info for image_info in image_data}
            for future in concurrent.futures.as_completed(future_to_url):
                image_name = future.result()
                images_name.append(image_name)
        return images_name
    
    def get_pic(self, amount=20):
        hits = self.fetch_pixabay_images(amount=amount)
        images_name = self.download_images(hits)
        return images_name
    
    def quit(self):
        pass

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
