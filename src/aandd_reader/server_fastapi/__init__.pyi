from typing import Any, List

from aandd_reader.server_fastapi.clients.async_aandd_reader_client import (
    AsyncAanddReaderClient,
)
from aandd_reader.server_fastapi.clients.sync_aandd_reader_client import (
    SyncAanddReaderClient,
)
from aandd_reader.server_fastapi.routers.aandd_reader_router import AanddReaderRouter

DEVICE_PROXY_NAME: str
DEVICE_PROXY_ALIASES: List[str]
aandd_reader_api_spec: Any

__all__: List[str]
