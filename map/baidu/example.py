"""
根据地址名称同步地址坐标
"""
import json

import pymysql
import logging.handlers
from requests import HTTPError
from map.coordinate_tool import bd09_to_wgs84

import map.baidu.baidu_web_api as bwa


def sync_baidu_position_byKey():
    LOG_FILE = r'./example.log'
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, encoding='utf-8')
    fmt = '%(asctime)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger('获取地理坐标')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    global conn
    api = bwa.baidu_web_api("****")
    # 连接DB
    # 处理mysql数据
    try:

        conn = pymysql.connect(host="****", port=6033, user="****", password="****",
                               database="****", charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            sql = "select id,cinema_name,address from c_cinema where id >8527"
            cursor.execute(sql)
            cinemas = cursor.fetchall()
            for cinema in cinemas:
                id = cinema["id"]
                print("处理到 ID：%s" % id)
                if not cinema["address"]:
                    continue
                try:
                    res = json.loads(api.show_location(cinema["address"]))
                    if res["status"] != 0:
                        logger.info("影院地理坐标信息获取失败 ID:%s 影院:%s 地址:%s 失败状态：%s 失败原因:%s" % (
                            id, cinema["cinema_name"], cinema["address"],
                            res["status"], res["msg"] if "msg" in res else res["message"]))
                    else:
                        lng = res["result"]["location"]["lng"]
                        lat = res["result"]["location"]["lat"]
                        lng, lat = bd09_to_wgs84(lng, lat)
                        cursor.execute(
                            "update c_cinema set longitude=" + str(lng) + ",latitude=" + str(
                                lat) + " where id=" + str(id))
                        conn.commit()
                except HTTPError as e:
                    logger.info("影院地理位置坐标信息HTTP错误 ID:%s 影院:%s 地址:%s 状态：%s" % (
                        cinema["id"], cinema["cinema_name"], cinema["address"], e))

    finally:
        conn.close()


sync_baidu_position_byKey()
