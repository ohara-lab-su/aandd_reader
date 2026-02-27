#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import re
from typing import Union, Optional, Set, Any
from pathlib import Path

from ese774_frame.routers.device_router import DeviceRouter
from x_logger.x_logger import XLogger


class AanddReaderRouter(DeviceRouter):
    def __init__(
        self,
        device_instance,
        api_spec=None,
        logger: Any = None,
        log_level: str = "INFO",
    ):
        if logger is None:
            import logging

            logging.basicConfig(level=log_level.upper())
            logger = logging.getLogger(__name__)

        self._logger = logger

        super().__init__(
            device_instance,
            api_spec=api_spec,
            logger=self._logger,
            log_level=log_level,
        )
