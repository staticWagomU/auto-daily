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
    echo "関連スクリプト:"
    echo "  ./scripts/report.sh   日報を生成"
    echo ""
    echo "環境変数:"
    echo "  AUTO_DAILY_LOG_DIR  ログ出力先ディレクトリ（デフォルト: ~/.auto-daily/logs/）"
    echo ""
    echo "必要な権限:"
    echo "  - 画面収録の権限（システム環境設定 > プライバシーとセキュリティ > 画面収録）"
    echo ""
    echo "Ollama が起動している必要があります。"
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

    # Ollama チェック
    check_ollama

    echo ""
    echo -e "${YELLOW}ウィンドウ監視を開始します。Ctrl+C で停止できます。${NC}"
    echo ""

    # アプリケーション起動
    python -m auto_daily --start
}

main "$@"
