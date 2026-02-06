#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import re
from typing import Union, Optional, Set, Any
from pathlib import Path

from fastapi_frame.routers.device_router import DeviceRouter
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

        # add: watcher (server internal object)
        self._weight_watcher = WeightWatcher(self._device)

    def watch_start(self, threshold: float, hysteresis: Optional[float] = 0.0):
        if not self._device.is_streaming():
            self._device.stream_start()
        watch_id = self._weight_watcher.watch_start(
            threshold=threshold,
            hysteresis=float(hysteresis or 0.0),
        )
        return {"watch_id": watch_id}

    def watch_stop(self, watch_id: str):
        ok = self._weight_watcher.watch_stop(watch_id)
        return {"result": ok}

    def wait_event(
        self,
        watch_id: str,
        timeout_sec: Optional[float] = None,
    ):
        ev = self._weight_watcher.wait_event(
            watch_id,
            timeout_sec=timeout_sec,
        )
        if ev is None:
            return {
                "triggered": False,
                "event_id": None,
                "weight": self._device.get_weight(),
                "status": self._device.get_status(),
                "unit": self._device.get_unit(),
            }
        return {
            "triggered": True,
            "event_id": ev.get("event_id"),
            "weight": ev.get("weight"),
            "status": ev.get("status"),
            "unit": ev.get("unit"),
        }
