import logging
log = logging.getLogger(__name__)

def print_log(timestamp, method = "", url = "", action = "", result = ""):
    log.debug("%s %s %s %s %s" % (timestamp, method, url, action, result))
