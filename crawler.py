from bs4 import BeautifulSoup
from utils import get_page_soup

class VnexpressCrawler():
    def __init__(self, url: str, base_url: str) -> None:
        self.url = url
        self.base_url = base_url
        self._crawled_url = []


    def _get_table_info(self, soup: BeautifulSoup) -> str:
        table_data = ""
        # Find the first <table> tag
        table = soup.find('table')
        if table:
            # Iterate through each row in the table
            for row in table.find_all('tr'):
                # Get all cells (both <td> and <th>)
                cells = row.find_all(['td', 'th'])
                
                # Extract the text from each cell
                for cell in cells:
                    table_data += cell.get_text(strip=True) + ' | '

        return table_data

    def _get_option_info(self, soup: BeautifulSoup) -> str:
        options = soup.find("div", id="phienban")
        option_data = ""
        if options:
            for option in options.find_all("p"):
                option_data += option.get_text() + " "
        return option_data

    def _get_number_of_seat_info(self, soup: BeautifulSoup) -> int:
        technical_detail_data = {}
        technical_detail = soup.find("div", class_="load-more center mt20")
        technical_soup = get_page_soup("https://vnexpress.net" + technical_detail.find("a", href=True).get("href"))
        technical_detail = technical_soup.find("div", class_="list-collaps mb30 list-version-infor")
        for li in technical_detail.find_all("li"):
            # Extract the label (inside <b>) and the value (inside <div> with class td2)
            label = li.find('b').get_text().strip() if li.find('b') else ''
            value = li.find('div', class_='td2').get_text().strip() if li.find('div', class_='td2') else ''
            technical_detail_data[label] = value

        return technical_detail_data.get("Số chỗ", "")
    def _get_technical_detail(self, soup: BeautifulSoup) -> str:
        technical_detail_data = ""
        technical_detail = soup.find("div", class_="thong-so-kt")
        if technical_detail:
            for technical in technical_detail.find_all("div"):
                technical_detail_data += technical.get_text() + " "

        return technical_detail_data

    def get_data(self):
        soup = get_page_soup(self.url)
        car_links = soup.find("div", class_="grid grid__8 list-hangxe list-company-home").find_all("a")
        car_info = {"listed_price": [], "detail_infomation": [], "technical_detail": [], "car_inventory_by_brand": [], "car_type": {}}
        for link in car_links:
            try:
                car_url = self.base_url + link.get("href")
                carbrand =  car_url.split("/")[-1]
                carbrand = " ".join(carbrand.split("-")[:-1])

                car_soup = get_page_soup(car_url)
                car_model_links = car_soup.find_all('div', class_="list-xe list-xe__company grid grid__4 mb60")
                car_inventory = []
                for car_model_link in car_model_links:
                    for link in car_model_link.find_all("a"):
                        carmodel_data = ""
                        carmodel_url = self.base_url + link.get("href")

                        if carmodel_url in self._crawled_url:
                            continue

                        # print(carmodel_url)
                        carmodel_name = carmodel_url.split("/")[-1]
                        carmodel_name = " ".join(carmodel_name.split("-")[:-1])

                        self._crawled_url.append(carmodel_url)
                        carmodel_soup = get_page_soup(carmodel_url)
                        car_info["listed_price"].append({"content": carmodel_name + " giá niêm yết: \n " + self._get_table_info(carmodel_soup), "metadata": {"link": carmodel_url}})

                        car_info["detail_infomation"].append({"content": carmodel_name + " mô tả/ đánh giá chi tiết: " + self._get_option_info(carmodel_soup), "metadata": {"link": carmodel_url}})
                        car_info["technical_detail"].append({"content": carmodel_name + " thông số kỹ thuật: " + self._get_technical_detail(carmodel_soup), "metadata": {"link": carmodel_url}})
                        no_car_seat = self._get_number_of_seat_info(carmodel_soup)
                        car_info["car_type"].setdefault(no_car_seat, []).append(carmodel_name)
                        car_inventory.append(carmodel_name)
                car_info["car_inventory_by_brand"].append({"content": ", ".join(car_inventory), "metadata": {"link": car_url}})
            except Exception as e:
                print(f"Failed to get car info. Error: {e}")
                print(link)
        return car_info