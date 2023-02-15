## 1、Description:

​		According alarm info generate Excel and convert to PDF then upload pdf to server automatical.



## 2、Environment:

​		Python 3.6.3 (v3.6.3:2c5fed8, Oct  3 2017, 18:11:49) 



## 3、网络通信分析

##### 		3.1、request与response分析

​		通过网络数据分析，发现了一个响应时间长达9000ms的请求，该请求方式为POST，需携带cookie，通过查看浏览器的Response，发现该请求返回的数据是一个超大Json数据包，数据包内携带全部所需的报警信息。

​		**request分析：**

![request Header](.\img\2-网络通信分析-获取json数据.png)

​		**response分析：**

![](.\img\2-网络通信分析-获取json数据2.png)



##### 		3.2、requests库模拟浏览器发起请求并将获取的json数据

​		利用requests库模拟发送请求，利用json库处理返回的数据，并保存在warningInfo.json中。

​		**Json库说明：**

- dumps()：将dict数据转为json数据。
- loads()：将json数据转为dict数据。

- load()：读取 **json文件**，转成dict数据。
- dump()：将dict数据，转成json后写入 **json文件**。

​		**总结：**不带s的方法操作文件**从文件读或写入文件**，带s的方法仅操作数据返回数据

```python
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

    # 请求为post形式，需要携带cookie否则无返回数据，返回的response为<class 'requests.models.Response'>数据类型。
    # response.status_code: 返回响应状态码（200）
    # response.headers: 返回请求头信息
    # response.text: 返回响应的主体内容（纯str格式）
    response = requests.post(url=url, headers=header, cookies=cookie)

    # 通过response.json()方法，将response.text转换为python dict(字典)数据格式，.json()相当于json.loads(response.text)
    # 拿到dict数据类型后再用dumps(dict)或者dump(dict)方法，将dict数据转化为json格式数据(dumps)或json文件(d)。
    # 因为python内置数据类型中没有json格式，所以type(json数据)也是str
    info = response.json()

    # 以写模式打开fileName(warningInfo.json)，
    with open(fileName, 'w', encoding='utf-8') as f:
        json.dump(info,fp=f, ensure_ascii=False)        # 方法1：使用dump方法将，dict数据写入。
        # f.write(response.text)                        # 方法2：使用write方法，将str数据写入。用方法2就无需再将response.json()处理了。

    print("Done!")

```



##### 		3.3、requests库提交表单信息及本机文件

通过网路网络分析，向服务器提交数据的HTML表单及数据格式如下：

- **form**表单的id为ff，通过最后的submit按钮提交，method为POST。

- **form**表单中一共有3种input框需要提交：
  - 1、携带报警id的input框，`{name="idsStr", value=id值}`
  - 2、报警类型单选input框，`{name="alarm", value=报警类型值}`
  - 3、文件提交input框，`{name='file'}`

- 需特别关注form表单中input框的name字段，name字段决定了表单被传送到服务器上的变量名称。如果你想模拟表单提交数据的行为，你就需要保证你提交的字典`{"name1":"value1", "name2":"value2",....}`name称与HTML代码中name字段名称是一一对应的。

![](img\2-网络通信分析-向服务器提交数据.png)



向服务器提交数据的JavaScript代码分析如下：

- 提交服务器**URL：**https://cmsp.evsmc.cn/sysSafeMessage/alarmSort

![](img\2-网络通信分析-向服务器提交数据2.png)



根据上面的HTML和JavaScript代码分析，利用requests库提交数据，代码如下：

- **POST请求代码：**`requests.post(url=uploadURL, headers=uploadHeader, cookies=cookie, data=data, files=files)`
- **url、headers、cookies：**不做过多说说明，url按照网络分析中的填写即可。



根据上面分析HTML代码的**form**表单中一共有3种input框需要提交（idStr，alarm，file），其中idStr和alarm需以字典格式配置到request的data字段，file也需以字典格式（`{"file1":open(filePath1,'rb',"file2":open(filePath2,'rb',...)}`）配置在request的files字段。

- **提交数据data：**字典格式，`data = {"idsStr": untreatedItem['id'], "alarm":value}`
- **提交文件file：**字典格式，`files = {"file": open(file_path, 'rb')}`，需要将需要上传的文件以二进制只读的形式打开，即'rb'。

```python
# 一下代码再modify_excel中的末尾
# 将pdf边生成边上传功能
# 获取新生成的PDF文件的路径
pdfPath = os.path.join(os.path.abspath("."), "pdf", todayFileName, pdfFileName)

# 组织需要上传至服务器的json数据，name是从HTML网页源码中的input框的name
data = {"idsStr": untreatedItem['id'], "alarm":value}

# 调用upload_file方法进行上传
upload_file(data, pdfPath, ui_cookie)



def upload_file(data, file_path, ui_cookie):
    """
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
```



