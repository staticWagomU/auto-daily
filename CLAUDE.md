# auto-daily

macOS でウィンドウ切り替え時に作業コンテキストを自動キャプチャし、Ollama を活用して日報を自動生成するツール。

## Tech Stack

- **Language**: Python 3.12+
- **Test**: pytest
- **Lint/Format**: ruff
- **Type Checker**: ty
- **macOS APIs**: pyobjc (Vision Framework, AppKit)

## Project Structure

```
auto-daily/
├── src/
│   └── auto_daily/
│       ├── __init__.py        # エントリーポイント
│       ├── window_monitor.py  # ウィンドウ切り替え検知
│       ├── capture.py         # スクリーンキャプチャ
│       ├── ocr.py             # Vision Framework OCR
│       ├── logger.py          # JSONL ログ保存
│       ├── processor.py       # ウィンドウ変更処理パイプライン
│       ├── scheduler.py       # 定期キャプチャ
│       ├── summarize.py       # 時間単位のログ要約
│       ├── config.py          # 設定管理
│       ├── ollama.py          # Ollama 連携・日報生成
│       ├── permissions.py     # macOS 権限チェック
│       ├── slack_parser.py    # Slack コンテキスト抽出
│       ├── calendar.py        # Google カレンダー iCal 連携
│       └── llm/               # LLM クライアント抽象化
│           ├── __init__.py
│           ├── protocol.py    # LLMClient Protocol
│           ├── ollama.py      # Ollama バックエンド
│           └── openai.py      # OpenAI バックエンド
├── scripts/
│   ├── start.sh               # アプリ起動スクリプト
│   ├── report.sh              # 日報生成スクリプト
│   └── setup-permissions.sh   # 権限設定スクリプト
├── tests/
├── plan.md                    # AI-Agentic Scrum Dashboard
├── plan-archive.md            # 完了した PBI のアーカイブ
└── pyproject.toml
```

## Commands

```bash
# Run tests
pytest tests/ -v

# Lint & Format
ruff check .
ruff format .

# Type check
ty check src/

# Run application
python -m auto_daily
```

## Development Workflow

Kent Beck の Tidy First 原則に従い、以下のワークフローで開発を行う:

```
1. /tidy:first    - 構造的改善を先に実施（import追加、関数抽出、コメント削除など）
2. /git:commit    - Tidy First のコミットを作成（refactor:）
3. 修正実施        - 実際の機能変更を実施
4. /git:commit    - 機能変更のコミットを作成（feat:/fix:）
5. /tidy:after    - 完了後の片付け（未使用importの削除など）
6. /git:commit    - Tidy After のコミットを作成（refactor:）
```

### コミットのガイドライン

- **こまめにコミット**: 1つの論理的な変更ごとにコミットを作成
- **構造と振る舞いを分離**: 構造的変更（リネーム、移動、抽出）と振る舞いの変更（ロジック追加、削除）は別コミットに
- **WHY を記述**: コミットメッセージには「なぜ」この変更が必要かを記述

## Development Notes

- macOS の権限設定が必要:
  - 画面収録: システム環境設定 > プライバシーとセキュリティ > 画面収録
  - アクセシビリティ: システム環境設定 > プライバシーとセキュリティ > アクセシビリティ
- Ollama または OpenAI API が必要
- pyobjc を使用して macOS ネイティブ API にアクセス
- 設定は `.env` ファイルまたは環境変数で管理
