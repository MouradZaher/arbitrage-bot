import logging
def get_logger(name):
      l = logging.getLogger(name)
      if not l.handlers:
                h = logging.StreamHandler()
                h.setFormatter(logging.Formatter("%(name)s | %(levelname)s | %(message)s"))
                l.addHandler(h)
                l.setLevel(logging.INFO)
            return l
