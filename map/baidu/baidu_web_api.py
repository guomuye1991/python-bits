import requests

import pymysql
from map.coordinate_tool import bd09_to_wgs84

class baidu_web_api:
    def __init__(self, ak):
        self.ak = ak

    def show_location(self, address):
        url = "http://api.map.baidu.com/geocoder/v2/?address=" + address + "&output=json&ak=" + self.ak
        res = requests.get(url)
        res.raise_for_status()
        return res.text
