#!/bin/bash
#
# auto-daily 起動スクリプト
#
# 使用方法:
#   ./scripts/start.sh          # アプリケーションを起動
#   ./scripts/start.sh --help   # ヘルプを表示
#

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
    echo "auto-daily 起動スクリプト"
    echo ""
    echo "使用方法:"
    echo "  $0          ウィンドウ監視を開始"
    echo "  $0 --help   このヘルプを表示"
    echo ""
    echo "機能:"
    echo "  - ウィンドウ切り替え時に画面キャプチャ・OCR・ログ保存を実行"
    echo "  - 30秒ごとの定期キャプチャ"
    echo "  - 1時間ごとにログを自動要約"
    echo ""
    echo "ログ出力:"
    echo "  - ログ: ~/.auto-daily/logs/YYYY-MM-DD/activity_HH.jsonl（時間ごと）"
    echo "  - 要約: ~/.auto-daily/summaries/YYYY-MM-DD/summary_HH.md（1時間ごとに自動生成）"
    echo ""
    echo "関連スクリプト:"
    echo "  ./scripts/report.sh            日報を生成（自動要約付き）"
    echo "  ./scripts/setup-permissions.sh 権限設定"
    echo ""
    echo "環境変数:"
    echo "  AUTO_DAILY_LOG_DIR       ログ出力先ディレクトリ（デフォルト: ~/.auto-daily/logs/）"
    echo "  AUTO_DAILY_SUMMARIES_DIR 要約出力先ディレクトリ（デフォルト: ~/.auto-daily/summaries/）"
    echo ""
    echo "必要な権限:"
    echo "  - 画面収録の権限（システム環境設定 > プライバシーとセキュリティ > 画面収録）"
    echo ""
    echo "Ollama が起動している必要があります。"
}

# macOS 権限チェック
check_permissions() {
    # Python を使って権限状態を確認
    local result
    result=$(python3 -c "
from auto_daily.permissions import check_all_permissions

permissions = check_all_permissions()
missing = [name for name, granted in permissions.items() if not granted]

if missing:
    print('MISSING:' + ','.join(missing))
else:
    print('OK')
" 2>/dev/null || echo "ERROR")

    if [[ "$result" == "OK" ]]; then
        echo -e "${GREEN}✓ macOS 権限が許可済み${NC}"
        return 0
    elif [[ "$result" == ERROR* ]]; then
        # 権限モジュールが読み込めない場合はスキップ
        echo -e "${YELLOW}⚠ 権限チェックをスキップ（モジュール読み込みエラー）${NC}"
        return 0
    else
        # 権限が不足している場合
        echo -e "${RED}⚠ 権限が不足しています${NC}"
        echo ""
        if [[ "$result" == *"screen_recording"* ]]; then
            echo "  - 画面収録の権限が必要です"
        fi
        if [[ "$result" == *"accessibility"* ]]; then
            echo "  - アクセシビリティの権限が必要です"
        fi
        echo ""
        echo "権限を設定するには:"
        echo "  ./scripts/setup-permissions.sh"
        echo ""
        echo -e "${YELLOW}権限なしで続行しますが、一部の機能が動作しない可能性があります。${NC}"
        return 0
    fi
}

# Ollama 起動チェック
check_ollama() {
    if ! curl -s --connect-timeout 2 http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${RED}エラー: Ollama が起動していません${NC}"
        echo ""
        echo "Ollama を起動してから再度実行してください:"
        echo "  ollama serve"
        exit 1
    fi
    echo -e "${GREEN}✓ Ollama が起動中${NC}"
}

# メイン処理
main() {
    # ヘルプオプションの処理
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi

    echo "auto-daily を起動しています..."
    echo ""

    # 権限チェック
    check_permissions

    # Ollama チェック
    check_ollama

    echo ""
    echo -e "${YELLOW}ウィンドウ監視を開始します。Ctrl+C で停止できます。${NC}"
    echo ""

    # アプリケーション起動
    python -m auto_daily --start
}

main "$@"
