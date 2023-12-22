import pandas as pd
import os,json,random,sys
from ggplot import *

def plot_qperf():
    # 读取 export.json 文件
    with open("result/qperf_result.json", "r") as f:
        df = pd.read_json(f, orient='records') 

    # 创建pic目录（如果不存在）
    if not os.path.exists("pic"):
        os.mkdir("pic")

    df['Rate(Mbps)'] = df['RateBytes']/1000/1000*8
    return df

def plot_tcp():
    # 从文件中读取 JSON 内容
    file_path = 'result/fairness_tcp_h1.txt'  # 替换为你的 JSON 文件路径
    with open(file_path, 'r') as file:
        json_content = file.read()

    # 将 JSON 转换为 Python 对象
    data = json.loads(json_content)
    # 提取 intervals.sum 中的数据
    intervals_sum_data = data["intervals"]

    # 提取 "seconds" 和 "bits_per_second" 的数据
    df_data = [{"second": interval["sum"]["seconds"], "bits_per_second": interval["sum"]["bits_per_second"]/1000/1000} for interval in intervals_sum_data]

    # 创建 Pandas DataFrame
    df = pd.DataFrame(df_data) 
    return df


def plot(test_name='test'):
    df1=plot_qperf()
    df2=plot_tcp()

    df=pd.DataFrame()
    df['second']=df1['Second']
    df['quic'] = df1['Rate(Mbps)']
    df['tcp'] = df2['bits_per_second']

    df = pd.melt(df, id_vars=['second'])
    print(df.head())

    # 绘制图表并保存
    p = ggplot(df,aes(x='second', y='value',color='variable')) +\
            geom_point() +\
              geom_line()+\
                ylab('rate(Mbps)')+\
                ggtitle('fairness between quic and tcp')
    img_name = f'./pic/{test_name}_{random.randint(0,999)}.png'
    print(f'img save at {img_name}')
    p.save(img_name)

if __name__ == '__main__':
    test_name='test'
    if len(sys.argv)>1:
        test_name = sys.argv[1]
    plot(test_name)
