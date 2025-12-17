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

# Made with Bob
