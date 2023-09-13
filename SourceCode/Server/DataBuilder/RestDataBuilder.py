from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import math
import pandas as pd


class RestDataBuilder:

    def __init__(self, config, progress_func):
        service = Service(executable_path=config["chrome_driver_path"])
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.minimize_window()
        self.api_url = config['api_url']
        self.web_paths = config['web_paths']
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.rest_to_pages_count = {}
        self.num_of_restaurants = 0
        self.data = []

    def pre_build_data(self):
        for web_path in self.web_paths:
            self.driver.get(self.api_url + web_path["path"] + '/')
            restaurants = self.get_num_of_restaurants()
            self.rest_to_pages_count[web_path["path"]] = math.ceil(restaurants / 15)
            self.num_of_restaurants += restaurants

    def build_data(self):
        for web_path in self.web_paths:
            self.get_raw_data_by_city(web_path["path"], web_path["city"])
        self.driver.quit()

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')

    def get_raw_data_by_city(self, path, city):
        for page in range(self.rest_to_pages_count[path]):
            self.driver.get(self.api_url + path + '/page-' + str(page + 1) + "/")
            self.get_page_raw_data_by_city(city)

    def get_num_of_restaurants(self):
        restaurant_info = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "restaurant-info-top")))
        return int(re.sub(",", "", restaurant_info.text.split(" ")[1]))

    def get_page_raw_data_by_city(self, city):
        elements = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "feature-column")))
        for element in elements:
            r_id = element.get_attribute("data-customer")
            info_element = element.find_element(By.CLASS_NAME, 'feature-info-bottom')
            values = info_element.text.split("\n")
            rest_name = None
            rest_type = None
            rest_price_level = None
            try:
                price_element = info_element.find_element(By.CLASS_NAME, 'nis-color')
                rest_price_level = len(price_element.find_element(By.TAG_NAME, 'small').text)
            except NoSuchElementException:
                pass
            if len(values) >= 3:
                rest_name = values[0]
                if "חוות דעת" in values[1]:
                    tags = values[2].split(" | ")
                    address = values[3].split(" | ")[0].split(", ")[0]
                else:
                    tags = values[1].split(" | ")
                    address = values[2].split(" | ")[0].split(", ")[0]

                if tags[0]:
                    rest_type = tags[0].split(", ")[0]
                    if "כשר" in rest_type or "מחיר" in rest_type or "שף" in rest_type:
                        rest_type = None

                self.data.append({
                    "id": r_id,
                    "name": rest_name,
                    "type": rest_type,
                    "kosher": "כשר" in tags,
                    "rest_price_level": rest_price_level,
                    "city": city,
                    "address": address
                })
            if self.progress_func is not None:
                self.progress_func(rest_name, self.num_of_restaurants)