## 4、openpyxl 库 python 生成 Excel 

使用openpyxl库向excel文件中写入str和插入image的基本代码如下：

```python
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

```



## 5、win32com 库 Excel 生成 PDF

​		利用win32com库将excel生成PDF，基本代码如下，其中单线程中pythoncom.CoInitialize()/pythoncom.CoUninitialize()可以不写，**多线程中必须要使用，不写的话可能会使主进程卡死。**

```python
import os
from win32com.client import DispatchEx

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
```



另多种格式的文档转PDF网络教程如下：

<img src=".\img\3-利用win32com库将文件输出成pdf的方法.png"/>



## 6、PyQt

##### 6.1、环境配置

- **安装PyQt：**`pip install PyQt5 -i https://pypi.douban.com/simple`
- **安装QtDesigner等工具：**`pip install PyQt5-tools -i https://pypi.douban.com/simple`

- 在PyCharm中配置外部工具关联QtDesigner/PyUic/PyRcc，注意项目若使用virtualenv，请填写项目venv目录中的designer.exe路径。

- 按照下面设置完成后，既可以在pycharm中右键，直接启动QtDsigner，保存后生成ui文件，

  ![](.\img\4-PyQt-环境配置.png)

按照上面相同的方式设置PyUic和PyRcc。

![](.\img\4-PyQt-环境配置PyUic.png)



![](.\img\4-PyQt-环境配置PyRcc.png)



![](.\img\4-PyQt-使用QtDesigner.png)



##### 6.2、PyQt代码

