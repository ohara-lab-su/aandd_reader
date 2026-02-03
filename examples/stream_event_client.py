import asyncio
from aandd_reader.server_fastapi.clients.async_aandd_reader_client import (
    AsyncAanddReaderClient,
)


def on_threshold_up(status, weight, unit):
    print("UP:", status, weight, unit)


def on_threshold_down(status, weight, unit):
    print("DOWN:", status, weight, unit)


async def background_job():
    while True:
        # 別のジョブが動いている前提の例
        await asyncio.sleep(2)
        print("background job running")


async def threshold_monitor(client, threshold, hysteresis=0.2, stable_only=True):
    """
    閾値を上回った/下回ったイベントをクライアント側で処理する。
    """
    last_over = False

    while True:
        triggered, status, weight, unit = await client.wait_threshold(
            threshold=threshold,
            stable_only=stable_only,
            hysteresis=hysteresis,
            timeout_sec=30.0,
        )

        # タイムアウト時は再試行
        if not triggered:
            continue

        # 上回りイベント
        if not last_over:
            last_over = True
            on_threshold_up(status, weight, unit)

        # 下回り検知のために「次の閾値待ち」を反転条件で行う
        # 簡易的に、一定時間待って再度 wait_threshold で判定を継続
        # （必要ならサーバー側に下回り用APIを追加）
        while last_over:
            triggered2, status2, weight2, unit2 = await client.wait_threshold(
                threshold=threshold - hysteresis,
                stable_only=stable_only,
                hysteresis=hysteresis,
                timeout_sec=30.0,
            )
            if (
                triggered2
                and weight2 is not None
                and weight2 < (threshold - hysteresis)
            ):
                last_over = False
                on_threshold_down(status2, weight2, unit2)


async def main():
    client = AsyncAanddReaderClient(
        server_ip="127.0.0.1", server_port=8000, logger=None
    )

    # サーバー側でストリーム開始
    await client.stream_start(
        threshold=None,
        stable_only=True,
        hysteresis=0.2,
        poll_interval=0.0,
    )

    # 並走タスクとして動かす
    await asyncio.gather(
        background_job(),
        threshold_monitor(client, threshold=10.0, hysteresis=0.2, stable_only=True),
    )


if __name__ == "__main__":
    asyncio.run(main())
