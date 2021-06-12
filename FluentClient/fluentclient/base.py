from fluentlib.common import cliparser

SUB_CLI_PARSER = cliparser.get_sub_cli_parser('fluent client commands')

BASE_ARGUMENTS = [
    cliparser.Argument('-d', '--debug',
                       action='store_true', help='show debug messages')
]
