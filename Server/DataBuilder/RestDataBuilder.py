from selenium import webdriver
from selenium.webdriver.common.by import By
from Server.DataBuilder.Utils import write_to_file
import time

SCROLL_JUMPING = 2000
SLEEP_TIME = 2


def scroll_to_end(driver):
    old_scroll_value = -1
    scroll_value = driver.execute_script("return window.pageYOffset;")
    while old_scroll_value != scroll_value:
        driver.execute_script("window.scrollBy(0, " + str(SCROLL_JUMPING) + ");")
        time.sleep(SLEEP_TIME)
        old_scroll_value = scroll_value
        scroll_value = driver.execute_script("return window.pageYOffset;")


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
    driver.get('https://www.rest.co.il/restaurants/haifa/')

    scroll_to_end(driver)
    write_to_file(get_data(driver), "../Dataset/rest-data.json")

    driver.quit()
