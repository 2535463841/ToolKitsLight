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

    def __init__(self):
        super().__init__(QtWidgets.QGridLayout())
        self.add_widget(QtWidgets.QLabel('二维码生成器'))

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
    def __init__(self):
        super().__init__(QtWidgets.QVBoxLayout())
        self.add_widget(QtWidgets.QLabel('进制转换器'))
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
            print('xxxxxxxxxx')
            
        except ValueError as e:
            self.data = 0
            LOG.error(e)
            # texteditor.setStyleSheet('QTextEdit[class="error"] { color: red }')
            texteditor.setProperty('level', 'error')
            texteditor.setStyleSheet(self.load_qss('app.qss') )
            # texteditor.
            texteditor.update()



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
