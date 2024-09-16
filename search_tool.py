from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import numpy as np
import time
from typing import Tuple, Dict
from utils import get_page_soup
from llama_index.core.tools import FunctionTool
import re

class GoogleSearch():
    def __init__(self) -> None:
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.google.com")
    
    def search(self, search_query: str):
        search_box = self.driver.find_element(By.NAME, "q")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)
        search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
        return search_results
        
class BonBanhCarPrice():
    def __init__(self) -> None:
        self.tool = FunctionTool.from_defaults(fn=self.get_old_price)
        self.base_url = "https://bonbanh.com/"

    def _get_old_price_from_bonbanh(self, url: str) -> Tuple[int, int]:
        soup = get_page_soup(url)
        price_soup = soup.find_all("b", itemprop='price')
        car_items = soup.find_all(class_=re.compile(r'\bcar-item\b'))
        metadata_link = []
        for car_item in car_items:
            car_url = car_item.find("a", href=True).get("href").lower()
            car_url = self.base_url + car_url
            metadata_link.append(car_url)
        car_price = []
        for price in price_soup:
            price = price.get_text().lower()
            if "tỷ" in price:
                car_price.append(float(price.replace(" tỷ ", ".").replace("triệu", "").strip()) * 1e9)
            elif "triệu" in price:
                car_price.append(float(price.split(" ")[0]) * 1e6)
        q1 = int(np.quantile(car_price, 0.25))
        q2 = int(np.quantile(car_price, 0.75))
        return {"price_range": [q1, q2], "metadata_link": metadata_link[:3]}

    def get_old_price(self, query: str) -> Dict:
        "get old car price from bonbanh.com"
        search_tool = GoogleSearch()
        search_results = search_tool.search(query + " bonbanh")
        price_range = (None, None)
        for _, result in enumerate(search_results, start=1):
            link_element = result.find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href")

            if "bonbanh" not in link:
                continue
            price_range = self._get_old_price_from_bonbanh(link)
            break
        search_tool.driver.quit()
        return price_range