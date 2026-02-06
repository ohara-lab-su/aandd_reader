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
        log_level: str = "info",
    ):
        # XLogger が存在しない時に仕方がないのでデフォルトの logging を使う
        if logger is None:
            import logging

            logging.basicConfig(level=log_level.upper())
            logger = logging.getLogger(__name__)

        self._logger = logger

        self._port = port or "COM3"
        self._baud_rate = baud_rate or 19200
        self._timeout = timeout or 0.5
        self._meas_mode = "Q"

        self._status: Optional[str] = None
        self._unit: Optional[str] = None
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
            sys.exit(1)

        # ----------------------------------
        # gRPC 利用を意識
        # _stream で得た値が式意図を超えたときの結果によってevent発生
        self._event_bus = None

        self._stream_thread = None
        self._stream_stop_event = threading.Event()

        self._event_topic = None
        self._event_threshold_g = None
        self._event_once = True
        self._event_armed = False
        # ----------------------------------

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

    def get_status(self) -> Optional[str]:
        return self._status

    def unit(self):
        return self._unit

    def get_unit(self) -> Optional[str]:
        return self._unit

    def get_weight(self) -> Optional[float]:
        return self._weight

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

        self._logger.debug(f"[Meas] mode = {mode}")

        if mode.upper() == "Q":
            return self._q()
        elif mode.upper() == "S":
            return self._s()
        else:
            return ""

    # ---------------------------------
    # Device Ctrl Driver
    # ---------------------------------

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
                self._status: Optional[str] = str(
                    line[0:2].decode()
                )  # 測定状態(ST:安定)
                self._weight: Optional[float] = float(line[3:12].decode())
                self._unit: Optional[str] = str(line[12:15].decode().strip())
            except Exception as e:
                self._logger.error(f"**Error**: {e}")
                self._logger.error(f"line: {line}")
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
            self._logger.error(
                f"計測時間が短くて前回の命令動作を本体足している可能性があります"
            )
            return False

        if len(line) == 17:
            line = line.rstrip()
            try:
                self._status: Optional[str] = str(
                    line[0:2].decode()
                )  # 測定状態(ST:安定)
                self._weight: Optional[float] = float(line[3:12].decode())
                self._unit: Optional[str] = str(line[12:15].decode().strip())
            except Exception as e:
                self._logger.error(f"**Error(line==17)**: {e}")
                self._logger.error(f"line: {line}")
                return False
        else:
            self._logger.error(f"**Error(len(line)!=17)**: {line}")
            self._logger.error(
                f"返信メッセージが正しくない可能性があります。たとえば「空」の可能性です"
            )
            self._logger.error(f"計測モードなどのパラメーターを疑ってください")
            self._logger.error(f"line: {line}")
            return False

        return self._weight

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
            self._status: Optional[str] = str(line[0:2].decode())
            self._weight: Optional[float] = float(line[3:12].decode())
            self._unit: Optional[str] = str(line[12:15].decode().strip())
        except Exception:
            return False

        return self._weight

    # ----------------------------
    # for Event
    # ----------------------------

    def _set_event_bus(self, event_bus) -> None:
        with self._lock:
            self._event_bus = event_bus

    def event_arm(
        self,
        *,
        topic: str,
        threshold_g: float,
        once: bool = True,
    ) -> bool:
        with self._lock:
            self._event_topic = topic
            self._event_threshold_g = float(threshold_g)
            self._event_once = bool(once)
            self._event_armed = True
        return True

    def stream_start(self) -> bool:
        with self._lock:
            thread_obj = self._stream_thread
            if thread_obj is not None:
                if thread_obj.is_alive():
                    return True

            self._stream_stop_event.clear()

            self._stream_thread = threading.Thread(
                target=self._stream_loop,
                name="AanddReaderStream",
                daemon=True,
            )
            self._stream_thread.start()
        return True

    def stream_stop(self) -> bool:
        with self._lock:
            self._stream_stop_event.set()

        thread_obj = None
        with self._lock:
            thread_obj = self._stream_thread

        if thread_obj is not None:
            try:
                thread_obj.join(timeout=2.0)
            except Exception:
                pass

        with self._lock:
            self._stream_thread = None

        return True

    def _stream_loop(self) -> None:
        while True:
            if self._stream_stop_event.is_set():
                return

            try:
                weight_str = self._stream()
            except Exception:
                time.sleep(0.05)
                continue

            try:
                weight_g, _unit = self._extract_weight(weight_str)
                weight_val = float(weight_g)
            except Exception:
                continue

            event_bus = None
            topic = None
            threshold_g = None
            armed = False
            once = True

            with self._lock:
                event_bus = self._event_bus
                topic = self._event_topic
                threshold_g = self._event_threshold_g
                armed = bool(self._event_armed)
                once = bool(self._event_once)

            if event_bus is None:
                continue
            if armed is False:
                continue
            if topic is None:
                continue
            if threshold_g is None:
                continue

            if weight_val >= float(threshold_g):
                payload = {
                    "weight_g": weight_val,
                    "threshold_g": float(threshold_g),
                }

                try:
                    event_bus.publish(topic, payload)
                except Exception:
                    pass

                if once:
                    with self._lock:
                        self._event_armed = False


if __name__ == "__main__":
    from x_logger import XLogger

    # log_level_ = "info"
    log_level_ = "debug"
    logger_ = XLogger(
        log_level=log_level_,
        logger_name="AandDReader",
    )

    aandd_reader = AanddReader(
        port="COM3",
        # port="COM4",
        logger=logger_,
        log_level=log_level_,
    )
    # aandd_reader.cal()
    logger_.info(f"SN: {aandd_reader.get_serial_number()}")
    time.sleep(0.5)
    logger_.info(aandd_reader.meas())
    # print(aandd_reader.status())
    # print(aandd_reader.unit())
