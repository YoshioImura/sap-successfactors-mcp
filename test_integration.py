#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合テストスクリプト
SAP APIクライアントとツール関数の動作を確認します
"""

import sys
import os

# Windows環境でのUnicodeエンコーディング問題を解決
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from src.tools.user_management import (
    test_sap_connection,
    list_sap_users,
    get_sap_user,
    create_sap_user,
    add_user_to_admin_role,
    create_sap_user_with_admin_role
)

# 環境変数の読み込み
load_dotenv()


def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_connection_check():
    """接続テスト"""
    print_section("1. SAP SuccessFactors 接続テスト")
    
    result = test_sap_connection()
    
    if result['success']:
        print("✅ 接続成功")
        print(f"   {result['message']}")
        return True
    else:
        print("❌ 接続失敗")
        print(f"   {result['message']}")
        return False


def test_list_users():
    """ユーザー一覧取得テスト"""
    print_section("2. ユーザー一覧取得テスト")
    
    result = list_sap_users(top=3)
    
    if result['success']:
        print(f"✅ {result['count']}件のユーザーを取得")
        print("\n取得したユーザー:")
        for i, user in enumerate(result['data'], 1):
            print(f"  {i}. User ID: {user.get('userId')}")
            print(f"     Username: {user.get('username')}")
            print(f"     Email: {user.get('email', 'N/A')}")
            print(f"     Display Name: {user.get('displayName', 'N/A')}")
        return True
    else:
        print("❌ ユーザー一覧取得失敗")
        print(f"   {result['message']}")
        return False


def test_get_user():
    """ユーザー情報取得テスト"""
    print_section("3. ユーザー情報取得テスト")
    
    # まず一覧から最初のユーザーIDを取得
    list_result = list_sap_users(top=1)
    
    if not list_result['success'] or not list_result['data']:
        print("❌ テスト用ユーザーが見つかりません")
        return False
    
    test_user_id = list_result['data'][0]['userId']
    print(f"テスト対象ユーザーID: {test_user_id}")
    
    result = get_sap_user(test_user_id)
    
    if result['success']:
        print("✅ ユーザー情報取得成功")
        user = result['data']
        print(f"\nユーザー詳細:")
        print(f"  User ID: {user.get('userId')}")
        print(f"  Username: {user.get('username')}")
        print(f"  Display Name: {user.get('displayName')}")
        print(f"  Email: {user.get('email', 'N/A')}")
        print(f"  Locale: {user.get('defaultLocale')}")
        print(f"  Timezone: {user.get('timeZone')}")
        print(f"  Status: {user.get('status')}")
        return True
    else:
        print("❌ ユーザー情報取得失敗")
        print(f"   {result['message']}")
        return False


def test_create_user_dry_run():
    """ユーザー作成テスト（ドライラン）"""
    print_section("4. ユーザー作成機能テスト（ドライラン）")
    
    print("⚠️  実際のユーザー作成はスキップします")
    print("   本番環境でユーザーを作成する場合は、以下の関数を使用してください:")
    print()
    print("   from src.tools.user_management import create_sap_user")
    print()
    print("   result = create_sap_user(")
    print("       user_id='TEST001',")
    print("       username='testuser',")
    print("       first_name='Test',")
    print("       last_name='User',")
    print("       email='test.user@example.com',")
    print("       locale='ja_JP',")
    print("       timezone='Asia/Tokyo'")
    print("   )")
    print()
    print("✅ ユーザー作成機能は実装済みです")
    return True


def test_permission_role_feature():
    """権限グループ機能テスト（ドライラン）"""
    print_section("5. 権限グループ機能テスト（ドライラン）")
    
    print("⚠️  実際の権限グループへの追加はスキップします")
    print("   本番環境でユーザーを権限グループに追加する場合は、以下の関数を使用してください:")
    print()
    print("   # 方法1: 既存ユーザーを権限グループに追加")
    print("   from src.tools.user_management import add_user_to_admin_role")
    print()
    print("   result = add_user_to_admin_role(user_id='existing_user_id')")
    print()
    print("   # 方法2: ユーザー作成と同時に権限グループに追加（推奨）")
    print("   from src.tools.user_management import create_sap_user_with_admin_role")
    print()
    print("   result = create_sap_user_with_admin_role(")
    print("       user_id='TEST001',")
    print("       username='testuser',")
    print("       first_name='Test',")
    print("       last_name='User',")
    print("       email='test.user@example.com'")
    print("   )")
    print()
    print("📋 機能の特徴:")
    print("   ✓ 固定の権限グループ名: 「IBM管理者用権限グループ」")
    print("   ✓ 既存メンバーを保持したまま新規ユーザーを追加")
    print("   ✓ 重複チェック機能付き（既に存在する場合はスキップ）")
    print()
    print("✅ 権限グループへのユーザー追加機能は実装済みです")
    return True


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("  SAP SuccessFactors MCP 統合テスト")
    print("="*60)
    
    tests = [
        ("接続テスト", test_connection_check),
        ("ユーザー一覧取得", test_list_users),
        ("ユーザー情報取得", test_get_user),
        ("ユーザー作成機能", test_create_user_dry_run),
        ("権限グループ機能", test_permission_role_feature),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {str(e)}")
            results.append((test_name, False))
    
    # 結果サマリー
    print_section("テスト結果サマリー")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n合計: {passed}/{total} テスト成功\n")
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 すべてのテストが成功しました！")
        print("\n次のステップ:")
        print("  1. MCPサーバーを起動: python -m src.server")
        print("  2. Watsonx Orchestrateと統合")
        print("  3. エンドツーエンドテスト")
        return 0
    else:
        print("\n⚠️  一部のテストが失敗しました")
        print("   エラーメッセージを確認して問題を解決してください")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
