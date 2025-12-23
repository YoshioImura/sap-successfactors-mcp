# SAP SuccessFactors MCP Server デプロイガイド

## 概要

このガイドでは、SAP SuccessFactors MCP ServerをIBM Cloud Code Engineにデプロイする手順を説明します。

## 前提条件

### 必須ツール

1. **IBM Cloud CLI**
   - インストール: https://cloud.ibm.com/docs/cli
   - バージョン確認: `ibmcloud --version`

2. **Docker Desktop**
   - インストール: https://www.docker.com/products/docker-desktop
   - バージョン確認: `docker --version`

3. **Git**
   - インストール: https://git-scm.com/downloads
   - バージョン確認: `git --version`

### IBM Cloudアカウント

- IBM Cloudアカウント（無料プランでも可）
- Code Engineへのアクセス権限

## デプロイ手順

### 方法1: 自動デプロイスクリプト（推奨）

#### Windows

```cmd
cd sap-successfactors-mcp
deploy.bat
```

#### macOS/Linux

```bash
cd sap-successfactors-mcp
chmod +x deploy.sh
./deploy.sh
```

スクリプトは以下を自動的に実行します：
1. 環境変数の確認
2. IBM Cloudへのログイン
3. Dockerイメージのビルドとプッシュ
4. Code Engineアプリケーションのデプロイ
5. シークレットの作成と設定

### 方法2: 手動デプロイ

#### ステップ1: IBM Cloudにログイン

```bash
ibmcloud login --sso
```

ブラウザが開くので、ワンタイムパスコードを取得してターミナルに入力します。

#### ステップ2: Code Engineプラグインのインストール

```bash
ibmcloud plugin install code-engine
```

#### ステップ3: Code Engineプロジェクトの作成

```bash
# プロジェクト一覧を表示
ibmcloud ce project list

# 新しいプロジェクトを作成（または既存のプロジェクトを選択）
ibmcloud ce project create --name sap-mcp-project --region jp-tok

# プロジェクトを選択
ibmcloud ce project select --name sap-mcp-project
```

#### ステップ4: Container Registryの設定

```bash
# Container Registryにログイン
ibmcloud cr login

# 名前空間を作成
ibmcloud cr namespace-add sap-mcp
```

#### ステップ5: Dockerイメージのビルドとプッシュ

```bash
# Dockerイメージをビルド
docker build -t jp.icr.io/sap-mcp/sap-successfactors-mcp:latest -f deployment/Dockerfile .

# Dockerイメージをプッシュ
docker push jp.icr.io/sap-mcp/sap-successfactors-mcp:latest
```

#### ステップ6: シークレットの作成

```bash
# .envファイルから環境変数を読み込む
source .env

# シークレットを作成
ibmcloud ce secret create --name sap-credentials \
    --from-literal SAP_API_URL="$SAP_API_URL" \
    --from-literal SAP_COMPANY_ID="$SAP_COMPANY_ID" \
    --from-literal SAP_USER_ID="$SAP_USER_ID" \
    --from-literal SAP_PASSWORD="$SAP_PASSWORD" \
    --from-literal MCP_AUTH_TOKEN="$MCP_AUTH_TOKEN" \
    --from-literal LOG_LEVEL="${LOG_LEVEL:-INFO}"
```

#### ステップ7: アプリケーションのデプロイ

```bash
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

#### ステップ8: アプリケーションURLの取得

```bash
ibmcloud ce app get --name sap-successfactors-mcp --output url
```

## デプロイ後の確認

### ヘルスチェック

```bash
# アプリケーションのURLを取得
APP_URL=$(ibmcloud ce app get --name sap-successfactors-mcp --output url)

# ヘルスチェック
curl $APP_URL/health
```

期待される出力: `OK`

### ログの確認

```bash
# リアルタイムログの表示
ibmcloud ce app logs --name sap-successfactors-mcp --follow

# 最新のログを表示
ibmcloud ce app logs --name sap-successfactors-mcp --tail 100
```

### アプリケーション情報の確認

```bash
ibmcloud ce app get --name sap-successfactors-mcp
```

## アップデート手順

コードを更新した後、以下の手順でアプリケーションを更新します：

### 自動アップデート

```bash
# Windows
deploy.bat

# macOS/Linux
./deploy.sh
```

### 手動アップデート

```bash
# 1. Dockerイメージを再ビルド
docker build -t jp.icr.io/sap-mcp/sap-successfactors-mcp:latest -f deployment/Dockerfile .

# 2. Dockerイメージをプッシュ
docker push jp.icr.io/sap-mcp/sap-successfactors-mcp:latest

# 3. アプリケーションを更新
ibmcloud ce app update --name sap-successfactors-mcp \
    --image jp.icr.io/sap-mcp/sap-successfactors-mcp:latest
