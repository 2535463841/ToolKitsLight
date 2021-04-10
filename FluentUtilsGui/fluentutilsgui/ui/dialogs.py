from PyQt5 import QtWidgets
from PyQt5 import QtCore


class CalendarDialog(QtWidgets.QDialog):

    def __init__(self, title="日历"):
        super().__init__()
        self.selected_date = None
        self.calendar = QtWidgets.QCalendarWidget(self)
        self.resize(300, 240)
        self.setWindowTitle(title)
        self.calendar.clicked[QtCore.QDate].connect(self.set_date)

    def set_date(self, date):
        self.selected_date = date
