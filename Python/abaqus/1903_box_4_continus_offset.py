#!/user/bin/python
# -* - coding:UTF-8 -*-

from abaqus import *
from abaqusConstants import *
from caeModules import *
from dxf2abq import importdxf
import math
import numpy as np
import json

# 文件名
file_name_1 = 'BOX_1.dxf'
file_name_2 = 'BOX_2.dxf'

# 箱梁参数
length = 90.0
height = 2.5
width = 18.5
angle1 = 30
angle2 = 30
thickness = 0.9    # 横梁厚度
cross_cut = (7.25, 5.95, 4.55, 2.45, 1.05)
support_loc = (-7, -3.5, 0, 3.5, 7)
density_i = 1.04

# 文件名参数
if angle1 == angle2:
	model_name = 'csb_p_' + str(angle1)
	job_name = 'csb_p_' + str(angle1) + '_out'
	res_out = './cae/csb_p_' + str(angle1) + '_res.json'
	rec_out = './cae/csb_p_' + str(angle1) + '_rec.json'
else:
	model_name = 'ssb_r_' + str(angle1) + '_' + str(angle2)
	job_name = 'ssb_r_' + str(angle1) + '_' + str(angle2) + '_out'
	res_out = './cae/ssb_r_' + str(angle1) + '_' + str(angle2) + '_res.json'
	rec_out = './cae/ssb_r_' + str(angle1) + '_' + str(angle2) + '_rec.json'


##### 创建模型 ================================================================================

model_1 = mdb.models['Model-1']
box_1 = mdb.Model(name = model_name)

# 导入截面
importdxf(fileName = file_name_1)
importdxf(fileName = file_name_2)
s1 = box_1.ConstrainedSketch(name = 'SBox_1', 
	objectToCopy = model_1.sketches[file_name_1.split('.')[0]])
s2 = box_1.ConstrainedSketch(name = 'SBox_2', 
	objectToCopy = model_1.sketches[file_name_2.split('.')[0]])

s3 = box_1.ConstrainedSketch(name = 'Cut', sheetSize = 500)
s3.rectangle(point1 = (-100, 5), point2 = (100, -5))

s4 = box_1.ConstrainedSketch(name = 'Support', sheetSize = 100)
s4.rectangle(point1 = (-0.25, -0.2), point2 = (0.25, 0))

##### 创建 Part ================================================================================

full_beam = box_1.Part(name = 'FullBeam', 
	dimensionality = THREE_D, type = DEFORMABLE_BODY)
full_beam.BaseSolidExtrude(sketch = s1, depth = 130)

full_plate = box_1.Part(name = 'FullPlate', 
	dimensionality = THREE_D, type = DEFORMABLE_BODY)
full_plate.BaseSolidExtrude(sketch = s2, depth = 130)

cut_cube = box_1.Part(name = 'CutCube', 
	dimensionality = THREE_D, type = DEFORMABLE_BODY)
cut_cube.BaseSolidExtrude(sketch = s3, depth = 200)

support = box_1.Part(name = 'Support', 
	dimensionality = THREE_D, type = DEFORMABLE_BODY)
support.BaseSolidExtrude(sketch = s4, depth = 0.5)

# 切割支座，此处注意如何确定 datums
p1 = support.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.25)
p2 = support.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0)
d1 = support.datums

support.PartitionCellByDatumPlane(datumPlane = d1[p1.id], cells = support.cells)
support.PartitionCellByDatumPlane(datumPlane = d1[p2.id], cells = support.cells)

##### 装配 ================================================================================

my_assembly = box_1.rootAssembly
i_full_beam = my_assembly.Instance(name = 'IFullBeam', 
	part = full_beam, dependent = OFF)
i_cut_cube_1 = my_assembly.Instance(name = 'ICutCube-1', 
	part = cut_cube, dependent = OFF)
i_cut_cube_2 = my_assembly.Instance(name = 'ICutCube-2', 
	part = cut_cube, dependent = OFF)

# 切出斜角
my_assembly.translate(instanceList = ('IFullBeam',), vector = (0, 0, -30))
my_assembly.translate(instanceList = ('ICutCube-1',), vector = (0, 0, -200))
my_assembly.translate(instanceList = ('ICutCube-2',), vector = (0, 0, length))
my_assembly.rotate(('ICutCube-1',), (0, 0, 0), (0, 1, 0), angle1)
my_assembly.rotate(('ICutCube-2',), (0, 0, length), (0, 1, 0), angle2)

