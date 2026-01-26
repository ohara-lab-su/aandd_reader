#!/usr/bin/env python
"""

Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import time
from aandd_reader import AanddReader
from x_logger import XLogger


if __name__ == "__main__":

    log_mode = "file"
    logger = XLogger(
        log_level="info",
        log_mode=log_mode,
        log_name="aandd.log",
        logger_name="aandd_reader",
    )

    aandd_reader = AanddReader(port="COM4", logger=logger)

    # Reset
    aandd_reader.reset()
    time.sleep(0.5)
    ret = aandd_reader.meas()
    # if not ret:
    #     logger.error(ret)

    # print(aandd_reader.get_serial_number())
    # while True:
    #     logger.info(aandd_reader.meas())
    #     time.sleep(0.05)

    # print(aandd_reader.status())
    # print(aandd_reader.unit())
