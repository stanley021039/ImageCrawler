import json
import time
import logging
import os
import shutil
import zipfile

from flask import Flask, render_template, jsonify, request, make_response, Response, send_file
from flask_restful import Api, Resource

from crawlers import pixabayCrawler, unsplashCrawler

app=Flask(__name__)
api = Api(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "logs", "app.log"), filemode='w')

@app.before_request
def set_application_root():
    script_name = request.headers.get('X-Script-Name', '')
    app.config['APPLICATION_ROOT'] = script_name

class Crawler:
    def __init__(self, query, sessionToken):
        self.query = query
        self.sessionToken = sessionToken

    def get_images(self, site, amount):
        if site == 'unsplash':
            self.crawler = unsplashCrawler(self.query, self.sessionToken)
        if site == 'pixabay':
            self.crawler = pixabayCrawler(self.query, self.sessionToken)
        
        images_name = []
        while len(images_name) < amount:
            new_images_name = self.crawler.get_pic(amount=amount-len(images_name))
            if not new_images_name:  # no more images
                break
            images_name.extend(new_images_name)
            for image_name in new_images_name:
                yield f"data: {image_name}\n\n"
            time.sleep(1)
        self.crawler.quit()
        yield "data: CLOSE\n\n"

class CrawlerPage(Resource):
    def get(self):
        return make_response(render_template('index.html', **app.config))

class CrawlerAPI(Resource):
    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        site = request.args.get('site', '')
        query = request.args.get('query', '')
        amount = int(request.args.get('amount', '20'))
        crawler = Crawler(query, sessionToken)
        return Response(crawler.get_images(site, amount), content_type='text/event-stream')
        
class Images(Resource):
    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        img_name = request.args.get('img_name', '')
        image_path = os.path.join(BASE_DIR, f"pic/{sessionToken}/{img_name}")
        return send_file(image_path, mimetype='image/jpeg')

    def delete(self):
        sessionToken = request.args.get('sessionToken', '')
        img_name = request.args.get('img_name', '')
        img_path = os.path.join(BASE_DIR, f"pic/unsplash/{sessionToken}/{img_name}")
        if os.path.exists(img_path):
            os.remove(img_path)
            return {'message': 'Image deleted successfully'}
        else:
            return {'message': 'Image not found'}, 404

class Sessions(Resource):
    def zipfiles(self, img_dir, save_dir):
        with zipfile.ZipFile(save_dir, 'w') as zipf:
            for root, dirs, files in os.walk(img_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, img_dir))

    def get(self):
        sessionToken = request.args.get('sessionToken', '')
        session_dir = os.path.join(BASE_DIR, f"pic/{sessionToken}")
        if not os.path.exists(session_dir):
            return {'message': 'Haven\'t creat session, please fetch images first...'}, 404

        zip_file_path = os.path.join(BASE_DIR, f"temp/{sessionToken}.zip")
        try:
            self.zipfiles(session_dir, zip_file_path)
            return send_file(zip_file_path, as_attachment=True)

        except Exception as e:
            return {'message': 'Failed to create zip file...'}, 500

        finally:
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)

    def delete(self):
        sessionToken = request.args.get('sessionToken', '')
        session_dir = os.path.join(BASE_DIR, f"pic/{sessionToken}")
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
            return {'message': 'Session deleted successfully'}
        else:
            print('not exist')
            return {'message': 'Session not found'}, 404

api.add_resource(CrawlerPage, f"{app.config['APPLICATION_ROOT']}/")
api.add_resource(CrawlerAPI, f"{app.config['APPLICATION_ROOT']}/api/Crawler")
api.add_resource(Sessions, f"{app.config['APPLICATION_ROOT']}/api/Sessions")
api.add_resource(Images, f"{app.config['APPLICATION_ROOT']}/api/Images")

if __name__ == '__main__':
    app.run(app, host='0.0.0.0', port=8001)
