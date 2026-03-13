# AandD 電子天秤 Reader (AandD reader)
K.NAKADA (Shimane University)  
view on [github](https://github.com/ohara-lab-su/aandd_reader/) / [ohara-lab-su (doc)](https://ohara-lab-su.github.io/)


---
```{toctree}
:maxdepth: 2
:caption: Contents:

api/modules
tutorials/intro
```
---

- ese774_frame 対応
- grpc_frame 対応

## 基本的な計測例

```python
#!/usr/bin/env python
import sys
import time
from aandd_reader import AanddReader
from x_logger import XLogger


if __name__ == "__main__":

    log_mode = "file"
    logger = XLogger(
        log_level="info",
        log_mode=log_mode,
        log_name="aandd.log",
        logger_name="aandd_reader",
    )

    # COMポートを選ぶ
    # aandd_reader = AanddReader(port="COM4", logger=logger)
    aandd_reader = AanddReader(port="COM3", logger=logger)

    # Reset
    aandd_reader.reset()
    time.sleep(0.5)
    
    # 測定
    ret = aandd_reader.meas()
    if ret is False:
        logger.error("Error measuring.")
        logger.error(ret)
        sys.exit(1)
        
    logger.info(ret)

```

# 作者
- Kengo NAKADA (中田謙吾)
  - kengo.nakada@mat.shimane-u.ac.jp
  - kengo.nakada@gmail.com
