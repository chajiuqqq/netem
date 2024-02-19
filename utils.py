import json
import yaml
def write_to_file(data,file='output.json'):
    # 写入数组到JSON文件
    with open(file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def read_config(file_path):
    # 打开YAML文件并解析内容
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # 打印解析后的YAML数据
    print("config:",yaml_data)
    return yaml_data