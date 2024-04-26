import streamlit as st
import json
import os
import base64
import subprocess
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

st.set_page_config(layout="wide")

def save_resource(content, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as file:
        file.write(content)

def process_har_file(har_content, base_dir):
    main_html_path = None
    entries = har_content['log']['entries']
    for entry in entries:
        url = entry['request']['url']
        parsed_url = urlparse(url)
        path = os.path.join(base_dir, parsed_url.netloc, parsed_url.path.strip('/'))
        if not path.endswith(os.path.sep):
            path += '.html' if 'text/html' in entry['response']['content']['mimeType'] else ''
        content = entry['response']['content'].get('text', '')
        if entry['response']['content'].get('encoding') == 'base64':
            content = base64.b64decode(content)
        else:
            content = content.encode()
        save_resource(content, path)
        if 'text/html' in entry['response']['content']['mimeType'] and main_html_path is None:
            main_html_path = path
    return main_html_path

def start_http_server(base_dir):
    cmd = f"python -m http.server --directory {base_dir} 8000"
    subprocess.Popen(cmd, shell=True)

def take_screenshot(url, save_path):
    # Retrieve GitHub token from environment
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise Exception("GitHub token not found in environment.")

    # Start Xvfb before starting Chrome
    xvfb_cmd = ["Xvfb", ":99", "-screen", "0", "1920x1080x24", "&"]
    subprocess.Popen(xvfb_cmd)
    os.environ["DISPLAY"] = ":99"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Add a cookie with the GitHub token
    driver.add_cookie({"name": "token", "value": github_token, "path": "/", "secure": True})

    # Refresh the page with the cookie set
    driver.get(url)

    driver.set_window_size(1920, 1080)  # Adjust as necessary
    driver.save_screenshot(save_path)
    driver.quit()

def main():
    st.title("HAR File Processor")

    uploaded_file = st.file_uploader("Upload HAR file", type=['har'])
    if uploaded_file is not None:
        har_content = json.load(uploaded_file)
        base_dir = "/workspaces/templater/data"
        if st.button("Process and Save HAR File"):
            main_html_path = process_har_file(har_content, base_dir)
            start_http_server(base_dir)  # Ensure the HTTP server is running
            if main_html_path:
                st.success(f"All files have been saved successfully to {base_dir}!")
                local_url = f"http://localhost:8000/{os.path.relpath(main_html_path, base_dir)}"
                st.markdown(f"### Main HTML Preview:")
                st.markdown(f'<iframe src="{local_url}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
                # Take a screenshot
                screenshot_path = os.path.join(base_dir, "screenshot.png")
                take_screenshot(local_url, screenshot_path)
                st.info(f"Screenshot saved to {screenshot_path}")
            else:
                st.error("No HTML file found in the HAR data.")

if __name__ == "__main__":
    main()