```python
import sys

from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QSizePolicy
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QThread
from app import modify_excel, get_json


# 自定义一个窗口继承于QMainWindow
class FistTest(QMainWindow):
    def __init__(self):
        super().__init__()          # 必须重调父类的__init__方法，否则界面不显示
        self.init_ui()              # 调用自定义的创建ui页面函数
        self.set_signal_slot()      # 调用自定义函数，设置信号与槽

    # 自定义函数，创建ui界面
    def init_ui(self):
        # 设置窗口大小
        self.setMinimumSize(300, 400)
        self.setMaximumSize(300, 400)

        # 设置窗口名字
        self.setWindowTitle('ClearAlarm')

        # 设置窗口ICON
        self.setWindowIcon(QIcon("./image/maintenance.png"))

        # 创建窗口中用到的控件
        self.cookie_info = QLineEdit()                                      # cookie输入框consolas
        self.lock_cookie_btn = QPushButton('LOCK')                          # cookie锁定按钮
        self.unlock_cookie_btn = QPushButton('UNLOCK')                      # cookie解锁按钮
        self.start_upload_btn = QPushButton('START')                        # 开始上传按钮
        self.stop_upload_btn = QPushButton('STOP')                          # 停止上传按钮

        # 设置控件样式
        self.cookie_info.setStyleSheet("color: rgb(100, 100, 100);")      # 设置cookie输入框内字体的颜色，消除输入框底框
        self.cookie_info.setFont(QFont('consolas', 8, 75))      # 设置cookie输入框内字体类型，字体大小，字体粗度
        self.lock_cookie_btn.setFont(QFont('Microsoft YaHei UI', 9, 75))  # 设置LOCK按钮字体
        self.unlock_cookie_btn.setFont(QFont('Microsoft YaHei UI', 9, 75))# 设置UNLOCK按钮字体
        self.start_upload_btn.setFont(QFont('Microsoft YaHei UI', 15, 75)) # 设置START按钮字体
        self.stop_upload_btn.setFont(QFont('Microsoft YaHei UI', 15, 75))  # 设置STOP按钮字体
        self.start_upload_btn.setEnabled(False)        # START按钮起始状态为不可用（LOCK按钮锁定后START按钮激活）

        # 设置控件的尺寸控制策略（策略选择为expanding,设置为expanding后, box layout addWidget和addLayou方法的strech参数就可使用了）
        self.cookie_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.start_upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stop_upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 创建cookie锁定/解锁按钮的布局（水平布局）,加入两个按钮。
        cookie_control_btn_layout = QHBoxLayout()
        cookie_control_btn_layout.addWidget(self.lock_cookie_btn)
        cookie_control_btn_layout.addWidget(self.unlock_cookie_btn)

        # 创建总体布局（竖直布局），加入组件。各组件的尺寸控制策略setSizePolicy设置为Expanding后stretch参数方可使用,stretch为占比
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.cookie_info,stretch=6)
        vertical_layout.addLayout(cookie_control_btn_layout,stretch=14)
        vertical_layout.addWidget(self.start_upload_btn,stretch=40)
        vertical_layout.addWidget(self.stop_upload_btn, stretch=40)

        # 创建一个QWidget对象,用这个对象获取布局。（不写这三行代码，只显示窗口没有控件）
        widget = QWidget(self)
        widget.setLayout(vertical_layout)
        self.setCentralWidget(widget)

    # 自定义函数，设置信号与槽
    def set_signal_slot(self):
        self.lock_cookie_btn.clicked.connect(self.cookie_info.setEnabled)           # lock按钮按下, cookie_info不可用
        self.lock_cookie_btn.clicked.connect(self.lock_cookie_btn.setEnabled)       # lock按钮按下, lock按钮锁定
        self.lock_cookie_btn.clicked.connect(self.start_upload_btn.setDisabled)     # lock按钮按下, start按钮解锁
        self.unlock_cookie_btn.clicked.connect(self.cookie_info.setDisabled)        # unlock按钮按下，cookie_info可用
        self.unlock_cookie_btn.clicked.connect(self.start_upload_btn.setEnabled)    # unlock按钮按下，START按钮锁定
        self.unlock_cookie_btn.clicked.connect(self.lock_cookie_btn.setDisabled)    # unlock按钮按下, lock按钮被锁定
        self.start_upload_btn.clicked.connect(self.start_upload_btn.setEnabled)     # START按钮按下后，START按钮不可用
        self.start_upload_btn.clicked.connect(self.unlock_cookie_btn.setEnabled)    # START按钮按下后，UNLOCK按钮不可用（防止上传过程中修改cookie）
        self.stop_upload_btn.clicked.connect(self.start_upload_btn.setDisabled)     # STOP按钮按下后，START按钮解锁
        self.stop_upload_btn.clicked.connect(self.unlock_cookie_btn.setDisabled)    # STOP按钮按下后，UNLOCK按钮解锁
        self.start_upload_btn.clicked.connect(self.start_upload_thread)             # 绑定自定义槽函数，START按钮按下后，执行start_upload_thread（开始上传线程）
        self.stop_upload_btn.clicked.connect(self.stop_upload_thread)               # 绑定自定义槽函数，STOP按钮按下后，执行stop_upload_thread（结束上传线程）

    # 启动上传线程
    def start_upload_thread(self):
        self.thread = UploadThread(self.cookie_info.text())     # 新建一个自定义上传线程类的对象，cookie_info.text()是从ui界面的QLineEdit控件接收用户输入信息，传给UploadThread的对象实例。
        self.thread.start()                                     # 调用对象的start()方法启动线程，相当于UploadThread的线程一旦CPU执行时间，就会自动去调用run方法。

    # 停止上传线程
    def stop_upload_thread(self):
        self.thread.terminate()                                 # 终止线程


# 自定义多线程类继承于QThread，多线程要使用Qt为我们提供的多线程QThread，若使用python内置多线程，会使Qt主线程阻塞，表现为主窗口卡死。
# UploadThread类的构造函数(__init__)新增一个cookie构造参数，方便从界面接收cookie数据，然后传给后台的get_json()方法和modify_excel()方法。
class UploadThread(QThread):

    def __init__(self, cookie):
        super(UploadThread, self).__init__()
        self.cookie = cookie
        self.working = True                     # 线程工作标志位

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        if self.working:
            get_json(self.cookie)
            modify_excel(self.cookie)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)            # 新建一个Qt程序
    main_window = FistTest()                # 实例化一个自定义的窗口类
    main_window.show()                      # 显示窗口
    sys.exit(app.exec_())

```



**注意：**

1、若使用`PyQt`做ui，则程序中使用`python`内置`time`模块提供的`time.sleep(sec)`方法需全部更换为`PyQt`中`QThread`模块提供的`QThread.sleep(sec)`方法。

2、使用PyQt做ui，并使用多线程时，要使用Qt提供的多线程类QThread来完成。

3、`QThead`类中`start()`方法和`run()`方法的区别：`start()`用来启动一个线程，当调用`start()`方法时，系统才会开启一个线程，通过`QThead`类中`start()`方法来启动的线程处于就绪状态（可运行状态），此时并没有运行，一旦得到CPU时间片，就自动开始执行`run()`方法。此时不需要等待`run()`方法执行完也可以继续执行下面的代码，所以也由此看出`run()`方法并没有实现多线程。`run()`方法是在本线程里的，只是线程里的一个函数,而不是多线程的。如果直接调用`run()`,其实就相当于是调用了一个普通函数而已，直接待用`run()`方法必须等待`run()`方法执行完毕才能执行下面的代码，所以执行路径还是只有一条，根本就没有线程的特征，所以在多线程执行时要使用`start()`方法而不是`run()`方法。

**另：PyQt不仅可以以自己的定义的函数作为槽函数，还可以自定义Signal函数：**

由于时间不够还没有研究，留个坑以后再研究

**例程一：**

