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
      port = "/dev/cu.usbserial-XXXXXXXX",
      baudrate = 115200,
      #parity = serial.PARITY_NONE,
      #bytesize = serial.EIGHTBITS,
      #stopbits = serial.STOPBITS_ONE,
      #timeout = None,
      #xonxoff = 0,
      #rtscts = 0,
      )