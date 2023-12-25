import json

def write_to_file(data,file='output.json'):
    # 写入数组到JSON文件
    with open(file, 'w') as json_file:
        json.dump(data, json_file, indent=4)
