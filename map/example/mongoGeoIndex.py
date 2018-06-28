import codecs
import json
import logging.handlers
import pymysql
from map.coordinate_tool import bd09_to_wgs84
from pymongo import MongoClient

LOG_FILE = r'./log/tmp.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, encoding='utf-8')
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger('A_B经纬度距离计算')
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class CinemaJob:
    def __init__(self):
        self.connection = pymysql.connect(host="***", user="***", password="***",
                                          database="***", charset='utf8',
                                          cursorclass=pymysql.cursors.DictCursor)
        self.client = MongoClient('***', 8888)
        admin = self.client.admin
        admin.authenticate("***", "***")

    # 生成数据
    def generate_data(self):
        # 处理mysql数据
        with self.connection.cursor() as cursor:
            # GBID，影院名称，院线，城市，影院影厅，影院座位数量
            sql = "select gb_cinema_id,cinema_name,cinema_line_id,city_name,halls_count,seats_count,longitude as lng,latitude as lat from cinemas"
            cursor.execute(sql)
            cinemas = cursor.fetchall()
            for cinema in cinemas:
                # 百度经纬度转GPS精准经纬度
                if not (cinema['lng'] and cinema['lat']):
                    continue
                cinema['location'] = {'type': "Point", 'coordinates': bd09_to_wgs84(cinema['lng'], cinema['lat'])}
                del cinema['lng']
                del cinema['lat']
        # 处理mongo数据
        ticket = self.client.ticket
        collection_cinemas = ticket.cinemas
        collection_cinemas.insert_many(cinemas)

    def static_data(self):
        try:
            ticket = self.client.ticket
            collection_cinemas = ticket.cinemas
            cinemas_cursor = collection_cinemas.find({}, {"_id": 0})
            # 生成产品所需数据
            cinemas = []
            for cinema in cinemas_cursor:
                cinemas.append(cinema)

                lng, lat = cinema['location']['coordinates']
                res = collection_cinemas.find({'location': {
                    '$nearSphere': {'$geometry': {'type': "Point", 'coordinates': [lng, lat]},
                                    '$minDistance': 1, '$maxDistance': 3000}}}, {"_id": 0})
                list_3000 = list(res)
                cinema['3000'] = {'count': len(list_3000), 'data': list_3000}
                res = collection_cinemas.find({'location': {
                    '$nearSphere': {'$geometry': {'type': "Point", 'coordinates': [lng, lat]},
                                    '$minDistance': 1, '$maxDistance': 5000}}}, {"_id": 0})
                list_5000 = list(res)
                cinema['5000'] = {'count': len(list_5000), 'data': list_5000}

            with codecs.open('./xxx.json', 'w', 'utf-8') as fd:
                json.dump(cinemas, fd, ensure_ascii=False, indent=2)
        except KeyError:
            print()

    def close(self):
        self.connection.close()
        self.client.close()


# 执行任务
cj = CinemaJob()
try:
    cj.static_data()
finally:
    cj.close()
