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
