#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
from typing import Any, Union, List, Optional
from pydantic import BaseModel


class ResultResponse(BaseModel):
    result: Optional[Any]
    # message: Optional[str] = None


class SetMeasModeRequest(BaseModel):
    mode: str


class StreamStartRequest(BaseModel):
    poll_interval: Optional[float] = None


# ---------------------------------
# stream mode 機能(alpha版)
# ---------------------------------


class WatchStartRequest(BaseModel):
    threshold: float
    hysteresis: Optional[float] = 0.0


class WatchStartResponse(BaseModel):
    watch_id: str


class WatchStopRequest(BaseModel):
    watch_id: str


class WaitEventRequest(BaseModel):
    watch_id: str
    timeout_sec: Optional[float] = None


class ThresholdEventResponse(BaseModel):
    triggered: bool
    event_id: Optional[int]
    weight: Optional[float]
    status: Optional[str]
    unit: Optional[str]
