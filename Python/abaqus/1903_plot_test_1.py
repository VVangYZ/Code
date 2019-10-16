import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

with open('ssb_15_res', 'r') as f:
    res = json.load(f)

x = np.array(res[0])
y = np.array(res[1])
r = np.array(res[2])

# 绘制柱状图
with open('rs.json', 'r') as f:
    rs = json.load(f)
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

plt.ylim(-2000, 2000)
plt.xlabel("支座", fontproperties="SimHei", fontsize=12)
plt.ylabel("支座反力（KN）", fontproperties="SimHei", fontsize=12)
plt.savefig('双侧反力.tif')
plt.show()


# 绘制线图
with open('ssb_30_res.json', 'r') as f:
    res = json.load(f)

u = np.array(res[0])    # 纵向挠度
s1 = np.array(res[1])    # 纵向应力
s2 = np.array(res[2])    # 横向应力

x1 = []
x2 = []
x3 = []
y1 = []
y2 = []
y3 = []

for i in range(len(u)):
    x1.append(u[i][0])
    y1.append(u[i][1])
    x2.append(s1[i][0])
    y2.append(s1[i][1])
    x3.append(s2[i][0])
    y3.append(s2[i][1])

fig = plt.figure()
plt.plot(x1, y1)
plt.xlabel("纵向坐标", fontproperties="SimHei")
plt.ylabel("挠度值 (m)", fontproperties="SimHei")
plt.show()

# 绘制网格图
fig = plt.figure()
ax = Axes3D(fig)
ax.plot_wireframe(x, y, r, rstride=1, cstride=1)
plt.xlabel('x')
plt.ylabel('y')
plt.show()

# 绘制面图
fig = plt.figure()
ax = Axes3D(fig)
ax.plot_surface(x, y, r, rstride=1, cstride=1, cmap=plt.get_cmap('jet'))
ax.contourf(x, y, r, zdir='y', offset=35, cmap=plt.get_cmap('jet'))
plt.ylabel("长度", fontproperties="SimHei")
plt.xlabel("宽度", fontproperties="SimHei")
plt.show()


