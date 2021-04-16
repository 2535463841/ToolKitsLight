import logging
from logging import handlers

_DEFAULT_LEVEL = logging.INFO
_DEFAULT_FORMAT = '%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'
_DEFAULT_FILE = None
_DEFAULT_MAX_BYTES = None
_DEFAULT_BACKUP_COUNT = None


def set_default(level=None, filename=None, max_mb=None, backup_count=None):
    global _DEFAULT_LEVEL
    global _DEFAULT_FILE, _DEFAULT_MAX_BYTES, _DEFAULT_BACKUP_COUNT
    _DEFAULT_LEVEL = level or logging.INFO
    _DEFAULT_FILE = filename
    _DEFAULT_MAX_BYTES = 1024 * 1024 * max_mb if max_mb else 0
    _DEFAULT_BACKUP_COUNT = backup_count or 0


def load_config(config_file):
    logging.config.fileConfig(config_file)


def getLogger(name):
    """
    >>> set_default(filename='test.log', level=logging.DEBUG)
    >>> LOG = getLogger(__name__)
    >>> LOG.debug('debug')
    >>> LOG.info('info' * 100)
    >>> LOG.error('error')
    """
    logger = logging.getLogger(name)
    logger.setLevel(_DEFAULT_LEVEL)
    if not logger.handlers:
        if _DEFAULT_FILE:
            handler = logging.FileHandler(_DEFAULT_FILE, mode='a')
            handler = handlers.RotatingFileHandler(
                _DEFAULT_FILE, mode='a',
                maxBytes=_DEFAULT_MAX_BYTES,
                backupCount=_DEFAULT_BACKUP_COUNT)
            handler.setLevel(logging.DEBUG)
        else:
            handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        logger.addHandler(handler)
    return logger
