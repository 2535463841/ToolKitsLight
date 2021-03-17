from abc import abstractmethod
import argparse

class Argument:

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs


class CliBase:
    NAME = ''
    ARGUMENTS = []

    def __call__(self, args):
        raise NotImplementedError()

class SubCliParser:

    def __init__(self, title) -> None:
        self.parser = argparse.ArgumentParser()
        self.sub_parser = self.parser.add_subparsers(title=title)

    def parse_args(self):
        return self.parser.parse_args()

    def register_cli(self, cls):
        cli_parser = self.sub_parser.add_parser(cls.NAME)
        for argument in cls.ARGUMENTS:
            cli_parser.add_argument(*argument.args, **argument.kwargs)
        cli_parser.set_defaults(cli=cls)
        return cli_parser
    
    def print_usage(self):
        self.parser.print_usage()

    def print_help(self):
        self.parser.print_help()


def get_sub_cli_parser(title):
    return SubCliParser(title)

def register_cli(sub_cli_parser):

    def wrapper(cls):
        cli_parser = sub_cli_parser.sub_parser.add_parser(cls.NAME)
        for argument in cls.ARGUMENTS:
            cli_parser.add_argument(*argument.args, **argument.kwargs)
        cli_parser.set_defaults(cli=cls)
        return cls

    return wrapper