i_cut_beam = my_assembly.InstanceFromBooleanCut('CutBeam', 
	instanceToBeCut = i_full_beam, cuttingInstances =(i_cut_cube_1, i_cut_cube_2))
cut_beam = box_1.parts['CutBeam']

# 切出横梁
# 横梁 1
i_full_plate_1 = my_assembly.Instance(name = 'IFullPlate-1', 
	part = full_plate, dependent = OFF)
i_cut_cube_3 = my_assembly.Instance(name = 'ICutCube-3', 
	part = cut_cube, dependent = OFF)
i_cut_cube_4 = my_assembly.Instance(name = 'ICutCube-4', 
	part = cut_cube, dependent = OFF)
	
my_assembly.translate(instanceList = ('IFullPlate-1',), vector = (0, 0, -30))
my_assembly.translate(instanceList = ('ICutCube-3',), vector = (0, 0, -200))
my_assembly.rotate(('ICutCube-3',), (0, 0, 0), (0, 1, 0), angle1)

my_assembly.translate(instanceList = ('ICutCube-4',), vector = (0, 0, thickness))
my_assembly.rotate(('ICutCube-4',), (0, 0, 0), (0, 1, 0), angle1)

i_plate_1 = my_assembly.InstanceFromBooleanCut('Plate-1', 
	instanceToBeCut = i_full_plate_1, 
	cuttingInstances = (i_cut_cube_3, i_cut_cube_4))
plate_1 = box_1.parts['Plate-1']

# 横梁 2
i_full_plate_2 = my_assembly.Instance(name = 'IFullPlate-2', 
	part = full_plate, dependent = OFF)
i_cut_cube_5 = my_assembly.Instance(name = 'ICutCube-5', 
	part = cut_cube, dependent = OFF)
i_cut_cube_6 = my_assembly.Instance(name = 'ICutCube-6', 
	part = cut_cube, dependent = OFF)
	
my_assembly.translate(instanceList = ('IFullPlate-2',), vector = (0, 0, -30))
my_assembly.translate(instanceList = ('ICutCube-5',), vector = (0, 0, length/3 + thickness/2))
my_assembly.rotate(('ICutCube-5',), (0, 0, length/3 + thickness/2), (0, 1, 0), angle2)

my_assembly.translate(instanceList = ('ICutCube-6',), 
	vector = (0, 0, (length/3 + thickness/2) - thickness - 200))
my_assembly.rotate(('ICutCube-6',), (0, 0, length/3 + thickness/2), (0, 1, 0), angle2)

i_plate_2 = my_assembly.InstanceFromBooleanCut('Plate-2', 
	instanceToBeCut = i_full_plate_2, cuttingInstances =(i_cut_cube_5, i_cut_cube_6))
plate_2 = box_1.parts['Plate-2']

# 横梁 3
i_full_plate_3 = my_assembly.Instance(name = 'IFullPlate-3', 
	part = full_plate, dependent = OFF)
i_cut_cube_7 = my_assembly.Instance(name = 'ICutCube-7', 
	part = cut_cube, dependent = OFF)
i_cut_cube_8 = my_assembly.Instance(name = 'ICutCube-8', 
	part = cut_cube, dependent = OFF)
	
my_assembly.translate(instanceList = ('IFullPlate-3',), vector = (0, 0, -30))
my_assembly.translate(instanceList = ('ICutCube-7',), vector = (0, 0, 2*length/3 + thickness/2))
my_assembly.rotate(('ICutCube-7',), (0, 0, 2*length/3 + thickness/2), (0, 1, 0), angle2)

my_assembly.translate(instanceList = ('ICutCube-8',), 
	vector = (0, 0, (2*length/3 + thickness/2) - thickness - 200))
my_assembly.rotate(('ICutCube-8',), (0, 0, 2*length/3 + thickness/2), (0, 1, 0), angle2)

i_plate_3 = my_assembly.InstanceFromBooleanCut('Plate-3', 
	instanceToBeCut = i_full_plate_3, cuttingInstances =(i_cut_cube_7, i_cut_cube_8))
plate_3 = box_1.parts['Plate-3']

# 横梁 4
i_full_plate_4 = my_assembly.Instance(name = 'IFullPlate-4', 
	part = full_plate, dependent = OFF)
