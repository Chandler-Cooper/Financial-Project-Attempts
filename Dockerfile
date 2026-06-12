# ============================================================================
# A股量化与舆情智能分析系统 - Docker 镜像构建
# ============================================================================
# 使用说明：
#   构建: docker build -t fin-analysis:latest .
#   运行: docker run -p 8501:8501 fin-analysis:latest
#   使用 docker-compose: docker-compose up -d
# ============================================================================

FROM python:3.11-slim

# ============================================================================
# 1. 设置工作目录与系统环境
# ============================================================================
WORKDIR /app

# 设置时区和字体支持
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ============================================================================
# 2. 安装系统依赖（中文字体用于词云）
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    libfreetype6-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/logs

# ============================================================================
# 3. 复制项目文件
# ============================================================================
COPY requirements.txt .
COPY *.py ./
COPY docker-compose.yml ./

# ============================================================================
# 4. 安装Python依赖
# ============================================================================
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# 5. 创建日志目录和缓存目录
# ============================================================================
RUN mkdir -p /app/logs /app/.streamlit && \
    echo '[logger]' > /app/.streamlit/config.toml && \
    echo 'level = "warning"' >> /app/.streamlit/config.toml && \
    echo '[client]' >> /app/.streamlit/config.toml && \
    echo 'showErrorDetails = false' >> /app/.streamlit/config.toml

# ============================================================================
# 6. 健康检查
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/health')" || exit 1

# ============================================================================
# 7. 启动应用
# ============================================================================
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
