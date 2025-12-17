# IBM Cloud Code Engine デプロイガイド（Windows版）

このガイドでは、Windows環境からSAP SuccessFactors MCPサーバーをIBM Cloud Code Engineにデプロイする手順を説明します。

## 前提条件

- ✅ Windows 10/11
- ✅ IBM Cloud アカウント（無料アカウントでOK）
- ✅ PowerShell 5.1以上
- ✅ Docker Desktop for Windows（オプション - ローカルでイメージをビルドする場合）

## デプロイ手順

### ステップ1: IBM Cloud CLIのセットアップ

#### 1.1 IBM Cloud CLIのインストール（Windows）

**方法A: PowerShellでインストール（推奨）**

1. PowerShellを**管理者として**実行
2. 以下のコマンドを実行：

```powershell
# IBM Cloud CLIのインストール
Set-ExecutionPolicy Bypass -Scope Process -Force
iex (New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```

**方法B: インストーラーを使用**

1. [IBM Cloud CLI ダウンロードページ](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli)にアクセス
2. Windows用インストーラー（.exe）をダウンロード
3. インストーラーを実行してインストール

#### 1.2 インストールの確認

```powershell
# バージョン確認
ibmcloud --version
```

期待される出力：
```
ibmcloud version 2.x.x
```

#### 1.2 必要なプラグインのインストール

```bash
# Code Engineプラグインのインストール
ibmcloud plugin install code-engine

# Container Registryプラグインのインストール
ibmcloud plugin install container-registry
```

**インストールの確認**

```bash
# インストール済みプラグインの一覧を表示
ibmcloud plugin list
```

期待される出力：
```
Listing installed plug-ins...

Plugin Name                            Version   Status             Private endpoints supported
code-engine/ce                         1.x.x                        false
container-registry                     1.x.x                        true
```

#### 1.3 IBM Cloudへのログイン

```bash
# SSOでログイン
ibmcloud login --sso
```

ログイン後、以下のメッセージが表示される場合があります：
```
アカウントがターゲットになっていません。'ibmcloud target -c ACCOUNT_ID' を使用してください
```

#### 1.4 アカウントのターゲット設定

新しいアカウントでログインした場合、アカウントIDを明示的に指定する必要があります。

```bash
# 利用可能なアカウントの一覧を表示
ibmcloud account list

# アカウントをターゲットに設定（ACCOUNT_IDは上記コマンドで表示されたIDを使用）
ibmcloud target -c ACCOUNT_ID
```

**例**:
```bash
# アカウント一覧の表示例
ibmcloud account list
# 出力例:
# Retrieving all accounts of user@example.com...
# OK
# Account GUID                          Name                State    Owner
# 1234567890abcdef1234567890abcdef      My Account          ACTIVE   user@example.com

# アカウントIDを指定してターゲット設定
ibmcloud target -c 1234567890abcdef1234567890abcdef
```

#### 1.5 リージョンの選択

```bash
# 東京リージョンを選択
ibmcloud target -r jp-tok
```

#### 1.6 リソース・グループのターゲット設定

```bash
# 利用可能なリソース・グループの一覧を表示
ibmcloud resource groups

# デフォルトのリソース・グループをターゲットに設定
ibmcloud target -g Default
```

**注意**:
- `Default`は標準のリソース・グループ名です
- 別のリソース・グループを使用する場合は、`Default`を実際のリソース・グループ名に置き換えてください

#### 1.7 ターゲット設定の確認

すべての設定が完了したら、現在のターゲット設定を確認します：

```bash
# 現在のターゲット設定を確認
ibmcloud target
```

期待される出力：
```
API endpoint:      https://cloud.ibm.com
Region:            jp-tok
User:              user@example.com
Account:           My Account (1234567890abcdef1234567890abcdef)
Resource group:    Default
```

**トラブルシューティング**:
- 「アカウントがターゲットになっていません」→ `ibmcloud target -c ACCOUNT_ID`
- 「リソース・グループがターゲットになっていません」→ `ibmcloud target -g Default`
- 設定を一度にまとめて行う場合：
  ```bash
  ibmcloud target -c ACCOUNT_ID -r jp-tok -g Default
  ```