i_cut_cube_9 = my_assembly.Instance(name = 'ICutCube-9', 
	part = cut_cube, dependent = OFF)
i_cut_cube_10 = my_assembly.Instance(name = 'ICutCube-10', 
	part = cut_cube, dependent = OFF)
	
my_assembly.translate(instanceList = ('IFullPlate-4',), vector = (0, 0, -30))
my_assembly.translate(instanceList = ('ICutCube-9',), vector = (0, 0, length))
my_assembly.rotate(('ICutCube-9',), (0, 0, length), (0, 1, 0), angle2)

my_assembly.translate(instanceList = ('ICutCube-10',), 
	vector = (0, 0, length - thickness - 200))
my_assembly.rotate(('ICutCube-10',), (0, 0, length), (0, 1, 0), angle2)

i_plate_4 = my_assembly.InstanceFromBooleanCut('Plate-4', 
	instanceToBeCut = i_full_plate_4, cuttingInstances =(i_cut_cube_9, i_cut_cube_10))
plate_4 = box_1.parts['Plate-4']

# 合并横隔板和主梁
my_assembly.makeIndependent(instances = (i_cut_beam, i_plate_1, i_plate_2, i_plate_3, i_plate_4))
i_beam = my_assembly.InstanceFromBooleanMerge('Beam', 
	instances = (i_cut_beam, i_plate_1, i_plate_2, i_plate_3, i_plate_4), keepIntersections = True)
beam = box_1.parts['Beam']
my_assembly.makeIndependent(instances = (i_beam,))

# 建立支座
ns = len(support_loc)
l_support = range(4*ns)
i_support = range(4*ns)

for i in range(ns):
	i1 = my_assembly.Instance(name = 'ISupport-' + str(i+1), 
		part = support, dependent = ON)
	l1 = i1.faces.findAt(((0, -0.2, 0.25), ))
	l_support[i] = l1
	i_support[i] = i1
	my_assembly.translate(instanceList = ('ISupport-' + str(i+1),), 
		vector = (support_loc[i], -1 * height, -support_loc[i] * tan(angle1 * pi / 180)))
	my_assembly.rotate(('ISupport-' + str(i+1),), 
		(support_loc[i], 0, -support_loc[i] * tan(angle1 * pi / 180)), (0, 1, 0), angle1)
	
	i2 = my_assembly.Instance(name = 'ISupport-' + str(i+ns+1), 
		part = support, dependent = ON)
	l2 = i2.faces.findAt(((0, -0.2, 0.25), ))
	l_support[i+ns] = l2
	i_support[i+ns] = i2
	my_assembly.translate(instanceList = ('ISupport-' + str(i+ns+1),), vector = 
		(support_loc[i], -1*height, -support_loc[i] * tan(angle2*pi/180) + length/3+0.25-0.5))
	my_assembly.rotate(('ISupport-' + str(i+ns+1),), 
		(support_loc[i], 0, -support_loc[i] * tan(angle2 * pi / 180) + length/3+0.25), 
		(0, 1, 0), angle2)
	
	i3 = my_assembly.Instance(name = 'ISupport-' + str(i+2*ns+1), 
		part = support, dependent = ON)
	l3 = i3.faces.findAt(((0, -0.2, 0.25), ))
	l_support[i+2*ns] = l3
	i_support[i+2*ns] = i3
	my_assembly.translate(instanceList = ('ISupport-' + str(i+2*ns+1),), vector = 
		(support_loc[i], -1*height, -support_loc[i] * tan(angle2*pi/180) + length/3*2+0.25-0.5))
	my_assembly.rotate(('ISupport-' + str(i+2*ns+1),), 
		(support_loc[i], 0, -support_loc[i] * tan(angle2 * pi / 180) + length/3*2+0.25), 
		(0, 1, 0), angle2)
	
	i4 = my_assembly.Instance(name = 'ISupport-' + str(i+3*ns+1), 
		part = support, dependent = ON)
	l4 = i4.faces.findAt(((0, -0.2, 0.25), ))
	l_support[i+3*ns] = l4
	i_support[i+3*ns] = i4
	my_assembly.translate(instanceList = ('ISupport-' + str(i+3*ns+1),), vector = 
		(support_loc[i], -1*height, -support_loc[i] * tan(angle2*pi/180) + length-0.5))
	my_assembly.rotate(('ISupport-' + str(i+3*ns+1),), 
		(support_loc[i], 0, -support_loc[i] * tan(angle2 * pi / 180) + length), 
		(0, 1, 0), angle2)


