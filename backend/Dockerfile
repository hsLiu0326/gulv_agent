FROM python:3.12-slim

WORKDIR /app

# 先拷贝依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["sh", "docker_entrypoint.sh"]
