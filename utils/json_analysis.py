import json
from utils.color import print亮红, print亮绿, print亮蓝, print亮黄

def get_nested_value(config_file_path="config/params.json", keys=["env", "INVALID_KEY"], default=None):
    """
    获取嵌套键的值
    :param config: 配置字典
    :param keys: 键列表
    :param default: 默认值
    :return: 键对应的值，如果键不存在则返回默认值
    """
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    
    current = config
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        print亮红("error json_analysis current = ", current, "keys = ", keys, "default = ", default)
        return default