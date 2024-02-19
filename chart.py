import pandas as pd
import os,json,random,sys
from ggplot import *
from utils import * 
import matplotlib.pyplot as plt
import seaborn as sns
import  utils
def read_qperf(test_name='test'):
    # 读取 export.json 文件
    with open(f"result/{test_name}_quic.json", "r") as f:
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
    df1=read_qperf(test_name)
    df2=read_tcp(f'{test_name}_tcp_h1.json')
    # df3=read_qperf(f'{test_name}_bom')

    # mean
    mean_dict ={}
    mean_dict['title']=f'{test_name} result(mbps)'
    mean_dict['quic']=df1['mbps'].mean()
    # mean_dict['quic-bom']=df3['mbps'].mean()
    mean_dict['tcp']=df2['mbps'].mean()
    write_to_file(mean_dict,f"result/{test_name}_mean.json")
    
    # set plot data
    df=pd.DataFrame()
    df['second']=df1['Second']
    df['quic'] = df1['mbps']
    # df['quic-bom'] = df3['mbps']
    df['tcp'] = df2['mbps']

    df = pd.melt(df, id_vars=['second'])
    print(df.head())

    test_title = test_name.split("_")[0]
    # 绘制图表并保存
    p = ggplot(df,aes(x='second', y='value',color='variable')) +\
            geom_point() +\
              geom_line()+\
                ylab('rate(Mbps)')+\
                ggtitle(f'{test_title} Test Result')
    
            #   geom_hline(y=mean_dict['quic'],linetype='dashed')+\
            #   geom_hline(y=mean_dict['tcp'],linetype='dashed')+\
    img_name = f'./pic/{test_name}_{now()}.png'
    try:
        p.save(img_name)
    except Exception as e:
        print('Error: ',e)
    else:
        print(f'img save at {img_name}')

def plot_video_stream(params):
    log_dict = {
        'second':[],
        'buffer_length':[],
        'type':[]
    }
   #1. 读取日志，并解析出bufferLength sec
    with open('logs/video_stream_http2_h1.txt', 'r') as file:
        for line in file:
            if line.startswith('{'):
                line_obj = json.loads(line)
                if 'sec' in line_obj:
                    log_dict['second'].append(line_obj['sec'])
                    log_dict['buffer_length'].append(line_obj['dp.BufferLength'])
                    log_dict['type'].append('h2')
    with open('logs/video_stream_quic_h1.txt', 'r') as file:
        for line in file:
            if line.startswith('{'):
                line_obj = json.loads(line)
                if 'sec' in line_obj:
                    log_dict['second'].append(line_obj['sec'])
                    log_dict['buffer_length'].append(line_obj['dp.BufferLength'])
                    log_dict['type'].append('quic')
    print(log_dict)

    df = pd.DataFrame(log_dict)
    # 3. 画图
    p = ggplot(df,aes(x='second', y='buffer_length',color='type')) +\
            geom_point() +\
              geom_line()+\
                ylab('buffer_length(s)')+\
                xlab('second(s)')+\
                ggtitle('Video Stream Test Result')
    img_name = f'./pic/{params["name"]}_{now()}.png'
    try:
        p.save(img_name)
    except Exception as e:
        print('Error: ',e)
    else:
        print(f'img save at {img_name}')

def plot_10mb_test():
   df = pd.DataFrame({'group':['GAE','MyQuicServer'],'time':[2000,996]})
   print(df.head())
   p = ggplot(df,aes(x='group',weight='time'))+geom_bar(fill='#2b8cbe')+ylab('Time(ms)')+xlab('Groups')+ggtitle('10MB Img over 100Mbps link')
   p.save('./pic/quic_std.png')

from datetime import datetime
def now():
    # 获取当前时间
    current_time = datetime.now()

    # 格式化时间戳
    timestamp_format = "%Y%m%d%H%M%S"
    timestamp = current_time.strftime(timestamp_format)
    return timestamp

from urllib.parse import urlparse
import os

def plot_plt_test():
    http2_name = 'result/plt_http2_result.json'
    qperf_name = 'result/qperf_http3_result.json'
    http2_data = load_json(http2_name)
    qperf_data = load_json(qperf_name)

    result=[]
    for item in http2_data:
        line = {}
        line['size']=item['url'].split('/')[-1].split('.')[0]
        line['loadTime']=item['averageLoadingTime']
        line['type']='tcp'
        result.append(line)
    for item in qperf_data:
        line={}
        line['size']=item['URL'].split('/')[-1].split('.')[0]
        line['loadTime']=item['TimeUsageMS']
        line['type']='quic'
        result.append(line)
    df = pd.DataFrame(result)
    print(df.head())
    plt.savefig(f'pic/plt_{now()}.png')

def load_json(filepath):
    # 从文件中读取 JSON 内容
    with open(filepath, 'r') as file:
        json_content = file.read()

    # 将 JSON 转换为 Python 对象
    data = json.loads(json_content)
    return data

if __name__ == '__main__':
    conf = utils.read_config('./conf/default.yaml')
    plot_video_stream(conf['tests']['video_stream']['params'])
