#!/usr/bin/env python
import time
from aandd_reader.aandd_reader import AanddReader


def on_sample(weight, status, unit):
    # 任意：連続データをログしたい時だけ使う
    # print(f"sample: {weight} {status} {unit}")
    pass


def on_threshold(weight, status, unit):
    # 閾値を越えたときに1回だけ実行される
    print(f"[THRESHOLD] {weight} {unit} status={status}")
    # ここに任意の処理を置く（例：外部コマンド、API呼び出し、DB記録など）
    # do_something()


reader = AanddReader(port="COM3")

# 10.0g を超えたら 1回だけ実行
# ヒステリシス 0.2g を設定（10.0 - 0.2 = 9.8 を下回るまで再発火しない）
reader.start_stream(
    on_sample=on_sample,
    threshold=10.0,
    on_threshold=on_threshold,
    stable_only=True,  # STのみ使うなら True
    hysteresis=0.2,
)

try:
    # バックグラウンドで動かし続ける
    while True:
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    reader.stop_stream()
