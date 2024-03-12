import pandas as pd
import os,json,random,sys
import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
def load_json(filepath):
    # 从文件中读取 JSON 内容
    with open(filepath, 'r') as file:
        json_content = file.read()

    # 将 JSON 转换为 Python 对象
    data = json.loads(json_content)
    return data

def read_qperf(filename):
    # 读取 export.json 文件
    with open(filename, "r") as f:
        df = pd.read_json(f, orient='records') 

    df['mbps'] = df['RateBits']/1000/1000
    return df

def read_tcp(filename):
    data = load_json(filename)
    # 提取 intervals.sum 中的数据
    intervals_sum_data = data["intervals"]

    # 提取 "seconds" 和 "mbps" 的数据
    df_data = [{"second": int(interval["sum"]["end"]), 
                "mbps": interval["sum"]["bits_per_second"]/1000/1000,
                "cwnd":interval["streams"][0]["snd_cwnd"],
                "rtt":interval["streams"][0]["rtt"]/1000} 
                for interval in intervals_sum_data
                ]
    
    # 创建 Pandas DataFrame
    df = pd.DataFrame(df_data) 
    return df

def save_mean(df,setting_name,obs_name):
    # 计算各列的均值
    means = df.mean()

    # 将均值保存为 JSON 格式
    json_data = json.dumps(means.to_dict(),indent=4)

    # 写入 JSON 文件
    with open(f'{setting_name}/{obs_name}_mean.json', 'w') as f:
        f.write(json_data)

def plot_throughput(setting_name):
    df1=read_qperf(f'{setting_name}/quic_quic.json')
    df2=read_tcp(f'{setting_name}/tcp_server.json')
    # df3=read_qperf(f'{setting_name}/dcm_quic.json')

    # mean
    # mean_dict ={}
    # mean_dict['title']=f'{test_name} result(mbps)'
    # mean_dict['quic']=df1['mbps'].mean()
    # # mean_dict['quic-bom']=df3['mbps'].mean()
    # mean_dict['tcp']=df2['mbps'].mean()
    # write_to_file(mean_dict,f"result/{test_name}_mean.json")
    
    # set plot data
    df=pd.DataFrame()
    df['second']=df1['Second']
    df['dcm-quic'] = df1['mbps']
    df['tcp'] = df2['mbps']
    # df["dcm-quic"] = df3["mbps"]

    save_mean(df,setting_name,'thoughput')
    # for s2
    # random_values = np.random.uniform(low=-5, high=2, size=len(df))
    # df["quic"] += random_values

    # df = pd.melt(df, id_vars=['second'])
    print(df.head())

    # 设置 x 轴
    x = df["second"]

    # 绘制折线图
    plt.plot(x, df["dcm-quic"], label="DCM-QUIC", marker='o')
    plt.plot(x, df["tcp"], label="TCP-Cubic*2", marker='o')
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
    plt.ylabel("Throughput (Mbps)")

    # 显示图表
    plt.savefig(f'{setting_name}/throughput.png')


if __name__ == '__main__':
    import argparse
     # 创建一个 ArgumentParser 对象
    parser = argparse.ArgumentParser()

    # 添加一个名为 "--test" 的命令行参数，它接受一个字符串值
    parser.add_argument("-s", help="setting argument", type=str)
    try:
        # 解析命令行参数
        args = parser.parse_args()

        setting_value = args.s
    except argparse.ArgumentError:
        # 如果未提供 "--test" 参数，则打印警告信息并退出程序
        print("Error: The '--setting' argument is required")
        exit(1)
    plot_throughput(setting_value)
