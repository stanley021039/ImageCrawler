# Image Viewer

This project is a simple web application built with Flask that allows users to fetch and view images from either Unsplash or Pixabay. It provides functionality to fetch images based on user queries, display them, and download them as a ZIP file.

## Features

- **Image Fetching:** Users can enter a query and select a source (Unsplash or Pixabay) to fetch images.
- **Real-time Display:** Fetched images are displayed in real-time as they are received from the server.
- **Download as ZIP:** Users can download all fetched images as a ZIP file for offline use.

## Demo Page

Visit the [demo page](https://www.hd0619-info.site/ImageCrawler) to see the Image Viewer in action.


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/stanley021039/ImageCrawler.git
    ```

2. **Establish Virtual Environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. **Setup Apache Environment:**
    Add the following configuration to your Apache virtual host file:
    ```apache
    <Location "/ImageCrawler">
        RequestHeader set X-Script-Name "/ImageCrawler"
        ProxyPass "http://127.0.0.1:8001"
        ProxyPassReverse "http://127.0.0.1:8001"
    </Location>
    ```
    This configuration will proxy requests to the ImageCrawler application running on `http://127.0.0.1:8001`. Adjust the `Location` directive and proxy URLs as needed based on your server setup.
    Make sure to reload or restart Apache for the changes to take effect:
    ```bash
    sudo service apache2 reload
    ```

5. **Run the application using Gunicorn:**
    ```bash
    gunicorn -c gunicorn_config.py image_crawler_app:app --log-level debug --daemon
    ```
    With this configuration, Apache will forward requests to the ImageCrawler application, allowing it to be accessible via the specified URL path.


## Usage

1. Access the web application using a web browser.
2. Enter a query and select a source (Unsplash or Pixabay).
3. Click the "Fetch Images" button to start fetching and displaying images.
4. Optionally, adjust the amount of images to fetch using the input field.
5. Click the "Download all images as ZIP" button to download fetched images as a ZIP file.

## Project Structure

- **app.py:** Main Flask application file containing routes and server configurations.
- **unsplash_crawler.py:** Module for fetching images from Unsplash.
- **pixabay_crawler.py:** Module for fetching images from Pixabay.
- **index.html:** HTML template for displaying fetched images.
- **static/css/index.css:** CSS file for styling the HTML template.
- **static/js/index.js:** JavaScript file for client-side functionality.

## Dependencies

- Flask
- Flask-RESTful