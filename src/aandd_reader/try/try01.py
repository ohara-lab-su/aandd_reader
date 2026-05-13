"""
FX-200i 天秤
 https://www.aandd.co.jp/pdf_storage/manual/balance/m_fzi_fxi_fziwp_fxiwp.pdf

USB シリアルコンバータ
RS-USB602F
https://www.ratocsystems.com/products/rs232c/
RATOC Systems, Inc
windows-driver
 https://www.ratocsystems.com/dlsoft/dlsoft_rs232c/dlsoft_232cusb/usb602f_win/
"""

import serial

ser = serial.Serial(
    port="COM3",
    # baudrate=2400,
    baudrate=19200,
    parity=serial.PARITY_EVEN,
    bytesize=serial.SEVENBITS,
    timeout=0.5,
)

ser.write(b"?SN\r\n")
# ser.write(b"?ID\r\n")
line_data = ser.readline()
print(line_data)
ser.close()
