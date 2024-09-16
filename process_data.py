import re
from typing import Dict, List
def extract_price(text: str) -> Dict[str, str]:
    # Regex pattern to match the car version and its prices
    pattern = r"(?P<version>[^\|]+)\|\s*(?P<giá_niêm_yết>\d+\s*(tỷ\s*\d+\s*triệu\s*VNĐ|\s*triệu\s*VNĐ))"


    # Find all matches
    matches = re.finditer(pattern, text, re.VERBOSE)

    # Parse the results into a dictionary
    parsed_prices = []

    for match in matches:
        parsed_prices.append({
            'version': match.group('version'),
            'giá_niêm_yết': match.group('giá_niêm_yết'),
        })
    return parsed_prices
    
def convert_string_price_to_int(price: str) -> int:
    if "tỷ" in price:
        price = round(float(price.replace("tỷ", ".").replace("triệu VNĐ", "").replace(" ", ""))*1e9, 0)
    elif "triệu" in price:
        price = round(float(price.replace("triệu VNĐ", "").replace(" ", ""))*1e6, 0)
    return int(price)

def get_price_range(car_info: Dict[str, str]) -> List[str]:
    listed_price_lower_than_1_billion = []
    listed_price_lower_than_2_billion = []
    listed_price_higher_than_2_billion = []
    price_range = []
    for car_price in car_info["listed_price"]:
        parse_prices = extract_price(car_price["content"])
        carmodel_name = car_price["content"].split("giá niêm yết")[0]
        if not parse_prices:
            continue
        for parse_price in parse_prices:
            price = convert_string_price_to_int(parse_price["giá_niêm_yết"])
            if price <= 1e9:
                listed_price_lower_than_1_billion.append(f"{carmodel_name}{parse_price['version']}: {price}")
            elif price < 2e9:
                listed_price_lower_than_2_billion.append(f"{carmodel_name}{parse_price['version']}: {price}")
            else:
                listed_price_higher_than_2_billion.append(f"{carmodel_name}{parse_price['version']}: {price}")
    
    price_range.append({"content": "Dưới 1 tỷ: " + "\n".join(listed_price_lower_than_1_billion), "metadata": {}})
    price_range.append({"content": "Dưới 2 tỷ: " + "\n".join(listed_price_lower_than_2_billion), "metadata": {}})
    price_range.append({"content": "Trên 2 tỷ: " + "\n".join(listed_price_higher_than_2_billion), "metadata": {}})
    return price_range

def get_car_type(data: Dict):

    processed_data = []
    for car_seat in data["car_type"]:
        processed_data.append({"content": f"Xe có {car_seat} chỗ: {', '.join(data['car_type'][car_seat])}", "metadata": {"link": ""}})
    car_type = {"coupe": [], "sedan": [], "suv": [], "mpv": [], "hatchback": []}
    for detail_info in data["detail_infomation"]:
        content = detail_info["content"].lower().replace(" mô tả/ đánh giá chi tiết", "")
        if "coupe" in content.lower():
            car_type["coupe"].append(content.split(':')[0])
        elif "sedan" in content.lower():
            car_type["sedan"].append(content.split(':')[0])
        elif "suv" in content.lower():
            car_type["suv"].append(content.split(':')[0])
        elif "mpv" in detail_info["content"].lower():
            car_type["mpv"].append(content.split(':')[0])
        elif "hatchback" in detail_info["content"].lower():
            car_type["hatchback"].append(content.split(':')[0])
    for type in car_type:
        processed_data.append({"content": f"Xe {type}: {', '.join(car_type[type])}", "metadata": {"link": ""}})
    return processed_data
        