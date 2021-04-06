import logging


_level = logging.INFO
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=_level)
logging.getLogger().setLevel(_level)
log = logging.getLogger()