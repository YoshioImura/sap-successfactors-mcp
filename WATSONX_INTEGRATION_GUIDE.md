# Watsonx Orchestrate 統合ガイド

このガイドでは、SAP SuccessFactors MCPサーバーをWatsonx Orchestrateと統合する手順を説明します。

## 前提条件

- ✅ MCPサーバーがデプロイ済み（ローカルまたはIBM Cloud Code Engine）
- ✅ 統合テストが成功している
- ✅ Watsonx Orchestrateへのアクセス権限

## 統合手順

### ステップ1: MCP接続情報の準備

#### ローカル環境の場合

```
Server Name: SAP SuccessFactors User Management
SSE Endpoint: http://localhost:8000/sse
Authentication Token: sap-mcp-secure-token-2024
```

#### IBM Cloud Code Engine環境の場合

```
Server Name: SAP SuccessFactors User Management
SSE Endpoint: https://sap-mcp-server.xxxxxx.jp-tok.codeengine.appdomain.cloud/sse
Authentication Token: [Code Engineで設定したMCP_AUTH_TOKEN]
```

### ステップ2: Watsonx Orchestrateへのログイン

1. **IBM Watsonx Orchestrateにアクセス**
   - URL: https://orchestrate.ibm.com（または社内環境のURL）
   - IBM IDでログイン

2. **適切なワークスペースを選択**
   - 開発環境またはSandbox環境を選択

### ステップ3: MCP接続の追加

#### 3.1 統合メニューへのアクセス

1. 左側のナビゲーションメニューから「**Integrations**」または「**Skills**」を選択
2. 「**Add Integration**」または「**Connect to MCP**」ボタンをクリック

#### 3.2 MCP接続情報の入力

以下の情報を入力します：

| フィールド | 値 |
|----------|-----|
| **Connection Name** | SAP SuccessFactors User Management |
| **Connection Type** | Model Context Protocol (MCP) |
| **Transport** | SSE (Server-Sent Events) |
| **Endpoint URL** | http://localhost:8000/sse または https://your-server.cloud/sse |
| **Authentication Type** | Bearer Token |
| **Token** | [MCP_AUTH_TOKEN] |

#### 3.3 接続テスト

1. 「**Test Connection**」ボタンをクリック
2. 接続が成功すると、利用可能なツールのリストが表示されます

**期待される結果:**
```
✅ Connection successful
Available tools:
  - create_user
  - get_user
  - update_user
  - list_users
  - test_connection
```

### ステップ4: スキルの登録

#### 4.1 ツールの選択

接続が成功したら、以下のツールをスキルとして登録します：

1. **create_user** - ユーザー作成
   - 説明: SAP SuccessFactorsに新規ユーザーを作成します
   - カテゴリ: User Management

2. **get_user** - ユーザー情報取得
   - 説明: ユーザー情報を取得します
   - カテゴリ: User Management

3. **list_users** - ユーザー一覧取得
   - 説明: ユーザー一覧を取得します
   - カテゴリ: User Management

#### 4.2 スキルの設定

各スキルに対して以下を設定：

**create_user スキルの設定例:**

| 設定項目 | 値 |
|---------|-----|
| **Skill Name** | SAP ユーザー作成 |
| **Description** | SAP SuccessFactorsに新規ユーザーアカウントを作成します |
| **Category** | User Management |
| **Input Parameters** | user_id, username, first_name, last_name, email, locale, timezone |
| **Required Parameters** | user_id, username |
| **Output Format** | JSON |

#### 4.3 スキルの公開

1. 各スキルの設定を保存
2. 「**Publish**」ボタンをクリック
3. スキルが利用可能になるまで数分待機

### ステップ5: 動作確認

#### 5.1 チャットインターフェースでのテスト

Watsonx Orchestrateのチャットインターフェースで以下のように入力：

**テスト1: 接続確認**
```
SAP SuccessFactorsへの接続をテストしてください
```

期待される応答：
```
✅ SAP SuccessFactors APIへの接続に成功しました
```

**テスト2: ユーザー一覧取得**
```
SAP SuccessFactorsのユーザー一覧を3件取得してください
```

期待される応答：
```
3件のユーザーを取得しました：
1. User ID: 101072, Username: devans, Email: Darcy.Evans@bestrun.com
2. User ID: 103119, Username: 103119, Email: lchang@email.com
3. User ID: 103165, Username: 103165, Email: aryan.bansal@bestrunsap.com
```

**テスト3: ユーザー情報取得**
```
ユーザーID 101072 の情報を取得してください
```

期待される応答：
```
ユーザー情報を取得しました：
- User ID: 101072
- Username: devans
- Display Name: Darcy Evans
- Email: Darcy.Evans@bestrun.com
- Locale: en_US
- Timezone: Europe/London
```

