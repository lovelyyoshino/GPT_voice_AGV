import requests
import time

set_context = {
    "地图数据上传":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "地图数据下载":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "AMR地图列表查询接口":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "AMR地图切换":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "站点数据批量上传":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "站点数据批量下载":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "路线数据批量上传":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "路线数据批量下载":
        "你现在是一个通信调用协议架师。请解析上述语句中",
    "AMR动作查询接口":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "任务指令下发":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "任务状态查询":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "任务取消接口":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
    "获取AMR状态接口":
        "你现在是一个通信调用协议架构师。请解析上述语句中",
}


def update_map_date(map_name: str):
    url = "http://ip:port/api/v1/getMap"
    payload = {
        "mapName": map_name,
        "base64Img": "<your_base64_encoded_image_here>",
        "mapImgHeight": 3800,
        "mapImgWidth": 2800,
        "requestTime": time.time()
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

