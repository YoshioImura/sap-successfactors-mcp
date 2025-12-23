#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
権限グループ追加機能のテストスクリプト
"""

import os
import sys
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# プロジェクトのルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from src.tools.user_management import (
    create_sap_user_with_admin_role,
    add_user_to_admin_role,
    get_sap_user
)

def test_create_user_with_admin_role():
    """ユーザー作成＋権限グループ追加のテスト"""
    print("="*60)
    print("  ユーザー作成＋権限グループ追加テスト")
    print("="*60)
    
    # テストユーザー情報
    user_id = "BobTEST0004"
    username = "bobtest0004"
    first_name = "Bob"
    last_name = "Test"
    email = "bob.test0004@example.com"
    
    print(f"\nテストユーザー: {user_id}")
    print(f"ユーザー名: {username}")
    print(f"メール: {email}")
    
    # ユーザー作成＋権限グループ追加
    print("\n--- ユーザー作成＋権限グループ追加を実行 ---")
    result = create_sap_user_with_admin_role(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    
    print(f"\n結果: {'成功' if result['success'] else '失敗'}")
    print(f"メッセージ: {result['message']}")
    
    if result['success']:
        print("\n--- ユーザー作成結果 ---")
        user_creation = result.get('user_creation', {})
        print(f"ユーザー作成: {'成功' if user_creation.get('success') else '失敗'}")
        
        print("\n--- 権限グループ追加結果 ---")
        role_assignment = result.get('role_assignment', {})
        print(f"権限グループ追加: {'成功' if role_assignment.get('success') else '失敗'}")
        print(f"権限グループ名: {role_assignment.get('role_name', 'N/A')}")
    else:
        print(f"\nエラー: {result.get('error', 'Unknown error')}")
    
    return result['success']


def test_add_existing_user_to_role():
    """既存ユーザーを権限グループに追加するテスト"""
    print("\n" + "="*60)
    print("  既存ユーザーを権限グループに追加テスト")
    print("="*60)
    
    # 既存のテストユーザー
    user_id = "BobTEST0003"
    
    print(f"\nテストユーザー: {user_id}")
    
    # ユーザーが存在するか確認
    print("\n--- ユーザー存在確認 ---")
    user_info = get_sap_user(user_id)
    
    if not user_info.get('success'):
        print(f"エラー: ユーザー {user_id} が見つかりません")
        return False
    
    print(f"ユーザー確認: OK")
    
    # 権限グループに追加
    print("\n--- 権限グループに追加 ---")
    result = add_user_to_admin_role(user_id)
    
    print(f"\n結果: {'成功' if result['success'] else '失敗'}")
    print(f"メッセージ: {result['message']}")
    print(f"権限グループ名: {result.get('role_name', 'N/A')}")
    
    if not result['success']:
        print(f"\nエラー: {result.get('error', 'Unknown error')}")
    
    return result['success']


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("  SAP SuccessFactors 権限グループ機能テスト")
    print("="*60)
    
    # テスト1: 既存ユーザーを権限グループに追加
    test1_success = test_add_existing_user_to_role()
    
    # テスト2: ユーザー作成＋権限グループ追加
    # test2_success = test_create_user_with_admin_role()
    
    # 結果サマリー
    print("\n" + "="*60)
    print("  テスト結果サマリー")
    print("="*60)
    print(f"テスト1（既存ユーザー追加）: {'✅ 成功' if test1_success else '❌ 失敗'}")
    # print(f"テスト2（ユーザー作成＋追加）: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    return 0 if test1_success else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob