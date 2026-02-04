#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
from fastapi_frame.models.api_spec import ApiSpec

# SPEC
from aandd_reader.server_fastapi.models.comman import (
    ResultResponse,
    SetMeasModeRequest,
    StreamStartRequest,
    ThresholdEventResponse,
    WatchStartRequest,
    WatchStartResponse,
    WatchStopRequest,
    WaitEventRequest,
)

# ここで「APIの数だけ」ApiSpecを作る
aandd_reader_api_spec = [
    ApiSpec(
        name="get_status",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="get_status()",
        description="""
        """,
    ),
    ApiSpec(
        name="get_unit",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="get_unit()",
        description="""
        """,
    ),
    ApiSpec(
        name="get_serial_number",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="get_serial_number",
        description="",
    ),
    ApiSpec(
        name="reset",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="reset",
        description="zero-reset",
    ),
    ApiSpec(
        name="meas",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="measure_single",
        description="計測(status,unit)",
    ),
    ApiSpec(
        name="get_meas_mode",
        object_name="aandd",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        summary="get_meas_mode",
        description="measのモードを取得",
    ),
    ApiSpec(
        name="set_meas_mode",
        object_name="aandd",
        request_model=SetMeasModeRequest,
        response_model=ResultResponse,
        method="post",
        summary="set_meas_mode",
        description="measのモードを設定 (Q/S)",
    ),
]
