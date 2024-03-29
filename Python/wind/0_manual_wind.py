import numpy as np
import pandas as pd

from pylatex import Document, Section, Subsection, Math, Command, Package
from pylatex.utils import NoEscape

geo = 'a4paper, left=2.5cm, right=2.5cm, top=3cm, bottom=3cm'
doc = Document('hi', documentclass='ctexart',document_options='cs4size, UTF8', geometry_options=geo)

# 加入包
doc.packages.append(Package("xeCJK"))
doc.packages.append(Package("fontspec"))

# 设置样式
doc.preamble.append(Command('setmainfont', 'Times New Roman'))
doc.preamble.append(Command('CTEXsetup', 'section', NoEscape(r'format={\raggedright\bfseries\Large}')))

# 标题栏
doc.preamble.append(Command('title', NoEscape(r'\heiti 桥梁风荷载计算')))
doc.preamble.append(Command('author', 'WYZ'))
doc.preamble.append(Command('date', NoEscape(r'\today')))
doc.append(NoEscape(r'\maketitle'))

# 正文
with doc.create(Section('风速计算')):
    doc.append('我是你爸爸。')
    doc.append((Math(data=['2*3', '=', 9])))

doc.generate_tex()

# 参数
## 基本参数
R = 2               # 风险区域
surface_class = 'C'               # 地表分类
W1 = 19.5               # 十年重现期风作用水平
W2 = 20.0              # 百年重现期风作用水平

Z = 105*2/3             # 主梁基准高度
L = 80              # 单跨长度
H = [105, 87, 30, 57, 30]               # 桥墩高度
rho = 1.25              # 空气密度(kg/m3)
CH = 1.8                # 桥梁横向力系数
beam_D = [0.2, 0.075]                # 梁高（桁架则为杆件高）
shape = 11              # 桥墩形状
w = [2 + i * 0.5 / 100 for i in H]         # 桥墩宽度


## 设计参数
U10 = W2                # 基本风速
l_alpha0 = {'A': 0.12, 'B': 0.16, 'C': 0.22, 'D': 0.30}           # 地表粗糙度系数
l_z0 = {'A': 0.01, 'B': 0.05, 'C': 0.3, 'D': 1.0}           # 地表粗糙高度
l_kc = {'A': 1.174, 'B': 1.0, 'C': 0.785, 'D': 0.564}         # 基本风速地表转化系数
l_kf = {1: 1.05, 2: 1.02, 3: 1.00}              # 抗风风险系数

GV_L_all = pd.read_csv('GV_L.csv')
GV_H_all = pd.read_csv('GV_H.csv')
CD_all = pd.read_csv('CD.csv')


# 设计基准风速

## 桥梁设计基准风速
Us10 = U10 * l_kc[surface_class]

## 桥梁构件基准高度处设计基准风速
kf = l_kf[R]
alpha0 = l_alpha0[surface_class]

Ud_beam = kf * (Z/10) ** alpha0 * Us10
Ud_pier = [kf * (0.65*i/10) ** alpha0 * Us10 for i in H]


# 风荷载

## 等效静阵风风速
GV_L = np.interp(L, GV_L_all['L'], GV_L_all[surface_class])
Ug_beam = GV_L * Ud_beam

GV_H = [np.interp(i, GV_H_all['H'], GV_H_all[surface_class]) for i in H]
Ug_pier = [Ud_pier[i] * GV_H[i] for i in range(len(Ud_pier))]

## 主梁等效静风荷载
Fg_beam = [1/2 * rho * Ug_beam ** 2 * CH * i for i in beam_D]

## 桥墩等效静风荷载
hw = [H[i] / w[i] for i in range(len(H))]
CD = []

for i in hw:
    cd_i = np.interp(i, CD_all.iloc[0], CD_all.iloc[shape])
    CD.append(cd_i)

Fg_pier = []
for i in range(len(H)):
    fg_i = 1/2 * rho * Ug_pier[i] ** 2 * CD[i] * w[i]
    Fg_pier.append(fg_i)

print(Fg_beam)
print(Fg_pier)


