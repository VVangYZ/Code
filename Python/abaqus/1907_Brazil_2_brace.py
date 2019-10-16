#!/user/bin/python
# -* - coding:UTF-8 -*-

from abaqus import *
from abaqusConstants import *
from caeModules import *
from dxf2abq import importdxf
import math
import numpy as np
import json

# 一些变量
beam_l = 27
brace_t_l = 8.45
brace_i_l = 6.95
space = 3.5
pro_s = 0.5
pro_n = 4
loc = [13.5, 10.25]

# 文件名
sec_name = []
sec_name.append('sec_beam.dxf')
sec_name.append('sec_brace.dxf')
sec_name.append('sec_brace_2.dxf')
sec_name.append('sec_panel.dxf')
sec_name.append('sec_cast.dxf')
sec_name.append('pro.dxf')

##### 创建模型 =====================================================================================

model_1 = mdb.models['Model-1']

# 导入截面
ss = []

for i in sec_name:
    importdxf(fileName = i)
    ss.append(model_1.sketches[i.split('.')[0]])

# 绘制切割体和车轮面
ss.append(model_1.ConstrainedSketch(name = 'Cut', sheetSize = 50))
ss[-1].rectangle(point1 = (0, -0.45), point2 = (20, 1))

ss.append(model_1.ConstrainedSketch(name = 'wheel', sheetSize = 50))
ss[-1].rectangle(point1 = (-0.25-0.1, 0), point2 = (0.25+0.1, 0.02))

##### 创建模型 =====================================================================================

