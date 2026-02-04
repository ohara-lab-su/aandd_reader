#!/usr/bin/env python
from typing import Optional, Dict
import time

from dataclasses import dataclass
import queue
import threading
import uuid


@dataclass
class _WatchState:
    threshold: float
    hysteresis: float
    over: bool
    q: "queue.Queue[dict]"


class WeightWatcher:
    def __init__(self, ctrl: "AanddReader"):
        self._ctrl = ctrl

        # これは毎回呼び出す必要があるのでここでのインスタンス変数化はしない
        # self._cond = self._ctrl.get_stream_update_condition()

        self._watches: Dict[str, _WatchState] = {}
        self._watches_lock = threading.Lock()

        self._thread = None
        self._stop = threading.Event()

        # 重さを測って、敷居を超えた回数
        self._event_id = 0

    def watch_start(
        self,
        *,
        threshold: float,
        hysteresis: float = 0.0,
    ) -> str:

        watch_id = uuid.uuid4().hex
        st = _WatchState(
            threshold=float(threshold),
            hysteresis=float(hysteresis),
            over=False,
            q=queue.Queue(),
        )
        with self._watches_lock:
            self._watches[watch_id] = st
            if self._thread is None or not self._thread.is_alive():
                self._stop.clear()
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
        return watch_id

    def watch_stop(
        self,
        *,
        watch_id: str,
    ) -> bool:
        with self._watches_lock:
            existed = self._watches.pop(watch_id, None) is not None
            empty = len(self._watches) == 0
        if empty:
            self._stop.set()
        return existed

    def wait_event(
        self,
        *,
        watch_id: str,
        timeout_sec: Optional[float] = None,
    ) -> Optional[dict]:
        with self._watches_lock:
            st = self._watches.get(watch_id)
        if st is None:
            return None
        try:
            if timeout_sec is None:
                return st.q.get()
            return st.q.get(timeout=float(timeout_sec))
        except queue.Empty:
            return None

    def _next_event_id(self) -> int:
        """"""
        self._event_id += 1
        return self._event_id

    def _run(self) -> None:
        """"""
        cond = self._ctrl.get_stream_update_condition()

        while not self._stop.is_set():
            with self._cond:
                cond.wait(timeout=1.0)

            weight = self._ctrl.get_weight()
            if weight is None:
                continue

            status = self._ctrl.get_status()
            unit = self._ctrl.get_unit()

            with self._watches_lock:
                items = list(self._watches.items())

            for wid, st in items:
                if st.over:
                    if weight <= (st.threshold - st.hysteresis):
                        st.over = False
                    continue

                if weight >= st.threshold:
                    st.over = True
                    ev = {
                        "event_id": self._next_event_id(),
                        "weight": weight,
                        "status": status,
                        "unit": unit,
                        "watch_id": wid,
                    }
                    st.q.put(ev)
