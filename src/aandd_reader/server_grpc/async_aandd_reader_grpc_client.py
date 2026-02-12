# async_grpc_client.py
from __future__ import annotations

# import asyncio
# import functools
from typing import Any, Optional, Callable
from grpc_frame.grpc_client import AsyncGrpcClient


class AsyncAanddReaderGrpcClient(AsyncGrpcClient):
    """
    擬似 async 版 GrpcClient（内部は sync gRPC をスレッド実行）
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
    ) -> None:
        """

        Args:
            config (Any):
            server_ip (str):
            server_port (int):
            timeout_sec (float):
            logger (Any):
            log_level (str):
        """
        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.GRPC_PORT

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            timeout_sec=timeout_sec,
            logger=logger,
            log_level=log_level,
        )
        self._wrap_async_methods()

        # for gRPC Event
        self._event_topic: Optional[str] = None
        self._event_once: bool = True

    # ----------------------
    #  for Event
    # ----------------------

    async def prepare_event_measurement(
        self,
        *,
        topic: str,
        threshold_g: float,
        above: bool = True,
        once: bool = True,
        # --- trigger mode ---
        trigger_mode: str = "raw",
        trigger_window: int = 3,
        trigger_min_samples: Optional[int] = None,
        trigger_alpha: float = 0.3,
        trigger_stable_only: bool = False,
    ) -> None:
        """
        Event 計測の用の煩雑な手続きを省略するメソッド
        """
        await self.stream_start()

        await self.event_set_config(
            threshold_g=threshold_g,
            above=above,
            topic=topic,
        )

        # --- trigger mode 設定 ---
        await self.set_trigger_mode(
            mode=trigger_mode,
            window=trigger_window,
            min_samples=trigger_min_samples,
            alpha=trigger_alpha,
            stable_only=trigger_stable_only,
        )

        await self.event_arm(once=once)

        self._event_topic = topic
        self._event_once = once

    async def wait_event(self):
        """1イベント待つための薄いラッパー（async 版）"""
        topic = getattr(self, "_event_topic", None)
        if topic is None:
            raise RuntimeError("event is not prepared")

        def _next_event():
            for event in self.subscribe(topic=topic, once=True):
                return event

        return await self._run_in_thread(_next_event, (), {})
