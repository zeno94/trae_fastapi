# 阶段1：构建阶段（包含 uv 和依赖安装）
FROM python:3.12-slim AS builder

# 安装 uv（官方方法）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置工作目录
WORKDIR /app

# 设置 PyPI 镜像源（加速 Python 包下载）
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 只复制依赖清单（利用 Docker 层缓存）
COPY requirements.txt .

# 使用 uv 安装依赖到虚拟环境（指定路径 /opt/venv）
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt

# 阶段2：运行阶段（最简镜像）
FROM python:3.12-slim

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 将虚拟环境的 bin 目录加入 PATH
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制项目代码（注意：.dockerignore 应排除 .venv, __pycache__ 等）
COPY . .

# 暴露端口（根据你的应用修改）
EXPOSE 8000

# 启动命令（使用虚拟环境中的 uvicorn）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]