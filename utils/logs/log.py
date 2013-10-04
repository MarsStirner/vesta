# -*- coding: utf-8 -*-
import logging
import urllib2
import socket
from utils.logs.pysimplelogs.pysimplelogs import Simplelog
from config import SIMPLELOGS_URL, DEBUG, MODULE_NAME


class SimplelogHandler(logging.Handler):

    def __init__(self, url):
        logging.Handler.__init__(self)
        self.url = url

    def emit(self, record):
        message = self.format(record)
        client = Simplelog(self.url)
        level = logging.getLevelName(self.level).lower()
        if not hasattr(client, level):
            level = 'debug'
        getattr(client, level)(MODULE_NAME, message, [MODULE_NAME])


class VestaLogger(object):

    @classmethod
    def __check_url(cls, url):
        try:
            if urllib2.urlopen(url, timeout=2).getcode() == 200:
                return True
        except urllib2.URLError, e:
            print u'Проблема с подключением к системе журналирования ({0})'.format(e)
        except socket.timeout, e:
            print u'Проблема с подключением к системе журналирования ({0})'.format(e)
        return False

    @classmethod
    def __log_except(cls, vesta_logger):
        #TODO: Нужно ли?! не будет ли зацикливания?
        if not DEBUG:
            # write to log all unhandled exceptions if not DEBUG mode
            import sys
            import traceback

            def log_except_hook(*exc_info):
                text = "".join(traceback.format_exception(*exc_info))
                vesta_logger.error("Unhandled exception: %s", text)

            sys.excepthook = log_except_hook

    @classmethod
    def get_logger(cls):
        vesta_logger = logging.getLogger(MODULE_NAME)
        vesta_logger.setLevel(logging.DEBUG)

        if cls.__check_url(SIMPLELOGS_URL):
            # create handler
            handler = SimplelogHandler(SIMPLELOGS_URL)
            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        else:
            # create handler and set level to debug
            handler = logging.StreamHandler()
            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # set handler level to debug
        handler.setLevel(logging.DEBUG)
        # add formatter to handler
        handler.setFormatter(formatter)

        vesta_logger.addHandler(handler)

        cls.__log_except(vesta_logger)

        return vesta_logger

logger = VestaLogger.get_logger()