```python
import sys
 
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMainWindow, QHBoxLayout
 
from PyQt5.QtCore import Qt, pyqtSignal
 
 
class CMainWindow(QMainWindow):
    signalTest = pyqtSignal()
    signalTest1 = pyqtSignal(str)
    signalTest2 = pyqtSignal(float, float)
 
    def __init__(self):
        super().__init__()
        # 确认PushButton设置
        btn = QPushButton("无参信号")
        btn.clicked.connect(self.buttonClicked)
        btn1 = QPushButton("单参信号")
        btn1.clicked.connect(self.buttonClicked1)
        btn2 = QPushButton('双参信号')
        btn2.clicked.connect(self.buttonClicked2)
        hBox = QHBoxLayout()
        hBox.addStretch(1)
        hBox.addWidget(btn)
        hBox.addWidget(btn1)
        hBox.addWidget(btn2)
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(hBox)
        self.signalTest.connect(self.signalNone)
        self.s.connect(self.signalOne)
        self.signalTest2.connect(self.signalTwo)
        self.setWindowTitle('pysignal的使用')
        self.show()
 
    def signalNone(self):
        print("无参信号，传来的信息")
 
    def signalOne(self, arg1):
        print("单参信号，传来的信息:", arg1)
 
    def signalTwo(self, arg1, arg2):
        print("双参信号，传来的信息:", arg1, arg2)
 
    def mousePressEvent(self, event):
        self.signalTest2.emit(event.pos().x(), event.pos().y())
 
    def buttonClicked(self):
        self.signalTest.emit()
 
    def buttonClicked1(self):
        self.signalTest1.emit("我是单参信号传来的")
 
    def buttonClicked2(self):
        self.signalTest2.emit(0, 0)
 
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = CMainWindow()
    sys.exit(app.exec_())
 
```



**例程二：**

```python
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys


class Test(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.file_list = QListWidget()
        self.btn = QPushButton('Start')
        layout = QGridLayout(self)
        layout.addWidget(self.file_list,0,0,1,2)
        layout.addWidget(self.btn,1,1)
        
        self.thread = Worker()
        self.thread.file_changed_signal.connect(self.update_file_list)
        self.btn.clicked.connect(self.thread_start)
        
    def update_file_list(self, file_inf):
        self.file_list.addItem(file_inf)
        
    def thread_start(self):
        self.btn.setEnabled(False)
        self.thread.start()
        
        
        
class Worker(QThread):
    
    file_changed_signal = pyqtSignal(str) # 信号类型：str
    
    def __init__(self, sec=0, parent=None):
        super().__init__(parent)
        self.working = True
        self.sec = sec
        
    def __del__(self):
        self.working = False
        self.wait()
        
    def run(self):
        while self.working == True:
            self.file_changed_signal.emit('当前秒数：{}'.format(self.sec))
            self.sleep(1)
            self.sec += 1
            
app = QApplication(sys.argv)
dlg = Test()
dlg.show()
sys.exit(app.exec_())
```



## 7、pyinstaller打包发布

##### 7.1、在项目的virtualenv中安装pyinstaller：

```python
pip install pyinstaller
```



##### 7.2、准备app的图标

​		若使用的是png或者jpg，可以去ico在线转换网站生成一个ico，生成大小可以选择（128*128），其他尺寸没有尝试，太小不清晰。将生成的ico存放在项目目录中（存哪都行，不影响生成）。

​		转换网站推荐：https://convertico.com/



##### 7.3、创建build目录

​		可以在项目目录中创建一个`build`文件夹，用以存放pyinstaller打包生成的两个目录`build`和`dist`。cmd进入该目录。

![](.\img\1-pyinstaller.png)



##### 7.4、打包发布

```cmd
pyinstaller -i ../image/maintenance.ico -n app -F ../ui.py		#（ui.py为主程序入口）
# 参数说明：
# -i:设定icon图标的路径
# -n:设定输出exe的名字
# -F:在dist文件夹中，打包成一个exe可执行文件,本例为(app.exe)
# -D:在dist文件夹中，会多生成一个名为app的文件夹，里面为依赖库及文件。
```

**-F 和 -D 对于移植兼容性的区别还没完全搞明白，先挖个坑以后看到了再来填。**



##### 7.5、将程序所需的资源文件考至exe可执行文件路径下

- 例如所需文件夹

- 图标图片

- 等资源文件

  若不将资源文件拷贝进来，可能遇到无法显示图标或者缺少必要文件等错误。

![](.\img\1-pyinstaller-资源文件按.png)



##### 7.6、发布注意事项

- 因为windows图标缓存原因，即使设置的-i参数，生成的图标可能还是默认图标，可以使用-n给输出文件重新起个名再重新生成一下exe，或者重新复制粘贴一下EXE，或者重启资源浏览器（explore.exe），就可以看到更换过icon的可执行文件。
- 注意软件正常运行所使用的资源文件，需要根据代码中所写的目录手动拷贝到exe相对位置。



