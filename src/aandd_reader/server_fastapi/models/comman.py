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
