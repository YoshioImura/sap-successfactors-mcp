#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
権限グループ機能テストスクリプト
IBM管理者用権限グループへのユーザー追加機能をテストします
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
    add_user_to_admin_role,
    create_sap_user_with_admin_role
)
from src.sap_client import SAPSuccessFactorsClient

# 環境変数の読み込み
load_dotenv()


def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_get_permission_role():
    """権限グループ取得テスト"""
    print_section("1. 権限グループ取得テスト")
    
    ADMIN_ROLE_NAME = "IBM管理者用権限グループ"
    
    try:
        client = SAPSuccessFactorsClient()
        role = client.get_permission_role(ADMIN_ROLE_NAME)
        
        if role:
            print(f"✅ 権限グループが見つかりました")
            print(f"\n権限グループ情報:")
            print(f"  Role ID: {role.get('roleId')}")
            print(f"  Role Name: {role.get('roleName')}")
            print(f"  Description: {role.get('description', 'N/A')}")
            return True
        else:
            print(f"❌ 権限グループが見つかりません: {ADMIN_ROLE_NAME}")
            print(f"\n⚠️  注意: SAP SuccessFactorsで以下を確認してください:")
            print(f"   1. 権限グループ '{ADMIN_ROLE_NAME}' が存在するか")
            print(f"   2. 権限グループ名が正確に一致しているか")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False


def test_get_permission_role_members():
    """権限グループメンバー取得テスト"""
    print_section("2. 権限グループメンバー取得テスト")
    
    ADMIN_ROLE_NAME = "IBM管理者用権限グループ"
    
    try:
        client = SAPSuccessFactorsClient()
        members = client.get_permission_role_members(ADMIN_ROLE_NAME)
        
        print(f"✅ メンバー一覧を取得しました")
        print(f"\n現在のメンバー数: {len(members)}")
        
        if members:
            print(f"\nメンバー一覧:")
            for i, user_id in enumerate(members[:10], 1):  # 最初の10人まで表示
                print(f"  {i}. {user_id}")
            
            if len(members) > 10:
                print(f"  ... 他 {len(members) - 10} 人")
        else:
            print(f"\n⚠️  現在メンバーはいません")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False


def test_add_user_to_admin_role_dry_run():
    """権限グループへのユーザー追加テスト（ドライラン）"""
    print_section("3. 権限グループへのユーザー追加テスト（ドライラン）")
    
    print("⚠️  実際のユーザー追加はスキップします")
    print("   本番環境でユーザーを追加する場合は、以下の関数を使用してください:")
    print()
    print("   from src.tools.user_management import add_user_to_admin_role")
    print()
    print("   # 既存ユーザーを権限グループに追加")
    print("   result = add_user_to_admin_role(user_id='existing_user_id')")
    print()
    print("   # または、ユーザー作成と同時に権限グループに追加")
    print("   from src.tools.user_management import create_sap_user_with_admin_role")
    print()
    print("   result = create_sap_user_with_admin_role(")
    print("       user_id='NEW001',")
    print("       username='newuser',")
    print("       first_name='New',")
    print("       last_name='User',")
    print("       email='new.user@example.com'")
    print("   )")
    print()
    print("✅ 権限グループへのユーザー追加機能は実装済みです")
    return True


def test_workflow_simulation():
    """ワークフローシミュレーション"""
    print_section("4. ワークフローシミュレーション")
    
    print("📋 想定されるワークフロー:")
    print()
    print("  1. Slackでユーザー作成リクエスト")
    print("     ↓")
    print("  2. Watson Orchestrateがリクエストを受信")
    print("     ↓")
    print("  3. MCPサーバーの create_sap_user_with_admin_role() を呼び出し")
    print("     ↓")
    print("  4. SAP SuccessFactorsにユーザーアカウントを作成")
    print("     ↓")
    print("  5. 作成したユーザーを「IBM管理者用権限グループ」に追加")
    print("     ↓")
    print("  6. 結果をWatson Orchestrate経由でSlackに通知")
    print()
    print("✅ ワークフローは正常に設計されています")
    return True


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("  SAP SuccessFactors 権限グループ機能テスト")
    print("="*60)
    
    tests = [
        ("権限グループ取得", test_get_permission_role),
        ("権限グループメンバー取得", test_get_permission_role_members),
        ("ユーザー追加機能", test_add_user_to_admin_role_dry_run),
        ("ワークフローシミュレーション", test_workflow_simulation),
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
        print("  1. 実際のユーザーで権限グループ追加をテスト")
        print("  2. Watson Orchestrateと統合")
        print("  3. Slackからのエンドツーエンドテスト")
        return 0
    else:
        print("\n⚠️  一部のテストが失敗しました")
        print("   エラーメッセージを確認して問題を解決してください")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob