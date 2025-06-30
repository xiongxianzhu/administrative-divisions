"""
请求腾讯行政区划API获取全国所有行政区划（省、市、区县、乡镇/街道）
腾讯API:
https://lbs.qq.com/service/webService/webServiceGuide/search/webServiceDistrict#2

注意：

- 中国没有区的市包括东莞市、中山市、儋州市和嘉峪关市，这些城市没有区县，只有街道/乡镇；
- 行政区划级别level的枚举值：1-省，2-市， 3-区，街道没有level，0-没有区的市（如东莞、中山、儋州、嘉峪关市）
- 此4个城市在接口返回的level = 0，要特殊处理；
"""
import os
import requests
import json
import time

# 腾讯位置服务API KEY
QQ_MAP_KEY = os.getenv('QQ_MAP_KEY', '你的腾讯位置服务API KEY')

# 腾讯行政区划API
QQ_DISTRICT_LIST_URL = 'https://apis.map.qq.com/ws/district/v1/list'
QQ_DISTRICT_CHILDREN_URL = 'https://apis.map.qq.com/ws/district/v1/getchildren'

# 保存路径
OUTPUT_PATH = 'qq_district.json'

# QPS限制，建议适当延时
SLEEP_SECONDS = 0.3


def fetch_qq_district_list(key):
    params = {
        'key': key,
        'struct_type': 1,  # 嵌套结构
        'output': 'json',
    }
    resp = requests.get(QQ_DISTRICT_LIST_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    if data.get('status') != 0:
        raise Exception(f"腾讯API请求失败: {data.get('message')}")
    return data['result']  # 省市区县三级嵌套


def fetch_qq_children(key, adcode):
    params = {
        'id': adcode,
        'key': key,
        'output': 'json',
    }
    resp = requests.get(QQ_DISTRICT_CHILDREN_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    if data.get('status') != 0:
        print(f"警告: 获取adcode={adcode}的四级区划失败: {data.get('message')}")
        return []
    return data['result'][0] if data['result'] else []


def add_street_to_county(county, key, path, structure_type):
    adcode = county.get('id')
    print(f'正在获取【{path}】({structure_type}) 的四级（街道/乡镇）数据... (adcode={adcode})')
    if not adcode:
        return
    streets = fetch_qq_children(key, adcode)
    county['districts'] = streets
    time.sleep(SLEEP_SECONDS)


def add_streets_to_all_counties(provinces, key):
    for province in provinces:
        province_name = province.get('fullname') or province.get('name') or ''
        for node in province.get('districts', []):
            # 市级（level=2）
            if node.get('level') == 2:
                city_name = node.get('fullname') or node.get('name') or ''
                # 遍历区县级
                for county in node.get('districts', []):
                    if county.get('level') == 3:
                        county_name = county.get('fullname') or county.get('name') or ''
                        path = f'{province_name}-{city_name}-{county_name}'
                        add_street_to_county(county, key, path, '省-市-区县')
                    if county.get('level') == 0:
                        # 没有区的市（如东莞、中山、儋州、嘉峪关市）
                        path = f'{province_name}-{city_name}'
                        add_street_to_county(county, key, path, '省-市')
            # 区县级（level=3），如北京、重庆等直辖市/特别行政区
            elif node.get('level') == 3:
                county_name = node.get('fullname') or node.get('name') or ''
                path = f'{province_name}-{county_name}'
                add_street_to_county(node, key, path, '省-区县')


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f'已保存到: {path}')


def main():
    print('正在获取省市区县三级数据...')
    provinces = fetch_qq_district_list(QQ_MAP_KEY)
    print('正在为每个区县获取四级（街道/乡镇）数据...')
    add_streets_to_all_counties(provinces, QQ_MAP_KEY)
    save_json(provinces, OUTPUT_PATH)
    print('全部完成！')


if __name__ == '__main__':
    main()
