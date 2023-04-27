from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Server.DataBuilder.Utils import write_to_file
import re
import math
import json
import pandas as pd


class RestDataBuilder:

    def __init__(self, config, progress_func):
        self.driver = webdriver.Chrome(executable_path=config["chrome_driver_path"])
        self.api_url = config['api_url']
        self.web_paths = config['web_paths']
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.rest_to_pages_count = {}
        self.restaurant_counter = 0
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
            name = None
            if len(values) >= 3:
                name = values[0]
                if "חוות דעת" in values[1]:
                    tags = values[2].split(" | ")
                    address = values[3].split(" | ")[0].split(", ")[0]
                else:
                    tags = values[1].split(" | ")
                    address = values[2].split(" | ")[0].split(", ")[0]

                self.data.append({
                    "id": r_id,
                    "name": name,
                    "type": tags[0].split(", ")[0] if tags[0] else None,
                    "kosher": "כשר" in tags,
                    "city": city,
                    "address": address
                })
            self.restaurant_counter += 1
            if self.progress_func is not None:
                self.progress_func(name, self.restaurant_counter, self.num_of_restaurants)


def rest_build_data():
    try:
        with open('./Server/DataConfig/rest-data-config.json', 'r', encoding='utf-8') as f:
            builder = RestDataBuilder(json.load(f), None)
            builder.pre_build_data()
            builder.build_data()
            builder.save_data()
    except IOError:
        print("Error")
