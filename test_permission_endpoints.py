#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP SuccessFactors 権限グループエンドポイントのテスト
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

SAP_API_URL = os.getenv('SAP_API_URL')
SAP_COMPANY_ID = os.getenv('SAP_COMPANY_ID')
SAP_USER_ID = os.getenv('SAP_USER_ID')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')

def create_auth_header():
    """Basic認証ヘッダーを作成"""
    auth_string = f"{SAP_USER_ID}@{SAP_COMPANY_ID}:{SAP_PASSWORD}"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    return base64_bytes.decode('ascii')

def test_endpoint(endpoint_name):
    """エンドポイントをテスト"""
    auth_header = create_auth_header()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    url = f"{SAP_API_URL}/odata/v2/{endpoint_name}"
    params = {'$top': 1, '$format': 'json'}
    
    print(f"\nテスト: {endpoint_name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 成功")
            data = response.json()
            if 'd' in data and 'results' in data['d']:
                print(f"取得件数: {len(data['d']['results'])}")
            return True
        elif response.status_code == 404:
            print("❌ エンドポイントが見つかりません")
        elif response.status_code == 401:
            print("❌ 認証エラー")
        elif response.status_code == 403:
            print("❌ アクセス拒否")
        else:
            print(f"❌ エラー: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 例外: {str(e)}")
    
    return False

def main():
    """メイン処理"""
    print("="*60)
    print("  SAP SuccessFactors 権限グループエンドポイントテスト")
    print("="*60)
    
    # テストするエンドポイント
    endpoints = [
        'PermissionRole',
        'RoleEntity',
        'Role',
        'PermissionGroup',
        'UserRole',
        'FORole',
        'RBPRole',
        'PerPerson',  # ユーザー情報
    ]
    
    successful_endpoints = []
    
    for endpoint in endpoints:
        if test_endpoint(endpoint):
            successful_endpoints.append(endpoint)
    
    print("\n" + "="*60)
    print("  結果サマリー")
    print("="*60)
    print(f"\n成功したエンドポイント: {len(successful_endpoints)}")
    for endpoint in successful_endpoints:
        print(f"  ✅ {endpoint}")
    
    if not successful_endpoints:
        print("\n⚠️  権限グループ関連のエンドポイントが見つかりませんでした")
        print("\n推奨事項:")
        print("1. SAP管理画面でOData APIのドキュメントを確認")
        print("2. 権限グループの管理方法を確認")
        print("3. APIユーザーの権限を確認")

if __name__ == "__main__":
    main()

# Made with Bob