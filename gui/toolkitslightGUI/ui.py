# -*- coding: utf-8 -*-

import logging
import sys
from PyQt5 import QtWidgets

from ui import window

from oslo_log import log
from oslo_config import cfg

LOG = logging.getLogger(__name__)


def main():
    log.register_options(cfg.CONF)
    cfg.CONF(sys.argv[1:], project='toolkitlight')
    log.setup(cfg.CONF, 'toolkitlight')

    app = QtWidgets.QApplication(sys.argv)
    main_window = window.MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
