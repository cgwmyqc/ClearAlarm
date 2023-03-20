# -- coding:UTF-8 --
import os
import random
from datetime import datetime, timedelta
import requests
import json
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.drawing.image import Image     # 使用Image类需要安装Pillow库
from win32com.client import DispatchEx
# 在多线程中使用win32com，需配合使用pythoncom，否则程序会闪退，并报"进程已结束,退出代码-1073740791 (0xC0000409)"。
# 打开运行的编辑配置，勾选"模拟输出控制台的终端"，会看到pywintypes.com_error: (-2147221008, '尚未调用 CoInitialize。', None, None)错误。
import pythoncom
from PyQt5.QtCore import QThread


def get_json(ui_cookie):

    """
    1、登陆后从 https://cmsp.evsmc.cn/sysSafeMessage/enterpriseAlarm?num=c 以POST方法获取json数据，需携带cookie。
    2、获取后将json数据以warningInfo.json的文件名保存至项目目录。
    3、依赖requests库
    """

    # 直接获取JSON数据的后台服务器地址（包含全部车辆报警信息）
    url = "https://cmsp.evsmc.cn/sysSafeMessage/enterpriseAlarm?num=c"

    # 请求信息Header伪装
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}

    # request携带的登陆cookie
    cookie = {"WEB_SESSION": ui_cookie}

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
        json.dump(info,fp=f, ensure_ascii=False)        # 方法1：使用dump方法将，dict数据写入。
        # f.write(response.text)                        # 方法2：使用write方法，将str数据写入。用方法2就无需再将response.json()处理了。

    print("Done!")


