import matplotlib.pyplot as plt
import numpy as np
import xlrd
from matplotlib.font_manager import FontProperties

ex_1 = xlrd.open_workbook("plot_wyz.xlsx")
sheet_1 = ex_1.sheets()[-7]

font = FontProperties(fname="wryh.ttf", size=18)
font_1 = FontProperties(fname="wryh.ttf", size=14)


def read_col(st, i):
    col_data = []
    for j in st.col_values(i):
        if type(j) == str:
            continue
        else:
            col_data.append(j)
    return np.array(col_data)


x1 = read_col(sheet_1, 0)
y1 = read_col(sheet_1, 1)
x2 = read_col(sheet_1, 2)
y2 = read_col(sheet_1, 3) * 1000
x3 = read_col(sheet_1, 4)
y3 = read_col(sheet_1, 5) * 1000
x4 = read_col(sheet_1, 6)
y4 = read_col(sheet_1, 7)
x5 = read_col(sheet_1, 8)
y5 = read_col(sheet_1, 9)
x6 = read_col(sheet_1, 10)
y6 = read_col(sheet_1, 11)
x7 = read_col(sheet_1, 12)
y7 = read_col(sheet_1, 13)

lab = ['网格模型', '实体模型']

plt.figure(figsize=(11, 5.5))
bar_w = 0.35
n = len(x1)
x = np.arange(1, n+1)
plt.bar(x-bar_w/2, x1, bar_w, label=lab[0])
plt.bar(x+bar_w/2, y1, bar_w, label=lab[1])
plt.ylim(-600, max(max(x1), max(y1))*1.15)
plt.xticks(np.arange(1, len(x1)+1))
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1, fancybox=True)
plt.xlabel("支座", fontproperties=font)
plt.ylabel("支反力（kN）", fontproperties=font)
plt.savefig('支反力.tif')
plt.show()


plt.figure(figsize=(11, 5.5))
plt.plot(x2, y2, 'o', label='空间网格')
plt.plot(x3, y3, '-', label='实体模型', linewidth=2.0)
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1)
plt.xlabel("纵向坐标（m）", fontproperties=font)
plt.ylabel("竖向位移（mm）", fontproperties=font)
plt.savefig('位移.tif')
plt.show()

plt.figure(figsize=(11, 5.5))
plt.plot(x4, y4, 'o', label='空间网格')
plt.plot(x5, y5, '-', label='实体模型', linewidth=2.0)
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1)
plt.xlabel("纵向坐标（m）", fontproperties=font)
plt.ylabel("纵向应力（MPa）", fontproperties=font)
plt.savefig('纵向应力.tif')
plt.show()


plt.figure(figsize=(11, 5.5))
plt.plot(x6, y6, 'o-', label='空间网格')
plt.plot(x7, y7, '-', label='实体模型', linewidth=2.0)
plt.ylim(min(min(y6), min(y7))*1.4, max(max(y6), max(y7))*1.4)
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1)
plt.xlabel("横向坐标（m）", fontproperties=font)
plt.ylabel("横向应力（MPa）", fontproperties=font)
plt.savefig('横向应力.tif')
plt.show()
# plt.xlim((0, 30))
# new_ticks = np.linspace(0, 30, 11)
# plt.xticks(new_ticks)


rs = read_col(sheet_1, 0)
ls = int(len(rs)/2)
xs = np.arange(ls) + 1
rs = np.array(rs)
rs1 = rs[:ls]
rs2 = rs[ls:]
plt.bar(xs, +rs1)
plt.bar(xs, -rs2)

for x, y in zip(xs, rs1):
    plt.text(x, y, '%.0f' % y, ha='center', va='bottom')
for x, y in zip(xs, rs2):
    plt.text(x, -y, '%.0f' % y, ha='center', va='top')

plt.ylim(-3000, 3000)
plt.xlabel("支座", fontproperties="SimHei", fontsize=12)
plt.ylabel("支座反力（KN）", fontproperties="SimHei", fontsize=12)
plt.savefig('双侧反力.tif')
plt.show()


stress = []
for i in range(10):
    s1 = x1 = read_col(sheet_1, i+1)
    stress.append(s1)
plt.figure(figsize=(11, 5.5))
for i in range(5):
    plt.plot(stress[2*i], stress[2*i+1]/1000000, label='腹板'+str(i+1), linewidth=3.0)
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1)
plt.xlabel("纵向坐标（m）", fontproperties=font)
plt.ylabel("纵向应力（MPa）", fontproperties=font)
plt.savefig('各道腹板应力.tif')
plt.show()

t_stress = []
for i in range(4):
    s1 = x1 = read_col(sheet_1, i+12)
    t_stress.append(s1)
plt.figure(figsize=(11, 5.5))
plt.plot(t_stress[0], t_stress[1]/1000000, '--', label='35m', linewidth=2.0)
plt.plot(t_stress[0], t_stress[2]/1000000, label='40m', linewidth=3.0)
plt.plot(t_stress[0], t_stress[3]/1000000, ':', label='44m', linewidth=2.0)
plt.xticks(fontproperties=font_1)
plt.yticks(fontproperties=font_1)
plt.legend(prop=font_1)
plt.xlabel("横向坐标（m）", fontproperties=font)
plt.ylabel("横向应力（MPa）", fontproperties=font)
plt.savefig('各道横向应力.tif')
plt.show()




