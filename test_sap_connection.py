#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP SuccessFactors API接続テストスクリプト

このスクリプトは以下をテストします:
1. 環境変数の読み込み
2. Basic認証の設定
3. SAP SuccessFactors OData API v2への接続
4. ユーザー情報の取得
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv
import json

# Windows環境でのUnicodeエンコーディング問題を解決
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 環境変数の読み込み
load_dotenv()

# 認証情報の取得
SAP_API_URL = os.getenv('SAP_API_URL')
SAP_COMPANY_ID = os.getenv('SAP_COMPANY_ID')
SAP_USER_ID = os.getenv('SAP_USER_ID')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')

def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_environment_variables():
    """環境変数の確認"""
    print_section("1. 環境変数の確認")
    
    required_vars = {
        'SAP_API_URL': SAP_API_URL,
        'SAP_COMPANY_ID': SAP_COMPANY_ID,
        'SAP_USER_ID': SAP_USER_ID,
        'SAP_PASSWORD': SAP_PASSWORD
    }
    
    all_present = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # パスワードは一部のみ表示
            if var_name == 'SAP_PASSWORD':
                display_value = '*' * len(var_value)
            else:
                display_value = var_value
            print(f"✓ {var_name}: {display_value}")
        else:
            print(f"✗ {var_name}: 未設定")
            all_present = False
    
    if not all_present:
        print("\n❌ エラー: 必要な環境変数が設定されていません")
        print("   .envファイルを確認してください")
        sys.exit(1)
    
    print("\n✅ すべての環境変数が設定されています")
    return True

def create_basic_auth_header():
    """Basic認証ヘッダーの作成"""
    print_section("2. Basic認証ヘッダーの作成")
    
    # SAP SuccessFactorsのBasic認証形式: UserID@CompanyID:Password
    auth_string = f"{SAP_USER_ID}@{SAP_COMPANY_ID}:{SAP_PASSWORD}"
    print(f"認証文字列形式: {SAP_USER_ID}@{SAP_COMPANY_ID}:{'*' * len(SAP_PASSWORD)}")
    
    # Base64エンコード
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    print(f"Base64エンコード完了: {base64_string[:20]}...")
    print("✅ Basic認証ヘッダーを作成しました")
    
    return base64_string

def test_api_connection(auth_header):
    """API接続テスト"""
    print_section("3. SAP SuccessFactors API接続テスト")
    
    # OData API v2エンドポイント
    endpoint = f"{SAP_API_URL}/odata/v2/User"
    params = {
        '$top': 1,  # 1件のみ取得
        '$format': 'json'
    }
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    print(f"エンドポイント: {endpoint}")
    print(f"パラメータ: {params}")
    print("\nAPIリクエストを送信中...")
    
    try:
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30
        )
        
        print(f"\nステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API接続成功!")
            
            # レスポンスの解析
            data = response.json()
            
            if 'd' in data and 'results' in data['d']:
                users = data['d']['results']
                print(f"\n取得したユーザー数: {len(users)}")
                
                if users:
                    print("\n--- サンプルユーザー情報 ---")
                    user = users[0]
                    print(json.dumps(user, indent=2, ensure_ascii=False))
            else:
                print("\n⚠️  レスポンス形式が予期しない形式です")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            
            return True
            
        elif response.status_code == 401:
            print("❌ 認証エラー (401 Unauthorized)")
            print("\n考えられる原因:")
            print("  - Company IDが間違っている")
            print("  - User IDが間違っている")
            print("  - パスワードが間違っている")
            print("  - 認証文字列の形式が間違っている (CompanyID\\UserID:Password)")
            return False
            
        elif response.status_code == 403:
            print("❌ アクセス拒否 (403 Forbidden)")
            print("\n考えられる原因:")
            print("  - APIユーザーに必要な権限がない")
            print("  - OData APIアクセスが有効になっていない")
            print("  - ユーザーがAPI Centerの許可リストに含まれていない")
            return False
            
        elif response.status_code == 404:
            print("❌ エンドポイントが見つかりません (404 Not Found)")
            print("\n考えられる原因:")
            print("  - API URLが間違っている")
            print("  - データセンターURLが間違っている")
            return False
            
        else:
            print(f"❌ 予期しないエラー (ステータスコード: {response.status_code})")
            print(f"\nレスポンス: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー")
        print("   APIサーバーへの接続がタイムアウトしました")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー")
        print("   APIサーバーに接続できません")
        print("   ネットワーク接続とAPI URLを確認してください")
        return False
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False

def test_user_entity_metadata():
    """Userエンティティのメタデータ取得テスト"""
    print_section("4. Userエンティティのメタデータ取得")
    
    auth_string = f"{SAP_COMPANY_ID}\\{SAP_USER_ID}:{SAP_PASSWORD}"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    # メタデータエンドポイント
    endpoint = f"{SAP_API_URL}/odata/v2/$metadata"
    
    headers = {
        'Authorization': f'Basic {base64_string}',
        'Accept': 'application/xml'
    }
    
    print(f"エンドポイント: {endpoint}")
    print("\nメタデータを取得中...")
    
    try:
        response = requests.get(
            endpoint,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ メタデータ取得成功!")
            print(f"\nメタデータサイズ: {len(response.text)} bytes")
            
            # Userエンティティの存在確認
            if 'EntityType Name="User"' in response.text:
                print("✅ Userエンティティが見つかりました")
            else:
                print("⚠️  Userエンティティが見つかりませんでした")
            
            return True
        else:
            print(f"❌ メタデータ取得失敗 (ステータスコード: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False

def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("  SAP SuccessFactors API接続テスト")
    print("="*60)
    
    # 1. 環境変数の確認
    check_environment_variables()
    
    # 2. Basic認証ヘッダーの作成
    auth_header = create_basic_auth_header()
    
    # 3. API接続テスト
    connection_success = test_api_connection(auth_header)
    
    # 4. メタデータ取得テスト
    if connection_success:
        test_user_entity_metadata()
    
    # 結果サマリー
    print_section("テスト結果サマリー")
    
    if connection_success:
        print("✅ すべてのテストが成功しました!")
        print("\n次のステップ:")
        print("  1. MCPサーバーの実装を開始できます")
        print("  2. ユーザー作成機能の実装に進めます")
        return 0
    else:
        print("❌ テストが失敗しました")
        print("\n対処方法:")
        print("  1. .envファイルの認証情報を確認してください")
        print("  2. SAP管理画面でAPI権限を確認してください")
        print("  3. SAP_CREDENTIALS_GUIDE.mdを参照してください")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
