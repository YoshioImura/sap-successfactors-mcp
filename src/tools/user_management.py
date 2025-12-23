"""
SAP SuccessFactors ユーザー管理ツール
MCPツールとして公開される関数を定義します
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..sap_client import SAPSuccessFactorsClient, SAPClientError

logger = logging.getLogger(__name__)


def create_sap_user(
    user_id: str,
    username: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    locale: str = "ja_JP",
    timezone: str = "Asia/Tokyo",
    status: str = "active",
    add_to_admin_role: bool = False
) -> Dict[str, Any]:
    """SAP SuccessFactorsに新規ユーザーを作成
    
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
        status: ステータス（デフォルト: active）
        add_to_admin_role: IBM管理者用権限グループに追加するか（デフォルト: False、現在無効）
        
    Returns:
        作成結果を含む辞書
        {
            "success": bool,
            "user_id": str,
            "message": str,
            "user_creation": dict,
            "role_assignment": dict (add_to_admin_role=Trueの場合)
        }
    """
    logger.info(f"Creating SAP user: {user_id} (add_to_admin_role={add_to_admin_role})")
    
    try:
        # SAP APIクライアントの初期化
        client = SAPSuccessFactorsClient()
        
        # ユーザーデータの構築
        user_data = {
            "userId": user_id,
            "username": username,
            "defaultLocale": locale,
            "timeZone": timezone,
            "status": status
        }
        
        # オプションフィールドの追加
        if first_name:
            user_data["firstName"] = first_name
        
        if last_name:
            user_data["lastName"] = last_name
        
        if email:
            user_data["email"] = email
        
        # 表示名の生成
        if first_name and last_name:
            user_data["displayName"] = f"{first_name} {last_name}"
        elif first_name:
            user_data["displayName"] = first_name
        elif last_name:
            user_data["displayName"] = last_name
        else:
            user_data["displayName"] = username
        
        # ユーザーの作成
        result = client.create_user(user_data)
        
        logger.info(f"User created successfully: {user_id}")
        
        user_creation_result = {
            "success": True,
            "user_id": user_id,
            "message": f"ユーザー '{user_id}' を正常に作成しました",
            "data": result
        }
        
        # 権限グループに追加（現在は警告メッセージのみ）
        if add_to_admin_role:
            logger.info(f"Attempting to add user {user_id} to admin role")
            role_result = add_user_to_admin_role(user_id)
            
            # 権限追加が失敗してもユーザー作成は成功として扱う
            message = f"ユーザー '{user_id}' を作成しました。"
            if not role_result.get('success'):
                message += " 権限グループへの追加は手動で行ってください。"
            
            return {
                "success": True,
                "user_id": user_id,
                "message": message,
                "user_creation": user_creation_result,
                "role_assignment": role_result
            }
        
        return user_creation_result
        
    except SAPClientError as e:
        logger.error(f"Failed to create user: {str(e)}")
        return {
            "success": False,
            "user_id": user_id,
            "message": f"ユーザー作成に失敗しました: {str(e)}",
            "error": str(e)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "user_id": user_id,
            "message": f"予期しないエラーが発生しました: {str(e)}",
            "error": str(e)
        }


def get_sap_user(user_id: str) -> Dict[str, Any]:
    """SAP SuccessFactorsからユーザー情報を取得
    
    Args:
        user_id: ユーザーID
        
    Returns:
        ユーザー情報を含む辞書
    """
    logger.info(f"Getting SAP user: {user_id}")
    
    try:
        client = SAPSuccessFactorsClient()
        user_data = client.get_user(user_id)
        
        if user_data is None:
            return {
                "success": False,
                "user_id": user_id,
                "message": f"ユーザー '{user_id}' が見つかりません"
            }
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "ユーザー情報を取得しました",
            "data": user_data
        }
        
    except SAPClientError as e:
        logger.error(f"Failed to get user: {str(e)}")
        return {
            "success": False,
            "user_id": user_id,
            "message": f"ユーザー情報の取得に失敗しました: {str(e)}",
            "error": str(e)
        }


def update_sap_user(
    user_id: str,
    **kwargs
) -> Dict[str, Any]:
    """SAP SuccessFactorsのユーザー情報を更新
    
    Args:
        user_id: ユーザーID
        **kwargs: 更新するフィールド
        
    Returns:
        更新結果を含む辞書
    """
    logger.info(f"Updating SAP user: {user_id}")
    
    try:
        client = SAPSuccessFactorsClient()
        
        # 更新データの構築
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return {
                "success": False,
                "user_id": user_id,
                "message": "更新するデータが指定されていません"
            }
        
        # ユーザーの更新
        result = client.update_user(user_id, update_data)
        
        return {
            "success": True,
            "user_id": user_id,
            "message": f"ユーザー '{user_id}' を正常に更新しました",
            "data": result
        }
        
    except SAPClientError as e:
        logger.error(f"Failed to update user: {str(e)}")
        return {
            "success": False,
            "user_id": user_id,
            "message": f"ユーザー更新に失敗しました: {str(e)}",
            "error": str(e)
        }


def list_sap_users(
    top: int = 10,
    skip: int = 0,
    filter_query: Optional[str] = None
) -> Dict[str, Any]:
    """SAP SuccessFactorsからユーザー一覧を取得
    
    Args:
        top: 取得件数（デフォルト: 10）
        skip: スキップ件数（デフォルト: 0）
        filter_query: フィルタクエリ（OData形式）
        
    Returns:
        ユーザー一覧を含む辞書
    """
    logger.info(f"Listing SAP users: top={top}, skip={skip}")
    
    try:
        client = SAPSuccessFactorsClient()
        users = client.list_users(top=top, skip=skip, filter_query=filter_query)
        
        return {
            "success": True,
            "message": f"{len(users)}件のユーザーを取得しました",
            "count": len(users),
            "data": users
        }
        
    except SAPClientError as e:
        logger.error(f"Failed to list users: {str(e)}")
        return {
            "success": False,
            "message": f"ユーザー一覧の取得に失敗しました: {str(e)}",
            "error": str(e)
        }


def test_sap_connection() -> Dict[str, Any]:
    """SAP SuccessFactors API接続をテスト
    
    Returns:
        接続テスト結果を含む辞書
    """
    logger.info("Testing SAP connection")
    
    try:
        client = SAPSuccessFactorsClient()
        success = client.test_connection()
        
        if success:
            return {
                "success": True,
                "message": "SAP SuccessFactors APIへの接続に成功しました"
            }
        else:
            return {
                "success": False,
                "message": "SAP SuccessFactors APIへの接続に失敗しました"
            }
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            "success": False,
            "message": f"接続テストに失敗しました: {str(e)}",
            "error": str(e)
        }


def add_user_to_admin_role(user_id: str) -> Dict[str, Any]:
    """ユーザーをIBM管理者用権限グループに追加
    
    注意: SAP SuccessFactorsのPermissionRoleエンドポイントが利用できないため、
    この機能は現在サポートされていません。
    代わりに、SAP管理画面から手動で権限を付与してください。
    
    Args:
        user_id: 追加するユーザーID
        
    Returns:
        追加結果を含む辞書
    """
    logger.warning(f"Permission role assignment not supported for user: {user_id}")
    
    ADMIN_ROLE_NAME = "IBM管理者用権限グループ"
    
    return {
        "success": False,
        "user_id": user_id,
        "role_name": ADMIN_ROLE_NAME,
        "message": f"権限グループへの自動追加は現在サポートされていません。SAP管理画面から手動で '{ADMIN_ROLE_NAME}' に追加してください。",
        "note": "SAP SuccessFactorsのPermissionRoleエンドポイントが利用できないため、この機能は無効化されています。"
    }


def create_sap_user_with_admin_role(
    user_id: str,
    username: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    locale: str = "ja_JP",
    timezone: str = "Asia/Tokyo",
    status: str = "active"
) -> Dict[str, Any]:
    """SAP SuccessFactorsに新規ユーザーを作成し、管理者権限グループに追加
    
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
        status: ステータス（デフォルト: active）
        
    Returns:
        作成結果を含む辞書
        {
            "success": bool,
            "user_id": str,
            "message": str,
            "user_creation": dict,
            "role_assignment": dict
        }
    """
    logger.info(f"Creating SAP user with admin role: {user_id}")
    
    # ステップ1: ユーザーを作成
    user_result = create_sap_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        locale=locale,
        timezone=timezone,
        status=status
    )
    
    if not user_result['success']:
        logger.error(f"User creation failed: {user_id}")
        return {
            "success": False,
            "user_id": user_id,
            "message": "ユーザー作成に失敗したため、権限グループへの追加をスキップしました",
            "user_creation": user_result,
            "role_assignment": None
        }
    
    logger.info(f"User created successfully, adding to admin role: {user_id}")
    
    # ステップ2: 管理者権限グループに追加
    role_result = add_user_to_admin_role(user_id)
    
    if not role_result['success']:
        logger.warning(f"Role assignment failed for user: {user_id}")
        return {
            "success": False,
            "user_id": user_id,
            "message": "ユーザーは作成されましたが、権限グループへの追加に失敗しました",
            "user_creation": user_result,
            "role_assignment": role_result
        }
    
    logger.info(f"User created and added to admin role successfully: {user_id}")
    
    return {
        "success": True,
        "user_id": user_id,
        "message": f"ユーザー '{user_id}' を作成し、IBM管理者用権限グループに追加しました",
        "user_creation": user_result,
        "role_assignment": role_result
    }

# Made with Bob