### ステップ2: Code Engineプロジェクトの作成

```bash
# プロジェクトの作成
ibmcloud ce project create --name sap-mcp-server

# プロジェクトの選択
ibmcloud ce project select --name sap-mcp-server
```

### ステップ3: Container Registryの設定

#### 3.1 Container Registryネームスペースの作成

```bash
# ネームスペースの作成
ibmcloud cr namespace-add sap-mcp

# ネームスペースの確認
ibmcloud cr namespace-list
```

#### 3.2 Container Registryへのログイン

```bash
# レジストリへのログイン
ibmcloud cr login
```

### ステップ4: Dockerイメージのビルドとプッシュ

#### 4.1 プロジェクトルートに移動

```bash
cd sap-successfactors-mcp
```

#### 4.2 Dockerイメージのビルド

```bash
# イメージのビルド
docker build -t jp.icr.io/sap-mcp/mcp-server:latest -f deployment/Dockerfile .
```

#### 4.3 イメージのプッシュ

```bash
# Container Registryにプッシュ
docker push jp.icr.io/sap-mcp/mcp-server:latest

# イメージの確認
ibmcloud cr image-list
```

### ステップ5: シークレットの作成

SAP認証情報を安全に保存するためのシークレットを作成します。

```bash
ibmcloud ce secret create --name sap-credentials \
  --from-literal SAP_API_URL=https://api68sales.successfactors.com \
  --from-literal SAP_COMPANY_ID=SFCPART001687 \
  --from-literal SAP_USER_ID=Bobapiadmin \
  --from-literal SAP_PASSWORD=Ibm12345!! \
  --from-literal MCP_AUTH_TOKEN=UCgZnTbqa7nxV1wwWSv6b9nXYTjOG2/Q9qbMMhXhK9s= \
  --from-literal MCP_PORT=8080
```

**重要**: `MCP_AUTH_TOKEN`は強力なランダム文字列に変更してください。

生成例：
```bash
# ランダムトークンの生成（Linux/macOS）
openssl rand -base64 32

# ランダムトークンの生成（Windows PowerShell）
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### ステップ6: アプリケーションのデプロイ

#### 6.1 最小構成でのデプロイ（無料枠内）

```bash
ibmcloud ce application create \
  --name sap-mcp-server \
  --image jp.icr.io/sap-mcp/mcp-server:latest \
  --cpu 0.125 \
  --memory 256M \
  --min-scale 1 \
  --max-scale 1 \
  --port 8080 \
  --env-from-secret sap-credentials \
  --registry-secret icr-secret
```

**パラメータ説明:**
- `--cpu 0.125`: 最小CPU（無料枠内）
- `--memory 256M`: 最小メモリ（無料枠内）
- `--min-scale 1`: 常時1インスタンス稼働
- `--max-scale 1`: 最大1インスタンス
- `--port 8080`: アプリケーションポート
- `--env-from-secret`: シークレットから環境変数を読み込み

#### 6.2 デプロイの確認

```bash
# アプリケーションの状態確認
ibmcloud ce application get --name sap-mcp-server

# URLの取得
ibmcloud ce application get --name sap-mcp-server --output url
```

出力例：
```
https://sap-mcp-server.xxxxxx.jp-tok.codeengine.appdomain.cloud
```

### ステップ7: 動作確認

#### 7.1 ヘルスチェック

```bash
# URLを環境変数に設定
export MCP_URL=$(ibmcloud ce application get --name sap-mcp-server --output url)

# ヘルスチェック
curl $MCP_URL/health
```

期待される出力：
```
OK
```

#### 7.2 ログの確認

```bash
# リアルタイムログの表示
ibmcloud ce application logs --name sap-mcp-server --follow

# 最新のログを表示
ibmcloud ce application logs --name sap-mcp-server --tail 100
```

### ステップ8: GitHub Actionsの設定

#### 8.1 GitHubリポジトリの作成

```bash
# Gitリポジトリの初期化
git init
git add .
git commit -m "Initial commit: SAP SuccessFactors MCP Server"