##### 定义材料、截面 ============================================================================

my_concrete = box_1.Material(name='Concrete')
e_property = (3.45e10, 0.167)
my_concrete.Elastic(table = (e_property, ))
my_concrete.Density(table = ((2600 * density_i, ), ))

my_section_1 = box_1.HomogeneousSolidSection(name='BeamSection',
	material = 'Concrete')

my_rubber = box_1.Material(name='Rubber')
e_property = (3.45e10/2, 0.167)
my_rubber.Elastic(table = (e_property, ))
my_rubber.Density(table = ((26 * density_i, ), ))

my_section_2 = box_1.HomogeneousSolidSection(name='SupportSection',
	material = 'Rubber')

region = (beam.cells,)
beam.SectionAssignment(region = region, sectionName = 'BeamSection')

region = (support.cells, )
support.SectionAssignment(region = region, sectionName = 'SupportSection')

##### 定义荷载步（自动建立 Initial） ============================================================

box_1.StaticStep(name = 'beamLoad', previous = 'Initial')
box_1.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'TF'))

##### 定义接触 ==================================================================================

sf_beam = []
f1 = i_beam.faces
f11 = f1.findAt(((0, -height, 0.01),))
sf1 = my_assembly.Surface(side1Faces = (f11, ), name = 'SBeam-1')
sf_beam.append(sf1)
f1 = i_beam.faces
f11 = f1.findAt(((0, -height, length/3 - 0.01),))
sf1 = my_assembly.Surface(side1Faces = (f11, ), name = 'SBeam-2')
sf_beam.append(sf1)
f1 = i_beam.faces
f11 = f1.findAt(((0, -height, length/3*2 - 0.01),))
sf1 = my_assembly.Surface(side1Faces = (f11, ), name = 'SBeam-3')
sf_beam.append(sf1)
f1 = i_beam.faces
f11 = f1.findAt(((0, -height, length - 0.01),))
sf1 = my_assembly.Surface(side1Faces = (f11, ), name = 'SBeam-4')
sf_beam.append(sf1)

sf_support = []
for i in range(len(i_support)):
	f1 = i_support[i].faces
	f11 = f1.getByBoundingBox(xMin = -1000, yMin = -height - 0.01, zMin = -1000, 
		xMax = 1000, yMax = -height + 0.01, zMax = 1000)
	sf1 = my_assembly.Surface(side1Faces = (f11, ) , name = 'S-' + str(i+1))
	sf_support.append(sf1)
	if i < len(i_support)/4:
		box_1.Tie(name = 'T-' + str(i+1), master = sf_beam[0], slave = sf1)
	elif i < len(i_support)/2:
		box_1.Tie(name = 'T-' + str(i+1), master = sf_beam[1], slave = sf1)
	elif i < len(i_support)/4*3:
		box_1.Tie(name = 'T-' + str(i+1), master = sf_beam[2], slave = sf1)
	else:
		box_1.Tie(name = 'T-' + str(i+1), master = sf_beam[3], slave = sf1)

##### 边界和荷载 ==============================================================================
# 通过坐标找表面
# p1 = (0, -0.1, 0)
# p2 = (0, -0.1, length)
# fix_face = cut_beam.faces.findAt((p1, ))
# top_face = cut_beam.faces.findAt((p2, ))
# fix_region = (fix_face,)
# top_region = ((top_face,SIDE1),) # SIDE1 表示施加在外侧

csys_1 = my_assembly.DatumCsysByThreePoints(
	name='Csys-1', coordSysType=CARTESIAN, origin=(0.0, 0.0, 0.0), 
	point1=(cos(angle1*pi/180), 0.0, -sin(angle1*pi/180)), point2=(0.0, 1.0, 0.0))

datum = my_assembly.datums[csys_1.id]
box_1.DisplacementBC(name='BC-1', createStepName='Initial', 
	region=(l_support[0], ), u1=SET, u2=SET, u3=SET, localCsys=datum)
box_1.DisplacementBC(name='BC-2', createStepName='Initial', 
	region=(l_support[len(l_support)/4], l_support[len(l_support)/2], 
		l_support[len(l_support)/4*3]), u1=SET, u2=SET)
