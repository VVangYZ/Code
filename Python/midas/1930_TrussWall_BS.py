import numpy as np
import pandas as pd
import time

# 文件参数
usual_file = 'usual_data_1030.txt'
filename = 'TrussWall_bs'

# 钢架参数
height = 22
width = 25
depth = 1
support_height = 12
support_depth = -4.5

hl_2 = np.arange(2, 24, 2)  ## 钢架横撑位置
support_support_1 = [4, 8]  ## 斜撑横撑位置
support_support_2 = np.arange(2, 12, 2) ## 斜撑纵撑位置
wl_n = np.arange(0, 21, 1)    # 宽度节点


hl = np.linspace(0, height, 12)    # 桁架高度及间距（层数）
wl = np.arange(0, width, 5)    # 桁架宽度
dl = np.array([0, depth])    # 桁架厚度
support_hl = np.array([0] + support_support_1 + [12])    # 支撑高度
support_hl_2 = np.arange(0, support_height, 2)    # 支撑高度

# 荷载参数
wind_10 = 28    # 10m 高度处基本风速
wind_h = [[3, 5, 10, 15, 20, 30], [0.6, 0.65, 0.74, 0.83, 0.9, 0.97]]   # 随高度变化
# a0 = 0.16   # 地表粗糙度系数（暂定 B 类地形）
# kf = 1  # 抗风风险系数（暂取 1，实际该风速应取 1.02）
# gv = 1  # 静阵风系数（暂取 1，实际该高度如果按 B 类地形应取 1.24）

# 建立节点
node_frame = pd.DataFrame(columns=['x', 'y', 'z'])
nnum = 0
for x in wl_n:
    for y in dl:
        for z in hl:
            nnum += 1
            node_frame.loc[nnum] = [x, y, z]

node_support = pd.DataFrame(columns=['x', 'y', 'z'])
for x in wl:
    for z in support_hl_2:
        nnum += 1
        y = np.interp(z, support_hl[[0, -1]], [support_depth, 0])
        node_support.loc[nnum] = [x, y, z]


# 建立单元
elem = pd.DataFrame(columns=['m', 's', 'b', 'n1', 'n2', 'WHAT'])
enum = 0

def elem_from_node(node, s, what, m=1, b=0):
    for i, j in enumerate(node[:-1]):
        global enum
        global elem
        enum += 1
        n1 = j
        n2 = node[i+1]
        elem.loc[enum] = [m, s, b, n1, n2, what]

## 立柱
for x in wl:
    for y in dl:
        n = node_frame[(node_frame['x']==x) & (node_frame['y'] == y)].index
        elem_from_node(n, 1, 'Link1')

## 横梁
for y in dl:
    for z in hl_2:
        n = node_frame[(node_frame['z']==z) & (node_frame['y'] == y)].index
        elem_from_node(n, 2, 'Link2')

## 小横梁
for x in wl:
    for z in hl[1:]:
        n = node_frame[(node_frame['z']==z) & (node_frame['x'] == x)].index
        elem_from_node(n, 3, 'Link3')

## 小斜撑
nz = len(hl)
for x in wl:
    n1 = node_frame[(node_frame['x'] == x) & (node_frame['y'] == dl[0])]
    n2 = node_frame[(node_frame['x'] == x) & (node_frame['y'] == dl[1])]
    n12 = [n1.iloc[np.arange(0, nz, 2)], n2.iloc[np.arange(1, nz, 2)]]
    n = pd.concat(n12).sort_values(by = 'z').index
    elem_from_node(n, 4, 'Link4')

## 大斜撑
for x in wl:
    n1 = node_frame[(node_frame['z'] == support_hl[-1]) & (node_frame['y'] == dl[0]) & (node_frame['x'] == x)]
    n2 = node_support[node_support['x'] == x]
    n = pd.concat([n1, n2]).sort_values(by = 'z').index
    elem_from_node(n, 5, 'Support1', b=90)

## 大斜撑横联
for x in wl:
    for z in support_support_2:
        n1 = node_frame[(node_frame['z'] == z) & (node_frame['y'] == dl[0]) & (node_frame['x'] == x)]
        n2 = node_support[(node_support['x']==x)&(node_support['z']==z)]
        n = pd.concat([n1, n2]).index
        elem_from_node(n, 6, 'Support2')

for z in support_hl[1:-1]:
    n = node_support[(node_support['z']==z)].index
    elem_from_node(n, 2, 'Link2')


# 写入 mct 文件
t1 = time.gmtime()
t2 = f'{t1.tm_year}{t1.tm_mon}{t1.tm_mday}'
mct_file = open(f'IO\{filename}_{t2[2:]}.mct', 'w+')

## 常规信息
with open(f'IO\{usual_file}') as f:
    usual_content = f.read()
