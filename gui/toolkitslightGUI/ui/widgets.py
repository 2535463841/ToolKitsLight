import os
import queue
import re
import functools

from typing import SupportsComplex, Text
from oslo_log import log

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QtFatalMsg

from toolkitslight import utils
import toolkitslight


LOG = log.getLogger(__name__)

home_dir = os.path.dirname(os.path.dirname(__file__))


class QLineEditWithDrogEvent(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mime_data = None
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.new_context_list = queue.Queue()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        mime_data = e.mimeData()
        text = mime_data.text()
        import threading
        threads = []
        for line in text.split('\n'):
            if not line:
                continue
            thread = threading.Thread(target=self.get_file_md5sum_info,
                             args=(line,))
            thread.setDaemon(True)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        while True:
            if self.new_context_list.empty():
                break
            context = self.new_context_list.get()
            self.append(context)
        end_str_num = int(self.width() / 8) - 1
        self.append('=' * end_str_num)

    def get_file_md5sum_info(self, text):
        matched = re.match(r'file:///(.+)', text)
        if not matched:
            LOG.error('error, not match')
            return ''
        file_path = matched.group(1)
        md5sum_value, sha1_value = utils.md5sum_file(
            file_path, read_bytes=102400)
        context = '文件路径: %s\n' \
                  'MD5  值: %s\n' \
                  'SHA1 值: %s\n' % (file_path, md5sum_value, sha1_value)
        self.new_context_list.put(context)
        return context


class WidgetWithLayout(QtWidgets.QWidget):

    def __init__(self, layout, qss_file=None):
        super(WidgetWithLayout, self).__init__()
        self._layout = layout
        self.qss_file = qss_file
        self.setLayout(self._layout)

        if self.qss_file:
            self.setStyleSheet(self.load_qss())

    def add_widget(self, *args, **kwargs):
        self._layout.addWidget(*args, **kwargs)
        return self

    def addHSpacer(self):
        # 水平Spacer
        self._layout.addItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))

    def addVSpacer(self):
        # 垂直Spacer
        self._layout.addItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding))

    @staticmethod
    def load_qss(file_name):
        file_path = os.path.join(home_dir,
                                 'qss', file_name)
        if not os.path.exists(file_path):
            LOG.error('qss file not found: %s', file_path)
            return ''
        else:
            with open(file_path) as f:
                file_content = f.read()
            return file_content

    @staticmethod
    def load_icon(file_name):
        file_path = os.path.join('qss', file_name)
        if not os.path.exists(file_path):
            LOG.error('icon not found: %s', file_path)
            file_path = os.path.join('qss', 'Error.png')
        return QtGui.QIcon(file_path)


class Md5sumWidget(WidgetWithLayout):

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel('计算MD5值'))
        
        self.label_tooltip = QtWidgets.QLabel('请将文件拖动到如下区域')
        self.button_clean = QtWidgets.QPushButton('清空')
        self.texteditor_md4sum = QLineEditWithDrogEvent()
        
        self.add_widget(self.button_clean)
        self.add_widget(self.label_tooltip)
        self.add_widget(self.texteditor_md4sum)

        self.button_clean.clicked.connect(self.clean_texteditor)

    def clean_texteditor(self):
        self.texteditor_md4sum.clear()


class QrCodeWidget(WidgetWithLayout):
    NAME = '二维码生成器'

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel(self.NAME))
        self._layout.addItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))
        self.texteditor_content = QtWidgets.QTextEdit('请输入需要生成的内容')
        self.texteditor_content.setFixedHeight(100)
        self.label_qrcode = QtWidgets.QLabel('显示二维码')
        self.label_qrcode.setFixedHeight(600)

        self.add_widget(self.texteditor_content)
        self.add_widget(self.label_qrcode)

        self.texteditor_content.textChanged.connect(self.texteditor_changed)

    def texteditor_changed(self):
        self.create_qrcode()

    def create_qrcode(self):
        content = self.texteditor_content.toPlainText()
        save_dir = os.path.join('.', 'tmp')
        save_file = os.path.join(save_dir, 'qrcode.jpg')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        elif os.path.exists(save_file):
            os.remove(save_file)
        utils.create_qrcode(content, output=save_file)
        if os.path.exists(save_file):
            self.label_qrcode.setPixmap(QtGui.QPixmap(save_file))
        else:
            LOG.error('create qrcode file failed')


