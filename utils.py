from bs4 import BeautifulSoup
import requests

def get_page_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None