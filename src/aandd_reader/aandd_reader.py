"""
基本トライ　ACK なしにする(出荷時)
"""

from typing import Any, Dict, List, Optional, Union, Tuple, Callable, Sequence
import serial
import time
import threading
import sys


class AanddReader:
    """
    通信速度
        天秤の 内部設定
            bPS (ボーレート) 19200bps

    全てのコマンドに対しての何らかの応答(ACK)を返すモードであるのが前提
        天秤の 内部設定
            SF(シリアルインターフェース)
            ErCd 1 (出力する AK,コード)
    """

    def __init__(
        self,
        port: str,
        baud_rate: Optional[int] = None,
        timeout: Optional[float] = None,
        logger: Optional[Any] = None,
    ):
        if logger is None:
            from x_logger import XLogger

            logger = XLogger(log_level="info")

        self._logger = logger

        self._port = port or "COM3"
        self._baud_rate = baud_rate or 19200
        self._timeout = timeout or 0.5
        self._meas_mode = "Q"

        self._status = None
        self._unit = None
        self._weight: Optional[float] = None

        self._logger.info(f"Create AandD Device (Serial)")
        self._logger.info(f"timeout = {self._timeout}")
        self._logger.info(f"baud_rate = {self._baud_rate}")
        self._logger.info(f"port = {self._port}")
        try:
            self._ser = serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                parity=serial.PARITY_EVEN,
                bytesize=serial.SEVENBITS,
                timeout=self._timeout,
            )
        except Exception as e:
            self._logger.error(f"**Error**: {e}")

        # stream / background mode
        self._stream_thread = None
        self._stream_stop = threading.Event()
        self._stream_running = False
        self._stream_last_weight = None

        # stream defaults
        self._stream_stable_only = False
        self._stream_hysteresis = 0.0
        self._stream_poll_interval = 0.0

    def __del__(self):
        try:
            self._ser.close()
        except Exception as e:
            pass

    # ---------------------------
    # Device Info API
    # ---------------------------

    def status(self):
        return self._status

    def get_status(self):
        return self._status

    def unit(self):
        return self._unit

    def get_unit(self):
        return self._unit

    @staticmethod
    def is_ack(data: bytes) -> bool:
        return data == b"\x06"

    def get_serial_number(self):
        """
        ?SN
        マニュアルには \r でも OK とあるが、\r\n が必須

        Returns:

        """
        self._logger.info(f"[Get Serial Number]")
        self._ser.reset_input_buffer()

        try:
            self._ser.write(b"?SN\r\n")
            line = self._ser.readline()
            self._logger.info(f"[ID raw] {line!r}")

            # return line.decode(errors="ignore").strip()
            serial_number = ""
            if len(line) == 13 and line != b"":
                line = line.rstrip()
                try:
                    serial_number = line[3:11].decode()
                except Exception as e:
                    self._logger.error(f"**Error**: {e}")
                    return False
            else:
                self._logger.error(line)
                return False
            return serial_number

        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return ""

    def set_meas_mode(self, val: str = "Q"):
        self._meas_mode: str = val

    def get_meas_mode(self) -> str:
        return self._meas_mode

    # ---------------------------------
    # Device Ctrl API
    # ---------------------------------

    def reset(self):
        """reset
        reset 後、測定するには 0.5 s くらい待たないとダメ
        """
        return self._r()

    def meas(
        self,
        mode: Optional[str] = None,
    ):
        """
        Q
        即時計測する
        Returns:
        """
        if mode is None:
            mode = self._meas_mode

        if mode.upper() == "Q":
            return self._q()
        elif mode.upper() == "S":
            return self._s()
        else:
            return ""

    # ---------------------------------
    # Device Ctrl Driver
    # ---------------------------------

    # def cal(self):
    #     """キャリブレーション(零点のリセットじゃないし、そもそも、このコマンドだけだと機能しない)"""
    #     self._logger.info(f"[CAL]")
    #     self._ser.reset_input_buffer()

    #     try:
    #         self._ser.write(b"CAL\r\n")
    #         line = self._ser.readline().rstrip()
    #         if not self.is_ack(line):
    #             self._logger.error(f"ACK is False")

    #     except Exception as e:
    #         self._logger.error(f"**Error**: {e}")
    #         return ""

    def _r(
        self,
    ) -> Union[str, bool]:
        """reset
        reset 後、測定するには 0.5 s くらい待たないとダメ
        """
        if self._ser is None:
            # raise RuntimeError("Serial port is not opened.")
            self._logger.error("Serial port is not opened.")
            return False

        self._ser.reset_input_buffer()
        self._ser.write(b"R\r\n")

        try:
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return False

        if len(line) == 0:
            self._logger.error("**Error**: No data received.")
            return False

        return line[0] == 0x06

    def _s(
        self,
    ) -> Union[bool, Union[str, float, None]]:
        """
        Q, 安定後、データ取得

        Returns:
        """
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return False

        self._ser.reset_input_buffer()

        try:
            self._ser.write(b"S\r\n")
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return False

        if len(line) == 17:
            line = line.rstrip()
            try:
                self._status = line[0:2].decode()  # 測定状態(ST:安定)
                self._weight = line[3:12].decode()
                self._unit = line[12:15].decode().strip()
            except Exception as e:
                self._logger.error(f"**Error**: {e}")
                return False
        else:
            self._logger.error(line)
            return False
        return self._weight

    def _q(
        self,
    ) -> Union[bool, Union[float, Tuple[str, str, str]]]:
        """
        Q, 即時

        Returns:
        """
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return False
        self._ser.reset_input_buffer()

        try:
            self._ser.write(b"Q\r\n")
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error(readline)**: {e}")
            return False

        if b"EC,E02" in line:
            # 計測時間が短くて前回の命令動作を本体足しているときなど
            self._logger.error(f"**Error(EC, E02)**: {line}")
            return False

        if len(line) == 17:
            line = line.rstrip()
            try:
                self._status = str(line[0:2].decode())  # 測定状態(ST:安定)
                self._weight = float(line[3:12].decode())
                self._unit = str(line[12:15].decode().strip())
            except Exception as e:
                self._logger.error(f"**Error(line==17)**: {e}")
                return False
        else:
            self._logger.error(f"**Error(len(line)!=17)**: {line}")
            return False

        return self._weight

    # ------------------------------------------
    # Stream API
    # ------------------------------------------

    def set_stream_stable_only(self, val: bool) -> None:
        """ストリーム時に ST のみ扱うかを設定する。"""
        self._stream_stable_only = bool(val)

    def get_stream_stable_only(self) -> bool:
        """ストリーム時に ST のみ扱うかを返す。"""
        return self._stream_stable_only

    def set_stream_hysteresis(self, val: float) -> None:
        """閾値イベントのヒステリシス幅を設定する。"""
        self._stream_hysteresis = float(val)

    def get_stream_hysteresis(self) -> float:
        """閾値イベントのヒステリシス幅を返す。"""
        return self._stream_hysteresis

    def set_stream_poll_interval(self, val: float) -> None:
        """ストリームループの待機秒数を設定する。"""
        self._stream_poll_interval = float(val)

    def get_stream_poll_interval(self) -> float:
        """ストリームループの待機秒数を返す。"""
        return self._stream_poll_interval

    def _stream(
        self,
    ) -> Union[float, Optional[bool]]:
        """
        ストリームデータを1行読む

        1/10d
        sample

        1. 長押し(2sec)
        2. bASFnc (分類項目) 1/10d 押すたびに変わる
           ...

        オートプリントモードA 設定
        --> dout
        --> Prt
        --> Prt 1  (一回目を押したら、Aモード(1)に変更

        """
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return False

        try:
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return False

        if not line:
            self._logger.error("No data received.")
            return False

        # 例: b'ST,+0000.000  g\r\n'
        line = line.rstrip()

        # 長さチェックは「厳密に固定しない」
        # フォーマット前提で切る
        try:
            self._status = str(line[0:2].decode())
            self._weight = float(line[3:12].decode())
            self._unit = str(line[12:15].decode().strip())
        except Exception:
            return False

        return self._weight

    def start_stream(
        self,
        on_sample: Optional[Callable[[float, str, str], None]] = None,
        threshold: Optional[float] = None,
        on_threshold: Optional[Callable[[float, str, str], None]] = None,
        stable_only: Optional[bool] = None,
        hysteresis: Optional[float] = None,
        poll_interval: Optional[float] = None,
    ) -> bool:
        """バックグラウンドでストリーム計測を開始する。

        Args:
            on_sample: 毎サンプルで呼ばれるコールバック。
                引数は (weight, status, unit)。
            threshold: 閾値。None の場合は閾値イベントを使わない。
            on_threshold: 重量が閾値を下→上に跨いだ時に呼ぶコールバック。
            stable_only: True の場合、status が "ST" のみ扱う。
            hysteresis: チャタリング防止用。閾値を下回る復帰点を
                (threshold - hysteresis) とする。
            poll_interval: ループ毎の待機秒数。0 の場合は readline 待ち。

        Returns:
            開始できた場合 True（すでに動作中でも True）、失敗時 False。
        """
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return False

        if stable_only is None:
            stable_only = self._stream_stable_only
        if hysteresis is None:
            hysteresis = self._stream_hysteresis
        if poll_interval is None:
            poll_interval = self._stream_poll_interval

        if self._stream_running:
            self._logger.error("Stream already running.")
            return False

        self._stream_stop.clear()
        self._stream_running = True
        self._stream_thread = threading.Thread(
            target=self._stream_loop,
            args=(
                on_sample,
                threshold,
                on_threshold,
                stable_only,
                hysteresis,
                poll_interval,
            ),
            daemon=True,
        )
        self._stream_thread.start()
        return True

    def stop_stream(self, join_timeout: float = 1.0) -> None:
        """バックグラウンド計測を停止する。

        Args:
            join_timeout: スレッド終了待ちのタイムアウト秒数。
        """
        if not self._stream_running:
            return
        self._stream_stop.set()
        if self._stream_thread is not None:
            self._stream_thread.join(timeout=join_timeout)
        self._stream_running = False

    def is_streaming(self) -> bool:
        """バックグラウンド計測が動作中かを返す。

        Returns:
            動作中なら True。
        """
        return self._stream_running

    def _stream_loop(
        self,
        on_sample: Optional[Callable[[float, str, str], None]],
        threshold: Optional[float],
        on_threshold: Optional[Callable[[float, str, str], None]],
        stable_only: bool,
        hysteresis: float,
        poll_interval: float,
    ) -> None:
        """バックグラウンド計測の内部ループ。

        たとえば threshold=10.0 で hysteresis=0.2 の場合:

        重さが 10.0g を超えた瞬間に1回発火
        その後は 9.8g（=10.0-0.2）を下回るまで 再発火しない
        9.8g を下回ったら「リセット状態」に戻る
        再び 10.0g を超えたらまた1回発火

        Args:
            on_sample: 毎サンプルで呼ぶコールバック。
            threshold: 閾値。
            on_threshold: 閾値を跨いだときのコールバック。
            stable_only: True の場合は "ST" のみ扱う。
            hysteresis: チャタリング防止用の幅。
            poll_interval: ループ毎の待機秒数。
        """
        last = None
        last_over = False

        while not self._stream_stop.is_set():
            val = self._stream()
            if val is False:
                # 読めない時は少し待ってリトライ
                time.sleep(0.05)
                continue

            # _stream() が値更新済みなので参照
            weight = self._weight
            status = self._status or ""
            unit = self._unit or ""

            if weight is None:
                continue

            if stable_only and status != "ST":
                continue

            if on_sample is not None:
                try:
                    on_sample(weight, status, unit)
                except Exception as e:
                    self._logger.error(f"**Error(on_sample)**: {e}")

            if threshold is not None and on_threshold is not None:
                over = weight >= threshold
                # ヒステリシス: 一度overになったら (threshold - hysteresis) を下回るまで解除しない
                if last_over:
                    if weight <= (threshold - hysteresis):
                        last_over = False
                else:
                    if over:
                        last_over = True
                        try:
                            on_threshold(weight, status, unit)
                        except Exception as e:
                            self._logger.error(f"**Error(on_threshold)**: {e}")

            # poll ループのインターバル
            if poll_interval > 0:
                time.sleep(poll_interval)


if __name__ == "__main__":
    _logger = XLogger(log_level="info")
    aandd_reader = AanddReader(port="COM3", logger=_logger)
    # aandd_reader.cal()
    print(aandd_reader.get_serial_number())
    print(aandd_reader.meas())
    print(aandd_reader.status())
    print(aandd_reader.unit())
