"""
    检测日期间隔
    日期的加减法
"""

from datetime import datetime


timeStr = "20230201082400"
time1 = datetime.strptime(timeStr, "%Y%m%d%H%M%S")
time2 = datetime.now()
e = time2-time1
print(e)                # 间隔时间
print(e.days < 6)       # 间隔天数
