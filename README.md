# auto-daily

macOS でウィンドウ切り替え時に作業コンテキストを自動キャプチャし、Ollama を活用して日報を自動生成するツール。

## 機能

- **ウィンドウ監視**: アクティブウィンドウの切り替えを検知し、アプリ名・ウィンドウタイトルを自動取得
- **画面キャプチャ & OCR**: ウィンドウ切り替え時に画面をキャプチャし、Vision Framework で日本語テキストを抽出
- **JSONL ログ保存**: 作業コンテキストを JSONL 形式で日付・時間ごとに自動保存
- **時間単位の要約**: 1時間ごとにログを要約し、コンテキスト制限を回避
- **日報自動生成**: Ollama または OpenAI を使って蓄積されたログまたは要約から日報を自動作成
- **カレンダー連携**: Google カレンダーの iCal URL から予定を取得し、日報生成に活用
- **カスタマイズ可能**: ログ出力先、日報保存先、プロンプトテンプレートを設定可能

## 動作要件

- macOS 12.0 以降
- Python 3.12 以上
- [Ollama](https://ollama.ai/) がローカルで起動していること（または OpenAI API キー）

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/staticWagomU/auto-daily.git
cd auto-daily
```

### 2. 依存関係のインストール

```bash
# pip を使用する場合
pip install -e .

# uv を使用する場合（推奨）
uv sync
```

### 3. Ollama のセットアップ

```bash
# Ollama をインストール（未インストールの場合）
brew install ollama

# Ollama を起動
ollama serve

# 使用するモデルをプル（例: llama3.2）
ollama pull llama3.2
```

### 4. macOS 権限設定

アプリケーションを動作させるには、以下の権限が必要です：

1. **画面収録**: システム環境設定 > プライバシーとセキュリティ > 画面収録
2. **アクセシビリティ**: システム環境設定 > プライバシーとセキュリティ > アクセシビリティ

権限設定を簡単に行うためのスクリプトがあります：

```bash
# 権限設定画面を開く
./scripts/setup-permissions.sh

# 現在の権限状態を確認
./scripts/setup-permissions.sh --check
```

## 使用方法

### ウィンドウ監視の開始

```bash
# ウィンドウ監視を開始
python -m auto_daily --start

# または CLI コマンドで起動
auto-daily --start

# スクリプトで起動（Ollama 起動チェック付き）
./scripts/start.sh

# バージョン確認
auto-daily --version
```

### 停止方法

`Ctrl + C` で安全に停止できます。

### ログの要約

1時間ごとのログを要約することで、長時間の作業でもコンテキスト制限を回避できます。

```bash
# 現在の時間のログを要約
python -m auto_daily summarize

# 特定の日時を指定して要約
python -m auto_daily summarize --date 2024-12-24 --hour 14
```

要約は `~/.auto-daily/summaries/YYYY-MM-DD/summary_HH.md` に保存されます。

### 日報の生成

蓄積された要約またはログから日報を生成できます。要約ファイルがある場合は優先的に使用されます。

```bash
# 今日の要約/ログから日報を生成
python -m auto_daily report

# または CLI コマンドで
auto-daily report

# スクリプトで実行（Ollama 起動チェック付き）
./scripts/report.sh

# 特定の日付の日報を生成
python -m auto_daily report --date 2024-12-24
./scripts/report.sh --date 2024-12-24

# 未要約のログを自動で要約してから日報を生成
python -m auto_daily report --auto-summarize
./scripts/report.sh --auto-summarize

# カレンダー情報を含めて日報を生成
python -m auto_daily report --with-calendar
```

生成された日報は `~/.auto-daily/reports/`（またはプロジェクトルートの `reports/`）に `daily_report_YYYY-MM-DD.md` という形式で保存されます。

## 設定

### .env ファイルによる設定

`~/.auto-daily/.env` ファイルで各種設定を一元管理できます。

```bash
# 設定ファイルを作成
mkdir -p ~/.auto-daily
cp .env.example ~/.auto-daily/.env

# 必要に応じて編集
vim ~/.auto-daily/.env
```

利用可能な環境変数：

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `AI_BACKEND` | LLM バックエンド（`ollama` または `openai`） | `ollama` |
| `OLLAMA_BASE_URL` | Ollama の接続先 URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | 使用する Ollama モデル | `llama3.2` |
| `OPENAI_API_KEY` | OpenAI API キー（`AI_BACKEND=openai` の場合必須） | なし |
| `OPENAI_MODEL` | 使用する OpenAI モデル | `gpt-4o-mini` |
| `AUTO_DAILY_CAPTURE_INTERVAL` | 定期キャプチャの間隔（秒） | `30` |
| `AUTO_DAILY_LOG_DIR` | ログ出力先ディレクトリ | `~/.auto-daily/logs/` |
| `AUTO_DAILY_SUMMARIES_DIR` | 要約出力先ディレクトリ | `~/.auto-daily/summaries/` |
| `AUTO_DAILY_REPORTS_DIR` | 日報出力先ディレクトリ | `~/.auto-daily/reports/` |

### ログ出力先のカスタマイズ

環境変数 `AUTO_DAILY_LOG_DIR` でログの出力先を指定できます。

```bash
# 例: ~/Documents/logs に保存
export AUTO_DAILY_LOG_DIR=~/Documents/logs
auto-daily --start
```

未設定の場合は `~/.auto-daily/logs/` に保存されます。

### プロンプトテンプレートのカスタマイズ

`~/.auto-daily/prompt.txt` にテンプレートファイルを作成することで、日報生成のプロンプトをカスタマイズできます。

```bash
# テンプレートファイルを作成
mkdir -p ~/.auto-daily
cat > ~/.auto-daily/prompt.txt << 'EOF'
以下のアクティビティログに基づいて、日報を作成してください。

## 今日のアクティビティ
{activities}

## 出力フォーマット
1. 今日の作業内容
2. 成果・進捗
3. 課題・所感
EOF
```

テンプレート内の `{activities}` プレースホルダーにアクティビティログが埋め込まれます。

### カレンダー連携

Google カレンダーの予定を日報生成に活用できます。

```bash
# 設定ファイルを作成
cp calendar_config.yaml.example calendar_config.yaml

# 設定を編集
vim calendar_config.yaml
```

設定ファイル形式:

```yaml
calendars:
  - name: "仕事"
    ical_url: "https://calendar.google.com/calendar/ical/xxx/private-xxx/basic.ics"
  - name: "個人"
    ical_url: "https://calendar.google.com/calendar/ical/yyy/private-yyy/basic.ics"
```

iCal URL の取得方法:
1. Google カレンダーを開く
2. 設定 → カレンダーを選択
3. 「カレンダーの統合」セクション
4. 「秘密のアドレス（iCal 形式）」をコピー

### OpenAI の使用

Ollama の代わりに OpenAI API を使用できます。

```bash
# .env ファイルに設定
cat >> .env << 'EOF'
AI_BACKEND=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
EOF
```

## 開発

### テストの実行

```bash
pytest tests/ -v
```

### Lint & Format

```bash
ruff check .
ruff format .
```

### 型チェック

```bash
ty check src/
```

## ライセンス

MIT License
