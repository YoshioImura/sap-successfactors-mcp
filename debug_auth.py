#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP SuccessFactors 認証デバッグスクリプト
異なる認証形式を試してAPIへの接続を確認します
"""

import os
import base64
import requests
from dotenv import load_dotenv

# Windows環境でのUnicodeエンコーディング問題を解決
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 環境変数の読み込み
load_dotenv()

SAP_API_URL = os.getenv('SAP_API_URL')
SAP_COMPANY_ID = os.getenv('SAP_COMPANY_ID')
SAP_USER_ID = os.getenv('SAP_USER_ID')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')

print("="*60)
print("  SAP SuccessFactors 認証デバッグ")
print("="*60)
print(f"\nAPI URL: {SAP_API_URL}")
print(f"Company ID: {SAP_COMPANY_ID}")
print(f"User ID: {SAP_USER_ID}")
print(f"Password: {'*' * len(SAP_PASSWORD)}")

# テストするエンドポイント
endpoint = f"{SAP_API_URL}/odata/v2/User"
params = {'$top': 1, '$format': 'json'}

# 試す認証形式のリスト
auth_formats = [
    # 形式1: CompanyID\UserID:Password (標準)
    {
        'name': '形式1: CompanyID\\UserID:Password',
        'auth_string': f"{SAP_COMPANY_ID}\\{SAP_USER_ID}:{SAP_PASSWORD}"
    },
    # 形式2: UserID@CompanyID:Password
    {
        'name': '形式2: UserID@CompanyID:Password',
        'auth_string': f"{SAP_USER_ID}@{SAP_COMPANY_ID}:{SAP_PASSWORD}"
    },
    # 形式3: UserID:Password (Company IDなし)
    {
        'name': '形式3: UserID:Password',
        'auth_string': f"{SAP_USER_ID}:{SAP_PASSWORD}"
    },
    # 形式4: CompanyID/UserID:Password (スラッシュ)
    {
        'name': '形式4: CompanyID/UserID:Password',
        'auth_string': f"{SAP_COMPANY_ID}/{SAP_USER_ID}:{SAP_PASSWORD}"
    },
]

print("\n" + "="*60)
print("  認証形式のテスト")
print("="*60)

for i, auth_format in enumerate(auth_formats, 1):
    print(f"\n--- テスト {i}: {auth_format['name']} ---")
    
    # Base64エンコード
    auth_bytes = auth_format['auth_string'].encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    # 認証文字列の表示（パスワード部分は隠す）
    display_auth = auth_format['auth_string'].replace(SAP_PASSWORD, '*' * len(SAP_PASSWORD))
    print(f"認証文字列: {display_auth}")
    print(f"Base64: {base64_string[:30]}...")
    
    # APIリクエスト
    headers = {
        'Authorization': f'Basic {base64_string}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 成功! この認証形式が正しいです")
            data = response.json()
            if 'd' in data and 'results' in data['d']:
                print(f"取得したユーザー数: {len(data['d']['results'])}")
            break
        elif response.status_code == 401:
            print("❌ 認証失敗 (401)")
        elif response.status_code == 403:
            print("❌ アクセス拒否 (403) - 認証は成功したが権限がない可能性")
        else:
            print(f"❌ エラー ({response.status_code})")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

print("\n" + "="*60)
print("  追加の診断情報")
print("="*60)

# メタデータエンドポイントのテスト
print("\nメタデータエンドポイントのテスト...")
metadata_endpoint = f"{SAP_API_URL}/odata/v2/$metadata"

for auth_format in auth_formats[:1]:  # 最初の形式のみテスト
    auth_bytes = auth_format['auth_string'].encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    headers = {
        'Authorization': f'Basic {base64_string}',
        'Accept': 'application/xml'
    }
    
    try:
        response = requests.get(metadata_endpoint, headers=headers, timeout=10)
        print(f"メタデータエンドポイント ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ メタデータ取得成功")
        elif response.status_code == 401:
            print("❌ メタデータ取得失敗 (401)")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

print("\n" + "="*60)
print("  推奨事項")
print("="*60)
print("""
1. SAP管理画面で以下を確認してください:
   - Admin Center → Company Settings → API Center
   - OData APIが有効になっているか
   - Basic認証が許可されているか
   - ユーザー 'Bobapiadmin' がAllowed Usersリストに含まれているか

2. ユーザー権限を確認してください:
   - Admin Center → Manage Permission Roles
   - 'Bobapiadmin' に以下の権限があるか:
     * User Management
     * OData API Access
     * View Users

3. パスワードを確認してください:
   - 特殊文字が正しく入力されているか
   - パスワードの有効期限が切れていないか

4. 別の方法を試してください:
   - SAP管理画面から直接APIテストツールを使用
   - Postmanなどのツールで手動テスト
""")

# Made with Bob
