#%%
from pyautocad import Autocad, APoint
import numpy as np


acad = Autocad(create_if_not_exists = False)

acad.prompt("Hello! AutoCAD from pyautocad.")
print(acad.doc.Name)

#%%
# a = []

# for item in acad.iter_objects("PolyLine"):
#     a.append(item.Coordinates)

# for text in acad.iter_objects(['Text']):
#     print('text: %s at: %s' % (text.TextString, text.InsertionPoint))



#%%
# from pyautocad import Autocad, APoint
# import win32com.client

# AutoCAD = win32com.client.Dispatch("AutoCAD.Application")
# acad = Autocad(create_if_not_exists = False)

# p1 = APoint(0, 0)
# p2 = APoint(50, 25)

# for i in range(5):
#     text = acad.model.AddText('Hi %s!' % i, p1, 2.5)
#     acad.model.AddLine(p1, p2)
#     acad.model.AddCircle(p1, 10)
#     p1.y += 10

# dp = APoint(10, 0)
# for text in acad.iter_objects(['Hi']):
#     print('text: %s at: %s' % (text.TextString, text.InsertionPoint))
#     text.InsertionPoint = APoint(text.InsertionPoint) + dp

# for line in acad.iter_objects(dont_cast = True):
#     print(line.ObjectName)

# AutoCAD.Visible = True

#%%
import comtypes.client

acad = comtypes.client.GetActiveObject("AutoCAD.Application")
    # 获取正在运行的AutoCAD应用程序对象
doc = acad.ActiveDocument
    # 获取当前文件
ms = doc.ModelSpace
    # 获取当前文件的模型空间
    
doc.Utility.Prompt("Hello! AutoCAD from comtypes.")
print(doc.Name)


#%%
import pythoncom
import win32com.client
import numpy as np
from array import array
 
acad = win32com.client.Dispatch("AutoCAD.Application")
doc = acad.ActiveDocument
mp = doc.ModelSpace

LayerObj = acad.ActiveDocument.Layers.Add("HIT_Layer")
p1 = array('d', [0, 0, 0])
p2 = array('d', [100, 0, 0])
line = mp.AddLine(p1, p2)

#%%