```

## Watsonx Orchestrateとの統合

### 1. SSE Endpointの取得

```bash
APP_URL=$(ibmcloud ce app get --name sap-successfactors-mcp --output url)
echo "SSE Endpoint: $APP_URL/sse"
```

### 2. Watsonx Orchestrateでの設定

1. Watsonx Orchestrateにログイン
2. 「Skills」または「Integrations」セクションに移動
3. 「Add MCP Server」を選択
4. 以下の情報を入力：
   - Server Name: `SAP SuccessFactors User Management`
   - SSE Endpoint: `<APP_URL>/sse`
   - Authentication Token: `.env`ファイルの`MCP_AUTH_TOKEN`

### 3. 利用可能なツールの確認

接続後、以下のツールが利用可能になります：

- `create_user`: ユーザー作成
- `create_user_with_admin_role`: ユーザー作成と権限グループ追加（推奨）
- `add_user_to_admin_role`: 既存ユーザーを権限グループに追加
- `get_user`: ユーザー情報取得
- `update_user`: ユーザー情報更新
- `list_users`: ユーザー一覧取得
- `test_connection`: 接続テスト

## トラブルシューティング

### デプロイエラー

#### エラー: "Image pull failed"

**原因**: Dockerイメージがプッシュされていない、または名前が間違っている

**解決方法**:
```bash
# イメージが存在するか確認
ibmcloud cr image-list | grep sap-successfactors-mcp

# イメージを再プッシュ
docker push jp.icr.io/sap-mcp/sap-successfactors-mcp:latest
```

#### エラー: "Secret not found"

**原因**: シークレットが作成されていない

**解決方法**:
```bash
# シークレットを再作成
ibmcloud ce secret create --name sap-credentials \
    --from-literal SAP_API_URL="$SAP_API_URL" \
    --from-literal SAP_COMPANY_ID="$SAP_COMPANY_ID" \
    --from-literal SAP_USER_ID="$SAP_USER_ID" \
    --from-literal SAP_PASSWORD="$SAP_PASSWORD" \
    --from-literal MCP_AUTH_TOKEN="$MCP_AUTH_TOKEN"
```

### アプリケーションエラー

#### エラー: "Application not responding"

**原因**: アプリケーションが起動していない、またはクラッシュしている

**解決方法**:
```bash
# ログを確認
ibmcloud ce app logs --name sap-successfactors-mcp --tail 100

# アプリケーションを再起動
ibmcloud ce app update --name sap-successfactors-mcp --image jp.icr.io/sap-mcp/sap-successfactors-mcp:latest
```

#### エラー: "SAP API connection failed"

**原因**: SAP認証情報が間違っている、またはネットワークエラー

**解決方法**:
1. シークレットの環境変数を確認
2. SAP SuccessFactorsへの接続をテスト
3. 必要に応じてシークレットを更新

```bash
# シークレットを削除
ibmcloud ce secret delete --name sap-credentials --force

# 正しい認証情報でシークレットを再作成
ibmcloud ce secret create --name sap-credentials \
    --from-literal SAP_API_URL="$SAP_API_URL" \
    --from-literal SAP_COMPANY_ID="$SAP_COMPANY_ID" \
    --from-literal SAP_USER_ID="$SAP_USER_ID" \
    --from-literal SAP_PASSWORD="$SAP_PASSWORD" \
    --from-literal MCP_AUTH_TOKEN="$MCP_AUTH_TOKEN"

# アプリケーションを再起動
ibmcloud ce app update --name sap-successfactors-mcp --image jp.icr.io/sap-mcp/sap-successfactors-mcp:latest
```

## コスト管理

### 無料枠

IBM Cloud Code Engineの無料枠：
- 月間100,000 vCPU秒
- 月間200,000 GBメモリ秒
- 月間100,000リクエスト

### コスト最適化

1. **最小スケールを0に設定**（開発環境）
   ```bash
   ibmcloud ce app update --name sap-successfactors-mcp --min-scale 0
   ```

2. **リソースを削減**
   ```bash
   ibmcloud ce app update --name sap-successfactors-mcp \
       --cpu 0.125 \
       --memory 0.25G
   ```

3. **使用していない場合は削除**
   ```bash
   ibmcloud ce app delete --name sap-successfactors-mcp --force
   ```

## セキュリティのベストプラクティス

1. **シークレットの管理**
   - 環境変数を直接指定せず、必ずシークレットを使用
   - 定期的にMCP_AUTH_TOKENを更新

2. **アクセス制限**
   - 必要に応じてIP制限を設定
   - Watsonx Orchestrateからのアクセスのみを許可

3. **ログの監視**
   - 定期的にログを確認
   - 異常なアクセスパターンを検出

## サポート

問題が発生した場合：

1. ログを確認: `ibmcloud ce app logs --name sap-successfactors-mcp --tail 100`
2. アプリケーション状態を確認: `ibmcloud ce app get --name sap-successfactors-mcp`
3. README.mdとUSAGE_GUIDE.mdを参照
4. GitHub Issuesで報告

## 次のステップ

- [ ] デプロイが成功したことを確認
- [ ] Watsonx OrchestrateでMCP接続を設定
- [ ] テストユーザーを作成して動作確認
- [ ] Slackからのエンドツーエンドテスト
- [ ] 本番環境での運用開始

# Made with Bob