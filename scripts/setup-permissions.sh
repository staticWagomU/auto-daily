#!/bin/bash
#
# macOS 権限設定スクリプト
#
# 使用方法:
#   ./scripts/setup-permissions.sh          # 権限設定画面を開く
#   ./scripts/setup-permissions.sh --check  # 現在の権限状態を確認
#   ./scripts/setup-permissions.sh --help   # ヘルプを表示
#

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
    echo "macOS 権限設定スクリプト"
    echo ""
    echo "使用方法:"
    echo "  $0          権限設定画面を開く"
    echo "  $0 --check  現在の権限状態を確認"
    echo "  $0 --help   このヘルプを表示"
    echo ""
    echo "必要な権限:"
    echo "  1. 画面収録（Screen Recording）"
    echo "     - screencapture コマンドに必要"
    echo "     - システム環境設定 > プライバシーとセキュリティ > 画面収録"
    echo ""
    echo "  2. アクセシビリティ（Accessibility）"
    echo "     - ウィンドウ情報取得に必要"
    echo "     - システム環境設定 > プライバシーとセキュリティ > アクセシビリティ"
}

# 権限状態チェック
check_permissions() {
    echo "権限状態を確認しています..."
    echo ""

    # Python を使って権限状態を確認
    python3 -c "
from auto_daily.permissions import check_all_permissions

permissions = check_all_permissions()

print('権限状態:')
print('')

# Screen Recording
if permissions['screen_recording']:
    print('  ✓ 画面収録: 許可済み')
else:
    print('  ✗ 画面収録: 未許可')

# Accessibility
if permissions['accessibility']:
    print('  ✓ アクセシビリティ: 許可済み')
else:
    print('  ✗ アクセシビリティ: 未許可')

print('')

# 総合判定
if all(permissions.values()):
    print('すべての権限が許可されています。')
    exit(0)
else:
    missing = [name for name, granted in permissions.items() if not granted]
    print(f'不足している権限: {len(missing)}個')
    print('')
    print('権限を設定するには:')
    print('  ./scripts/setup-permissions.sh')
    exit(1)
"
    return $?
}

# 権限設定画面を開く
open_settings() {
    echo -e "${YELLOW}権限設定画面を開いています...${NC}"
    echo ""

    # Screen Recording 設定を開く
    echo "1. 画面収録の設定画面を開きます..."
    open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
    sleep 1

    # Accessibility 設定を開く
    echo "2. アクセシビリティの設定画面を開きます..."
    open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

    echo ""
    echo -e "${GREEN}設定画面が開きました。${NC}"
    echo ""
    echo "各設定画面で、ターミナル（またはアプリケーション）を許可リストに追加してください。"
    echo ""
    echo "設定完了後、権限状態を確認するには:"
    echo "  ./scripts/setup-permissions.sh --check"
}

# メイン処理
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --check)
            check_permissions
            ;;
        "")
            open_settings
            ;;
        *)
            echo -e "${RED}エラー: 不明なオプション: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
