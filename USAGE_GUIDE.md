# SAP SuccessFactors MCP Server 使用ガイド

## 概要

このMCPサーバーは、Watsonx OrchestrateからSAP SuccessFactorsのユーザー管理機能にアクセスするためのインターフェースを提供します。

## セットアップ完了の確認

以下のテストがすべて成功していることを確認してください：

```bash
cd sap-successfactors-mcp
python test_integration.py
```

期待される出力：
```
🎉 すべてのテストが成功しました！
```

## MCPサーバーの起動

### ローカル環境での起動

```bash
cd sap-successfactors-mcp
python -m src.server
```

サーバーが起動すると、以下のようなログが表示されます：

```
2024-XX-XX XX:XX:XX - src.server - INFO - MCP Server initialized
2024-XX-XX XX:XX:XX - src.server - INFO - Starting MCP Server on port 8000
```

## 利用可能なツール

MCPサーバーは以下のツールを提供します：

### 1. create_user - ユーザー作成

新規ユーザーをSAP SuccessFactorsに作成します。

**パラメータ：**
- `user_id` (必須): ユーザーID（一意である必要があります）
- `username` (必須): ユーザー名（ログイン名）
- `first_name`: 名
- `last_name`: 姓
- `email`: メールアドレス
- `locale`: ロケール（デフォルト: ja_JP）
- `timezone`: タイムゾーン（デフォルト: Asia/Tokyo）

**使用例：**
```python
result = create_user(
    user_id="USER001",
    username="taro.yamada",
    first_name="太郎",
    last_name="山田",
    email="taro.yamada@example.com",
    locale="ja_JP",
    timezone="Asia/Tokyo"
)
```

**レスポンス：**
```json
{
  "success": true,
  "user_id": "USER001",
  "message": "ユーザー 'USER001' を正常に作成しました",
  "data": { ... }
}
```

### 2. get_user - ユーザー情報取得

指定したユーザーIDのユーザー情報を取得します。

**パラメータ：**
- `user_id` (必須): ユーザーID

**使用例：**
```python
result = get_user(user_id="USER001")
```

### 3. update_user - ユーザー情報更新

既存ユーザーの情報を更新します。

**パラメータ：**
- `user_id` (必須): ユーザーID
- `first_name`: 名
- `last_name`: 姓
- `email`: メールアドレス
- `locale`: ロケール
- `timezone`: タイムゾーン

**使用例：**
```python
result = update_user(
    user_id="USER001",
    email="new.email@example.com"
)
```

### 4. list_users - ユーザー一覧取得

ユーザー一覧を取得します。

**パラメータ：**
- `top`: 取得件数（デフォルト: 10）
- `skip`: スキップ件数（デフォルト: 0）
- `filter_query`: フィルタクエリ（OData形式）

**使用例：**
```python
result = list_users(top=20, skip=0)
```

### 5. test_connection - 接続テスト

SAP SuccessFactors APIへの接続をテストします。

**使用例：**
```python
result = test_connection()
```

## Watsonx Orchestrateとの統合

### 1. MCPサーバーのデプロイ

#### オプションA: ローカル実行（開発・テスト用）

```bash
python -m src.server
```

#### オプションB: IBM Cloud Code Engineへのデプロイ（本番用）

詳細は `IMPLEMENTATION_PLAN.md` の「IBM Cloud Code Engine デプロイ」セクションを参照してください。

### 2. Watsonx Orchestrateでの設定

1. **Watsonx Orchestrateにログイン**
   - IBM社内Sandbox環境にアクセス

2. **MCP接続の追加**
   - 「Skills」または「Integrations」セクションに移動
   - 「Add MCP Server」を選択

3. **接続情報の入力**
   - Server Name: `SAP SuccessFactors User Management`
   - SSE Endpoint: `http://localhost:8000/sse` (ローカル) または Code EngineのURL
   - Authentication Token: `.env`ファイルの`MCP_AUTH_TOKEN`

4. **スキルの登録**
   - 接続後、利用可能なツールが表示される
   - 必要なツールを選択してスキルとして登録

### 3. 使用例

Watsonx Orchestrateのチャットインターフェースで以下のように入力：

```
SAP SuccessFactorsに新しいユーザーを作成してください。
ユーザーID: USER001
ユーザー名: taro.yamada
名: 太郎
姓: 山田
メールアドレス: taro.yamada@example.com
```

## トラブルシューティング

### エラー: 認証失敗

**症状：** `SAPAuthenticationError: 認証に失敗しました`

**解決方法：**
1. `.env`ファイルの認証情報を確認
2. SAP管理画面でユーザーが有効か確認
3. パスワードが正しいか確認

### エラー: アクセス拒否

**症状：** `SAPAPIError: アクセスが拒否されました`

**解決方法：**
1. SAP管理画面でAPIユーザーの権限を確認
2. 必要な権限（User Management、OData API Access）が付与されているか確認

### エラー: ユーザー作成失敗

**症状：** ユーザー作成時にエラーが発生

**解決方法：**
1. ユーザーIDが一意であることを確認
2. 必須フィールド（user_id、username）が指定されているか確認
3. SAP管理画面でユーザー作成権限があるか確認

## ログの確認

MCPサーバーのログは標準出力に出力されます。

ログレベルを変更する場合は、`.env`ファイルで設定：

```env
LOG_LEVEL=DEBUG
```

利用可能なログレベル：
- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 一般的な情報（デフォルト）
- `WARNING`: 警告メッセージ
- `ERROR`: エラーメッセージ

## セキュリティのベストプラクティス

1. **認証情報の管理**
   - `.env`ファイルをGitにコミットしない
   - 本番環境では環境変数またはシークレット管理サービスを使用

2. **MCP認証トークン**
   - 強力なランダムトークンを使用
   - 定期的にトークンを更新

3. **ネットワークセキュリティ**
   - 本番環境ではHTTPSを使用
   - ファイアウォールで適切にアクセス制限

## サポート

問題が発生した場合：

1. `test_integration.py`を実行して基本機能を確認
2. ログを確認してエラーメッセージを特定
3. `SAP_CREDENTIALS_GUIDE.md`を参照して認証情報を確認
4. `IMPLEMENTATION_PLAN.md`を参照して設定を確認

## 次のステップ

- [ ] ローカル環境でMCPサーバーを起動
- [ ] Watsonx OrchestrateでMCP接続を設定
- [ ] テストユーザーを作成して動作確認
- [ ] IBM Cloud Code Engineへのデプロイ（本番環境）
- [ ] エンドツーエンドテストの実施