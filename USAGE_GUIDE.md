# SAP SuccessFactors MCP Server 使用ガイド（更新版）

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

### 6. add_user_to_admin_role - 管理者権限グループへの追加（NEW）

既存ユーザーを「IBM管理者用権限グループ」に追加します。

**パラメータ：**
- `user_id` (必須): ユーザーID

**使用例：**
```python
result = add_user_to_admin_role(user_id="USER001")
```

**レスポンス：**
```json
{
  "success": true,
  "user_id": "USER001",
  "role_name": "IBM管理者用権限グループ",
  "message": "ユーザー 'USER001' を 'IBM管理者用権限グループ' に追加しました",
  "data": {
    "roleId": "ROLE_ID",
    "status": "added",
    "totalMembers": 15
  }
}
```

### 7. create_user_with_admin_role - ユーザー作成と権限追加（NEW・推奨）

新規ユーザーを作成し、同時に「IBM管理者用権限グループ」に追加します。

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
result = create_user_with_admin_role(
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
  "message": "ユーザー 'USER001' を作成し、IBM管理者用権限グループに追加しました",
  "user_creation": {
    "success": true,
    "message": "ユーザー 'USER001' を正常に作成しました"
  },
  "role_assignment": {
    "success": true,
    "message": "ユーザー 'USER001' を 'IBM管理者用権限グループ' に追加しました"
  }
}
```

**特徴：**
- ユーザー作成と権限グループへの追加を一度に実行
- 既存メンバーを保持したまま新規ユーザーを追加
- 重複チェック機能付き（既に存在する場合はスキップ）
- エラーハンドリング（ユーザー作成失敗時は権限追加をスキップ）

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

## 権限グループ機能の詳細

### 概要

新しく追加された権限グループ機能により、ユーザー作成時に自動的に「IBM管理者用権限グループ」に追加できます。

### 使用シナリオ

#### シナリオ1: 新規ユーザー作成と同時に権限付与（推奨）

```python
from src.tools.user_management import create_sap_user_with_admin_role

result = create_sap_user_with_admin_role(
    user_id="NEW001",
    username="newuser",
    first_name="新規",
    last_name="ユーザー",
    email="new.user@example.com"
)

if result['success']:
    print("✅ ユーザー作成と権限付与が完了しました")
else:
    print(f"❌ エラー: {result['message']}")
```

#### シナリオ2: 既存ユーザーに権限を追加

```python
from src.tools.user_management import add_user_to_admin_role

result = add_user_to_admin_role(user_id="EXISTING_USER")

if result['success']:
    print("✅ 権限グループに追加しました")
else:
    print(f"❌ エラー: {result['message']}")
```

### 差分追加の仕組み

この機能は、既存のメンバーを削除せずに新しいユーザーを追加します：

1. 現在の権限グループメンバーを取得
2. 新しいユーザーが既に存在するかチェック
3. 既存メンバー + 新規ユーザーのリストを作成
4. 権限グループを更新

これにより、既存のメンバーが誤って削除されることを防ぎます。

### テスト方法

権限グループ機能のテストスクリプトを実行：

```bash
python test_permission_role.py
```

このテストでは以下を確認します：
- 権限グループ「IBM管理者用権限グループ」の存在確認
- 現在のメンバー一覧の取得
- 権限グループへのユーザー追加機能の動作確認

### Watsonx Orchestrateでの使用例

Slackからの自動化フロー：

```
1. Slackで新規ユーザー作成リクエスト
   ↓
2. Watson Orchestrateがリクエストを受信
   ↓
3. MCPサーバーの create_user_with_admin_role を呼び出し
   ↓
4. SAP SuccessFactorsにユーザーアカウントを作成
   ↓
5. 作成したユーザーを「IBM管理者用権限グループ」に追加
   ↓
6. 結果をWatson Orchestrate経由でSlackに通知
```

### 権限グループ名のカスタマイズ

デフォルトの権限グループ名は「IBM管理者用権限グループ」です。
別の権限グループを使用する場合は、`src/tools/user_management.py`の`ADMIN_ROLE_NAME`を変更してください：

```python
# src/tools/user_management.py の add_user_to_admin_role 関数内
ADMIN_ROLE_NAME = "あなたの権限グループ名"
```

### エラーハンドリング

#### 権限グループが見つからない場合

```json
{
  "success": false,
  "message": "権限グループへの追加に失敗しました: 権限グループが見つかりません: IBM管理者用権限グループ"
}
```

**解決方法：**
1. SAP SuccessFactorsで権限グループが存在するか確認
2. 権限グループ名が正確に一致しているか確認
3. APIユーザーに権限グループへのアクセス権限があるか確認

#### ユーザーが既に存在する場合

```json
{
  "success": true,
  "message": "ユーザー 'USER001' は既に 'IBM管理者用権限グループ' のメンバーです",
  "data": {
    "status": "already_exists"
  }
}
```

これはエラーではなく、重複を防ぐための正常な動作です。

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