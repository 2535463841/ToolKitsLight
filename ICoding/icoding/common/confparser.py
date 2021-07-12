import collections
from six.moves import configparser


class ConfigParserWrapper(object):

    def __init__(self):
        self._parser = configparser.ConfigParser()
        self._defaults = None

    def defaults(self):
        if self._defaults is None:
            self._defaults =  self._parser.defaults()
        return self._defaults

    def read(self, file):
        if isinstance(file, str):
            self._parser.read(file)
        else:
            self._parser.readfp(file)

    def sections(self):
        return self._parser.sections()

    def options(self, section, ignore_default=False):
        if section == 'DEFAULT':
            return self._parser.defaults()
        options = collections.OrderedDict()
        for option in self._parser.options(section):
            value = self._parser.get(section, option)
            if ignore_default and value == self.defaults().get(option):
                continue
            options[option] = self._parser.get(section, option)
        return options