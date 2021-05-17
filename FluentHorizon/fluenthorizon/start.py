import logging

from fluentcore.common import log


def main():
    log.set_default(level=logging.DEBUG)

    import server
    http_server = server.HorizonHttpServer()
    http_server.start(debug=True)


if __name__ == '__main__':
    main()
