import logging
from logging import handlers

_DEFAULT_LEVEL = logging.INFO
_DEFAULT_FORMAT = '%(asctime)s %(levelname)s %(name)s:%(lineno)s %(message)s'
_DEFAULT_FILE = None
_DEFAULT_MAX_BYTES = None
_DEFAULT_BACKUP_COUNT = None

_LOGGER = set([])

def set_default(level=None, filename=None, max_mb=None, backup_count=None):
    global _DEFAULT_LEVEL
    global _DEFAULT_FILE, _DEFAULT_MAX_BYTES, _DEFAULT_BACKUP_COUNT
    _DEFAULT_LEVEL = level or logging.INFO
    _DEFAULT_FILE = filename
    _DEFAULT_MAX_BYTES = 1024 * 1024 * max_mb if max_mb else 0
    _DEFAULT_BACKUP_COUNT = backup_count or 0

    for name in _LOGGER:
        logger = logging.getLogger(name)
        logger.setLevel(_DEFAULT_LEVEL)
        if not logger.handlers:
            logger.addHandler(get_handler())
        else:
            logger.handlers[0] = get_handler()


def load_config(config_file):
    logging.config.fileConfig(config_file)


def get_handler():
    if _DEFAULT_FILE:
        handler = handlers.RotatingFileHandler(
            _DEFAULT_FILE, mode='a',
            maxBytes=_DEFAULT_MAX_BYTES,
            backupCount=_DEFAULT_BACKUP_COUNT)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    return handler


def getLogger(name):
    """
    >>> set_default(filename='test.log', level=logging.DEBUG)
    >>> LOG = getLogger(__name__)
    >>> LOG.debug('debug')
    >>> LOG.info('info' * 100)
    >>> LOG.error('error')
    """
    global _LOGGER
    _LOGGER.add(name)
    logger = logging.getLogger(name)
    logger.setLevel(_DEFAULT_LEVEL)
    if not logger.handlers:
        handler = get_handler()
        logger.addHandler(handler)
    return logger