def modify_excel(ui_cookie):

    """
    1、从json数据筛选出未处理的报警数据，将未处理的数据对象存入untreatedList，随后遍历untreatedList，取到json中需要的数据。
    2、利用openpyxl库对报警说明模板documentationTemplate.xlsx进行修改，然后保存，文件名格式为（id-vin+国标三级报警故障处理+json中的alarmTime）。
    3、利用win32库，将输出的excel转化为pdf。
    """

    # 项目目录
    basePath = os.path.abspath(".")

    # 在excel文件夹以及pdf文件夹中生成以当前日期命名的文件夹
    today = datetime.now()
    todayFileName = today.strftime("%Y-%m-%d-%H-%M-%S")
    os.mkdir(path=os.path.join(basePath, "excel", todayFileName))
    os.mkdir(path=os.path.join(basePath, "pdf", todayFileName))

    # 读出报警总数
    with open('warningInfo.json', 'r', encoding='utf-8') as f:
        warningInfo = json.load(f)

    # 获取总数量
    allWarningAmount = warningInfo['total']
    print("总数量：", allWarningAmount)

    # 读出报警分类json
    with open('warningClassification.json', 'r', encoding='utf-8') as c:
        warningClassification = json.load(c)

    # 从json中获取未处理三级报警数据（state:0-未处理 14-已处理; type:1-三级报警）
    # 将未处理的数据的存入untreatedList
    untreatedList = []
    for item in warningInfo['rows']:
        if item['state'] == 0 and item['type'] == 1:
            untreatedList.append(item)
    print("未处理：",len(untreatedList))

    # 以下是利用openpyxl库生成表格
    # 给指定单元格赋值
    for untreatedItem in untreatedList:

        # 检测故障发生时间，只处理距离当日2天以上的故障（以后可屏蔽掉此功能）
        wTime = datetime.strptime(untreatedItem['alarmTime'], "%Y%m%d%H%M%S")
        e = today-wTime
        if e.days <= 2:
            continue

        # 获取工作簿对象, 打开documentationTemplate.xlsx文件
        workbook = load_workbook(os.path.join(basePath, "excel", "template", "documentationTemplate.xlsx"))

        # 激活工作簿，获取当前工作页对象
        worksheet = workbook.active

        # 故障描述-故障分类-故障处理方式的索引
        warningIndex = 0

        for description in warningClassification['description']:                                                                   # 遍历warningClassification.json中故障描述

            if description in untreatedItem['message']:                                                                            # 查看标准故障描述是否出现在出处理报警数据的message中

                # 表头报警分类
                title = "报警分类：" + warningClassification['classification'][warningIndex]                                         # [输出至excel]拼接显示故障分类的title（eg."报警分类：单车偶发故障报警"）

                # 报警分类
                classAndDesc = warningClassification['classification'][warningIndex]+"-"+description                               # [输出至excel]拼接显示故障分类和故障描述（ec."单车偶发故障报警-电池单体一致性差"）

                # 故障周期（故障报警时间）
                warningTimeStrFromJson = untreatedItem['alarmTime']                                                                 # 获取json中alarmTime时间字符串
                warningTimeClass = datetime.strptime(warningTimeStrFromJson, "%Y%m%d%H%M%S")                                        # json中时间格式是20220628131113，利用datetime模块的strptime()方法将此种格式识别成datetime对象
                warningTime = datetime.strftime(warningTimeClass, "%Y{y}%m{m}%d{d}").format(y='年', m='月', d='日')                  # [输出至excel]拿到2022-06-28这种格式的字符串

                # 处理周期（处理开始时间~处理结束时间）
                treatStartTimeClass = warningTimeClass + timedelta(days=random.randint(1,2))                                       # 处理开始时间datetime类，报警时间+随机数（1-3）
                treatStopTimeClass = treatStartTimeClass + timedelta(days=random.randint(2,4))                                    # 处理结束时间datetime类，开始时间+随机数（10-15）
                treatStartTime = datetime.strftime(treatStartTimeClass, "%Y{y}%m{m}%d{d}").format(y='年', m='月', d='日')            # 处理开始时间str
                treatStopTime = datetime.strftime(treatStopTimeClass, "%Y{y}%m{m}%d{d}").format(y='年', m='月', d='日')              # 处理结束时间str
                treatPeriod = treatStartTime + "～" + treatStopTime                                                                  # [输出至excel]处理周期字符串

                # 车辆VIN
                vin = untreatedItem['vin']                                                                                          # [输出至excel]车辆vin

                # 报警原因及处理方案
                reasonAndTreatment = "故障原因：" + "\n" + "    " \
                                     + warningClassification['reason'][warningIndex]+"\n"\
                                     + "处理方案：" + "\n"+"    "\
                                     + warningClassification['treatment'][warningIndex]

                # 向EXCEL中写入数据
                worksheet['A5'] = title
                worksheet['A7'] = classAndDesc
                worksheet['A7'].alignment = Alignment(horizontal='center', vertical='center', wrapText=True)
                worksheet['D7'] = warningTime
                worksheet['G7'] = treatPeriod
                worksheet['G7'].alignment = Alignment(horizontal='center', vertical='center', wrapText=True)
                worksheet['A10'] = vin
                worksheet['A25'] = reasonAndTreatment
                worksheet['A25'].alignment = Alignment(horizontal='left', vertical='center', wrapText=True)
                worksheet['A55'] = treatStartTime
                worksheet['A55'].alignment = Alignment(horizontal='right', vertical='center', wrapText=True)

                # 向指定单元格插入图片，Image(图片路径)，add_image(图片，锚点), Image模块依赖与Pillow库，使用前徐安装
                img = Image(os.path.join(os.path.abspath("."), "excel", "template", "stamp.png"))
                img.width, img.height = (180, 180)
                worksheet.add_image(img, "G48")

                # 分析网页提交的form表单数据(<input type="radio" name= "alarm" value="x">)，
                # 单车偶发故障报警：value = 0; 多车偶发故障报警：value = 1; 车辆设计原因报警：value=2; 电池故障报警：value=5; 车辆部件导致的故障报警：value=4; 其他原因：value=3
                # 海马的故障类型中无：电池故障报警、车辆部件导致的故障报警
                warningItem = {"单车偶发故障报警":"0", "多车偶发故障报警":"1", "车辆设计原因报警":"2", "电池故障报警":"5", "车辆部件导致的故障报警":"4", "其他原因":"3"}
                value = warningItem[warningClassification['classification'][warningIndex]]

                # 在excel文件夹中的当前日期文件夹中生成excel，然后保存表格
                excelFileName = untreatedItem['id'] + "-" + value + "-" + untreatedItem['vin'] + "国标三级报警故障处理" + untreatedItem['alarmTime'] + ".xlsx"
                workbook.save(filename=os.path.join(basePath, "excel", todayFileName, excelFileName))

                # 使用win32com库将excel输出为pdf
                pdfFileName = untreatedItem['id'] + "-" + value + "-" + untreatedItem['vin'] + "国标三级报警故障处理" + untreatedItem['alarmTime'] + ".pdf"
                # 若不使用CoInitialize:在多线程中使用win32com，需配合使用pythoncom，否则程序会闪退，并报"进程已结束,退出代码-1073740791 (0xC0000409)"。
                # 若不使用CoInitialize:打开运行的编辑配置，勾选"模拟输出控制台的终端"，会看到pywintypes.com_error: (-2147221008, '尚未调用 CoInitialize。', None, None)错误。
                # 在单线程程序中，CoInitialize()和CoUninitialize()可以不写，多线程里面使用win32com调用com组件的时候，需要用pythoncom.CoInitialize初始化一下。最后还需要用pythoncom.CoUninitialize释放资源。
                # Coinitialize是Windows提供的API函数，用来告诉Windows系统单独一个线程创建COM对象。也就是说我这个多线程的脚本里面的线程和这个COM对象的线程创建一个套间，令其可以正常关联和执行。
                pythoncom.CoInitialize()
                excelApp = DispatchEx("Excel.Application")
                excelApp.Visible = False    # 设置excel不可见，即相当于后台运行。
                excelApp.DisplayAlerts = 0
                books = excelApp.Workbooks.Open(os.path.join(basePath, "excel", todayFileName, excelFileName), False)
                books.ExportAsFixedFormat(0, os.path.join(os.path.abspath("."), "pdf", todayFileName, pdfFileName))
                books.Close(False)
                excelApp.Quit()
                del(excelApp)               # 在excelApp.Quit()执行后，发现excel进程并没有退出，会造成生成的临时excel文件无法删除的现象，使用del命令删除excelApp变量后，才能实现excel软件的退出。
                pythoncom.CoUninitialize()  # 配合CoInitialize使用释放资源

                # 将pdf边生成边上传功能
                # 获取新生成的PDF文件的路径
                pdfPath = os.path.join(os.path.abspath("."), "pdf", todayFileName, pdfFileName)
                # 组织需要上传至服务器的json数据，name是从HTML网页源码中的input框的name
                data = {"idsStr": untreatedItem['id'], "alarm":value}
                # 调用upload_file方法进行上传
                upload_file(data, pdfPath, ui_cookie)

            # 索引加1
            warningIndex += 1

            # if warningIndex >= len(warningClassification['description']):
            #     print(untreatedItem['vin'], "未匹配上故障描述，请更新warningClassification.json文件文件或手动输入！")
            #     with open("error.txt", 'w', encoding='utf-8') as error:
            #         errorInfo = "id:"+untreatedItem['id'] + " vin:" + untreatedItem['vin'] + " time:" + untreatedItem['alarmTime'] + 'description:' + untreatedItem['message'] + '\n'
            #         error.write(errorInfo)


