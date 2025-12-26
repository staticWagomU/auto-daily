# Repository Guidelines

## プロジェクト構成とモジュール配置
- `src/auto_daily/`: アプリ本体（ウィンドウ監視、キャプチャ、OCR、ログ、スケジューラ、要約、LLM 連携）。
- `tests/`: pytest のテスト群。
- `scripts/`: 補助スクリプト（`start.sh`, `report.sh`, `setup-permissions.sh`）。
- ルート設定: `pyproject.toml`, `prompt.txt`, `summary_prompt.txt`, `calendar_config.yaml.example`, `slack_config.yaml.example`。

## ビルド/テスト/開発コマンド
- `python -m auto_daily`: アプリのエントリーポイント起動。
- `python -m auto_daily --start`: 監視 + キャプチャのパイプライン開始。
- `python -m auto_daily summarize`: 現在の1時間分ログの要約。
- `python -m auto_daily report`: 日報生成。
- `pytest tests/ -v`: テスト実行。
- `ruff check .`: lint。
- `ruff format .`: フォーマット。
- `ty check src/`: 型チェック。

## コーディングスタイルと命名規約
- 言語: Python 3.12+。型ヒントを活用し、責務が小さい関数を作る。
- フォーマット/ lint: `ruff` に準拠し、import を整理する。
- 命名: 関数/変数は snake_case、クラスは PascalCase、定数は UPPER_SNAKE_CASE。
- パス操作: `pathlib.Path` を優先。

## テストガイドライン
- フレームワーク: `pytest`。
- テストファイル: `tests/test_*.py`、テスト関数: `test_*`。
- `logger.py` や `summarize.py` などはユニットテストを優先。
- 変更前後で `pytest tests/ -v` を実行する。

## コミット/プルリクガイドライン
- “Tidy First” に従い、構造変更と振る舞い変更を分ける。
- 目安の接頭辞: `refactor:`, `feat:`, `fix:`。可能なら本文で「なぜ」を記載。
- PR には変更概要、実行したテスト、設定変更（`.env` や YAML 追加/更新）を記載。

## セキュリティ/設定の注意
- 秘密情報はコミットしない。キーは `.env`、Slack/Calendar はローカル YAML を使う。
- macOS 権限（画面収録/アクセシビリティ）が必要。`./scripts/setup-permissions.sh` を使用。

## エージェント向け指示
- Scrum ダッシュボードを扱う場合は `plan.md` のロール/ワークフローに従って更新する。