# GitHubリポジトリの作成（GitHub CLIを使用）
gh repo create sap-successfactors-mcp --public --source=. --remote=origin --push
```

#### 8.2 GitHub Actionsワークフローの更新

`.github/workflows/keepalive.yml`を編集して、実際のURLに置き換えます：

```yaml
# 以下の行を実際のURLに置き換え
RESPONSE=$(curl -f -s -o /dev/null -w "%{http_code}" https://sap-mcp-server.xxxxxx.jp-tok.codeengine.appdomain.cloud/health || echo "000")
```

#### 8.3 GitHub Actionsの有効化

1. GitHubリポジトリページにアクセス
2. 「Actions」タブをクリック
3. ワークフローを有効化

### ステップ9: Watsonx Orchestrateとの統合

#### 9.1 MCP接続情報の準備

- **Server Name**: SAP SuccessFactors User Management
- **SSE Endpoint**: `https://sap-mcp-server.xxxxxx.jp-tok.codeengine.appdomain.cloud/sse`
- **Authentication Token**: シークレットで設定した`MCP_AUTH_TOKEN`

#### 9.2 Watsonx Orchestrateでの設定

1. Watsonx Orchestrateにログイン
2. 「Skills」または「Integrations」セクションに移動
3. 「Add MCP Server」を選択
4. 接続情報を入力
5. 接続テスト
6. スキルとして登録

## アップデート手順

### コードの更新

```bash
# 1. コードを更新
git pull

# 2. 新しいイメージをビルド
docker build -t jp.icr.io/sap-mcp/mcp-server:latest -f deployment/Dockerfile .

# 3. イメージをプッシュ
docker push jp.icr.io/sap-mcp/mcp-server:latest

# 4. アプリケーションを更新
ibmcloud ce application update --name sap-mcp-server \
  --image jp.icr.io/sap-mcp/mcp-server:latest
```

### 環境変数の更新

```bash
# シークレットの削除
ibmcloud ce secret delete --name sap-credentials

# 新しいシークレットの作成
ibmcloud ce secret create --name sap-credentials \
  --from-literal SAP_API_URL=... \
  --from-literal SAP_COMPANY_ID=... \
  # ... 他の環境変数

# アプリケーションの再起動
ibmcloud ce application update --name sap-mcp-server
```

## トラブルシューティング

### アプリケーションが起動しない

```bash
# ログを確認
ibmcloud ce application logs --name sap-mcp-server --tail 100

# アプリケーションの詳細を確認
ibmcloud ce application get --name sap-mcp-server
```

### イメージのプッシュに失敗

```bash
# Container Registryへの再ログイン
ibmcloud cr login

# ネームスペースの確認
ibmcloud cr namespace-list
```

### 環境変数が反映されない

```bash
# シークレットの確認
ibmcloud ce secret get --name sap-credentials

# アプリケーションの再起動
ibmcloud ce application update --name sap-mcp-server
```

## コスト管理

### 無料枠の確認

```bash
# リソース使用状況の確認
ibmcloud ce project get --name sap-mcp-server
```

### 無料枠内での運用

- **vCPU**: 0.125 vCPU × 24時間 × 30日 = 90,000 vCPU秒/月（無料枠: 100,000）
- **メモリ**: 256MB × 24時間 × 30日 = 184,320 MB秒/月（無料枠: 200,000）
- **結果**: ✅ 無料枠内で運用可能

## クリーンアップ

### アプリケーションの削除

```bash
# アプリケーションの削除
ibmcloud ce application delete --name sap-mcp-server

# シークレットの削除
ibmcloud ce secret delete --name sap-credentials

# プロジェクトの削除
ibmcloud ce project delete --name sap-mcp-server
```

### Container Registryのクリーンアップ

```bash
# イメージの削除
ibmcloud cr image-rm jp.icr.io/sap-mcp/mcp-server:latest

# ネームスペースの削除（オプション）
ibmcloud cr namespace-rm sap-mcp
```

## 参考リンク

- [IBM Cloud Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [IBM Cloud CLI Reference](https://cloud.ibm.com/docs/cli)
- [Container Registry Documentation](https://cloud.ibm.com/docs/Registry)

## サポート

問題が発生した場合：
1. ログを確認
2. 環境変数を確認
3. ネットワーク接続を確認
4. IBM Cloud サポートに問い合わせ