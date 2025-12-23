# Docker トラブルシューティングガイド

## エラー: Docker Desktopが起動していない

### エラーメッセージ
```
ERROR: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### 原因
Docker Desktopが起動していないか、正しくインストールされていません。

## 解決方法

### 方法1: Docker Desktopを起動する（推奨）

1. **Docker Desktopを起動**
   - Windowsスタートメニューから「Docker Desktop」を検索
   - Docker Desktopアイコンをクリックして起動
   - タスクバーにDockerアイコンが表示されるまで待つ（1-2分）

2. **起動確認**
   ```cmd
   docker version
   ```
   
   成功すると以下のような出力が表示されます：
   ```
   Client:
    Version:           29.1.3
    ...
   Server:
    Engine:
     Version:          29.1.3
     ...
   ```

3. **デプロイを再実行**
   ```cmd
   cd sap-successfactors-mcp
   deploy.bat
   ```

### 方法2: IBM Cloud Build Serviceを使用（Dockerなし）

Dockerをローカルで使用せず、IBM Cloud上でビルドする方法です。

#### ステップ1: ソースコードをGitHubにプッシュ

```bash
# Gitリポジトリを初期化（まだの場合）
cd sap-successfactors-mcp
git init
git add .
git commit -m "Add permission role feature"

# GitHubリポジトリにプッシュ
git remote add origin https://github.com/YOUR_USERNAME/sap-successfactors-mcp.git
git push -u origin main
```

#### ステップ2: IBM Cloud Code Engineでビルド

```bash
# IBM Cloudにログイン
ibmcloud login --sso

# Code Engineプロジェクトを選択
ibmcloud ce project select --name YOUR_PROJECT_NAME

# ビルド設定を作成
ibmcloud ce build create --name sap-mcp-build \
    --source https://github.com/YOUR_USERNAME/sap-successfactors-mcp \
    --context-dir . \
    --dockerfile deployment/Dockerfile \
    --image jp.icr.io/sap-mcp/sap-successfactors-mcp:latest \
    --registry-secret icr-secret

# ビルドを実行
ibmcloud ce buildrun submit --build sap-mcp-build

# ビルド状況を確認
ibmcloud ce buildrun list
```

#### ステップ3: アプリケーションをデプロイ

```bash
# シークレットを作成
ibmcloud ce secret create --name sap-credentials \
    --from-literal SAP_API_URL="YOUR_SAP_API_URL" \
    --from-literal SAP_COMPANY_ID="YOUR_COMPANY_ID" \
    --from-literal SAP_USER_ID="YOUR_USER_ID" \
    --from-literal SAP_PASSWORD="YOUR_PASSWORD" \
    --from-literal MCP_AUTH_TOKEN="YOUR_TOKEN"

# アプリケーションを作成
ibmcloud ce app create --name sap-successfactors-mcp \
    --image jp.icr.io/sap-mcp/sap-successfactors-mcp:latest \
    --env-from-secret sap-credentials \
    --port 8000 \
    --min-scale 1 \
    --max-scale 3 \
    --cpu 0.25 \
    --memory 0.5G
```

### 方法3: IBM Cloud Toolchainを使用（CI/CD）

最も自動化された方法です。

1. **IBM Cloud Toolchainを作成**
   - IBM Cloud Console → DevOps → Toolchains
   - 「Create toolchain」をクリック
   - 「Build your own toolchain」を選択

2. **GitHubリポジトリを接続**
   - GitHub統合を追加
   - リポジトリを選択

3. **Delivery Pipelineを設定**
   - Build Stage: Dockerイメージをビルド
   - Deploy Stage: Code Engineにデプロイ

4. **自動デプロイ**
   - コードをプッシュすると自動的にビルド・デプロイ

## Docker Desktopのインストール

Docker Desktopがインストールされていない場合：

1. **ダウンロード**
   - https://www.docker.com/products/docker-desktop

2. **インストール**
   - インストーラーを実行
   - WSL 2バックエンドを有効化（推奨）
   - 再起動が必要な場合があります

3. **起動確認**
   ```cmd
   docker version
   docker run hello-world
   ```

## よくある問題

### Docker Desktopが起動しない

**原因**: WSL 2が有効になっていない

**解決方法**:
```powershell
# PowerShellを管理者として実行
wsl --install
wsl --set-default-version 2
```

### Docker Desktopが遅い

**原因**: リソース不足

**解決方法**:
1. Docker Desktop設定を開く
2. Resources → Advanced
3. CPUとメモリを増やす

### ビルドエラー

**原因**: Dockerfileのパスが間違っている

**解決方法**:
```cmd
# 正しいパスを指定
docker build -t sap-mcp:latest -f deployment/Dockerfile .
```

## 推奨デプロイ方法の比較

| 方法 | 難易度 | 必要なツール | 自動化 | 推奨度 |
|------|--------|--------------|--------|--------|
| Docker Desktop | 低 | Docker Desktop | 半自動 | ⭐⭐⭐⭐⭐ |
| IBM Cloud Build | 中 | IBM Cloud CLI | 半自動 | ⭐⭐⭐⭐ |
| IBM Toolchain | 高 | なし | 完全自動 | ⭐⭐⭐⭐⭐ |

## サポート

問題が解決しない場合：

1. Docker Desktopのログを確認
2. IBM Cloud Supportに問い合わせ
3. GitHub Issuesで報告

# Made with Bob