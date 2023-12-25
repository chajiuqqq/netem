import pandas as pd
import os,json,random,sys
from ggplot import *
from utils import * 

def read_qperf():
    # 读取 export.json 文件
    with open("result/qperf_result.json", "r") as f:
        df = pd.read_json(f, orient='records') 

    # 创建pic目录（如果不存在）
    if not os.path.exists("pic"):
        os.mkdir("pic")

    df['mbps'] = df['RateBits']/1000/1000
    return df

def read_tcp(file='fairness_tcp_h1.json'):
    # 从文件中读取 JSON 内容
    file_path = f'result/{file}'  # 替换为你的 JSON 文件路径
    with open(file_path, 'r') as file:
        json_content = file.read()

    # 将 JSON 转换为 Python 对象
    data = json.loads(json_content)
    # 提取 intervals.sum 中的数据
    intervals_sum_data = data["intervals"]

    # 提取 "seconds" 和 "mbps" 的数据
    df_data = [{"second": int(interval["sum"]["end"]), "mbps": interval["sum"]["bits_per_second"]/1000/1000} for interval in intervals_sum_data]

    # 创建 Pandas DataFrame
    df = pd.DataFrame(df_data) 
    return df


def plot(test_name='test'):
    df1=read_qperf()
    df2=read_tcp()

    # mean
    mean_dict ={}
    mean_dict['title']='fairness result(mbps)'
    mean_dict['quic']=df1['mbps'].mean()
    mean_dict['tcp']=df2['mbps'].mean()
    write_to_file(mean_dict,"result/fairness.json")
    
    # set plot data
    df=pd.DataFrame()
    df['second']=df1['Second']
    df['quic'] = df1['mbps']
    df['tcp'] = df2['mbps']

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

def plot_single(test_name='tcp'):
    if test_name=='tcp':
        df=read_tcp('single_tcp_h1.json')

        p = ggplot(df,aes(x='second', y='mbps')) +\
            geom_point() +\
              geom_line()+\
                ylab('rate(Mbps)')+\
                ggtitle(f'{test_name} test')
    
    if test_name=='quic':
        df=read_qperf()

        p = ggplot(df,aes(x='Second', y='Rate(Mbps)')) +\
            geom_point() +\
              geom_line()+\
                ylab('rate(Mbps)')+\
                ggtitle(f'{test_name} test')
    img_name = f'./pic/{test_name}_{random.randint(0,999)}.png'
    print(f'img save at {img_name}')
    p.save(img_name)

if __name__ == '__main__':
    test_name='test'
    if len(sys.argv)>1:
        test_name = sys.argv[1]
    plot(test_name)
