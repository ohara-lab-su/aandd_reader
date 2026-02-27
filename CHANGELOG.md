# CHANGELOG

## 2026.02.27 v0.2.8, nakada

名前空間とリポジトリ名を変更・調整

- 旧: fastapi_frame
- 新: ese774_frame

調整パッケージ

- ese774_frame: 0.4.13
- cobotta2: 0.10.3
- cobotta2_client: 0.1.0
- aandd_reader: 0.2.8

## 2026.02.04 v0.2.7, nakada

server.py
少しでも巡回インポートが起こるケースを潰すために、ctrl系とサーバー系のルートを別にする

## 2026.02.04 v0.2.6, nakada

差分

## 2026.02.04 v0.2.5, nakada

差分

## 2026.02.04 v0.2.4, nakada

- async 対応版

## 2026.02.04 v0.2.3, nakada

- server/start (example側) script のバグ修正
- client 側に追加している trigger モードなどの機能を
prepared に反映してたものを　example についか
 
## 2026.02.04 v0.2.2, nakada

若干のバグ修正/トリガー機能(閾値判定)の拡張（使うのに利便性を伴った改修）

- Evnet 機能の追加修正
  - 閾値判定に使う値を平均使うか？(その時の平均のウィンドウ幅)
  - ST 値を判定に使うか？
  - raw 値で判定するか？
  - 閾値判定を上下どちらでも
- これらのイベント機能および onece などの制御を client 側の prepared にまとめた。

## 2026.02.04 v0.2.1, nakada

bugfix

## 2026.02.04 v0.2.0, nakada

- aandd_reader.py (v0.2.0)
- gRPC_frame.py (v0.4.4)

修正内容

- Event モードの動作テストおよびそれ位対して若干の改修
- 天秤側の動作モードを少し勘違いしていたのを修正(基本クラスの修正) <- これが v0.2.0 へのバージョン変更の理由
- make_pyi.py 修正(dispatchされる継承元と継承先)
- stream モード中に(スレッド動作中に) meas()をうごかしたときは、インスタンス変数値をとる
  - インスタンス変数は readline でストリームの値を取得し続けいる

## 2026.02.04 v0.1.1, nakada, (gRPC 利用モードの実装)

- bugfix
  - grpc_client_stream_event.py
    - イベントを実際に使ったストリーム利用例
  - aandd_reader.py
    - デバイス制御(ストレームモードを使える形に整備)
    - そのほか細かくないバグ(バージョンごとに変えたことの不整合)修正
    - スレッドとEventフラグ周りの整理と一緒にメソッド周りを整理
  - aandd_reader_grpc_client.py

## 2026.02.04 v0.1.0, nakada, (gRPC 利用モードの実装)

- stream未テスト,watch 昨日は削除済み
- new pyi 作成はテスト済み

**gRPC frame の joypad 以外の利用**

- 基本利用: テストOK
- event は gRPC を用いて再度実装やり直し中

 
## 2026.02.04 v0.0.6, nakada (stream未テスト, pyi はテスト済み)

- `.pyi` が実装ファイルを隠す仕様により、
  `AsyncAanddReaderClient` 側でオーバーライド・追加している
  - `start_watch_listener`
  - `stop_watch_listener`
  などの **stream / watch 補助メソッドが存在しない扱いになる問題を修正**。

## 2026.02.03 v0.0.5, nakada

alpha版(正式に使える形になってない)

- stream モードで動作する スレッド型
  - client から longpolling されて
  - 重さが閾値を超えたら client 側で好きな実行が可能にする


## 2026.01.27 v0.0.4, nakada

- bugfix
- reset fnc

## 2025.10.16 v0.0.3, nakada

- added sphinx module (project.toml)
 
## 2025.09.1 v0.0.2, nakada

- fix toml
 
## 2025.07.29 v0.0.1, nakada

namespace 調整

## 2025.07.29 v0.0.0, nakada

- 暫定リリース(FastAPI / local)

