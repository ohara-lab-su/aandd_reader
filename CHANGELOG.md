# CHANGELOG

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

