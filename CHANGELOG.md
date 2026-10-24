# CHANGELOG

## 2026.10.09 v0.2.14, nakada

- Updated the implementation to support the `DeviceProxy` type.

## 2026.06.27 v0.2.13, nakada

**Requires ese774_frame v0.4.20 or later.**

- Updated `make.py` for `DeviceProxy` support.
- Added automatic generation of `server_fastapi/__init__.py`.
- Added automatic generation of `server_fastapi/__init__.pyi`.
- Changed the approach so `make.py` generates the `DeviceProxy` registration code.
- Revised `.pyi` generation to support `DeviceProxy` while retaining existing correction and code-insertion features.
- Reorganized code generation to maintain separation from the framework.

## 2026.05.13 v0.2.12, nakada (DeviceProxy test)

**Requires ese774_frame v0.4.20 or later.**

- Tested `DeviceProxy`.
- Fixed `__init__`-related code.
- Added a `DeviceProxy` example.

## 2026.05.13 v0.2.11, nakada

**Requires ese774_frame v0.4.20 or later.**

- Updated configuration path handling to follow the new approach used by cobotta2 v0.13.8.

## 2026.05.13 v0.2.11, nakada

**Requires ese774_frame v0.4.20 or later.**

- Added `DeviceProxy` registration in `__ini__.py` (filename as written in the original changelog).

## 2026.03.15 v0.2.10, nakada

- Updated documentation.
- Final version before the business trip (2026-03-15).

## 2026.03.09 v0.2.9, nakada

- Updated documentation.

## 2026.02.27 v0.2.8, nakada

Renamed and adjusted the namespace and repository name:

- Previous: `fastapi_frame`
- New: `ese774_frame`

Related package versions:

- ese774_frame: 0.4.13
- cobotta2: 0.10.3
- cobotta2_client: 0.1.0
- aandd_reader: 0.2.8

## 2026.02.04 v0.2.7, nakada

- In `server.py`, separated the control-class and server import paths to reduce the possibility of circular imports.

## 2026.02.04 v0.2.6, nakada

- Changes (not specified in the original changelog).

## 2026.02.04 v0.2.5, nakada

- Changes (not specified in the original changelog).

## 2026.02.04 v0.2.4, nakada

- Added asynchronous support.

## 2026.02.04 v0.2.3, nakada

- Fixed bugs in the server/start scripts under `examples`.
- Moved client-side features such as trigger modes, previously reflected in `prepared`, into examples.

## 2026.02.04 v0.2.2, nakada

Minor bug fixes and improvements to trigger functionality (threshold detection) for easier use:

- Added and revised event functionality:
  - Select whether to use the mean for threshold detection, including the averaging window width.
  - Option to use the ST value for detection.
  - Option to use the raw value for detection.
  - Support threshold detection in either direction (above or below).
- Consolidated event features and controls such as `once` into client-side `prepared`.

## 2026.02.04 v0.2.1, nakada

- Bug fixes.

## 2026.02.04 v0.2.0, nakada

- `aandd_reader.py` (v0.2.0)
- `gRPC_frame.py` (v0.4.4)

Changes:

- Tested event mode and made minor adjustments.
- Corrected a misunderstanding of balance operating modes in the base control class; this was the reason for the version change to v0.2.0.
- Fixed `make_pyi.py` (the inheritance source and destination for dispatched methods).
- When `meas()` is called during streaming (while the worker thread is running), it reads the instance variable instead:
  - The instance variable is continuously updated with stream values obtained by `readline`.

## 2026.02.04 v0.1.1, nakada (gRPC mode implementation)

Bug fixes:

- `grpc_client_stream_event.py`: example of event-based stream use.
- `aandd_reader.py`:
  - Prepared the device control class for streaming mode.
  - Fixed other compatibility bugs introduced across versions.
  - Reorganized methods alongside thread and event-flag handling.
- `aandd_reader_grpc_client.py`.

## 2026.02.04 v0.1.0, nakada (gRPC mode implementation)

- Streaming untested; watch functionality had already been removed.
- New `.pyi` generation tested.

**Use of the gRPC framework beyond the joypad application:**

- Basic operation: tested successfully.
- Event handling: being reimplemented using gRPC.

## 2026.02.04 v0.0.6, nakada (streaming untested; .pyi tested)

- Fixed a problem where `.pyi` files hide implementation-file members from type checking, causing stream/watch helper methods overridden or added in `AsyncAanddReaderClient`—such as `start_watch_listener` and `stop_watch_listener`—to appear missing.

## 2026.02.03 v0.0.5, nakada

- Alpha release (not yet ready for regular use).
- Thread-based streaming mode:
  - The client uses long polling.
  - When the measured weight exceeds a threshold, a client-side action can be executed.

## 2026.01.27 v0.0.4, nakada

- Bug fixes.
- Reset function.

## 2025.10.16 v0.0.3, nakada

- Added Sphinx module (`project.toml`, as written in the original changelog).

## 2025.09.1 v0.0.2, nakada

- Fixed TOML.

## 2025.07.29 v0.0.1, nakada

- Adjusted namespace.

## 2025.07.29 v0.0.0, nakada

- Provisional release (FastAPI / local).
