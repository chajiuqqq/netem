import pandas as pd
import os,json,random,sys
from ggplot import *
from utils import * 

def read_qperf(test_name='test'):
    # 读取 export.json 文件
    with open(f"result/qperf_{test_name}_result.json", "r") as f:
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

    # mean
    mean_dict ={}
    mean_dict['title']=f'{test_name} result(mbps)'
    mean_dict['quic']=df1['mbps'].mean()
    mean_dict['tcp']=df2['mbps'].mean()
    write_to_file(mean_dict,f"result/{test_name}_mean.json")
    
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
                ggtitle(f'{test_name} between quic and tcp')
    img_name = f'./pic/{test_name}_{now()}.png'
    print(f'img save at {img_name}')
    p.save(img_name)

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
if __name__ == '__main__':
    # test_name='test'
    # if len(sys.argv)>1:
    #     test_name = sys.argv[1]
    # plot(test_name)
    print(diamonds.head())
    plot_10mb_test()
