"""
設定管理モジュール
環境変数から設定を読み込み、アプリケーション全体で使用できるようにします
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # SAP SuccessFactors API設定
    sap_api_url: str = Field(..., description="SAP SuccessFactors API URL")
    sap_company_id: str = Field(..., description="SAP Company ID")
    sap_user_id: str = Field(..., description="SAP API User ID")
    sap_password: str = Field(..., description="SAP API User Password")
    
    # OAuth 2.0設定（オプション）
    sap_oauth_client_id: Optional[str] = Field(None, description="OAuth Client ID")
    sap_oauth_client_secret: Optional[str] = Field(None, description="OAuth Client Secret")
    sap_oauth_token_url: Optional[str] = Field(None, description="OAuth Token URL")
    
    # MCP Server設定
    mcp_auth_token: str = Field(default="default-token", description="MCP認証トークン")
    mcp_port: int = Field(default=8000, description="MCPサーバーポート")
    
    # ログ設定
    log_level: str = Field(default="INFO", description="ログレベル")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# グローバル設定インスタンス
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """設定インスタンスを取得（シングルトンパターン）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """設定を再読み込み"""
    global _settings
    _settings = Settings()
    return _settings

# Made with Bob
