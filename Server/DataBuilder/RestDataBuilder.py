from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Server.DataBuilder.Utils import write_to_file
import re
import math
import json


class RestDataBuilder:

    def __init__(self, chrome_driver_path: str, api_url: str, web_paths: list):
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path)
        self.api_url = api_url
        self.web_paths = web_paths
        self.data = []

    def build_data(self):
        for web_path in self.web_paths:
            self.get_raw_data_by_city(web_path["path"], web_path["city"])
        self.driver.quit()

    def get_raw_data_by_city(self, path, city):
        self.driver.get(self.api_url + path + '/')
        for i in range(self.get_num_of_pages()):
            self.driver.get(self.api_url + path + '/page-' + str(i + 1) + "/")
            self.get_page_raw_data_by_city(city)

    def get_num_of_pages(self):
        pages = 0
        try:
            restaurant_info = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "restaurant-info-top")))
            rest_num = int(re.sub(",", "", restaurant_info.text.split(" ")[1]))
            pages = math.ceil(rest_num / 15)
        except:
            pass
        return pages

    def get_page_raw_data_by_city(self, city):
        try:
            elements = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "feature-column")))
            for element in elements:
                r_id = element.get_attribute("data-customer")
                info_element = element.find_element(By.CLASS_NAME, 'feature-info-bottom')
                values = info_element.text.split("\n")
                if len(values) < 3:
                    continue
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
        except:
            pass


def rest_build_data():
    try:
        with open('./DataConfig/rest-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            builder = RestDataBuilder(config["chrome_driver_path"], config['api_url'], config['web_paths'])
            builder.build_data()
            write_to_file(builder.data, config["output_path"])
    except IOError:
        print("Error")
