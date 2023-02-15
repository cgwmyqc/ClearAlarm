import requests
import json

"""
1、登陆后从 https://cmsp.evsmc.cn/sysSafeMessage/enterpriseAlarm?num=c 以POST方法获取json数据，需携带cookie。
2、获取后将json数据以warningInfo.json的文件名保存至项目目录。
3、依赖requests库
"""

# 直接获取JSON数据的后台服务器地址（包含全部车辆报警信息）
url = "https://cmsp.evsmc.cn/sysSafeMessage/enterpriseAlarm?num=c"

# 请求信息Header伪装
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}

# request携带的登陆cookie
cookie = {"WEB_SESSION": "6DE126FB19213CC6AB7B4646C723D9D3"}

# 报警信息存储文件Json格式，文件目录为项目所在目录
fileName = "warningInfo.json"

# 通过数据包分析请求为post形式，需要携带cookie否则无返回数据，返回的response为<class 'requests.models.Response'>数据类型。
# response.status_code: 返回响应状态码
# response.headers: 返回请求头信息
# response.text: 返回响应的主体内容（纯str格式）
response = requests.post(url=url, headers=header, cookies=cookie)

# 通过response.json()方法，将response.text转换为python dict(字典)数据格式，.json()相当于json.loads(response.text)
# 拿到dict数据类型后再用dumps(dict)或者dump(dict)方法，将dict数据转化为json格式数据。
# 因为python内置数据类型中没有json格式，所以type(json数据)也是str
info = response.json()

# 以写模式打开fileName(warningInfo.json)，
with open(fileName, 'w', encoding='utf-8') as f:
    json.dump(info, fp=f, ensure_ascii=False)       # 方法1：使用dump方法将，dict数据写入。
    # f.write(response.text)                        # 方法2：使用write方法，将str数据写入。

print("Done!")