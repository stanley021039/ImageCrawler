import requests
import os
import hashlib
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

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
            per_page = min(200, amount)
            amount -= 200
            page += 1
            url = f"https://pixabay.com/api/?key={self.api_key}&q={self.query}&per_page={per_page}&page={page}"
            print('request endpoint:', url)
            response = requests.get(url)
            data = response.json()
            if 'hits' in data:
               hits.extend(data['hits'])
            else:
                print("Error fetching data from Pixabay")
                break
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
