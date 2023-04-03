from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Server.DataBuilder.Utils import write_to_file
import re
import math
import json


def get_raw_data(chrome_driver_path, web_paths):
    res = []
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    for web_path in web_paths:
        res += get_raw_data_by_city(driver, web_path["path"], web_path["city"])
    driver.quit()
    return res


def get_raw_data_by_city(driver, path, city):
    res = []
    driver.get('https://www.rest.co.il/restaurants/' + path + '/')
    for i in range(get_num_of_pages(driver)):
        driver.get('https://www.rest.co.il/restaurants/' + path + '/page-' + str(i + 1) + "/")
        res += get_page_raw_data_by_city(driver, city)
    return res


def get_num_of_pages(driver):
    pages = 0
    try:
        restaurant_info = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "restaurant-info-top")))
        rest_num = int(re.sub(",", "", restaurant_info.text.split(" ")[1]))
        pages = math.ceil(rest_num / 15)
    except:
        pass
    return pages


def get_page_raw_data_by_city(driver, city):
    res = []
    try:
        elements = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "feature-column")))
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

            res.append({
                "id": r_id,
                "name": name,
                "type": tags[0] if tags[0] else None,
                "kosher": "כשר" in tags,
                "city": city,
                "address": address
            })
    except:
        pass
    return res


def rest_build_data():
    try:
        with open('./DataConfig/rest-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            write_to_file(get_raw_data(config["chrome_driver_path"], config["web_paths"]), config["output_path"])
    except IOError:
        print("Error")
