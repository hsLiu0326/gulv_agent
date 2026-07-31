FROM python:3.12-slim

WORKDIR /app

# 国内网络下直连 PyPI 不稳定，默认使用阿里云镜像源；可通过 --build-arg 覆盖
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ARG PIP_TRUSTED_HOST=mirrors.aliyun.com
ENV PIP_INDEX_URL=$PIP_INDEX_URL \
    PIP_TRUSTED_HOST=$PIP_TRUSTED_HOST

# 先拷贝依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["sh", "docker_entrypoint.sh"]
