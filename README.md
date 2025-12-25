# auto-daily

macOS でウィンドウ切り替え時に作業コンテキストを自動キャプチャし、Ollama を活用して日報を自動生成するツール。

## 機能

- **ウィンドウ監視**: アクティブウィンドウの切り替えを検知し、アプリ名・ウィンドウタイトルを自動取得
- **画面キャプチャ & OCR**: ウィンドウ切り替え時に画面をキャプチャし、Vision Framework で日本語テキストを抽出
- **JSONL ログ保存**: 作業コンテキストを JSONL 形式で日付ごとに自動保存
- **日報自動生成**: Ollama を使って蓄積されたログから日報を自動作成
- **カスタマイズ可能**: ログ出力先やプロンプトテンプレートを設定可能

## 動作要件

- macOS 12.0 以降
- Python 3.12 以上
- [Ollama](https://ollama.ai/) がローカルで起動していること

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

1. **システム環境設定** > **プライバシーとセキュリティ** > **画面収録**
2. ターミナル（または使用する IDE）に画面収録の権限を付与

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

### 日報の生成

蓄積されたログから日報を生成できます。

```bash
# 今日のログから日報を生成
python -m auto_daily report

# または CLI コマンドで
auto-daily report

# スクリプトで実行（Ollama 起動チェック付き）
./scripts/report.sh

# 特定の日付のログから日報を生成
python -m auto_daily report --date 2024-12-24
./scripts/report.sh --date 2024-12-24
```

生成された日報は `~/.auto-daily/reports/` に `daily_report_YYYY-MM-DD.md` という形式で保存されます。

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
| `OLLAMA_BASE_URL` | Ollama の接続先 URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | 使用する Ollama モデル | `llama3.2` |
| `AUTO_DAILY_CAPTURE_INTERVAL` | 定期キャプチャの間隔（秒） | `30` |
| `AUTO_DAILY_LOG_DIR` | ログ出力先ディレクトリ | `~/.auto-daily/logs/` |

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