**テスト4: ユーザー作成（実際の作成前に確認）**
```
SAP SuccessFactorsに新しいユーザーを作成したいです。
ユーザーID: TEST001
ユーザー名: test.user
名: テスト
姓: ユーザー
メールアドレス: test.user@example.com
```

期待される応答：
```
以下の情報でユーザーを作成しますか？
- User ID: TEST001
- Username: test.user
- First Name: テスト
- Last Name: ユーザー
- Email: test.user@example.com
- Locale: ja_JP
- Timezone: Asia/Tokyo

[確認] [キャンセル]
```

### ステップ6: 自然言語での操作

Watsonx Orchestrateは自然言語での指示を理解します。以下のような表現が可能です：

#### ユーザー作成の例

```
山田太郎さんのアカウントを作成してください。
メールアドレスは taro.yamada@example.com です。
```

```
新入社員の佐藤花子さん（hanako.sato@example.com）のSAPアカウントを作成お願いします。
```

#### ユーザー検索の例

```
メールアドレスに "evans" を含むユーザーを探してください
```

```
最近作成されたユーザーを5件表示してください
```

### ステップ7: ワークフローへの統合

#### 7.1 ワークフローの作成

1. Watsonx Orchestrateで「**Workflows**」セクションに移動
2. 「**Create Workflow**」をクリック
3. ワークフロー名を入力（例: 新入社員オンボーディング）

#### 7.2 スキルの追加

1. ワークフローエディタで「**Add Skill**」をクリック
2. 「SAP ユーザー作成」スキルを選択
3. 入力パラメータをマッピング

#### 7.3 ワークフロー例: 新入社員オンボーディング

```
1. 人事システムから新入社員情報を取得
   ↓
2. SAP SuccessFactorsにユーザーアカウントを作成
   - スキル: create_user
   - 入力: 新入社員情報
   ↓
3. メール通知を送信
   - 宛先: 新入社員、上司、IT部門
   - 内容: アカウント作成完了通知
   ↓
4. 完了
```

## トラブルシューティング

### 接続エラー

**症状**: "Connection failed" エラーが表示される

**解決方法:**
1. MCPサーバーが起動しているか確認
   ```bash
   curl http://localhost:8000/health
   ```
2. エンドポイントURLが正しいか確認
3. 認証トークンが正しいか確認

### ツールが表示されない

**症状**: 接続は成功するが、ツールが表示されない

**解決方法:**
1. MCPサーバーのログを確認
2. サーバーを再起動
3. Watsonx Orchestrateで接続を削除して再作成

### ユーザー作成が失敗する

**症状**: "User creation failed" エラー

**解決方法:**
1. SAP認証情報を確認
2. ユーザーIDが一意であることを確認
3. 必須フィールドがすべて入力されているか確認
4. SAP管理画面でAPI権限を確認

### タイムアウトエラー

**症状**: "Request timeout" エラー

**解決方法:**
1. ネットワーク接続を確認
2. SAP APIサーバーの状態を確認
3. MCPサーバーのリソースを確認（CPU、メモリ）

## ベストプラクティス

### 1. エラーハンドリング

ワークフローでは必ずエラーハンドリングを実装：

```
Try:
  SAP ユーザー作成
Catch:
  エラーログを記録
  管理者に通知
  代替処理を実行
```

### 2. 入力検証

ユーザー入力を検証してから実行：

- メールアドレスの形式チェック
- ユーザーIDの重複チェック
- 必須フィールドの存在チェック

### 3. ログとモニタリング

- すべての操作をログに記録
- 定期的にログを確認
- 異常なパターンを検出

### 4. セキュリティ

- 認証トークンを定期的に更新
- アクセス権限を最小限に設定
- 機密情報をログに出力しない

## 高度な使用例

### 例1: バルクユーザー作成

```
CSVファイルから複数のユーザーを一括作成してください。
ファイルパス: /path/to/new_employees.csv
```

### 例2: 条件付きユーザー作成

```
部署が "営業部" の新入社員のみSAPアカウントを作成してください。
```

### 例3: 既存ユーザーの更新

```
ユーザーID 101072 のメールアドレスを new.email@example.com に更新してください。
```

## 参考リソース

- [Watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [SAP SuccessFactors API Documentation](https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM)

## サポート

問題が発生した場合：

1. **ローカルテスト**: `test_integration.py`を実行
2. **ログ確認**: MCPサーバーのログを確認
3. **ドキュメント参照**: `USAGE_GUIDE.md`を確認
4. **IBM サポート**: Watsonx Orchestrateのサポートに問い合わせ

## 次のステップ

- [ ] 本番環境でのテスト
- [ ] ユーザートレーニング
- [ ] 運用手順書の作成
- [ ] モニタリング設定
- [ ] バックアップ計画の策定

---

**統合ステータス**: 準備完了 ✅