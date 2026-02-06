"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""

import os
import yaml


class Config:
    DEVICE_PORT = "COM2"
    SERVER_LOGGER_NAME = "AanddReaderServer"
    # SERVER_IP = "10.170.10.33"
    SERVER_IP = "10.170.10.38"
    # SERVER_PORT = 8004
    FASTAPI_PORT = 8004
    GRPC_PORT = 50051
    CLIENT_LOGGER_NAME = "AanddReaderClient"

    def __init__(self, yaml_path=None):
        # インスタンスで使いたいときだけ、ここで個別設定
        if yaml_path:
            self._load_yaml(yaml_path)

    @classmethod
    def load_yaml(cls, yaml_path=None):
        if yaml_path is None:
            yaml_path = os.environ.get("AANDD_READER_CONFIG_YAML")
            if yaml_path is None:
                return
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        for k, v in data.items():
            if hasattr(cls, k):
                setattr(cls, k, v)
            else:
                print("NO SUCH VAR:", k)

    def _load_yaml(self, yaml_path=None):
        # インスタンス用：インスタンスdictにのみ上書き
        if yaml_path is None:
            yaml_path = os.environ.get("AANDD_READER_CONFIG_YAML")
            if yaml_path is None:
                return
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        for k, v in data.items():
            setattr(self, k, v)