# 主梁
beam = model_1.Part(name = 'Beam',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
beam.BaseSolidExtrude(sketch = ss[0], depth = beam_l)

# 横撑
brace_t = model_1.Part(name = 'Brace_t',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
brace_t.BaseSolidExtrude(sketch = ss[1], depth = brace_t_l)

# 斜撑
brace_i = model_1.Part(name = 'Brace_i',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
brace_i.BaseSolidExtrude(sketch = ss[2], depth = brace_i_l)

# 搭班
panel = model_1.Part(name = 'Panel',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
panel.BaseSolidExtrude(sketch = ss[3], depth = space - 0.39)

# 现浇板
cast = model_1.Part(name = 'Cast',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
cast.BaseSolidExtrude(sketch = ss[4], depth = beam_l)

p0 = cast.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=-0.1)
p = cast.datums
cast.PartitionCellByDatumPlane(datumPlane = p[p0.id], cells = cast.cells)

# 预应力筋
pro = model_1.Part(name = 'Prostress',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
pro.BaseWire(sketch = ss[5])

# 切割斜撑构件
cut = model_1.Part(name = 'Cut',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
cut.BaseSolidExtrude(sketch = ss[-2], depth = 5)

# 车轮
wheel = model_1.Part(name = 'Wheel',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
wheel.BaseSolidExtrude(sketch = ss[-1], depth = 0.4)

##### 装配 =========================================================================================

# 建立主梁、横撑、斜撑以及切割件
myass = model_1.rootAssembly
i_beam = myass.Instance(name = 'IBeam',
    part = beam, dependent = ON)

i_brace_t = myass.Instance(name = 'IBrace_t',
    part = brace_t, dependent = OFF)

i_brace_i = myass.Instance(name = 'IBrace_i',
    part = brace_i, dependent = OFF)

i_cut = myass.Instance(name = 'ICut',
    part = cut, dependent = OFF)

# 定位横撑、斜撑
myass.rotate(('IBrace_t', 'IBrace_i'), (0, 0, 0), (0, 1, 0), 90)
myass.translate(('IBrace_i', ), vector = (-0.5, 0, 0))
myass.rotate(('IBrace_i',), (6.45, -0.275, 0), (0, 0, 1), 23)
myass.translate(('IBrace_i', 'IBrace_t'), 
    vector = (12.25-8.45, 0, (beam_l % space)/2))

# 切割和合并三角撑，并复制
i_brace_i_2 = myass.InstanceFromBooleanCut('IBrace_i_2', instanceToBeCut = i_brace_i,
     cuttingInstances =(i_cut, i_beam))
myass.features['IBeam'].resume()
i_brace_t_2 = myass.InstanceFromBooleanCut('IBrace_t_2', instanceToBeCut = i_brace_t,
     cuttingInstances =(i_beam, ))
myass.features['IBeam'].resume()
i_brace = myass.InstanceFromBooleanMerge(name='IBrace', instances=(i_brace_i_2, 
    i_brace_t_2, ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
i_brace_r = myass.LinearInstancePattern(instanceList = ('IBrace-1',), 
    number1 = int(beam_l//space+1), spacing1 = space, number2 = 1, spacing2 = 1, 
    direction1 = (0, 0, 1))
brace = model_1.parts['IBrace']

brace_name = ['IBrace-1', ]
braces = [i_brace, ]

for i in i_brace_r:
    brace_name.append(i.name)
    braces.append(i)

i_brace_l = myass.RadialInstancePattern(instanceList = tuple(brace_name), 
    point=(0, 0, beam_l/2.0), axis=(0, 1, 0), number=2, totalAngle=180.0)

for i in i_brace_l:
    brace_name.append(i.name)
    braces.append(i)

# 建立搭板
i_panel = myass.Instance(name = 'IPanel',part = panel, dependent = ON)
myass.translate(('IPanel', ), vector = (0, 0, (beam_l%space)/2+0.39/2))
i_panel_all = myass.LinearInstancePattern(instanceList = ('IPanel',), 
    number1 = int(beam_l//space), spacing1 = space, number2 = 2, 
    spacing2 = -18.25, direction1 = (0, 0, 1), direction2 = (1, 0, 0))

panel_name = ['IPanel', ]
panels = [i_panel, ]

for i in i_panel_all:
    panel_name.append(i.name)
    panels.append(i)

# 建立现浇板
i_cast = myass.Instance(name = 'ICast', part = cast, dependent = ON)
i_cast_r = myass.InstanceFromBooleanCut('ICast_r', instanceToBeCut = i_cast,
     cuttingInstances = tuple(braces))

for i in brace_name:
    myass.features[i].resume()

i_cast_l = myass.LinearInstancePattern(instanceList = ('ICast_r-1',), number1 = 2, 
    spacing1 = -18.25, number2 = 1, spacing2 = 1, direction1 = (1, 0, 0))
cast_1 = model_1.parts['ICast_r']

cast_name = ['ICast_r-1', ]
casts = [i_cast_r, ]

cast_name.append(i_cast_l[0].name)
casts.append(i_cast_l[0])

beam_name = ['IBeam', ]
beams = [i_beam, ]

# 建立预应力
i_pro = myass.Instance(name = 'IPro', part = pro, dependent = ON)
myass.translate(('IPro', ), vector = (0, 0, pro_s/2))
i_pro_l = myass.LinearInstancePattern(instanceList = ('IPro',), 
    number1 = int(beam_l//pro_s), spacing1 = pro_s, number2 = 1, 
    spacing2 = 1, direction1 = (0, 0, 1))

pros = [i_pro, ]
for i in i_pro_l:
    pros.append(i)

# 建立车轮
i_wheel = myass.Instance(name = 'IWheel', part = wheel, dependent = ON)
myass.translate(('IWheel', ), vector = (loc[1]-1, 0, loc[0]-1.5-0.2))
i_wheel_all = myass.LinearInstancePattern(instanceList = ('IWheel',), 
    number1 = 3, spacing1 = 1.5, number2 = 2, spacing2 = 2, 
    direction1 = (0, 0, 1), direction2 = (1, 0, 0))

wheels = [i_wheel, ]
for i in i_wheel_all:
    wheels.append(i)

##### 定义材料特性 =================================================================================

# 混凝土
my_concrete = model_1.Material(name='Concrete')
e_property = (3.45e10, 0.167)
my_concrete.Elastic(table = (e_property, ))
my_concrete.Density(table = ((2600 , ), ))

my_section_1 = model_1.HomogeneousSolidSection(name='BeamSection',
	material = 'Concrete')

# 钢束
my_steel = model_1.Material(name = 'Steel')
e_property = (1.95e11, 0.3)
my_steel.Elastic(table = (e_property, ))
my_steel.Density(table = ((7.8e3, ), ))
my_steel.Expansion(table=((1.2e-05, ), ))

my_section_2 = model_1.TrussSection(name='ProSection', material='Steel', 
    area=(15.2/2000)**2*pi*pro_n)

# 赋予混凝土
region = (beam.cells, )
beam.SectionAssignment(region = region, sectionName = 'BeamSection')
region = (panel.cells, )
panel.SectionAssignment(region = region, sectionName = 'BeamSection')
region = (cast_1.cells, )
cast_1.SectionAssignment(region = region, sectionName = 'BeamSection')
region = (brace.cells, )
brace.SectionAssignment(region = region, sectionName = 'BeamSection')
region = (wheel.cells, )
wheel.SectionAssignment(region = region, sectionName = 'BeamSection')

# 赋予钢束
region = (pro.edges, )
pro.SectionAssignment(region = region, sectionName = 'ProSection')

##### 定义荷载步 ===================================================================================

model_1.StaticStep(name='beam', previous='Initial')    # 主梁架设,斜撑也上
model_1.StaticStep(name='panel', previous='beam')    # 搭板搭设（加载现浇力）
model_1.StaticStep(name='cast', previous='panel')    # 现浇板凝结（横向预应力）
model_1.StaticStep(name='pavement', previous='cast')    # 二期
model_1.StaticStep(name='vehicle', previous='pavement')    # 汽车

# 设定输出量
model_1.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'TF'))

##### 定义相互作用 =================================================================================

# 定义施工步骤 Model Change -----------------------------------------------------------------------

# 搭板和现浇板失效
p_cell = []

for i in panels:
    p_cell.append(i.cells)

myass.Set(cells=tuple(p_cell), name='panel')

for i in casts:
    p_cell.append(i.cells)

model_1.ModelChange(name='beam_and_brace', createStepName='beam', 
    region=tuple(p_cell), activeInStep=False, includeStrain=False)

# 预应力失效
region = []
for i in pros:
    region.append(i.edges)

model_1.ModelChange(name='no_pro', createStepName='beam', 
    region=tuple(region), activeInStep=False, includeStrain=False)

# 车轮失效
region = []
for i in wheels:
    region.append(i.cells)

model_1.ModelChange(name='no_wheel', createStepName='beam', 
    region=tuple(region), activeInStep=False, includeStrain=False)

# 激活搭板
model_1.ModelChange(name='panel', createStepName='panel', 
    region=tuple(p_cell[:len(panels)]), activeInStep=True, includeStrain=False)

# 激活现浇板
model_1.ModelChange(name='cast', createStepName='cast', 
    region=tuple(p_cell[len(panels):]), activeInStep=True, includeStrain=False)

# 激活预应力
region = []
for i in pros:
    region.append(i.edges)

model_1.ModelChange(name='pro', createStepName='cast', 
    region=tuple(region), activeInStep=True, includeStrain=False)

# 激活车轮
region = []
for i in wheels:
    region.append(i.cells)

model_1.ModelChange(name='wheel', createStepName='vehicle', 
    region=tuple(region), activeInStep=True, includeStrain=False)


# 定义各部件之间的相互关系 --------------------------------------------------------------------------

# 主梁和现浇板（现浇板为主）
beam_cast = []
for i in beams:
    beam_cast.append(i.faces.getByBoundingBox(xMin = -6-0.01, yMin = -10,
     zMin = -100, xMax = -6+0.01, yMax = 10, zMax = 100))
    beam_cast.append(i.faces.getByBoundingBox(xMin = 6-0.01, yMin = -10, 
    zMin = -100, xMax = 6+0.01, yMax = 10, zMax = 100))

myass.Surface(side1Faces=tuple(beam_cast), name='beam_cast')

cast_beam = []
for i in casts:
    cast_beam.append(i.faces.getByBoundingBox(xMin = -6-0.01, yMin = -10, 
    zMin = -100, xMax = -6+0.01, yMax = 10, zMax = 100))
    cast_beam.append(i.faces.getByBoundingBox(xMin = 6-0.01, yMin = -10, 
    zMin = -100, xMax = 6+0.01, yMax = 10, zMax = 100))

myass.Surface(side1Faces=tuple(cast_beam), name='cast_beam')

region1=myass.surfaces['cast_beam']
region2=myass.surfaces['beam_cast']
model_1.Tie(name='cast_beam', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 搭板和现浇板（现浇板为主）
panel_top = []
for i in panels:
    panel_top.append(i.faces.getByBoundingBox(xMin = -1000, yMin = -0.225-0.001, 
    zMin = -1000, xMax = 1000, yMax = -0.225+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(panel_top), name='panel_top')

cast_panel = []
for i in casts:
    cast_panel.append(i.faces.getByBoundingBox(xMin = -1000, yMin = -0.225-0.001, 
    zMin = -1000, xMax = 1000, yMax = -0.225+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(cast_panel), name='cast_panel')

region1=myass.surfaces['cast_panel']
region2=myass.surfaces['panel_top']
model_1.Tie(name='panel_cast', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 支撑和搭板（支撑为主）
brace_panel = []
for i in braces:
    brace_panel.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.275-0.001, 
    zMin = -1000, xMax = 100, yMax = -0.275+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(brace_panel), name='brace_panel')

panel_bot = []
for i in panels:
    panel_bot.append(i.faces.getByBoundingBox(xMin = -1000, yMin = -0.275-0.001, 
    zMin = -1000, xMax = 1000, yMax = -0.275+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(panel_bot), name='panel_bot')

region1=myass.surfaces['brace_panel']
region2=myass.surfaces['panel_bot']
model_1.Tie(name='brace_panel', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 主梁和支撑（主梁为主）
beam_brace = []
for i in beams:
    beam_brace.append(i.faces.getByBoundingBox(xMin = -7, yMin = -10, zMin = -1000, 
		xMax = -4, yMax = 10, zMax = 1000))
    beam_brace.append(i.faces.getByBoundingBox(xMin = 4, yMin = -10, zMin = -1000, 
		xMax = 7, yMax = 10, zMax = 1000))

myass.Surface(side1Faces=tuple(beam_brace), name='beam_brace')

brace_beam = []
for i in braces:
    brace_beam.append(i.faces.getByBoundingBox(xMin = -7, yMin = -10, zMin = -1000, 
		xMax = 7, yMax = 10, zMax = 1000))

myass.Surface(side1Faces=tuple(brace_beam), name='brace_beam')

region1=myass.surfaces['beam_brace']
region2=myass.surfaces['brace_beam']
model_1.Tie(name='beam_brace', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 支撑和现浇板（支撑为主）
brace_cast = []
for i in braces:
    brace_cast.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.1-0.001, 
    zMin = -1000, xMax = 100, yMax = -0.1+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(brace_cast), name='brace_cast')

cast_brace = []
for i in casts:
    cast_brace.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.1-0.001, 
    zMin = -1000, xMax = 100, yMax = -0.1+0.001, zMax = 1000))

myass.Surface(side1Faces=tuple(cast_brace), name='cast_brace')

region1=myass.surfaces['brace_cast']
region2=myass.surfaces['cast_brace']
model_1.Tie(name='brace_cast', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 车轮和主梁、现浇板（车轮为主）
wheel_bot = []
for i in wheels:
    wheel_bot.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.001, 
    zMin = -100, xMax = 100, yMax = 0.001, zMax = 100))

myass.Surface(side1Faces=tuple(wheel_bot), name='wheel_bot')

bridge_up = []
for i in beams:
    bridge_up.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.001, 
    zMin = -100, xMax = 100, yMax = 0.001, zMax = 100))

for i in casts:
    bridge_up.append(i.faces.getByBoundingBox(xMin = -100, yMin = -0.001, 
    zMin = -100, xMax = 100, yMax = 0.001, zMax = 100))

myass.Surface(side1Faces=tuple(bridge_up), name='pavement')

region1=myass.surfaces['wheel_bot']
region2=myass.surfaces['pavement']
model_1.Tie(name='wheel_bridge', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)

# 预应力束
region = []
for i in pros:
    region.append(i.edges)

model_1.EmbeddedRegion(name='pro', embeddedRegion=tuple(region), 
    hostRegion=None, weightFactorTolerance=1e-06, absoluteTolerance=0.0, 
    fractionalTolerance=0.05, toleranceMethod=BOTH)


##### 定义边界和荷载 ================================================================================

# 约束
bo_l = i_beam.edges.findAt(((0, -3.5, 0),),((0, -3.5, beam_l),))
myass.Set(edges=bo_l, name='bo_l')

region = myass.sets['bo_l']
model_1.DisplacementBC(name='BC', createStepName='Initial', 
    region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)

# 梁体自重
cell_beam = (i.cells for i in beams)
model_1.Gravity(name='beam', createStepName='beam', 
    comp2=-9.8, distributionType=UNIFORM, field='', region = tuple(cell_beam))

# 支撑自重
cell_brace = (i.cells for i in braces)
model_1.Gravity(name='brace', createStepName='beam', 
    comp2=-9.8, distributionType=UNIFORM, field='', region = tuple(cell_brace))

# 搭板自重
cell_panel = (i.cells for i in panels)
model_1.Gravity(name='panel', createStepName='panel', 
    comp2=-9.8, distributionType=UNIFORM, field='', region = tuple(cell_panel))

# 现浇板重量
region = myass.surfaces['panel_top']
model_1.Pressure(name='cast_g', createStepName='panel', 
    region=region, distributionType=TOTAL_FORCE, magnitude=0.225*6.25*30*2*25000, 
    amplitude=UNSET)

# 二期铺装（面荷载只能施加在 surface 组上？）
region1=myass.surfaces['pavement']

model_1.Pressure(name='pavement', createStepName='pavement', 
    region=region1, distributionType=TOTAL_FORCE, magnitude=85000*30, 
    amplitude=UNSET)

# 预应力
region = []
for i in pros:
    region.append(i.edges)

model_1.Temperature(name='pro', createStepName='cast', 
    region=region, distributionType=UNIFORM, 
    crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, magnitudes=(-500.0, ))

# 车轮荷载
region = []
for i in wheels:
    region.append(i.faces.getByBoundingBox(xMin = -100, yMin = 0.02-0.001, 
    zMin = -100, xMax = 100, yMax = 0.02+0.001, zMax = 100))

region = myass.Surface(side1Faces=tuple(region), name='wheel_top')

model_1.Pressure(name='vehicle', createStepName='vehicle', 
    region=region, distributionType=TOTAL_FORCE, magnitude=75000*6, 
    amplitude=UNSET)

##### 划分网格，提交分析 ============================================================================






