# SAP SuccessFactors MCP Server Dockerfile
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 依存パッケージのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY src/ ./src/
COPY .env.example .env

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ポートの公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# アプリケーションの起動
CMD ["python", "-m", "src.server"]