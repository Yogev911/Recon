import logging


def get_logger():
    logger = logging.getLogger('Recon')
    hdlr = logging.FileHandler('logger.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)