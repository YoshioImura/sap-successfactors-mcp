"""
SAP SuccessFactors MCP Server
FastMCPを使用してMCPサーバーを実装します
"""

import logging
from typing import Any
from fastmcp import FastMCP

from .tools.user_management import (
    create_sap_user,
    get_sap_user,
    update_sap_user,
    list_sap_users,
    test_sap_connection,
    add_user_to_admin_role as add_user_to_admin_role_impl,
    create_sap_user_with_admin_role as create_user_with_admin_role_impl
)
from .config.settings import get_settings

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 設定の読み込み
settings = get_settings()

# FastMCPサーバーの初期化
mcp = FastMCP("SAP SuccessFactors User Management")

logger.info("MCP Server initialized")


@mcp.tool()
def create_user(
    user_id: str,
    username: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    locale: str = "ja_JP",
    timezone: str = "Asia/Tokyo"
) -> dict[str, Any]:
    """SAP SuccessFactorsに新規ユーザーを作成します
    
    注意: 権限グループへの自動追加は現在サポートされていません。
    ユーザー作成後、SAP管理画面から手動で権限を付与してください。
    
    Args:
        user_id: ユーザーID（必須、一意である必要があります）
        username: ユーザー名（必須、ログイン名として使用）
        first_name: 名
        last_name: 姓
        email: メールアドレス
        locale: ロケール（デフォルト: ja_JP）
        timezone: タイムゾーン（デフォルト: Asia/Tokyo）
        
    Returns:
        作成結果を含む辞書
    """
    logger.info(f"Tool called: create_user for {user_id}")
    
    return create_sap_user(
        user_id=user_id,
        username=username,
        first_name=first_name if first_name else None,
        last_name=last_name if last_name else None,
        email=email if email else None,
        locale=locale,
        timezone=timezone,
        add_to_admin_role=False
    )


@mcp.tool()
def get_user(user_id: str) -> dict[str, Any]:
    """SAP SuccessFactorsからユーザー情報を取得します
    
    Args:
        user_id: ユーザーID
        
    Returns:
        ユーザー情報を含む辞書
    """
    logger.info(f"Tool called: get_user for {user_id}")
    return get_sap_user(user_id)


@mcp.tool()
def update_user(
    user_id: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    locale: str = "",
    timezone: str = ""
) -> dict[str, Any]:
    """SAP SuccessFactorsのユーザー情報を更新します
    
    Args:
        user_id: ユーザーID
        first_name: 名
        last_name: 姓
        email: メールアドレス
        locale: ロケール
        timezone: タイムゾーン
        
    Returns:
        更新結果を含む辞書
    """
    logger.info(f"Tool called: update_user for {user_id}")
    
    # 空文字列をNoneに変換
    kwargs = {}
    if first_name:
        kwargs['firstName'] = first_name
    if last_name:
        kwargs['lastName'] = last_name
    if email:
        kwargs['email'] = email
    if locale:
        kwargs['defaultLocale'] = locale
    if timezone:
        kwargs['timeZone'] = timezone
    
    return update_sap_user(user_id, **kwargs)


@mcp.tool()
def list_users(
    top: int = 10,
    skip: int = 0,
    filter_query: str = ""
) -> dict[str, Any]:
    """SAP SuccessFactorsからユーザー一覧を取得します
    
    Args:
        top: 取得件数（デフォルト: 10）
        skip: スキップ件数（デフォルト: 0）
        filter_query: フィルタクエリ（OData形式）
        
    Returns:
        ユーザー一覧を含む辞書
    """
    logger.info(f"Tool called: list_users (top={top}, skip={skip})")
    
    return list_sap_users(
        top=top,
        skip=skip,
        filter_query=filter_query if filter_query else None
    )


@mcp.tool()
def test_connection() -> dict[str, Any]:
    """SAP SuccessFactors API接続をテストします
    
    Returns:
        接続テスト結果を含む辞書
    """
    logger.info("Tool called: test_connection")
    return test_sap_connection()


@mcp.tool()
def add_user_to_admin_role(user_id: str) -> dict[str, Any]:
    """既存ユーザーをIBM管理者用権限グループに追加します
    
    Args:
        user_id: ユーザーID
        
    Returns:
        追加結果を含む辞書
    """
    logger.info(f"Tool called: add_user_to_admin_role for {user_id}")
    return add_user_to_admin_role_impl(user_id)


@mcp.tool()
def create_user_with_admin_role(
    user_id: str,
    username: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    locale: str = "ja_JP",
    timezone: str = "Asia/Tokyo"
) -> dict[str, Any]:
    """SAP SuccessFactorsに新規ユーザーを作成し、IBM管理者用権限グループに追加します
    
    この関数は以下の処理を順次実行します：
    1. ユーザーアカウントの作成
    2. IBM管理者用権限グループへの追加
    
    Args:
        user_id: ユーザーID（必須、一意である必要があります）
        username: ユーザー名（必須、ログイン名として使用）
        first_name: 名
        last_name: 姓
        email: メールアドレス
        locale: ロケール（デフォルト: ja_JP）
        timezone: タイムゾーン（デフォルト: Asia/Tokyo）
        
    Returns:
        作成結果を含む辞書
    """
    logger.info(f"Tool called: create_user_with_admin_role for {user_id}")
    
    return create_user_with_admin_role_impl(
        user_id=user_id,
        username=username,
        first_name=first_name if first_name else None,
        last_name=last_name if last_name else None,
        email=email if email else None,
        locale=locale,
        timezone=timezone
    )


# ヘルスチェックエンドポイント
@mcp.resource("health://status")
def health_check() -> str:
    """ヘルスチェック"""
    return "OK"


def main():
    """サーバーを起動"""
    logger.info(f"Starting MCP Server on port {settings.mcp_port}")
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=settings.mcp_port
    )


if __name__ == "__main__":
    main()

# Made with Bob