# 此功能暂时不可用，遍历文件夹内的pdf可能有错误因为又增加了子文件夹需要修改
def upload_from_dir(ui_cookie):
    """
    1、遍历指定pdf文件夹内的所有pdf文件；
    2、获取文件名称中的报警id
    3、根据不同id，向不同的Request URL提交文件, 具体方法说明见uploadPDF
    :return:
    """

    # POST请求提交地址
    uploadURL = "https://cmsp.evsmc.cn/sysSafeMessage/alarmSort"

    # POST请求的headers
    uploadHeader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    # cookie
    cookie = {"WEB_SESSION": ui_cookie}

    # 遍历生成的pdf文件（文件名的格式为：id+报警分类+vin+"国标三级报警故障处理+报警日期"）
    for root, dirs, files in os.walk(os.path.join(os.path.abspath("."), "pdf", "2023-02-06")):

        for name in files:

            # 分割pdf文件名，获取报警id及alarm分类
            fileNameSplitList = name.split("-")

            # 获取需上传的pdf文件的绝对路径
            filePath = os.path.join(root, name)

            # 需request上传文件的
            files = {"file": open(filePath, 'rb')}

            # 建立传向服务器的json格式的数据（id + alarm value）
            datas = {"idsStr": fileNameSplitList[0], "alarm":fileNameSplitList[1]}

            # POST方法将pdf文件（报警处理文档）、报警id、alarm value
            response = requests.post(url=uploadURL, headers=uploadHeader, cookies=cookie, data=datas, files=files)
            print(response)

            # 设置延迟时间, 采用QT自己的延迟函数，防止界面主线程在延迟的时候阻塞卡死
            QThread.sleep(20)


def upload_file(data, file_path, ui_cookie):
    """
    1、
    在 modify_excel()中引用此方法，
    :param ui_cookie:从ui界面中接收的用户设置的cookie值
    :param data:一个字典{id,alarm_value}，里面存储的是报警项id和报警类型
    :param file_path:新生成的pdf所在路径
    :return:无
    """
    # 延迟5s，等待生成pdf,采用QT自己的延迟函数，防止界面主线程在延迟的时候阻塞卡死
    QThread.sleep(5)

    # POST请求提交地址
    uploadURL = "https://cmsp.evsmc.cn/sysSafeMessage/alarmSort"

    # POST请求的headers
    uploadHeader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    # cookie
    cookie = {"WEB_SESSION": ui_cookie}

    # 需request上传文件的
    files = {"file": open(file_path, 'rb')}

    # POST方法将pdf文件（报警处理文档）、报警id、alarm value
    response = requests.post(url=uploadURL, headers=uploadHeader, cookies=cookie, data=data, files=files)
    print("已上传：",file_path, response, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # 延迟10-15s,采用QT自己的延迟函数，防止界面主线程在延迟的时候阻塞卡死.
    QThread.sleep(random.randint(5,10))


# if __name__ == "__main__":
#
#     # cookie需根据实际情况填写
#     get_json("6DE126FB19213CC6AB7B4646C723D9D3")
#
#     modify_excel("6DE126FB19213CC6AB7B4646C723D9D3")