mct_file.write(usual_content + '\n')

## 写入节点
## 节点信息
nodes = pd.concat([node_frame, node_support])

mct_file.write('*NODE\n')
for i, j in nodes.iterrows():
    mct_file.write(f"{i}, {j['x']}, {j['y']}, {j['z']}\n")

## 单元信息
mct_file.write('*ELEMENT\n')
for i, j in elem.iterrows():
    mct_file.write(f"{i}, BEAM, {j['m']}, {j['s']}, {j['n1']}, {j['n2']}, {j['b']}\n")

## 约束信息
mct_file.write('*BNDR-GROUP\nsupport\n')    # 定义约束组
mct_file.write('*CONSTRAINT\n')
for i, j in nodes.iterrows():
    res = '111111'
    if j['z'] == 0:
        mct_file.write(f'{i}, {res}, support\n')

## 荷载信息
### 自重
mct_file.write('*USE-STLD, DEAD\n')
mct_file.write('*SELFWEIGHT, 0, 0, -1, self-weight\n')

### 风荷载
mct_file.write('*USE-STLD, WIND1\n')
mct_file.write('*BEAMLOAD\n')
elem_wind = elem[elem['WHAT'] == 'Link1']

for i, j in elem_wind.iterrows():
    x1 = nodes.loc[j['n1']]['x']
    y1 = nodes.loc[j['n1']]['y']
    z1 = nodes.loc[j['n1']]['z']
    z2 = nodes.loc[j['n2']]['z']
    if y1 == 0 or z1 == 0: continue
    wind1 = np.interp(z1, wind_h[0], wind_h[1]) * wind_10
    wind2 = np.interp(z2, wind_h[0], wind_h[1]) * wind_10
    fg1 = 0.613 * wind1 ** 2 * (-2+0.3) * 5 / 1000
    fg2 = 0.613 * wind2 ** 2 * (-2+0.3) * 5 / 1000
    if x1 in wl[[0, -1]]:
        fg1 *= 0.5
        fg2 *= 0.5
    mct_file.write(f'{i}, BEAM, UNILOAD, GY, NO , NO, aDir[1], ,\
            , , 0, {fg1}, 1, {fg2}, 0, 0, 0, 0, wind, NO, 0, 0, NO\n') 

mct_file.write('*USE-STLD, WIND2\n')
mct_file.write('*BEAMLOAD\n')
for i, j in elem_wind.iterrows():
    x1 = nodes.loc[j['n1']]['x']
    y1 = nodes.loc[j['n1']]['y']
    z1 = nodes.loc[j['n1']]['z']
    z2 = nodes.loc[j['n2']]['z']
    if y1 == 0 or z1 == 0: continue
    wind1 = np.interp(z1, wind_h[0], wind_h[1]) * wind_10
    wind2 = np.interp(z2, wind_h[0], wind_h[1]) * wind_10
    fg1 = - 0.613 * wind1 ** 2 * (-2+0.3) * 5 / 1000
    fg2 = - 0.613 * wind2 ** 2 * (-2+0.3) * 5 / 1000
    if x1 in wl[[0, -1]]:
        fg1 *= 0.5
        fg2 *= 0.5
    mct_file.write(f'{i}, BEAM, UNILOAD, GY, NO , NO, aDir[1], ,\
            , , 0, {fg1}, 1, {fg2}, 0, 0, 0, 0, wind, NO, 0, 0, NO\n')

elem_wind = elem[elem['WHAT'] == 'Link2']
for i, j in elem_wind.iterrows():
    x1 = nodes.loc[j['n1']]['x']
    y1 = nodes.loc[j['n1']]['y']
    z1 = nodes.loc[j['n1']]['z']
    z2 = nodes.loc[j['n2']]['z']
    if y1 == 0 or z1 == 0: continue
    wind1 = np.interp(z1, wind_h[0], wind_h[1]) * wind_10
    wind2 = np.interp(z2, wind_h[0], wind_h[1]) * wind_10
    fg1 = - 0.613 * wind1 ** 2 * (-2+0.3) * 0.07 / 1000
    fg2 = - 0.613 * wind2 ** 2 * (-2+0.3) * 0.07 / 1000
    mct_file.write(f'{i}, BEAM, UNILOAD, GY, NO , NO, aDir[1], ,\
            , , 0, {fg1}, 1, {fg2}, 0, 0, 0, 0, wind, NO, 0, 0, NO\n')


## 荷载组合
mct_file.write('*LOADCOMB\n')
mct_file.write('NAME=w12, GEN, ACTIVE, 0, 0, , 0, 0\n')
mct_file.write('ST, DEAD, 1.2, ST, WIND1, 1.4\n')

# 写入 mct 文件完毕
mct_file.write('*ENDDATA')
mct_file.close()

