#!/bin/sh
set -e

echo "[entrypoint] 等待 MySQL 就绪..."
python - <<'PY'
import os
import sys
import time

import pymysql

url = os.environ.get("DATABASE_URL", "")
try:
    _, rest = url.split("://", 1)
    auth, rest = rest.split("@", 1)
    user, password = auth.split(":", 1)
    host_port, database = rest.split("/", 1)
    host, port = host_port.rsplit(":", 1)
except Exception:
    print("[entrypoint] 无法解析 DATABASE_URL，直接启动应用")
    sys.exit(0)

for i in range(60):
    try:
        pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connect_timeout=3,
        ).close()
        print("[entrypoint] MySQL 就绪")
        sys.exit(0)
    except Exception as e:
        print(f"[entrypoint] 等待 MySQL ({i + 1}/60): {e}")
        time.sleep(2)

print("[entrypoint] MySQL 等待超时，退出")
sys.exit(1)
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
