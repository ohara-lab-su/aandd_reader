from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec
from aandd_reader.server_fastapi.clients.async_aandd_reader_client import (
    AsyncAanddReaderClient,
)
from aandd_reader.server_fastapi.clients.sync_aandd_reader_client import (
    SyncAanddReaderClient,
)
from ese774_frame.clients import register_device_proxy

register_device_proxy(
    "AanddReader",
    async_client_cls=AsyncAanddReaderClient,
    sync_client_cls=SyncAanddReaderClient,
    api_spec=aandd_reader_api_spec,
    default_async_mode=True,
    aliases=["aandd"],
)
