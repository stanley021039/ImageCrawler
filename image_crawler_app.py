from flask import Flask, render_template, jsonify, request, make_response, Response, send_file
from flask_restful import Api, Resource, reqparse
import time
import os
import logging
import json
import zipfile
from unsplash_crawler import unsplashCrawler
from pixabay_crawler import pixabayCrawler

app=Flask(__name__)
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "logs", "app.log"), filemode='w')

@app.before_request
def set_application_root():
    script_name = request.headers.get('X-Script-Name', '')
    app.config['APPLICATION_ROOT'] = script_name


class CrawlerPage(Resource):
    def get(self):
        return make_response(render_template('index.html', **app.config))

class CrawlerData(Resource):
    def generate_images(self, site, query, amount, sessionToken):
        if site == 'unsplash':
            self.crawler = unsplashCrawler(query, sessionToken)
        if site == 'pixabay':
            self.crawler = pixabayCrawler(query, sessionToken)
        
        images_name = []
        while len(images_name) < amount:
            print('amount=', amount-len(images_name))
            new_images_name = self.crawler.get_pic(amount=amount-len(images_name))
            if len(new_images_name) == 0:  # no more images
                break
            images_name.extend(new_images_name)
            for image_name in new_images_name:
                yield f"data: {image_name}\n\n"
            time.sleep(1)
        self.crawler.quit()
        yield "data: CLOSE\n\n"

    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        site = request.args.get('site', '')
        query = request.args.get('query', '')
        amount = int(request.args.get('amount', '0'))
        print(f'request site={site}, query={query}, amount={amount}')
        return Response(self.generate_images(site, query, amount, sessionToken), content_type='text/event-stream')

class GetImage(Resource):
    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        img_name = request.args.get('img_name', '')
        image_path = os.path.join(BASE_DIR, f"pic/{sessionToken}/{img_name}")
        return send_file(image_path, mimetype='image/jpeg')

class SessionImage(Resource):
    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        img_dir = os.path.join(BASE_DIR, f"pic/{sessionToken}")
        if not os.path.exists(img_dir):
            return {'message': 'Session not found'}, 404

        zip_file_path = os.path.join(BASE_DIR, f"temp/{sessionToken}.zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(img_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, img_dir))

        return send_file(zip_file_path, as_attachment=True)
        
    def delete(self):
        sessionToken = request.args.get('sessionToken', '')
        img_name = request.args.get('img_name', '')
        img_path = os.path.join(BASE_DIR, f"pic/unsplash/{sessionToken}/{img_name}")
        if os.path.exists(img_path):
            os.remove(img_path)
            return {'message': 'Image deleted successfully'}
        else:
            return {'message': 'Image not found'}, 404


api.add_resource(CrawlerPage, f"{app.config['APPLICATION_ROOT']}/")
api.add_resource(CrawlerData, f"{app.config['APPLICATION_ROOT']}/api/Crawler")
api.add_resource(GetImage, f"{app.config['APPLICATION_ROOT']}/api/GetImage")
api.add_resource(SessionImage, f"{app.config['APPLICATION_ROOT']}/api/SessionImage")


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8001)