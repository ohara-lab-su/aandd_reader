"""
基本トライ　ACK なしにする(出荷時)
"""

import serial
import time
import sys

from x_logger import XLogger


class AanddReader:
    """
    通信速度
        天秤の 内部設定
            bPS (ボーレート) 19200bps

    全てのコマンドに対しての何らかの応答
        天秤の 内部設定
            SF(シリアルインターフェース)
            ErCd 1 (出力する AK,コード)
    """

    def __init__(
        self,
        port: str,
        baud_rate: int | None = None,
        timeout: float | None = None,
        logger: XLogger = None,
    ):
        self._logger = logger

        self._port = port or "COM3"
        self._baud_rate = baud_rate or 19200
        self._timeout = timeout or 0.5
        self._status = None
        self._unit = None

        # FX-200i だと、baud rate 2400 しかダメ
        try:
            self._ser = serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                parity=serial.PARITY_EVEN,
                bytesize=serial.SEVENBITS,
                timeout=0.5,
            )
        except Exception as e:
            self._logger.error(f"**Error**: {e}")

    def __del__(self):
        self._ser.close()

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
            else:
                self._logger.error(line)
            return serial_number

        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return ""

    def cal(self):
        """キャリブレーション"""
        self._logger.info(f"[CAL]")
        self._ser.reset_input_buffer()

        try:
            self._ser.write(b"CAL\r\n")
            line = self._ser.readline().rstrip()
            if not self.is_ack(line):
                self._logger.error(f"ACK is False")

        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return ""

    def meas(self):
        """
        Q
        即時計測する

        Returns:

        """
        status = ""
        weight = ""
        unit = ""
        try:
            self._ser.write(b"Q\r\n")
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return status, weight, unit

        if len(line) == 17:
            line = line.rstrip()
            try:
                self._status = line[0:2].decode()  # 測定状態(ST:安定)
                weight = line[3:12].decode()
                self._unit = line[12:15].decode().strip()
            except Exception as e:
                self._logger.error(f"**Error**: {e}")
        else:
            print(line)
        return weight


if __name__ == "__main__":
    _logger = XLogger(log_level="info")
    aandd_reader = AanddReader(port="COM3", logger=_logger)
    # aandd_reader.cal()
    print(aandd_reader.get_serial_number())
    print(aandd_reader.meas())
    print(aandd_reader.status())
    print(aandd_reader.unit())
