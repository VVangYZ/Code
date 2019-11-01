from sympy import *
import numpy as np
x = Symbol('x')
y = Symbol('y')

# ==================================================================================
# WK5
# 桥台桩基信息
p1 = 5.75    # 前桩（距桥台后距离）
p2 = 1.25    # 后桩
num_p = 3    # 每排桩数量
loc_bear = 5.12    # 支座

# 荷载信息
## 支反力，包括恒载和汽车荷载，已考虑分项系数
f = 5949

## 桥台信息
g = 9898.15    # 桥台自重，未考虑分项系数
loc_g = 3.85    # 桥台重心距承台后距离

## 上填土重量
g_soil = 50.505 * 9.8 * 18
loc_soil = 4.55/2

## 土压力
### 无汽车荷载时的主动土压力
phi = 30 * pi / 180    # 土的内摩擦角
alpha = 0 * pi / 180    # 桥台台背与竖直面的夹角
beta = 0 * pi / 180    # 填土表面与水平面的夹角
delta = phi / 2    # 台背与填土间的摩擦角，可取内摩擦角的一半

mu = (cos(phi - alpha))**2/((cos(alpha))**2*(cos(alpha + delta))*(1+sqrt((sin(phi + delta)*sin(phi - beta))/(cos(alpha + delta)* cos(alpha - beta))))**2)
mu = float(mu)

B = 11.1    # 桥台计算宽度
gamma = 18    # 桥台土重度
H = 9.8    # 计算土层高度
E = 0.5*B*mu*gamma*H**2
loc_E = 0.3 * H + 2

### 汽车荷载引起的主动土压力
# omega = alpha + delta + phi
# tan_theta = - tan(omega) + sqrt((cot(phi)+tan(omega))*((tan(omega) - tan(alpha))))
# l0 = H/(tan_theta + tan(alpha))

# 求解桩顶力
R = solve([x + y - f - g - g_soil, x * p1 + y * p2 - g * loc_g - f * loc_bear - g_soil * loc_soil - E * loc_E],[x, y])
print(R[x]/num_p, R[y]/num_p)


# ====================================================================================
# WK7
# 边桩信息
p1 = 5.75    # 前桩（距桥台后距离）
p2 = 1.25    # 后桩
loc_bear = 5.25    # 支座
num_p = 4    # 每排桩数量

# 荷载信息
## 支反力，包括恒载和汽车荷载，已考虑分项系数
f = 10711

## 桥台信息
g = 14004.75    # 桥台自重，未考虑分项系数
loc_g = 3.9    # 桥台重心距承台后距离

## 上填土重量
g_soil = 86.6775 * 9.8 * 18
loc_soil = 4.55/2

## 土压力
### 无汽车荷载时的主动土压力
phi = 30 * pi / 180    # 土的内摩擦角
alpha = 0 * pi / 180    # 桥台台背与竖直面的夹角
beta = 0 * pi / 180    # 填土表面与水平面的夹角
delta = phi / 2    # 台背与填土间的摩擦角，可取内摩擦角的一半

mu = (cos(phi - alpha))**2/((cos(alpha))**2*(cos(alpha + delta))*(1+sqrt((sin(phi + delta)*sin(phi - beta))/(cos(alpha + delta)* cos(alpha - beta))))**2)
mu = float(mu)

B = 19.05    # 桥台计算宽度
gamma = 18    # 桥台土重度
H = 9.8    # 计算土层高度
E = 0.5*B*mu*gamma*H**2
loc_E = 0.3 * H + 1.8

### 汽车荷载引起的主动土压力
# omega = alpha + delta + phi
# tan_theta = - tan(omega) + sqrt((cot(phi)+tan(omega))*((tan(omega) - tan(alpha))))
# l0 = H/(tan_theta + tan(alpha))

# 求解桩顶力
R = solve([x + y - f - g - g_soil, x * p1 + y * p2 - g * loc_g - f * loc_bear - g_soil * loc_soil - E * loc_E],[x, y])
print(R[x]/num_p, R[y]/num_p)


# ====================================================================================
# WK8
# 边桩信息
p1 = 5.75    # 前桩（距桥台后距离）
p2 = 1.25    # 后桩
loc_bear = 5.12    # 支座
num_p = 3    # 每排桩数量

# 荷载信息
## 支反力，包括恒载和汽车荷载，已考虑分项系数
f = 5957

## 桥台信息
g = 9898.15    # 桥台自重，未考虑分项系数
loc_g = 3.85    # 桥台重心距承台后距离

## 上填土重量
g_soil = 50.505 * 9.8 * 18
loc_soil = 4.55/2

## 土压力
### 无汽车荷载时的主动土压力
phi = 30 * pi / 180    # 土的内摩擦角
alpha = 0 * pi / 180    # 桥台台背与竖直面的夹角
beta = 0 * pi / 180    # 填土表面与水平面的夹角
delta = phi / 2    # 台背与填土间的摩擦角，可取内摩擦角的一半

mu = (cos(phi - alpha))**2/((cos(alpha))**2*(cos(alpha + delta))*(1+sqrt((sin(phi + delta)*sin(phi - beta))/(cos(alpha + delta)* cos(alpha - beta))))**2)
mu = float(mu)

B = 11.1    # 桥台计算宽度
gamma = 18    # 桥台土重度
H = 9.8    # 计算土层高度
E = 0.5*B*mu*gamma*H**2
loc_E = 0.3 * H + 2

### 汽车荷载引起的主动土压力
# omega = alpha + delta + phi
# tan_theta = - tan(omega) + sqrt((cot(phi)+tan(omega))*((tan(omega) - tan(alpha))))
# l0 = H/(tan_theta + tan(alpha))

# 求解桩顶力
R = solve([x + y - f - g - g_soil, x * p1 + y * p2 - g * loc_g - f * loc_bear - g_soil * loc_soil - E * loc_E],[x, y])
print(R[x]/num_p, R[y]/num_p)


