# 计算两坐标之间距离
# p=(lnt,lat)
import math

from map.coordinate_tool import bd09_to_wgs84


bd_point_a = 116.418119, 39.921471
bd_point_b = 117.197646, 39.143459

point_a = bd09_to_wgs84(bd_point_a[0], bd_point_a[1])
point_b = bd09_to_wgs84(bd_point_b[0], bd_point_b[1])


def distance_wgs84(point_a, point_b):
    """
         p=(lnt,lat)
        return:米
    """
    radius = 6370996.81  # 球半径
    if point_a and point_b:
        if point_a == point_b:
            return 0
        else:
            a_lng = point_a[0] * math.pi / 180
            a_lat = point_a[1] * math.pi / 180
            try:b_lng = point_b[0] * math.pi / 180
            except TypeError:
                print()
            b_lat = point_b[1] * math.pi / 180
            return radius * math.acos(
                math.sin(a_lat) * math.sin(b_lat) + math.cos(a_lat) * math.cos(b_lat) * math.cos(b_lng - a_lng))

print(distance_wgs84(point_a, point_b))

