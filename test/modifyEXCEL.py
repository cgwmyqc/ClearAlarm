from openpyxl import *
from openpyxl.styles import Alignment
from openpyxl.drawing.image import Image
import os

# 获取工作簿对象
workbook = load_workbook(os.path.join(os.path.abspath(".."), "../excel", "template", "a.xlsx"))

# 激活工作簿，获取当前工作页对象
worksheet = workbook.active

# 获取A1的值
print(worksheet["A1"].value)

# 给指定单元格赋值
worksheet['A10'] = '故障原因：'+'\n'+'    LMVAFLEX3JA00052'
worksheet['A10'].alignment = Alignment(horizontal='left', vertical='center', wrapText=True)

# 向指定单元格插入图片，Image(图片路径)，add_image(图片，锚点), Image模块依赖与PIL库，使用前徐安装
img = Image(os.path.join(os.path.abspath(".."), "../excel", "template", "stamp.png"))
img.width, img.height = (180, 180)
worksheet.add_image(img, "G49")

# 保存表格b
workbook.save(filename="./excel/b.xlsx")


# # 重新获取获取工作簿对象
# workbook = load_workbook(os.path.join(os.path.abspath("."), "excel", "a.xlsx"))
#
# # 重新激活激活工作簿，获取当前工作页对象
# worksheet = workbook.active
#
# # 保存表格c
# worksheet['A25'] = '123'
# workbook.save(filename="./excel/c.xlsx")


