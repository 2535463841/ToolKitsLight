import logging

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from ui import dialogs
from ui import widgets

import functools

LOG = logging.getLogger(__name__)


class BaseGridWindow(widgets.WidgetWithLayout):

    def __init__(self, title=None, width=None, height=None):
        super().__init__(QtWidgets.QHBoxLayout())
        self.widget_list = {}
        self.setWindowTitle(title or self.__class__.__name__)

        self.h_box = QtWidgets.QHBoxLayout()
        self.left_widget_layout = QtWidgets.QVBoxLayout()
        self.right_widget_layout = QtWidgets.QVBoxLayout()
        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setLayout(self.right_widget_layout)

        self.left_widget = QtWidgets.QWidget()
        self.left_widget.setFixedSize(140, 768)
        self.left_widget.setLayout(self.left_widget_layout)

        self.add_widget(self.left_widget)
        self.add_widget(self.right_widget)

        self.resize(width, height)
        # self.left_widget.setStyleSheet(self.load_qss('left_widget.qss'))
        # self.right_widget.setStyleSheet(self.load_qss('right_widget.qss'))
        # self.setStyleSheet(
        #     "QWidget{border: 0px}"
        #     ""
        # )

    # def _show_widget(self, widget_list, item: QtWidgets.QListWidgetItem):
    #     print(widget_list)
    #     for i in range(len(widget_list)):
    #         if i == item.listWidget().selectedIndexes()[0].row():
    #             widget_list[i].show()
    #         else:
    #             widget_list[i].hide()

    # def set_list_widget_controller(self, list_widget: QtWidgets.QListWidget,
    #                                widget_list):
    #     list_widget.itemClicked.connect(
    #         functools.partial(self._show_widget, widget_list)
    #     )


class MainWindow(BaseGridWindow):

    def __init__(self, width=800, height=10):
        super().__init__(title="FluentUtils", width=width, height=height)
        self.setGeometry(0, 0, width, height)
        self.button_coutroller = []

        self.button_system = QtWidgets.QPushButton('系统信息')
        self.button_md5sum = QtWidgets.QPushButton('MD5计算器')
        self.button_qrcode = QtWidgets.QPushButton('二维码生成器')
        self.button_base_convert = QtWidgets.QPushButton('进制转换器')
        self.button_dateformater = QtWidgets.QPushButton('时间格式化')
        self.button_password = QtWidgets.QPushButton('密码生成器')

        self.button_ftpd = QtWidgets.QPushButton('文件服务器')
        self.button_rcp = QtWidgets.QPushButton('远程文件拷贝')

        self.widget_system = widgets.WidgetSystem()
        self.widget_md5sum = widgets.Md5sumWidget()
        self.widget_qrcode = widgets.QrCodeWidget()
        self.widget_dateformter = widgets.WidgetDateFormater()
        self.widget_ftpd = widgets.WidgetFTPD()
        
        self.widget_password = widgets.WidgetRandomPassword()
        
        # self.widget_sshd = widgets.WidgetSSHD()
        self.widget_rcp = widgets.WidgetRCP()
        self.widget_base_convert = widgets.WidgetBaseConverter()

        self.register_bt_controller(self.button_system, self.widget_system)
        self.register_bt_controller(self.button_md5sum, self.widget_md5sum)
        self.register_bt_controller(self.button_qrcode, self.widget_qrcode)
        self.register_bt_controller(self.button_base_convert,
                                    self.widget_base_convert)

        self.register_bt_controller(self.button_dateformater,
                                    self.widget_dateformter)
        self.register_bt_controller(self.button_password,
                                    self.widget_password)
        self.register_bt_controller(self.button_ftpd, self.widget_ftpd)
        # self.register_bt_controller(self.button_sshd, self.widget_sshd)
        self.register_bt_controller(self.button_rcp, self.widget_rcp)

        # self.setStyleSheet(self.load_qss('app.qss'))
        # self.bt_new_project = QtWidgets.QPushButton("+新建")
        # self.projects_widget = WidgetWithLayout(QtWidgets.QGridLayout())

        # self.bt_close_left = QtWidgets.QPushButton(
        #     icon=self.load_icon('侧边栏收缩后'))
        # self.bt_close_left.setProperty('class', 'success')
        # self.bt_close_left.setFixedWidth(40)

        # self.bt_search = QtWidgets.QPushButton(
        #     icon=self.load_icon('029-放大镜'))
        # self.bt_search.setProperty('class', 'secondary')
        # self.bt_search.setFixedWidth(40)
        self.left_widget_layout.addStretch()

        # init widgets, show first and hide the others
        self.show_widget(1)

    def register_bt_controller(self, button: QtWidgets.QPushButton,
                               widget: QtWidgets.QWidget):
        def on_click_event(event):
            tmp_widget = None
            for bt, widget in self.button_coutroller:
                if button != bt:
                    widget.hide()
                    bt.setProperty('class', 'light')
                    bt.setStyleSheet(self.load_qss('app.qss'))
                else:
                    tmp_widget = widget
                    bt.setProperty('class', 'default')
                    bt.setStyleSheet(self.load_qss('app.qss'))
                    
            LOG.info('click:%s show: %s', button, widget)
            # button.remove
            tmp_widget.show()
        button.clicked.connect(on_click_event)

        button.setProperty('class', 'light')
        button.setStyleSheet(self.load_qss('app.qss'))
        self.left_widget_layout.addWidget(button)
        self.right_widget_layout.addWidget(widget)
        self.button_coutroller.append((button, widget))

    def show_widget(self, index):
        for _, widget in self.button_coutroller[:index-1]:
            widget.hide()
        for _, widget in self.button_coutroller[index:]:
            widget.hide()
        self.button_coutroller[index-1][1].show()
        bt = self.button_coutroller[index-1][0]
        bt.setProperty('class', 'default')
        bt.setStyleSheet(self.load_qss('app.qss'))
        print(bt)
