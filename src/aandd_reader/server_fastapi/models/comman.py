#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
from typing import Union, List
from typing import Any, Union, List, Optional
from pydantic import BaseModel


class ResultResponse(BaseModel):
    result: Optional[Any]
    # message: Optional[str] = None


class SetMeasModeRequest(BaseModel):
    mode: str


class StreamStartRequest(BaseModel):
    threshold: Optional[float] = None
    stable_only: Optional[bool] = False
    hysteresis: Optional[float] = None
    poll_interval: Optional[float] = None


# ---------------------------------
# stream mode 機能(alpha版)
# ---------------------------------


class WaitThresholdRequest(BaseModel):
    """
    重さが閾値を超えた時に Server がからレスポンスするための method
    """

    threshold: float
    stable_only: Optional[bool] = False
    hysteresis: Optional[float] = None
    timeout_sec: Optional[float] = None


class ThresholdEventResponse(BaseModel):
    """
    重さが閾値を超えた時に Server がからレスポンスするための method
    """

    triggered: bool
    weight: Optional[float]
    status: Optional[str]
    unit: Optional[str]
