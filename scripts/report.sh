#!/bin/bash
#
# auto-daily 日報生成スクリプト
#
# 使用方法:
#   ./scripts/report.sh                    # 今日のログから日報を生成
#   ./scripts/report.sh --date 2024-12-24  # 特定の日付のログから日報を生成
#   ./scripts/report.sh --help             # ヘルプを表示
#

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
    echo "auto-daily 日報生成スクリプト"
    echo ""
    echo "使用方法:"
    echo "  $0                       今日の要約/ログから日報を生成（自動要約付き）"
    echo "  $0 --date YYYY-MM-DD     特定の日付の日報を生成"
    echo "  $0 --no-auto-summarize   自動要約をスキップして日報を生成"
    echo "  $0 --with-calendar       カレンダー情報を含めて日報を生成"
    echo "  $0 --help                このヘルプを表示"
    echo ""
    echo "オプション:"
    echo "  --date, -d              日報を生成する日付（YYYY-MM-DD 形式）"
    echo "  --auto-summarize, -a    未要約のログを自動で要約してから日報を生成（デフォルト）"
    echo "  --no-auto-summarize, -n 自動要約をスキップ"
    echo "  --with-calendar, -c     カレンダー情報を含めて日報を生成"
    echo ""
    echo "例:"
    echo "  $0                        # 今日の日報を生成（自動要約付き）"
    echo "  $0 --date 2024-12-24      # 2024年12月24日の日報を生成（自動要約付き）"
    echo "  $0 -d 2024-12-24          # 同上（短縮形）"
    echo "  $0 --no-auto-summarize    # 自動要約をスキップして日報を生成"
    echo "  $0 -n -d 2024-12-24       # 特定日付を自動要約なしで日報を生成"
    echo "  $0 --with-calendar        # カレンダー情報を含めて日報を生成"
    echo ""
    echo "出力先:"
    echo "  要約: ~/.auto-daily/summaries/YYYY-MM-DD/summary_HH.md"
    echo "  日報: ~/.auto-daily/reports/daily_report_YYYY-MM-DD.md"
    echo "       （プロジェクト内に reports/ がある場合はそちらを優先）"
    echo ""
    echo "環境変数:"
    echo "  AUTO_DAILY_LOG_DIR       ログ読み込み元ディレクトリ（デフォルト: ~/.auto-daily/logs/）"
    echo "  AUTO_DAILY_SUMMARIES_DIR 要約保存先ディレクトリ（デフォルト: ~/.auto-daily/summaries/）"
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

# 日付バリデーション
validate_date() {
    local date_str="$1"
    if [[ ! "$date_str" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo -e "${RED}エラー: 日付形式が不正です${NC}"
        echo "YYYY-MM-DD 形式で指定してください（例: 2024-12-24）"
        exit 1
    fi
}

# メイン処理
main() {
    local date_option=""
    local auto_summarize="--auto-summarize"  # デフォルトで有効
    local with_calendar=""

    # 引数の解析
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --date|-d)
                if [[ -z "$2" ]]; then
                    echo -e "${RED}エラー: --date オプションには日付が必要です${NC}"
                    exit 1
                fi
                validate_date "$2"
                date_option="--date $2"
                shift 2
                ;;
            --auto-summarize|-a)
                auto_summarize="--auto-summarize"
                shift
                ;;
            --no-auto-summarize|-n)
                auto_summarize=""
                shift
                ;;
            --with-calendar|-c)
                with_calendar="--with-calendar"
                shift
                ;;
            *)
                echo -e "${RED}エラー: 不明なオプション: $1${NC}"
                echo "ヘルプを表示するには: $0 --help"
                exit 1
                ;;
        esac
    done

    echo -e "${BLUE}日報を生成しています...${NC}"
    if [[ -n "$auto_summarize" ]]; then
        echo -e "${YELLOW}（未要約のログがある場合は自動で要約します）${NC}"
    fi
    echo ""

    # Ollama チェック
    check_ollama

    echo ""

    # アプリケーション実行
    # shellcheck disable=SC2086
    python -m auto_daily report $date_option $auto_summarize $with_calendar

    echo ""
    echo -e "${GREEN}✓ 日報の生成が完了しました${NC}"
}

main "$@"
