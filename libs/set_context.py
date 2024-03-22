import requests
import time

set_context = {
    "地图数据上传":
        "上面是本地存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的地图名称，由于我的吐词有可能不太清晰，需要你根据本地的地图数据来判断我要上传的地图，并直接以[map:地图名称]的格式返回。如果没有找到对应名称的地图数据，则直接返回[map:null]:",
    "地图数据下载":
        "上面是云端存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的地图名称，由于我的吐词有可能不太清晰，需要你根据云端查找到的地图数据来判断我要下载的地图，并直接以[map:地图名称]的格式返回。如果没有找到对应名称的地图数据，则直接返回[map:null]:",
    "AMR地图列表查询接口":
        "",
    "AMR地图切换":
        "上面是云端存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的原始地图与新地图的名称，由于我的吐词有可能不太清晰，需要你根据云端查找到的地图数据来判断我要切换的两张地图，并直接以[map:原始地图, 新地图]的格式返回。如果没有找到对应名称的地图数据，则直接返回[map:null, null]:",
    "站点数据批量上传":
        "上面是本地存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的地图名称，由于我的吐词有可能不太清晰，需要你根据本地的地图数据来判断我要上传的地图，然后判断",
    "站点数据批量下载":
        "上面是云端存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的地图名称，由于我的吐词有可能不太清晰，需要你根据云端查找到的地图数据来判断我要下载的地图数据，并直接以[map:地图名称]的格式返回。如果没有找到对应名称的地图数据，则直接返回[map:null]:",
    "路线数据批量上传":
        "xxxxxxxxxxxxxxxxx",
    "路线数据批量下载":
        "上面是云端存在的地图数据，你现在是一个通信调用协议架构师。请解析上述语句中的地图名称，由于我的吐词有可能不太清晰，需要你根据云端查找到的地图数据来判断我要下载的地图数据，并直接以[map:地图名称]的格式返回。如果没有找到对应名称的地图数据，则直接返回[map:null]:",
    "AMR动作查询接口":
        "",
    "任务指令下发":
        "xxxxxxxxxxxxxxxxx",
    "任务状态查询":
        "你现在是一个通信调用协议架构师。请解析上述语句中的编码，这个编码是由纯数组组成。由于我的吐词有可能不太清晰，需要将相近发音的字符转为阿拉伯数字，并直接以[tasksn:地图名称]的格式返回如果没有找到对应名称的地图数据，则直接返回[tasksn:null]:",
    "任务取消接口":
        "",
    "获取AMR状态接口":
        "",
    "根据你的知识库回答问题":
        """
        Answer  the question using only the details provided in the context.If the necessary information is not available, 
        simply state "answer is not available in the context" instead of providing incorrect information.
        
        Context:\n {context}?\n
        Question: \n{question}\n
        """,
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

