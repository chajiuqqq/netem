import pandas as pd
import os
from ggplot import *
# 读取 export.json 文件
with open("result/qperf_result.json", "r") as f:
    df = pd.read_json(f, orient='records') 

# 创建pic目录（如果不存在）
if not os.path.exists("pic"):
    os.mkdir("pic")

df['Rate(Mbps)'] = df['RateBytes']/1024/1024*8
# 绘制图表并保存
p = ggplot(df,aes(x='Second', y='Rate(Mbps)')) + geom_point() + geom_line(color='b')
p.save('./pic/example2.png')