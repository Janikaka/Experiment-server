import logging
log = logging.getLogger(__name__)

"""
Logger for this framework. Use this instead of normal print(). Also append here log.error.
"""


def print_log(timestamp, method = "", url = "", action = "", result = ""):
    log.debug("%s %s %s %s %s" % (timestamp, method, url, action, result))
