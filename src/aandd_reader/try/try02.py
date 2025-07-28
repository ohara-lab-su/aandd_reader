"""
基本トライ　ACK なしにする(出荷時)
"""

import serial
import time
import sys

from x_logger import XLogger


class AanddReader:
    def __init__(
        self,
        port: str,
        baud_rate: int | None = None,
        timeout: float | None = None,
        logger: XLogger = None,
    ):
        self._logger = logger

        self._port = port or "COM3"
        self._baud_rate = baud_rate or 2400
        self._timeout = timeout or 0.5

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

    def get_serial_number(self):
        """
        ?SN
        マニュアルには \r でも OK とあるが、\r\n が必須

        Returns:

        """
        self._logger.info(f"[Get Serial Number]")

        try:
            self._ser.reset_input_buffer()
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

    def measure_single(self):
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
                status = line[0:2].decode()  # 測定状態(ST:安定)
                weight = line[3:12].decode()
                unit = line[12:15].decode()
            except Exception as e:
                self._logger.error(f"**Error**: {e}")
        else:
            print(line)
        return status, weight, unit


if __name__ == "__main__":
    _logger = XLogger(log_level="info")
    aandd_reader = AanddReader(port="COM3", logger=_logger)
    print(aandd_reader.get_serial_number())
    print(aandd_reader.measure_single())
