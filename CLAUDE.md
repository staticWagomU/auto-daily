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
│       ├── __init__.py
│       ├── window_monitor.py  # ウィンドウ切り替え検知
│       ├── capture.py         # スクリーンキャプチャ
│       ├── ocr.py             # Vision Framework OCR
│       ├── logger.py          # JSONL ログ保存
│       └── ollama.py          # Ollama 連携・日報生成
├── tests/
├── plan.md                    # AI-Agentic Scrum Dashboard
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

## Development Notes

- macOS の権限設定が必要: システム環境設定 > プライバシーとセキュリティ > 画面収録
- Ollama がローカルで起動している必要がある
- pyobjc を使用して macOS ネイティブ API にアクセス