class WidgetBaseConverter(WidgetWithLayout):
    NAME = '进制转换器'

    def __init__(self):
        super().__init__(QtWidgets.QVBoxLayout())
        self.add_widget(QtWidgets.QLabel(self.NAME))
        self._layout.addItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))
        self.data = 0
        for i in [2, 8, 10, 16]:
            setattr(self, 'textedit_%s' % i, QtWidgets.QTextEdit())
            textedit = getattr(self, 'textedit_%s' % i)
            textedit.setFixedHeight(40)
            textedit.setStyleSheet(self.load_qss('app.qss') )
            # textedit.setProperty('level', 'error')
            self.add_widget(QtWidgets.QLabel('%s进制' % i))
            self.add_widget(textedit) 
            textedit.textChanged.connect(
                functools.partial(self.convert, textedit, i)
            )
        self._layout.addStretch()

    def convert(self, texteditor: QtWidgets.QTextEdit, num):
        try:
            text = texteditor.toPlainText().strip()
            if not text:
                text = '0'
            texteditor.setProperty('level', 'default')
            texteditor.setStyleSheet(self.load_qss('app.qss') )
            if int(text, num) == self.data:
                return
            self.data = int(text, num)
            for i in [2, 8, 10, 16]:
                editor = getattr(self, 'textedit_%s' % i)
                if editor == texteditor:
                    continue
                else:
                    editor.setText(
                        utils.convert_base(self.data, num, target_base=i)
                    )
        except ValueError as e:
            self.data = 0
            LOG.error(e)
            texteditor.setProperty('level', 'error')
            texteditor.setStyleSheet(self.load_qss('app.qss') )
            texteditor.update()


class WidgetDateFormater(WidgetWithLayout):
    NAME = '时间格式化'
    DEFAULT_FORMAT = 'YYYY-mm-dd HH:MM:SS'

    def __init__(self):
        super().__init__(QtWidgets.QVBoxLayout())
        self.add_widget(QtWidgets.QLabel(self.NAME))
        self.addHSpacer()

        self.add_widget(QtWidgets.QLabel('时间戳'))
        self.lineedit_timestamp = QtWidgets.QLineEdit()
        # self.lineedit_timestamp.
        self.add_widget(self.lineedit_timestamp)
        
        self.add_widget(QtWidgets.QLabel('格式化: ' + self.DEFAULT_FORMAT))
        self.lineedit_format = QtWidgets.QLineEdit()
        self.add_widget(self.lineedit_format)
        self._layout.addStretch()

        self.lineedit_timestamp.textChanged.connect(self.format)
        self.lineedit_format.textChanged.connect(self.conver_dateformat)


    def format(self):
        """
        %a 星期的简写。如 星期三为Web
        %A 星期的全写。如 星期三为Wednesday
        %b 月份的简写。如4月份为Apr
        %B 月份的全写。如4月份为April
        %c:  日期时间的字符串表示。（如： 04/07/10 10:43:39）
        %d:  日在这个月中的天数（是这个月的第几天）
        %f:  微秒（范围[0,999999]）
        %H:  小时（24小时制，[0, 23]）
        %I:  小时（12小时制，[0, 11]）
        %j:  日在年中的天数 [001,366]（是当年的第几天）
        %m:  月份（[01,12]）
        %M:  分钟（[00,59]）
        %p:  AM或者PM
        %S:  秒（范围为[00,61]，为什么不是[00, 59]，参考python手册~_~）
        %U:  周在当年的周数当年的第几周），星期天作为周的第一天
        %w:  今天在这周的天数，范围为[0, 6]，6表示星期天
        %W:  周在当年的周数（是当年的第几周），星期一作为周的第一天
        %x:  日期字符串（如：04/07/10）
        %X:  时间字符串（如：10:43:39）
        %y:  2个数字表示的年份
        %Y:  4个数字表示的年份
        %z:  与utc时间的间隔 （如果是本地时间，返回空字符串）
        %Z:  时区名称（如果是本地时间，返回空字符串）
        %%:  %% => %
        """
        timestamp = self.lineedit_timestamp.text().strip()
        if timestamp == '':
            return
        try:
            timestamp = float(timestamp)
            date_str = utils.format_timestamp(timestamp)
            if self.lineedit_format.text() != date_str:
                self.lineedit_format.setText(utils.format_timestamp(timestamp))
        except Exception as e:
            LOG.exception(e)

    def conver_dateformat(self):
        date_str = self.lineedit_format.text().strip()
        if date_str == '':
            return
        try:
            self.lineedit_timestamp.setText(
                str(utils.format_datetime(date_str))
            )
        except Exception as e:
            LOG.exception(e)


class WidgetFTPD(WidgetWithLayout):

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel('简单文件服务器'))


class WidgetSSHD(WidgetWithLayout):

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel('简单sshd服务'))


class WidgetRCP(WidgetWithLayout):

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel('远程文件拷贝'))
