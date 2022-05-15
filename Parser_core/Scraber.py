import requests
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scraber:
    def __init__(self, scraber_=None, source_=None):
        self.scraber = scraber_
        self.source = source_

    @classmethod
    def create_scraber(cls, headers, source):
        """Создаем на основе headers скрабер requests"""
        scraber = requests.Session()
        scraber.headers = headers
        return cls(scraber, source)

    def return_page(self, page_id, restart=0):
        """Получаем страничку скрабером если ошибка то пропускаем"""
        if self.source == 'PubMed':
            url = 'https://pubmed.ncbi.nlm.nih.gov/{}/'.format(page_id)
        elif self.source == 'PMC':
            url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/{}/'.format(page_id)

        print(url)

        page = self.scraber.get(url)
        print(page.status_code)
        if page.status_code == 200:
            return page
        elif page.status_code == 403:
            print('Connection error 403')
            while restart < 2:
                time.sleep(10 + restart*10)
                self.return_page(page_id, restart+1)
        else:
            print('Connection error', page.status_code)
            print(url)

    def get_page(self, page_id):
        try:
            page = self.return_page(page_id)
        except Exception as e:
            print(e)
            page = None
        finally:
            return page, page_id


# path_to_driver = os.path.abspath('chromedriver')
path_to_driver = str(Path.joinpath(Path(__file__).resolve().parent, 'chromedriver'))
print(path_to_driver)

class Driver:
    def __init__(self, driver_=None, source_=None):
        self.driver = driver_
        self.source = source_

    def run_driver(self, headers):
        chrome_options = Options()
        for key, value in headers.items():
            chrome_options.add_argument(f'{key}={value}')
        self.driver = webdriver.Chrome(executable_path=path_to_driver, options=chrome_options)

    def close_driver(self):
        self.driver.close()

    def get_page(self, page_id):
        if self.source == 'PMC':
            url = 'https://pubmed.ncbi.nlm.nih.gov/{}/'.format(page_id)
        elif self.source == 'PubMed':
            url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/{}/'.format(page_id)
        try:
            self.driver.get(url=url)
        except Exception as e:
            print(e)
            self.driver.page_source = None
        finally:
            return self.driver.page_source




