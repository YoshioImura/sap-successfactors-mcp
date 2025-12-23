@echo off
REM SAP SuccessFactors MCP Server デプロイスクリプト (Windows)
REM IBM Cloud Code Engineへのデプロイを自動化します

setlocal enabledelayedexpansion

echo ============================================================
echo   SAP SuccessFactors MCP Server デプロイ
echo ============================================================

REM 環境変数の確認
if not exist .env (
    echo ❌ エラー: .envファイルが見つかりません
    echo    .env.exampleをコピーして.envを作成し、認証情報を設定してください
    exit /b 1
)

echo ✅ 環境変数ファイルが見つかりました

REM IBM Cloud CLIのインストール確認
where ibmcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ エラー: IBM Cloud CLIがインストールされていません
    echo    https://cloud.ibm.com/docs/cli からインストールしてください
    exit /b 1
)

echo ✅ IBM Cloud CLIが見つかりました

REM IBM Cloudにログイン
echo.
echo IBM Cloudにログインしています...
ibmcloud login --sso

REM Code Engineプラグインのインストール確認
ibmcloud plugin list | findstr "code-engine" >nul
if %errorlevel% neq 0 (
    echo Code Engineプラグインをインストールしています...
    ibmcloud plugin install code-engine
)

REM プロジェクトの選択
echo.
echo 利用可能なCode Engineプロジェクト:
ibmcloud ce project list

echo.
set /p PROJECT_NAME="プロジェクト名を入力してください（新規作成する場合は新しい名前を入力）: "

REM プロジェクトの存在確認
ibmcloud ce project get --name "%PROJECT_NAME%" >nul 2>nul
if %errorlevel% equ 0 (
    echo 既存のプロジェクト '%PROJECT_NAME%' を使用します
    ibmcloud ce project select --name "%PROJECT_NAME%"
) else (
    echo 新しいプロジェクト '%PROJECT_NAME%' を作成します
    set /p REGION="リージョンを入力してください（例: jp-tok）: "
    ibmcloud ce project create --name "%PROJECT_NAME%" --region "!REGION!"
    ibmcloud ce project select --name "%PROJECT_NAME%"
)

REM アプリケーション名
set APP_NAME=sap-successfactors-mcp

echo.
echo ============================================================
echo   Dockerイメージのビルドとプッシュ
echo ============================================================

REM Container Registryの設定
set REGISTRY_NAMESPACE=sap-mcp
set IMAGE_NAME=%REGISTRY_NAMESPACE%/%APP_NAME%

REM Container Registryにログイン
ibmcloud cr login

REM 名前空間の作成（存在しない場合）
ibmcloud cr namespace-list | findstr "%REGISTRY_NAMESPACE%" >nul
if %errorlevel% neq 0 (
    echo Container Registry名前空間を作成しています...
    ibmcloud cr namespace-add "%REGISTRY_NAMESPACE%"
)

REM Dockerイメージのビルド
echo Dockerイメージをビルドしています...
docker build -t "jp.icr.io/%IMAGE_NAME%:latest" -f deployment/Dockerfile .

REM Dockerイメージのプッシュ
echo Dockerイメージをプッシュしています...
docker push "jp.icr.io/%IMAGE_NAME%:latest"

echo ✅ Dockerイメージのビルドとプッシュが完了しました

echo.
echo ============================================================
echo   Code Engineアプリケーションのデプロイ
echo ============================================================

REM シークレットの作成（環境変数用）
set SECRET_NAME=sap-credentials

REM .envファイルから環境変数を読み込む
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set "%%a=%%b"
)

REM 既存のシークレットを削除（存在する場合）
ibmcloud ce secret get --name "%SECRET_NAME%" >nul 2>nul
if %errorlevel% equ 0 (
    echo 既存のシークレットを削除しています...
    ibmcloud ce secret delete --name "%SECRET_NAME%" --force
)

REM 新しいシークレットを作成
echo シークレットを作成しています...
ibmcloud ce secret create --name "%SECRET_NAME%" --from-literal SAP_API_URL="%SAP_API_URL%" --from-literal SAP_COMPANY_ID="%SAP_COMPANY_ID%" --from-literal SAP_USER_ID="%SAP_USER_ID%" --from-literal SAP_PASSWORD="%SAP_PASSWORD%" --from-literal MCP_AUTH_TOKEN="%MCP_AUTH_TOKEN%" --from-literal LOG_LEVEL="%LOG_LEVEL%"

REM アプリケーションのデプロイ
echo アプリケーションをデプロイしています...

ibmcloud ce app get --name "%APP_NAME%" >nul 2>nul
if %errorlevel% equ 0 (
    REM 既存のアプリケーションを更新
    echo 既存のアプリケーションを更新しています...
    ibmcloud ce app update --name "%APP_NAME%" --image "jp.icr.io/%IMAGE_NAME%:latest" --env-from-secret "%SECRET_NAME%" --port 8000 --min-scale 1 --max-scale 3 --cpu 0.25 --memory 0.5G
) else (
    REM 新しいアプリケーションを作成
    echo 新しいアプリケーションを作成しています...
    ibmcloud ce app create --name "%APP_NAME%" --image "jp.icr.io/%IMAGE_NAME%:latest" --env-from-secret "%SECRET_NAME%" --port 8000 --min-scale 1 --max-scale 3 --cpu 0.25 --memory 0.5G
)

REM アプリケーションのURLを取得
for /f "tokens=*" %%i in ('ibmcloud ce app get --name "%APP_NAME%" --output url') do set APP_URL=%%i

echo.
echo ============================================================
echo   デプロイ完了！
echo ============================================================
echo.
echo ✅ アプリケーションが正常にデプロイされました
echo.
echo アプリケーションURL: %APP_URL%
echo SSE Endpoint: %APP_URL%/sse
echo.
echo 次のステップ:
echo 1. Watsonx Orchestrateで上記のSSE Endpointを設定
echo 2. MCP_AUTH_TOKENを使用して認証
echo 3. 利用可能なツールを確認
echo.
echo ログの確認:
echo   ibmcloud ce app logs --name %APP_NAME% --follow
echo.

endlocal
pause

REM Made with Bob

@REM Made with Bob
