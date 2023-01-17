import logging

logger = logging.getLogger("hubspace-ng")
logger.setLevel(logging.DEBUG)
__ch__ = logging.StreamHandler()
__ch__.setLevel(logging.DEBUG)
__formatter__ = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
__ch__.setFormatter(__formatter__)
logger.addHandler(__ch__)


def setLogLevel(level):
    logger.setLevel(level)
    __ch__.setLevel(level)
