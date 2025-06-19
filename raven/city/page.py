from bs4 import BeautifulSoup
from os.path import exists
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd, makedirs
from os.path import exists
import requests


class Page:

    def __init__(s, page_dir=getcwd() + "/data/page"):
        s.page_dir = page_dir
        if not exists(page_dir):
            makedirs(page_dir)
        s.options = Options()
        s.options.add_argument("--headless")

    def save_html(s, url, file_path):
        
        driver = webdriver.Chrome(options=s.options)
        # driver = webdriver.Chrome(ChromeDriverManager().install())

        try:
            driver.get(url)          
            # Wait for core content
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, "main"))
            )            
            # Verify page completion
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )   
        except TimeoutException:
            print("TimeoutException: Page took too long to load")
        finally:
            html = driver.page_source
            driver.quit()

        html = requests.get(url).text

        # print("Write", file_path)

        file = open(file_path, "w", encoding="utf-8")
        file.write(html)
        file.close()
            
        return html

    def id(s, st):
        return hashlib.sha256(str.encode(st)).hexdigest()

    def get_html(s, url):

        dig = s.id(url)
        file_path = s.page_dir + '/' + str(dig)
        if exists(file_path):
            file = open(file_path, "r", encoding="utf-8")
            html = file.read()
            file.close()
            print("Read", dig, url)
        else:
            print("Downloading", url)
            html = s.save_html(url, file_path)
            print("Saved", dig, url)
        return html

    def get_soup(s, url):
        html = s.get_html(url)
        return BeautifulSoup(html, "html.parser")
    

if __name__ == "__main__":

    # base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    # url = base_url + "/api/3/action/package_show"
    # package = requests.get(url).json()
    # print("---package")
          
    page_dir = getcwd() + '/data_test/page'
    page = Page(page_dir=page_dir)
    soup = page.get_soup("https://open.toronto.ca/catalogue/?n=5")
    