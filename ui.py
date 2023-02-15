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
        self.cookie_info = QLineEdit()                                                      # cookie输入框consolas
        self.lock_cookie_btn = QPushButton('LOCK')                                          # cookie锁定按钮
        self.unlock_cookie_btn = QPushButton('UNLOCK')                                      # cookie解锁按钮
        self.start_upload_btn = QPushButton('START')                                        # 开始上传按钮
        self.stop_upload_btn = QPushButton('STOP')                                          # 停止上传按钮

        # 设置控件样式
        self.cookie_info.setStyleSheet("color: rgb(100, 100, 100);")                        # 设置cookie输入框内字体的颜色，消除输入框底框
        self.cookie_info.setFont(QFont('consolas', 8, 75))                                  # 设置cookie输入框内字体类型，字体大小，字体粗度
        self.lock_cookie_btn.setFont(QFont('Microsoft YaHei UI', 9, 75))                    # 设置LOCK按钮字体
        self.unlock_cookie_btn.setFont(QFont('Microsoft YaHei UI', 9, 75))                  # 设置UNLOCK按钮字体
        self.start_upload_btn.setFont(QFont('Microsoft YaHei UI', 15, 75))                  # 设置START按钮字体
        self.stop_upload_btn.setFont(QFont('Microsoft YaHei UI', 15, 75))                   # 设置STOP按钮字体
        self.start_upload_btn.setEnabled(False)                                             # START按钮起始状态为不可用（LOCK按钮锁定后START按钮激活）

        # 设置控件的尺寸控制策略（策略选择为expanding,设置为expanding后, box layout addWidget和addLayout方法的stretch参数就可使用了）
        self.cookie_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.start_upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stop_upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 创建cookie锁定/解锁按钮的布局（水平布局）,加入两个按钮。
        cookie_control_btn_layout = QHBoxLayout()
        cookie_control_btn_layout.addWidget(self.lock_cookie_btn)
        cookie_control_btn_layout.addWidget(self.unlock_cookie_btn)

        # 创建总体布局（竖直布局），加入组件。各组件的尺寸控制策略setSizePolicy设置为Expanding后stretch参数方可使用，stretch为占比
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.cookie_info,stretch=6)
        vertical_layout.addLayout(cookie_control_btn_layout,stretch=14)
        vertical_layout.addWidget(self.start_upload_btn,stretch=40)
        vertical_layout.addWidget(self.stop_upload_btn, stretch=40)

        # 创建一个QWidget对象,用这个对象获取布局（不写这三行代码，只显示窗口没有控件）
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