box_1.DisplacementBC(name='BC-3', createStepName='Initial', 
	region=tuple(l_support[1:len(l_support)/4]), u2=SET, u3=SET, localCsys=datum)

box_1.DisplacementBC(name='BC-4', createStepName='Initial', 
	region=tuple(l_support[len(l_support)/4+1:len(l_support)/2]), u2=SET)
box_1.DisplacementBC(name='BC-5', createStepName='Initial', 
	region=tuple(l_support[len(l_support)/2+1:len(l_support)/4*3]), u2=SET)
box_1.DisplacementBC(name='BC-6', createStepName='Initial', 
	region=tuple(l_support[len(l_support)/4*3+1:len(l_support)]), u2=SET)

all_d = my_assembly.instances['ISupport-5'].datums
p3 = my_assembly.DatumPlaneByOffset(plane = all_d[2], flip = SIDE1, 
	offset = length / 2 * cos(angle1*pi/180) - 0.25)
all_d = my_assembly.datums
p4 = my_assembly.DatumPlaneByPrincipalPlane(principalPlane = YZPLANE, offset = -3.5)
my_assembly.PartitionCellByDatumPlane(datumPlane = all_d[p3.id], cells = i_beam.cells)
my_assembly.PartitionCellByDatumPlane(datumPlane = all_d[p4.id], cells = i_beam.cells)

p_force = i_beam.vertices.findAt(((-3.5, 0, length/2 + 3.5 * tan(angle1*pi/180)), ))
region = my_assembly.Set(vertices = p_force, name = 'Set_Force')
box_1.ConcentratedForce(name='Load-1', 
    createStepName='beamLoad', region = region, cf2=-10000000.0, 
    distributionType = UNIFORM, field='', localCsys=None)

##### 网格划分 ==============================================================================

region = (i_beam.cells, )
elem_type = mesh.ElemType(elemCode = C3D8I, elemLibrary = STANDARD)
my_assembly.setElementType(regions = region, elemTypes=(elem_type,))

my_assembly.seedPartInstance(regions = (i_beam, ), size = 0.2)
my_assembly.generateMesh(regions = (i_beam, ))

support.seedPart(size=0.1, deviationFactor=0.1, minSizeFactor=0.1)
support.generateMesh()

##### 提交分析 ==============================================================================

jobName = 'test_30_2'
my_job = mdb.Job(name = jobName, model = model_name)
my_job.submit()
my_job.waitForCompletion()


##### =====================================================================================
##### 后处理 ==============================================================================
##### =====================================================================================

# 显示，准备
vp_1 = session.viewports['Viewport: 1']
box_1_odb = session.openOdb(name = jobName + '.odb', readOnly = False)
vp_1.setValues(displayedObject = box_1_odb)
o_assembly = box_1_odb.rootAssembly
o_ins = o_assembly.instances


##### 获取支座反力 ===========================================================================


# 通过 XYDATA 获得支反力，数据较多，不推荐
# def get_rec_1(name):
# 	a = len(o_ins[name].nodes)
# 	b = range(1,a+1)
# 	c = tuple(b)
# 	r_data = session.xyDataListFromField(odb = box_1_odb, outputPosition = NODAL, 
# 		variable = (('TF', NODAL, ((COMPONENT, 'TF2'), )), ), nodeLabels = ((name, b, ), ))

# 通过 odb 直接输出结果，较为推荐
def get_rec_2(name):
	f1 = box_1_odb.steps['beamLoad'].frames[-1]
	fop = f1.fieldOutputs['TF']
	rec = []
	for i in range(1,len(o_ins[name].nodes)+1):
		n1 = o_ins[name].getNodeFromLabel(label = i)
		fop_n1 = fop.getSubset(region = n1)
		a = fop_n1.values[0].data[1]
		rec.append(a)
	print sum(rec)
	return rec

RS = []
for i in range(1, 21):
	name = 'ISUPPORT-' + str(i)
	rec_1 = sum(get_rec_2(name))
	RS.append(rec_1)

# with open(rec_out, 'w') as f:
# 	json.dump(RS, f)


##### 获取位移、应力 ==========================================================================

