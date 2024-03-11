

import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd


def plot_video_stream(setting,play_strategy):
    log_dict = {
        'second':[],
        'quic':[],
        'tcp':[],
    }
   #1. 读取日志，并解析出bufferLength sec
    with open(f'{setting}/{play_strategy}_http2_client.txt', 'r') as file:
        for line in file:
            if line.startswith('{'):
                line_obj = json.loads(line)
                if 'sec' in line_obj:
                    log_dict['second'].append(line_obj['sec'])
                    log_dict['tcp'].append(line_obj['dp.BufferLength'])
    with open(f'{setting}/{play_strategy}_quic_client.txt', 'r') as file:
        for line in file:
            if line.startswith('{'):
                line_obj = json.loads(line)
                if 'sec' in line_obj:
                    log_dict['quic'].append(line_obj['dp.BufferLength'])
    print(len(log_dict['second']),len(log_dict['quic']),len(log_dict['tcp']))
    totalDuration = len(log_dict['second'])/2
    df = pd.DataFrame(log_dict)
    df['dcm-quic']=df['quic']
    print(df.head())

    # 直接将 DataFrame 保存为 JSON 文件
    df.to_json(f'{setting}/data.json',orient='records', indent=4)
    
    # 去除头尾的10s
    # filtered_df = df[(df['second'] >= 10) & (df['second'] <= totalDuration-10)]

    # 设置 x 轴
    x = df["second"]

    # 绘制折线图
    plt.plot(x, df["quic"], label="QUIC-Cubic", marker='o')
    plt.plot(x, df["tcp"], label="TCP-Cubic", marker='o')
    # plt.plot(x, df["dcm-quic"], label="DCM-QUIC", marker='o')

    # 添加图例
    plt.legend()

    # 设置背景色为灰色
    plt.gca().set_facecolor('#f8f8f8')

    # 添加网格
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    # 设置 x 轴的刻度从 0 开始
    plt.gca().set_xlim(left=0)
    plt.gca().set_ylim(bottom=0)

    # 设置 x 轴的标签为 "Time (s)"
    plt.xlabel("Time (s)")

    # 设置 y 轴的标签为 "Throughput (Mbps)"
    plt.ylabel("Buffer Time (s)")

    # 显示图表
    plt.savefig(f'{setting}/buffer_time_{play_strategy}.png')

def load_json(filepath):
    # 从文件中读取 JSON 内容
    with open(filepath, 'r') as file:
        json_content = file.read()

    # 将 JSON 转换为 Python 对象
    data = json.loads(json_content)
    return data

def save_mean(df,setting_name):
    # 计算各列的均值
    means = df.mean()

    # 将均值保存为 JSON 格式
    json_data = json.dumps(means.to_dict(),indent=4)

    # 写入 JSON 文件
    with open(f'{setting_name}/buffer_mean.json', 'w') as f:
        f.write(json_data)

def plot_data(setting):
    log_dict=load_json(f'{setting}/data.json')
    df = pd.DataFrame(log_dict)
    save_mean(df,setting)
    print(df.head())
    # 设置 x 轴
    x = df["second"]

    # 绘制折线图
    plt.plot(x, df["quic"], label="QUIC-Cubic", marker='o')
    plt.plot(x, df["tcp"], label="TCP-Cubic", marker='o')
    plt.plot(x, df["dcm-quic"], label="DCM-QUIC", marker='o')

    # 添加图例
    plt.legend()

    # 设置背景色为灰色
    plt.gca().set_facecolor('#f8f8f8')

    # 添加网格
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    # 设置 x 轴的刻度从 0 开始
    plt.gca().set_xlim(left=0)
    plt.gca().set_ylim(bottom=0)

    # 设置 x 轴的标签为 "Time (s)"
    plt.xlabel("Time (s)")

    # 设置 y 轴的标签为 "Throughput (Mbps)"
    plt.ylabel("Buffer Time (s)")

    # 显示图表
    plt.savefig(f'{setting}/buffer_time.png')




if __name__ == '__main__':
    plot_data('s3')
