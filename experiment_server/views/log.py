"Logging-related module"

def print_log(timestamp, method, url, action, result):
    """Logger"""
    print("%s REST method=%s, url=%s, action=%s, result=%s" %
          (timestamp, method, url, action, result))