# 建立路径，得到 xydata
variable = ('U', NODAL, ((COMPONENT, 'U2'), ), )
variable1 = ('S', INTEGRATION_POINT, ((COMPONENT, 'S33'), ), )
variable2 = ('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), ), )
res_i = 0

def get_path(x, y, z, v, d):
	# d 为方向，1 为纵向（x 为横向位置），2 为横向（x 为纵向位置）；
	global res_i
	res_i += 1
	if d == 1:
		origin = (x, -y, -x * tan(angle1*pi/180))
		axis_y = (x, 10, -x * tan(angle1*pi/180))
		axis_x = (x, -y, length - x * tan(angle2*pi/180))
		t1 = (origin, axis_y, axis_x)
		path_1 = session.Path(name = 'Path-1', type = RADIAL,  expression = t1, 
		circleDefinition = ORIGIN_AXIS, numSegments = 100, radialAngle = 0,
		startRadius = 0, 
		endRadius = (length - x * tan(angle2*pi/180) + x * tan(angle1*pi/180)))
		dirction = Z_COORDINATE
	elif d == 2:
		origin = (-width/2, -y, z)
		axis_y = (-width/2, 10, z)
		axis_x = (width/2, -y, z)
		t1 = (origin, axis_y, axis_x)
		path_1 = session.Path(name = 'Path-1', type = RADIAL,  expression = t1, 
		circleDefinition = ORIGIN_AXIS, numSegments = 100, radialAngle = 0,
		startRadius = 0, 
		endRadius = width)
		dirction = X_COORDINATE
	my_data = session.XYDataFromPath(path = path_1, name = 'Data-' + str(res_i) ,
		includeIntersections = False, shape = UNDEFORMED,
		labelType = dirction, variable = v)
	return my_data

res_0 = get_path(3.5, 0, 0, variable, 1)
res_1 = get_path(3.5, 0, 0, variable1, 1)
res_2 = get_path(0, 0, 44, variable2, 2)

for i in res_2:
	print i[0], i[1]

# 输出至文件
# res = [[], [], []]
# for i in range(len(res_0)):
# 	res[0].append(res_0[i])
# 	res[1].append(res_1[i])
# 	res[2].append(res_2[i])

# with open(res_out, 'w') as f:
# 	json.dump(res, f)

print 'done!'

# 绘制网格
# xx = np.linspace(-9.25, 9.25, 25)
# res_u = []

# for i in xx:
# 	data_1 = get_path(i, 0.05, 15, variable1, 1)
# 	res_u.append(data_1)

# X = []
# Y = []
# R = []

# for i in range(len(xx)):
# 	x1 = []
# 	y1 = []
# 	r1 = []
# 	for j in range(100):
# 		x11 = xx[i]
# 		y11 = res_u[i][j][0]
# 		r11 = res_u[i][j][1]
# 		x1.append(x11)
# 		y1.append(y11)
# 		r1.append(r11)
# 	X.append(x1)
# 	Y.append(y1)
# 	R.append(r1)
#   RES = [X, Y, R]


##### 指定绘制区域 ===========================================================================

# 直接后处理，速度较慢
def get_result(ins, xmin, ymin, zmin, xmax, ymax, zmax):
	l_elem = []
	for i in ins.elements:
		for j in i.connectivity:
			x = ins.nodes[j-1].coordinates[0]
			y = ins.nodes[j-1].coordinates[1]
			z = ins.nodes[j-1].coordinates[2]
			if (xmin < x < xmax) and (ymin < y < ymax) and (zmin < z < zmax):
				l_elem.append(i.label)
	leaf = dgo.LeafFromElementLabels(partInstanceName = ins.name, elementLabels = tuple(l_elem))
	session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf = leaf)
	return l_elem

# 连续后处理，速度较快
a = get_result(o_beam, -100, -10, 10, 100, 10, 20)

def get_result_2(ins, xmin, ymin, zmin, xmax, ymax, zmax):
	a = ins.elements.getByBoundingBox(xMin = xmin, yMin = ymin, zMin = zmin, 
		xMax = xmax, yMax = ymax, zMax = zmax)
	l_elem = []
	for i in a:
		l_elem.append(i.label)
	leaf = dgo.LeafFromElementLabels(partInstanceName = ins.name.upper(), 
		elementLabels = tuple(l_elem))
	session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf = leaf)

get_result_2(i_beam,  -100, -10, 10, 100, 10, 20)

vp_1.odbDisplay.setPrimaryVariable(variableLabel='S', 
	outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 'S33'), )    # 效应
vp_1.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))    # 变形


