# 获取行政区划数据

本项目通过请求腾讯行政区划API来获取全国所有行政区划信息，包括省、市、区县以及乡镇/街道。

[腾讯API](https://lbs.qq.com/service/webService/webServiceGuide/search/webServiceDistrict#2)

## 前置条件

- Python 3.7+

## 使用方法

### 创建虚拟环境

```shell
python3 -m venv venv
source venv/bin/activate
```

### 安装依赖

```shell
pip install -r requirements.txt
```

### 设置环境变量

```shell
export QQ_MAP_KEY=你的腾讯API KEY
```

### 运行脚本

```shell
python get_qq_district.py
```
