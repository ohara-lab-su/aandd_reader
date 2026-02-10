"""
K.NAKADA, kengo.nakada@gmail.com/kengo.nakada@mat.shimane-u.ac.jp

返信メッセージの形式

- ACK なし(出荷時)
- ACK あり(現在)

PRT モードとデーター取得について

PRT は **「データ出力（Serial Print）の自動出力条件」**
天秤が“自分の判断で”出力を送るタイミングの設定であり、
Q/S/SIR などの“コマンド要求”とは別軸となる

1	Auto print A（基準=ゼロ）	安定＋条件成立で自動出力
2	Auto print B（基準=前回の安定値）	安定＋条件成立で自動出力
3	Stream mode	連続出力（表示更新周期に依存）
    SIR と実施的には同じである
    SIR はコマンドでスタートをキックできる PTR3 は開始したら動きっぱなし
    どちらも readline で値を読み続けることができる
    *) 測定可能なサイクルは 5pd で、 5/10/20 回/秒設定が可能
       SAMPLE-key --> ba5fnc
4	Key mode B	PRINTキーを押すと出力（安定不要）
5	Key mode C	PRINTキーで出力（安定なら即、非安定なら待つ）
6	Interval mode	一定間隔で周期出力( mode3 との違いに注意)

--- 上記は結果をシリアルに流すので、コマンドで値要求(Q/S/SIR)と
混ざるとどの応答をシリアルで捉えているのか分かりにくい
STREAM MODE の測定周期は天秤側に設定する必要がある

コマンド出力(Q/S/SIR)
PCからのコマンドに対して天秤が返す出力
SIR は readline のストリームに流す。

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
        log_level: Optional[str] = None,
    ):
        # XLogger が存在しない時に仕方がないのでデフォルトの logging を使う
        if logger is None:
            import logging

            log_level = log_level or "INFO"
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
        # stream 測定スレッド制御
        self._stream_thread = None
        self._stream_stop_event = threading.Event()
        # ----------------------------------

        # ----------------------------------
        # gRPC 利用を意識
        # _stream で得た値が式意図を超えたときの結果によってevent発生
        # Event / stream related
        self._lock = threading.Lock()

        # ----------------------------------
        # 外部通知先 (gRPC Event)
        #
        # 測定クライアント側で
        # AanddReader生成
        #   → EventBus生成
        #   → reader._set_event_bus(event_bus)
        #   → stream_start()
        #   → event_arm()
        self._event_bus: Optional[Any] = None
        #
        # eventを使わない場合
        # (1) _event_sub は None
        # (2) stream_start() は呼ばれない
        # (3) event_arm() は呼ばれない

        # ----------------------------------
        # イベント条件・状態
        # (gRPCに依存してないが実質的にはgRPC-Eventで用いる)
        self._event_topic: Optional[str] = None
        self._event_threshold_g: Optional[float] = None
        self._event_once: bool = True
        self._event_armed: bool = False

        self._event_above: bool = True
        # ----------------------------------

        # ----------------------------------
        # トリガ判定用（streamイベント用）
        self._trigger_mode: str = "raw"  # raw / mean / median / ema
        self._trigger_window: int = 3
        self._trigger_min_samples: int = 1
        self._trigger_alpha: float = 0.3
        self._trigger_buffer: List[float] = []
        self._trigger_ema: Optional[float] = None
        self._trigger_stable_only: bool = False
        # ----------------------------------

    def __del__(self):
        try:
            self._close()
        except Exception as e:
            pass

    def _close(self) -> None:
        """
        ストリーム停止とシリアルクローズを確実に行う
        gRPC からもし使うときに gRPC側の close() とかぶるので名前を変えておく
        """
        try:
            self.stream_stop()
        except Exception:
            pass

        try:
            self._ser.close()
        except Exception:
            pass

    # ---------------------------
    # Device Info API
    # ---------------------------

    def status(self) -> Optional[str]:
        return self._status

    def get_status(self) -> Optional[str]:
        return self._status

    def unit(self) -> Optional[str]:
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

    def reset(self) -> Union[bool, str]:
        """reset
        reset 後、測定するには 0.5 s くらい待たないとダメ
        """
        return self._r()

    def meas(
        self,
        mode: Optional[str] = None,
    ) -> Union[bool, float, str, None]:
        """
        Q
        即時計測する
        Returns:
        """
        # --- ストリームが動いているなら、必ず最新のストリーム値を返す ---
        thread_obj = self._stream_thread
        if thread_obj is not None and thread_obj.is_alive():
            # 初回値がまだなら短時間だけ待つ
            wait_sec = self._timeout if self._timeout is not None else 0.5
            t0 = time.time()
            while self._weight is None and (time.time() - t0) < wait_sec:
                time.sleep(0.01)
            return self._weight

        # --- 通常の Q/S 測定 ---
        mode_val = mode
        if mode_val is None:
            mode_val = self._meas_mode

        if mode_val.upper() == "Q":
            return self._q()

        if mode_val.upper() == "S":
            return self._s()

        return False

    # ---------------------------------
    # Device Ctrl Driver
    # ---------------------------------

    def _r(
        self,
    ) -> Union[str, bool]:
        """reset
        ACK前提

        reset 後、測定するには 0.5 s くらい待たないとダメ
        """
        self._logger.debug(f"[Serial] Reset(): _r")
        if self._ser is None:
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

        if line[0] == 0x06:
            return True
        return False

    def _s(
        self,
    ) -> Union[bool, float]:
        """
        ACKモード前提

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

        parsed = self._parse_measure_line(line)
        if parsed is None:
            self._logger.error(line)
            return False

        status, weight, unit = parsed
        self._status = status
        self._weight = weight
        self._unit = unit
        return float(weight)

    def _q(
        self,
    ) -> Union[bool, float]:
        """
        ACKモード前提

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
            self._logger.error(f"**Error(EC, E02)**: {line}")
            self._logger.error(
                "計測時間が短くて前回の命令動作を本体足している可能性があります"
            )
            return False

        parsed = self._parse_measure_line(line)
        if parsed is None:
            self._logger.error(f"**Error(len(line)!=17)**: {line}")
            self._logger.error(
                "返信メッセージが正しくない可能性があります。たとえば「空」の可能性です"
            )
            self._logger.error("計測モードなどのパラメーターを疑ってください")
            self._logger.error(f"line: {line}")
            return False

        status, weight, unit = parsed
        self._status = status
        self._weight = weight
        self._unit = unit
        return float(weight)

    def _stream(self) -> Union[bool, float]:
        """
        ストリームデータを1行読む
        Q/S や SIR もしくは PRT の各モードも readline に値を書き出す
        ので、どれがどれに対応しているのあわからなくなるので

        Q/S で使うとき
        SIR で readline を loop で撮り続ける

        をきちんと区別して使い分けないとおかしいことになる。
        また、PRT の各モードは上記のコマンドベースにキックされて　readline に
        流れる以外にPRTの各機能でそれぞれの周期やボタンで readline にデーターを
        流すので Q/S/SIR を使う時は PRT を 0 にしておかないと訳がわからなくなる。
        """
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return False

        try:
            line = self._ser.readline()
        except Exception as e:
            self._logger.error(f"**Error**: {e}")
            return False

        # SIR だとタイムアウトで空行は起こり得るので無視
        if not line:
            # self._logger.error("No data received.")
            return False

        # SIRの失敗は EC,Exx が返る
        if line.startswith(b"EC,"):
            self._logger.error(f"**Error(EC)**: {line!r}")
            return False

        # erCd=1 の場合、各コマンドに ACK(0x06) が返るため無視
        if line == b"\x06":
            return False

        parsed = self._parse_measure_line(line)
        if parsed is None:
            return False

        status, weight, unit = parsed
        self._status = status
        self._weight = weight
        self._unit = unit
        return float(weight)

    @staticmethod
    def _parse_measure_line(
        line: bytes,
    ) -> Optional[Tuple[str, float, str]]:
        """"""
        if line is None:
            return None

        raw = line.rstrip()

        # 例: b'ST,+0000.000  g\r\n' を想定
        # 固定長の厳密チェックはしないが、最低限の slicing が成立する長さは必要
        if len(raw) < 15:
            return None

        try:
            status = raw[0:2].decode()
            weight = float(raw[3:12].decode())
            unit = raw[12:15].decode().strip()
        except Exception:
            return None

        return status, weight, unit

    # ----------------------------
    # for Event (gRPC and thread)
    # ----------------------------

    def _set_event_bus(self, event_bus: Any) -> None:
        """
        gRPC の event による制御が回るように gRPC のイベントを挿入
        """
        with self._lock:
            self._event_bus = event_bus

    def event_set_config(
        self,
        *,
        topic: str,
        threshold_g: float,
        above: bool = True,
    ) -> bool:
        """
        Event 条件の設定だけを行う。
        設定後、event_arm() で armed を有効化する。
        """
        with self._lock:
            self._event_topic = topic
            self._event_threshold_g = float(threshold_g)
            self._event_above = bool(above)
        return True

    def event_arm(
        self,
        *,
        once: bool = True,
    ) -> bool:
        """
        Event の armed フラグを立てる。
        topic/threshold は event_set_config() で先に設定する。

        armed を立てていると gRPC のイベントモードになるのでチェックする
        そのときに onece を入れていると、一回だけ閾値超え判定がある。

        Args:
            once (bool):  イベントは一回のみ

        Returns:
            bool:

        """
        with self._lock:
            if self._event_topic is None:
                return False
            if self._event_threshold_g is None:
                return False
            self._event_once = bool(once)
            self._event_armed = True
        return True

    def event_disarm(self) -> bool:
        with self._lock:
            self._event_armed = False
        return True

    def set_trigger_mode(
        self,
        *,
        mode: str = "raw",
        window: int = 3,
        min_samples: Optional[int] = None,
        alpha: float = 0.3,
        stable_only: bool = False,
    ) -> None:
        """
        streamイベントのトリガ値算出方法を設定する。

        mode=raw, stable_only=True で値が stable のものだけ閾値チェック

        Args:
            mode: raw / mean / median / ema
            window: 平均・中央値で使う窓サイズ
            min_samples: 判定に必要な最小サンプル数（Noneならwindow）
            alpha: EMA係数（0-1）
            stable_only: TrueならST以外は無視
        """
        with self._lock:
            self._trigger_mode = str(mode).lower()
            w = max(1, int(window))
            self._trigger_window = w
            if min_samples is None:
                self._trigger_min_samples = w
            else:
                self._trigger_min_samples = max(1, int(min_samples))
            self._trigger_alpha = float(alpha)
            self._trigger_buffer = []
            self._trigger_ema = None
            self._trigger_stable_only = bool(stable_only)

    def _calc_trigger_value(self, weight_val: float) -> Optional[float]:
        """
        トリガ判定に使う値を計算する。
        None を返した場合は判定をスキップする。
        """
        # 安定値だけ使う場合
        if self._trigger_stable_only:
            if self._status != "ST":
                return None

        buf = self._trigger_buffer
        buf.append(weight_val)
        if len(buf) > self._trigger_window:
            del buf[0]

        if len(buf) < self._trigger_min_samples:
            return None

        mode = self._trigger_mode

        if mode == "raw":
            return weight_val

        if mode == "mean":
            return sum(buf) / float(len(buf))

        if mode == "median":
            b = sorted(buf)
            return b[len(b) // 2]

        if mode == "ema":
            if self._trigger_ema is None:
                self._trigger_ema = weight_val
            else:
                a = self._trigger_alpha
                self._trigger_ema = (a * weight_val) + ((1.0 - a) * self._trigger_ema)
            return self._trigger_ema

        # 不明なモードは raw と同じ扱い
        return weight_val

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
        """"""
        # stream_loop での thread停止をするために thread-event set する
        with self._lock:
            self._stream_stop_event.set()

        thread_obj: Optional[threading.Thread] = None
        with self._lock:
            thread_obj = self._stream_thread

        # 念の為 SIRの停止コマンド
        try:
            if self._ser is not None:
                self._ser.write(b"C\r\n")
        except Exception:
            pass

        # loop で readline 取得を止める
        if thread_obj is not None:
            try:
                thread_obj.join(timeout=2.0)
            except Exception:
                pass

        with self._lock:
            self._stream_thread = None

        return True

    def _stream_loop(self) -> None:
        """
        1. stream_start() でスレッド起動
        2. _stream_loop の先頭で SIR を送る
        3. readline() で連続取得
        4. stream_stop() で停止フラグ
        5. _stream_loop 側で C を送って終了

        Returns:

        """
        # --- SIR 開始 ---
        if self._ser is None:
            self._logger.error("Serial port is not opened.")
            return

        try:
            self._ser.reset_input_buffer()
            self._ser.write(b"SIR\r\n")  # 連続データ要求
        except Exception as e:
            self._logger.error(f"**Error(SIR start)**: {e}")
            return

        # SIR開始直後の1行目はゴミになることがあるので捨てる
        try:
            _ = self._ser.readline()
        except Exception:
            pass

        while True:
            if self._stream_stop_event.is_set():
                try:
                    self._ser.write(b"C\r\n")  # SIR 停止
                except Exception:
                    pass
                return

            stream_val = self._stream()
            if isinstance(stream_val, bool):
                time.sleep(0.01)
                continue

            weight_val = float(stream_val)

            event_bus: Optional[Any] = None
            topic: Optional[str] = None
            threshold_g: Optional[float] = None
            armed = False
            once = True

            ###################################################
            # トリガーとして raw 値ではなくて計算する
            trigger_val = self._calc_trigger_value(weight_val)
            if trigger_val is None:
                continue
            weight_val = trigger_val
            ###################################################

            with self._lock:
                above = bool(self._event_above)
                event_bus = self._event_bus
                topic = self._event_topic
                threshold_g = self._event_threshold_g
                armed = bool(self._event_armed)
                once = bool(self._event_once)

            if event_bus is None:
                continue
            if topic is None:
                continue
            if threshold_g is None:
                continue

            ###################################################
            # 閾値チェックを入れるか入れないか？
            # gRPC-event 入れるか？入れないか？
            if armed is False:
                continue

            # 閾値より上と下を選べる
            # if weight_val >= float(threshold_g):
            if (above and weight_val >= float(threshold_g)) or (
                (not above) and weight_val <= float(threshold_g)
            ):
                ###################################################
                payload: Dict[str, Any] = {
                    "weight_g": weight_val,
                    "threshold_g": float(threshold_g),
                }

                try:
                    event_bus.publish(topic, payload)
                except Exception:
                    pass

                # 閾値判定は一回だけ発火(発火後のみどす)
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
    logger_.info(f"{aandd_reader.meas()}")
    # print(aandd_reader.status())
    # print(aandd_reader.unit())
