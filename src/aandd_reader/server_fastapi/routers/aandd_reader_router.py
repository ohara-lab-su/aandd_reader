#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import re
from typing import Union, Optional, Set
from pathlib import Path

from fastapi_frame.routers.device_router import DeviceRouter
from x_logger import XLogger


class AanddReaderRouter(DeviceRouter):
    def __init__(self, device_instance, api_spec=None, logger: XLogger = None):
        super().__init__(device_instance, api_spec=api_spec, logger=logger)
