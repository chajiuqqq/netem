import pandas as pd
import os,json,random,sys
from ggplot import *
from utils import * 
import matplotlib.pyplot as plt
import seaborn as sns
import  utils

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
    df_data = [{"second": int(interval["sum"]["end"]), "mbps": interval["sum"]["bits_per_second"]/1000/1000} for interval in intervals_sum_data]
    
    # 创建 Pandas DataFrame
    df = pd.DataFrame(df_data) 
    return df


def plot():
    df1=read_qperf('')
    df2=read_tcp('')

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
    df['quic'] = df1['mbps']
    df['tcp'] = df2['mbps']

    df = pd.melt(df, id_vars=['second'])
    print(df.head())

    # 绘制图表并保存
    p = ggplot(df,aes(x='second', y='value',color='variable')) +\
            geom_point() +\
              geom_line()+\
                ylab('rate(Mbps)')
    
            #   geom_hline(y=mean_dict['quic'],linetype='dashed')+\
            #   geom_hline(y=mean_dict['tcp'],linetype='dashed')+\
    try:
        p.save('result.png')
    except Exception as e:
        print('Error: ',e)
    else:
        print(f'img saved')


if __name__ == '__main__':

