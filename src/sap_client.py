"""
SAP SuccessFactors APIクライアント
OData API v2を使用してSAP SuccessFactorsと通信します
"""

import base64
import logging
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .config.settings import get_settings

logger = logging.getLogger(__name__)


class SAPClientError(Exception):
    """SAP APIクライアントのエラー"""
    pass


class SAPAuthenticationError(SAPClientError):
    """SAP認証エラー"""
    pass


class SAPAPIError(SAPClientError):
    """SAP APIエラー"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class SAPSuccessFactorsClient:
    """SAP SuccessFactors APIクライアント"""
    
    def __init__(self):
        """クライアントの初期化"""
        self.settings = get_settings()
        self.base_url = self.settings.sap_api_url
        self.company_id = self.settings.sap_company_id
        self.user_id = self.settings.sap_user_id
        self.password = self.settings.sap_password
        
        # OData API v2エンドポイント
        self.odata_endpoint = f"{self.base_url}/odata/v2"
        
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"SAP Client initialized for {self.base_url}")
    
    def _create_auth_header(self) -> str:
        """Basic認証ヘッダーを作成
        
        SAP SuccessFactorsの認証形式: UserID@CompanyID:Password
        
        Returns:
            Base64エンコードされた認証文字列
        """
        auth_string = f"{self.user_id}@{self.company_id}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        return base64_bytes.decode('ascii')
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """APIリクエストを実行
        
        Args:
            method: HTTPメソッド (GET, POST, PUT, DELETE)
            endpoint: APIエンドポイント
            params: クエリパラメータ
            data: リクエストボディ
            timeout: タイムアウト秒数
            
        Returns:
            APIレスポンス
            
        Raises:
            SAPAuthenticationError: 認証エラー
            SAPAPIError: APIエラー
        """
        # 認証ヘッダーを追加
        auth_header = self._create_auth_header()
        headers = {
            'Authorization': f'Basic {auth_header}',
            **self.session.headers
        }
        
        # 完全なURL
        url = f"{self.odata_endpoint}/{endpoint}"
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=timeout
            )
            
            # ステータスコードのチェック
            if response.status_code == 401:
                logger.error("Authentication failed")
                raise SAPAuthenticationError(
                    "認証に失敗しました。Company ID、User ID、Passwordを確認してください。"
                )
            
            if response.status_code == 403:
                logger.error("Access forbidden")
                raise SAPAPIError(
                    "アクセスが拒否されました。APIユーザーの権限を確認してください。",
                    status_code=403
                )
            
            if response.status_code == 404:
                logger.error(f"Endpoint not found: {url}")
                raise SAPAPIError(
                    f"エンドポイントが見つかりません: {endpoint}",
                    status_code=404
                )
            
            if not response.ok:
                error_data = None
                try:
                    error_data = response.json()
                except:
                    pass
                
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise SAPAPIError(
                    f"APIエラー: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            # レスポンスをJSON形式で返す
            return response.json()
            
        except Timeout:
            logger.error("Request timeout")
            raise SAPAPIError("リクエストがタイムアウトしました")
        
        except ConnectionError:
            logger.error("Connection error")
            raise SAPAPIError("SAP SuccessFactorsに接続できません")
        
        except RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise SAPAPIError(f"リクエストエラー: {str(e)}")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザー情報を取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            ユーザー情報、存在しない場合はNone
        """
        try:
            response = self._make_request(
                method='GET',
                endpoint=f"User('{user_id}')"
            )
            
            if 'd' in response:
                return response['d']
            return response
            
        except SAPAPIError as e:
            if e.status_code == 404:
                return None
            raise
    
    def list_users(self, top: int = 10, skip: int = 0, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """ユーザー一覧を取得
        
        Args:
            top: 取得件数
            skip: スキップ件数
            filter_query: フィルタクエリ（OData形式）
            
        Returns:
            ユーザー一覧
        """
        params = {
            '$top': top,
            '$skip': skip,
            '$format': 'json'
        }
        
        if filter_query:
            params['$filter'] = filter_query
        
        response = self._make_request(
            method='GET',
            endpoint='User',
            params=params
        )
        
        if 'd' in response and 'results' in response['d']:
            return response['d']['results']
        return []
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """新規ユーザーを作成
        
        Args:
            user_data: ユーザーデータ
            
        Returns:
            作成されたユーザー情報
            
        Raises:
            SAPAPIError: ユーザー作成エラー
        """
        logger.info(f"Creating user: {user_data.get('userId', 'unknown')}")
        
        response = self._make_request(
            method='POST',
            endpoint='User',
            data=user_data
        )
        
        if 'd' in response:
            logger.info(f"User created successfully: {response['d'].get('userId')}")
            return response['d']
        
        logger.info("User created successfully")
        return response
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """ユーザー情報を更新
        
        Args:
            user_id: ユーザーID
            user_data: 更新するユーザーデータ
            
        Returns:
            更新されたユーザー情報
        """
        logger.info(f"Updating user: {user_id}")
        
        response = self._make_request(
            method='PUT',
            endpoint=f"User('{user_id}')",
            data=user_data
        )
        
        logger.info(f"User updated successfully: {user_id}")
        return response
    
    def delete_user(self, user_id: str) -> bool:
        """ユーザーを削除
        
        Args:
            user_id: ユーザーID
            
        Returns:
            削除成功の場合True
        """
        logger.info(f"Deleting user: {user_id}")
        
        self._make_request(
            method='DELETE',
            endpoint=f"User('{user_id}')"
        )
        
        logger.info(f"User deleted successfully: {user_id}")
        return True
    
    def test_connection(self) -> bool:
        """API接続をテスト
        
        Returns:
            接続成功の場合True
        """
        try:
            self.list_users(top=1)
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_permission_role(self, role_name: str) -> Optional[Dict[str, Any]]:
        """権限グループ（Permission Role）を名前で取得
        
        Args:
            role_name: 権限グループ名
            
        Returns:
            権限グループ情報、存在しない場合はNone
        """
        try:
            # OData filterを使用して権限グループを検索
            filter_query = f"roleName eq '{role_name}'"
            response = self._make_request(
                method='GET',
                endpoint='PermissionRole',
                params={
                    '$filter': filter_query,
                    '$format': 'json'
                }
            )
            
            if 'd' in response and 'results' in response['d']:
                results = response['d']['results']
                if results:
                    logger.info(f"Permission role found: {role_name}")
                    return results[0]
            
            logger.warning(f"Permission role not found: {role_name}")
            return None
            
        except SAPAPIError as e:
            if e.status_code == 404:
                return None
            raise
    
    def get_permission_role_members(self, role_name: str) -> List[str]:
        """権限グループのメンバー一覧を取得
        
        Args:
            role_name: 権限グループ名
            
        Returns:
            メンバーのユーザーIDリスト
        """
        role = self.get_permission_role(role_name)
        if not role:
            raise SAPAPIError(f"権限グループが見つかりません: {role_name}")
        
        # PermissionRoleのpeopleプロパティからメンバーを取得
        members = []
        if 'people' in role and 'results' in role['people']:
            members = [member.get('userId') for member in role['people']['results'] if member.get('userId')]
        
        logger.info(f"Found {len(members)} members in role: {role_name}")
        return members
    def create_permission_role(self, role_name: str, description: str = "") -> Dict[str, Any]:
        """権限グループ（Permission Role）を作成
        
        Args:
            role_name: 権限グループ名
            description: 説明（オプション）
            
        Returns:
            作成された権限グループ情報
            
        Raises:
            SAPAPIError: 権限グループ作成エラー
        """
        logger.info(f"Creating permission role: {role_name}")
        
        # 権限グループデータ
        role_data = {
            'roleName': role_name,
            'description': description or f"Auto-created role: {role_name}",
            'people': []  # 初期メンバーは空
        }
        
        try:
            response = self._make_request(
                method='POST',
                endpoint='PermissionRole',
                data=role_data
            )
            
            if 'd' in response:
                logger.info(f"Permission role created successfully: {role_name}")
                return response['d']
            
            logger.info(f"Permission role created: {role_name}")
            return response
            
        except SAPAPIError as e:
            logger.error(f"Failed to create permission role: {str(e)}")
            raise
    
    def ensure_permission_role_exists(self, role_name: str) -> Dict[str, Any]:
        """権限グループが存在することを確認し、存在しない場合は作成
        
        Args:
            role_name: 権限グループ名
            
        Returns:
            権限グループ情報
        """
        # 既存の権限グループを取得
        role = self.get_permission_role(role_name)
        
        if role:
            logger.info(f"Permission role already exists: {role_name}")
            return role
        
        # 存在しない場合は作成
        logger.info(f"Permission role not found, creating: {role_name}")
        return self.create_permission_role(role_name)
    
    
    def add_user_to_permission_role(self, user_id: str, role_name: str, auto_create: bool = True) -> Dict[str, Any]:
        """権限グループにユーザーを追加（差分追加）
        
        既存のメンバーを保持したまま、新しいユーザーを追加します。
        権限グループが存在しない場合、auto_createがTrueなら自動的に作成します。
        
        Args:
            user_id: 追加するユーザーID
            role_name: 権限グループ名
            auto_create: 権限グループが存在しない場合に自動作成するか（デフォルト: True）
            
        Returns:
            更新結果
            
        Raises:
            SAPAPIError: API呼び出しエラー
        """
        logger.info(f"Adding user {user_id} to permission role: {role_name}")
        
        # 権限グループを取得または作成
        if auto_create:
            role = self.ensure_permission_role_exists(role_name)
        else:
            role = self.get_permission_role(role_name)
            if not role:
                raise SAPAPIError(f"権限グループが見つかりません: {role_name}")
        
        role_id = role.get('roleId')
        if not role_id:
            raise SAPAPIError(f"権限グループIDが取得できません: {role_name}")
        
        # 既存のメンバーを取得
        existing_members = self.get_permission_role_members(role_name)
        
        # ユーザーが既に存在するかチェック
        if user_id in existing_members:
            logger.info(f"User {user_id} is already a member of {role_name}")
            return {
                'roleId': role_id,
                'roleName': role_name,
                'userId': user_id,
                'status': 'already_exists',
                'message': f"ユーザーは既に権限グループのメンバーです"
            }
        
        # 新しいメンバーリストを作成（既存 + 新規）
        new_members = existing_members + [user_id]
        
        # 権限グループを更新
        update_data = {
            'people': [{'userId': uid} for uid in new_members]
        }
        
        response = self._make_request(
            method='PUT',
            endpoint=f"PermissionRole('{role_id}')",
            data=update_data
        )
        
        logger.info(f"User {user_id} added to permission role {role_name} successfully")
        
        return {
            'roleId': role_id,
            'roleName': role_name,
            'userId': user_id,
            'status': 'added',
            'totalMembers': len(new_members),
            'message': f"ユーザーを権限グループに追加しました"
        }

# Made with Bob
