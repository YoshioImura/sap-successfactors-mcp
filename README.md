# SAP SuccessFactors MCP Server

Watsonx OrchestrateからSAP SuccessFactorsにユーザーアカウントを作成するためのMCPサーバー

## プロジェクト概要

このプロジェクトは、Model Context Protocol (MCP)を使用して、Watsonx OrchestrateとSAP SuccessFactorsを統合します。リモートMCPサーバーとして動作し、SAP SuccessFactors OData API v2を通じてユーザー管理機能を提供します。

## 機能

- ✅ SAP SuccessFactorsへのユーザーアカウント作成
- ✅ Basic認証によるセキュアなAPI接続
- ✅ Watsonx Orchestrateとのシームレスな統合
- ✅ IBM Cloud Code Engineでの無料デプロイ

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd sap-successfactors-mcp
```

### 2. Python仮想環境の作成

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、SAP認証情報を設定します：

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

`.env`ファイルを編集して、以下の情報を設定：

```env
SAP_API_URL=https://api68sales.successfactors.com
SAP_COMPANY_ID=YOUR_COMPANY_ID
SAP_USER_ID=YOUR_USER_ID
SAP_PASSWORD=YOUR_PASSWORD
MCP_AUTH_TOKEN=your-secure-random-token
```

### 5. API接続テスト

```bash
python test_sap_connection.py
```

成功すると以下のような出力が表示されます：

```
============================================================
  SAP SuccessFactors API接続テスト
============================================================

============================================================
  1. 環境変数の確認
============================================================
✓ SAP_API_URL: https://api68sales.successfactors.com
✓ SAP_COMPANY_ID: SFCPART001687
✓ SAP_USER_ID: yoshio.imura@ibm.com
✓ SAP_PASSWORD: ***********

✅ すべての環境変数が設定されています

============================================================
  2. Basic認証ヘッダーの作成
============================================================
認証文字列形式: SFCPART001687\yoshio.imura@ibm.com:***********
Base64エンコード完了: U0ZDUEFSV...
✅ Basic認証ヘッダーを作成しました

============================================================
  3. SAP SuccessFactors API接続テスト
============================================================
エンドポイント: https://api68sales.successfactors.com/odata/v2/User
パラメータ: {'$top': 1, '$format': 'json'}

APIリクエストを送信中...

ステータスコード: 200
✅ API接続成功!
```

## プロジェクト構造

```
sap-successfactors-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCPサーバーのメインエントリーポイント
│   ├── sap_client.py          # SAP SuccessFactors APIクライアント
│   ├── tools/
│   │   ├── __init__.py
│   │   └── user_management.py # ユーザー管理ツール
│   └── config/
│       ├── __init__.py
│       └── settings.py        # 設定管理
├── tests/
│   ├── __init__.py
│   └── test_sap_client.py
├── .github/
│   └── workflows/
│       └── keepalive.yml      # GitHub Actions自動ウェイクアップ
├── deployment/
│   ├── Dockerfile
│   └── ibm-code-engine.yaml   # IBM Code Engine設定
├── requirements.txt
├── .env.example
├── .env                       # ← Gitにコミットしない
├── .gitignore
├── test_sap_connection.py     # API接続テストスクリプト
└── README.md
```

## SAP認証情報の取得

詳細な手順は[SAP_CREDENTIALS_GUIDE.md](../SAP_CREDENTIALS_GUIDE.md)を参照してください。

### 必要な情報

1. **データセンターURL**: SAP SuccessFactorsのAPIサーバーURL
2. **Company ID**: 会社ID
3. **API User ID**: APIアクセス用のユーザーID
4. **API User Password**: APIユーザーのパスワード

### 必要な権限

APIユーザーには以下の権限が必要です：

- ☑ User Management
- ☑ OData API Access
- ☑ Create Users
- ☑ Edit Users
- ☑ View Users

## トラブルシューティング

### 401 Unauthorized エラー

**原因**: 認証情報が間違っている

**解決方法**:
1. `.env`ファイルの認証情報を確認
2. Company IDとUser IDの形式を確認（`CompanyID\UserID`）
3. パスワードに特殊文字が含まれている場合は正しくエスケープされているか確認

### 403 Forbidden エラー

**原因**: APIユーザーに必要な権限がない

**解決方法**:
1. SAP管理画面でAPIユーザーの権限を確認
2. Permission Roleに必要な権限が含まれているか確認
3. API Centerで「Allowed Users」にユーザーが追加されているか確認

### 404 Not Found エラー

**原因**: API URLが間違っている

**解決方法**:
1. データセンターURLを再確認
2. OData API v2のエンドポイントを確認: `/odata/v2/`

## 次のステップ

1. ✅ API接続テストが成功したら、MCPサーバーの実装に進みます
2. ✅ ローカルでMCPサーバーをテストします
3. ✅ IBM Cloud Code Engineにデプロイします
4. ✅ Watsonx Orchestrateと統合します

## ライセンス

MIT License

## サポート

問題が発生した場合は、以下を確認してください：

1. [SAP_CREDENTIALS_GUIDE.md](../SAP_CREDENTIALS_GUIDE.md) - 認証情報の取得方法
2. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - 実装計画の詳細
3. GitHub Issues - バグ報告や機能リクエスト