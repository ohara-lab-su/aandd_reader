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

    def __del__(self):
        try:
            self._ser.close()
        except Exception as e:
            pass

    # ---------------------------
    # Device Info API
    # ---------------------------

    # def status(self):
    #     return self._status

    def get_status(self) -> Optional[str]:
        return self._status

    # def unit(self):
    #     return self._unit

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
                self._status: Optional[str] = str(
                    line[0:2].decode()
                )  # 測定状態(ST:安定)
                self._weight: Optional[float] = float(line[3:12].decode())
                self._unit: Optional[str] = str(line[12:15].decode().strip())
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
                self._status: Optional[str] = str(
                    line[0:2].decode()
                )  # 測定状態(ST:安定)
                self._weight: Optional[float] = float(line[3:12].decode())
                self._unit: Optional[str] = str(line[12:15].decode().strip())
            except Exception as e:
                self._logger.error(f"**Error(line==17)**: {e}")
                return False
        else:
            self._logger.error(f"**Error(len(line)!=17)**: {line}")
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


if __name__ == "__main__":
    _logger = XLogger(log_level="info")
    aandd_reader = AanddReader(port="COM3", logger=_logger)
    # aandd_reader.cal()
    print(aandd_reader.get_serial_number())
    print(aandd_reader.meas())
    print(aandd_reader.status())
    print(aandd_reader.unit())
