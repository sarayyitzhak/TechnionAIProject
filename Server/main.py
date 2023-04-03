from Server.DataBuilder.GovDataBuilder import gov_build_data
from Server.DataBuilder.RestDataBuilder import rest_build_data
from Server.DataParser.DataParser import parse_data
from Server.DataBuilder.GoogleDataBuilder import google_build_data
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# import time
import pandas as pd
from Server.DataBuilder.Utils import write_to_file
import textdistance
import re
from itertools import combinations


def main():
    # driver = webdriver.Chrome(executable_path='chromedriver')
    # wait = WebDriverWait(driver, 10)
    # driver.get("https://www.google.com/maps")
    # wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput"))).send_keys("מחוז חיפה")
    # wait.until(EC.element_to_be_clickable((By.ID, "searchbox-searchbutton"))).click()
    # time.sleep(5)
    # ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//html/body")).context_click().perform()
    # print(wait.until(EC.visibility_of_element_located(
    #     (By.ID, "action-menu"))).text)

    # name1 = "Wasabi Beach ‏מסעדה סושי"
    # name2 = "WASABI SUSHI"

    # names = ["damerau_levenshtein", "strcmp95", "needleman_wunsch", "gotoh", "smith_waterman", "ratcliff_obershelp"]
    # for (name, value) in zip(names, other_distance(name1, name2)):
    #     print(name + ": " + str(value))
    # gov_build_data()
    parse_data()
    # rest_build_data()
    # google_build_data()
    # df = pd.read_json("./Dataset/google-data.json")
    # cities = {}
    # for i in range(len(df)):
    #     for address in df["address_components"][i]:
    #         if 'locality' in address["types"]:
    #             if address["long_name"] not in cities:
    #                 cities[address["long_name"]] = 0
    #             cities[address["long_name"]] += 1
    #
    # rel_cities = [city for city in cities if cities[city] > 55]
    # print(rel_cities)

    # print(other_distance("Shrimps House", "שרימפס האוס Shrimps House"))
    # print([" ".join(item) for item in list(combinations("שרימפס האוס Shrimps House".split(" "), 2))])
    # print(list(combinations([0,1,2,3], 2)))

def other_distance(s1, s2):
    return [textdistance.damerau_levenshtein.normalized_similarity(s1, s2),
            textdistance.strcmp95.normalized_similarity(s1, s2),
            textdistance.needleman_wunsch.normalized_similarity(s1, s2),
            textdistance.gotoh.normalized_similarity(s1, s2),
            textdistance.smith_waterman.normalized_similarity(s1, s2),
            textdistance.ratcliff_obershelp.normalized_similarity(s1, s2)]


if __name__ == '__main__':
    main()
