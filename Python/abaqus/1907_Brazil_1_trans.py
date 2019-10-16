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
thickness = 0.2

# 文件名
file_name_1 = 'sec.dxf'
file_name_2 = 'prostress.dxf'
model_name = 'beam_transverse'


##### 创建模型 ================================================================================

model_1 = mdb.models['Model-1']
box_1 = mdb.Model(name = model_name)

# 导入截面
importdxf(fileName = file_name_1)
importdxf(fileName = file_name_2)
s1 = box_1.ConstrainedSketch(name = 'SBox_1', 
	objectToCopy = model_1.sketches[file_name_1.split('.')[0]])
s2 = box_1.ConstrainedSketch(name = 'Prostress', 
	objectToCopy = model_1.sketches[file_name_2.split('.')[0]])


##### 创建 Part ================================================================================

beam = box_1.Part(name = 'Beam', 
	dimensionality = THREE_D, type = DEFORMABLE_BODY)
beam.BaseSolidExtrude(sketch = s1, depth = 70)

p0 = beam.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=-0.93)

p1 = []
p1.append(beam.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=35-0.1-thickness))
p1.append(beam.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=35+0.1+thickness))

p2 = []
for i in range(2):
    p2.append(beam.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=24.5/2-1+0.3+thickness-i*(1.8+1.3)))
    p2.append(beam.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=24.5/2-1-0.3-thickness-i*(1.8+1.3)))
    p2.append(beam.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=24.5/2-1-1.8+0.3+thickness-i*(1.8+1.3)))
    p2.append(beam.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=24.5/2-1-1.8-0.3-thickness-i*(1.8+1.3)))

d1 = beam.datums
beam.PartitionCellByDatumPlane(datumPlane = d1[p0.id], cells = beam.cells)


for i in p2:
    l4 = beam.cells.findAt(((1, -0.2, 10), ))
    beam.PartitionCellByDatumPlane(datumPlane = d1[i.id], cells = l4)

for i in p1:
    beam.PartitionCellByDatumPlane(datumPlane = d1[i.id], cells = beam.cells)


pro = box_1.Part(name = 'Prostress',
    dimensionality = THREE_D, type = DEFORMABLE_BODY)
pro.BaseWire(sketch = s2)
pro = box_1.parts['Prostress']

##### 装配 ================================================================================

my_assembly = box_1.rootAssembly
i_beam = my_assembly.Instance(name = 'IBeam', 
	part = beam, dependent = OFF)

i_pro = my_assembly.Instance(name = 'IPro',
    part = pro, dependent = ON)

my_assembly.translate(instanceList = ('IPro',), vector = (0, 0, 0.2))
my_assembly.LinearInstancePattern(instanceList = ('IPro',), number1 = 117, 
    spacing1 = 0.6, number2 = 1, spacing2 = 1, direction1 = (0, 0, 1))

##### 定义材料、截面 ============================================================================

my_concrete = box_1.Material(name='Concrete')
e_property = (3.45e10, 0.167)
my_concrete.Elastic(table = (e_property, ))
my_concrete.Density(table = ((2600 , ), ))

my_section_1 = box_1.HomogeneousSolidSection(name='BeamSection',
	material = 'Concrete')

my_steel = box_1.Material(name = 'Steel')
e_property = (1.95e11, 0.3)
my_steel.Elastic(table = (e_property, ))
my_steel.Density(table = ((7.8e3, ), ))
my_steel.Expansion(table=((1.2e-05, ), ))

my_section_2 = box_1.TrussSection(name='ProSection', material='Steel', 
    area=0.000968)

region = (beam.cells, )
beam.SectionAssignment(region = region, sectionName = 'BeamSection')
region = (pro.edges, )
pro.SectionAssignment(region = region, sectionName = 'ProSection')


##### 定义荷载步（自动建立 Initial） ============================================================

box_1.StaticStep(name = 'beamLoad', previous = 'Initial')
box_1.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'TF'))

##### 边界和荷载 ==============================================================================
bc_f_1 = i_beam.faces.getByBoundingBox(xMin = -20, xMax = 20, yMin = -20, yMax = 10, zMin = -0.1, zMax = 0.1)
bc_f_2 = i_beam.faces.getByBoundingBox(xMin = -20, xMax = 20, yMin = -20, yMax = 10, zMin = 69.9, zMax = 70.1)
box_1.DisplacementBC(name='BC-1', createStepName='Initial', 
	region=(bc_f_1, bc_f_2), u1=SET, u2=SET, u3=SET)



##### 网格划分 ==============================================================================


##### 提交分析 ==============================================================================


##### 后处理 ==============================================================================
7020, 36925:36984:1, 7022, 37013:37040:1, 36632, 34611:34614:1, 279, 16034:16036:1, 259, 16003:16006:1, 233, 15972, 232, 33355:33358:1, 215, 15954:15956:1, 193, 15919:15922:1, 192, 33323, 33324, 5900

7018, 36862:36850:-1, 7016, 36836:36823:-1, 7014, 7008, 36802:36793:-1, 7006, 36782:36748:-1, 7004, 36712:36703:-1, 7000, 6115, 34616, 282, 16040:16042:1, 262, 16011:16014:1, 238, 15974, 235, 33364, 33363, 5911, 33360, 218, 15960:15962:1, 198, 15927:15930:1, 195, 33327, 33328, 5901







