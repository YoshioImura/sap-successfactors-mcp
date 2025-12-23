#!/bin/bash
# SAP SuccessFactors MCP Server デプロイスクリプト
# IBM Cloud Code Engineへのデプロイを自動化します

set -e

echo "============================================================"
echo "  SAP SuccessFactors MCP Server デプロイ"
echo "============================================================"

# 環境変数の確認
if [ ! -f .env ]; then
    echo "❌ エラー: .envファイルが見つかりません"
    echo "   .env.exampleをコピーして.envを作成し、認証情報を設定してください"
    exit 1
fi

# 環境変数の読み込み
source .env

# 必須環境変数のチェック
required_vars=("SAP_API_URL" "SAP_COMPANY_ID" "SAP_USER_ID" "SAP_PASSWORD" "MCP_AUTH_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ エラー: 環境変数 $var が設定されていません"
        exit 1
    fi
done

echo "✅ 環境変数の確認完了"

# IBM Cloud CLIのインストール確認
if ! command -v ibmcloud &> /dev/null; then
    echo "❌ エラー: IBM Cloud CLIがインストールされていません"
    echo "   https://cloud.ibm.com/docs/cli からインストールしてください"
    exit 1
fi

echo "✅ IBM Cloud CLIが見つかりました"

# IBM Cloudにログイン
echo ""
echo "IBM Cloudにログインしています..."
ibmcloud login --sso

# Code Engineプラグインのインストール確認
if ! ibmcloud plugin list | grep -q "code-engine"; then
    echo "Code Engineプラグインをインストールしています..."
    ibmcloud plugin install code-engine
fi

# プロジェクトの選択
echo ""
echo "利用可能なCode Engineプロジェクト:"
ibmcloud ce project list

echo ""
read -p "プロジェクト名を入力してください（新規作成する場合は新しい名前を入力）: " PROJECT_NAME

# プロジェクトの存在確認
if ibmcloud ce project get --name "$PROJECT_NAME" &> /dev/null; then
    echo "既存のプロジェクト '$PROJECT_NAME' を使用します"
    ibmcloud ce project select --name "$PROJECT_NAME"
else
    echo "新しいプロジェクト '$PROJECT_NAME' を作成します"
    read -p "リージョンを入力してください（例: jp-tok）: " REGION
    ibmcloud ce project create --name "$PROJECT_NAME" --region "$REGION"
    ibmcloud ce project select --name "$PROJECT_NAME"
fi

# アプリケーション名
APP_NAME="sap-successfactors-mcp"

echo ""
echo "============================================================"
echo "  Dockerイメージのビルドとプッシュ"
echo "============================================================"

# Container Registryの設定
REGISTRY_NAMESPACE="sap-mcp"
IMAGE_NAME="$REGISTRY_NAMESPACE/$APP_NAME"

# Container Registryにログイン
ibmcloud cr login

# 名前空間の作成（存在しない場合）
if ! ibmcloud cr namespace-list | grep -q "$REGISTRY_NAMESPACE"; then
    echo "Container Registry名前空間を作成しています..."
    ibmcloud cr namespace-add "$REGISTRY_NAMESPACE"
fi

# Dockerイメージのビルド
echo "Dockerイメージをビルドしています..."
docker build -t "jp.icr.io/$IMAGE_NAME:latest" -f deployment/Dockerfile .

# Dockerイメージのプッシュ
echo "Dockerイメージをプッシュしています..."
docker push "jp.icr.io/$IMAGE_NAME:latest"

echo "✅ Dockerイメージのビルドとプッシュが完了しました"

echo ""
echo "============================================================"
echo "  Code Engineアプリケーションのデプロイ"
echo "============================================================"

# シークレットの作成（環境変数用）
SECRET_NAME="sap-credentials"

# 既存のシークレットを削除（存在する場合）
if ibmcloud ce secret get --name "$SECRET_NAME" &> /dev/null; then
    echo "既存のシークレットを削除しています..."
    ibmcloud ce secret delete --name "$SECRET_NAME" --force
fi

# 新しいシークレットを作成
echo "シークレットを作成しています..."
ibmcloud ce secret create --name "$SECRET_NAME" \
    --from-literal SAP_API_URL="$SAP_API_URL" \
    --from-literal SAP_COMPANY_ID="$SAP_COMPANY_ID" \
    --from-literal SAP_USER_ID="$SAP_USER_ID" \
    --from-literal SAP_PASSWORD="$SAP_PASSWORD" \
    --from-literal MCP_AUTH_TOKEN="$MCP_AUTH_TOKEN" \
    --from-literal LOG_LEVEL="${LOG_LEVEL:-INFO}"

# アプリケーションのデプロイ
echo "アプリケーションをデプロイしています..."

if ibmcloud ce app get --name "$APP_NAME" &> /dev/null; then
    # 既存のアプリケーションを更新
    echo "既存のアプリケーションを更新しています..."
    ibmcloud ce app update --name "$APP_NAME" \
        --image "jp.icr.io/$IMAGE_NAME:latest" \
        --env-from-secret "$SECRET_NAME" \
        --port 8000 \
        --min-scale 1 \
        --max-scale 3 \
        --cpu 0.25 \
        --memory 0.5G
else
    # 新しいアプリケーションを作成
    echo "新しいアプリケーションを作成しています..."
    ibmcloud ce app create --name "$APP_NAME" \
        --image "jp.icr.io/$IMAGE_NAME:latest" \
        --env-from-secret "$SECRET_NAME" \
        --port 8000 \
        --min-scale 1 \
        --max-scale 3 \
        --cpu 0.25 \
        --memory 0.5G
fi

# アプリケーションのURLを取得
APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | grep -o '"url":"[^"]*' | cut -d'"' -f4)

echo ""
echo "============================================================"
echo "  デプロイ完了！"
echo "============================================================"
echo ""
echo "✅ アプリケーションが正常にデプロイされました"
echo ""
echo "アプリケーションURL: $APP_URL"
echo "SSE Endpoint: $APP_URL/sse"
echo ""
echo "次のステップ:"
echo "1. Watsonx Orchestrateで上記のSSE Endpointを設定"
echo "2. MCP_AUTH_TOKENを使用して認証"
echo "3. 利用可能なツールを確認"
echo ""
echo "ログの確認:"
echo "  ibmcloud ce app logs --name $APP_NAME --follow"
echo ""

# Made with Bob