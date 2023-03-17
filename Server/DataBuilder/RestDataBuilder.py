from selenium import webdriver
from selenium.webdriver.common.by import By
from Server.DataBuilder.Utils import write_to_file
import time
import re
import math

SLEEP_TIME = 1


def get_num_of_pages(driver):
    driver.get('https://www.rest.co.il/restaurants/haifa/')
    time.sleep(1)
    restaurant_info = driver.find_element(By.CLASS_NAME, 'restaurant-info-top')
    rest_num = int(re.sub(",", "", restaurant_info.text.split(" ")[1]))
    return math.ceil(rest_num / 15)


def get_data(driver):
    res = []
    info_elements = driver.find_elements(By.CLASS_NAME, 'feature-info-bottom')
    for info_element in info_elements:
        values = info_element.text.split("\n")
        if len(values) < 3:
            continue
        name = values[0]
        if "חוות דעת" in values[1]:
            tags = values[2].split(" | ")
            address = values[3].split(" | ")[0]
        else:
            tags = values[1].split(" | ")
            address = values[2].split(" | ")[0]

        if tags[0]:
            res.append({
                "name": name,
                "type": tags[0],
                "kosher": "כשר" in tags,
                "address": address
            })

    return res


def rest_build_data():
    driver = webdriver.Chrome(executable_path='chromedriver')

    res = []
    for i in range(get_num_of_pages(driver)):
        driver.get('https://www.rest.co.il/restaurants/haifa/page-' + str(i + 1) + "/")
        time.sleep(SLEEP_TIME)
        res += get_data(driver)

    write_to_file(res, "./Dataset/rest-data.json")

    driver.quit()
