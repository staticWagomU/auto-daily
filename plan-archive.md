# Plan Archive - Completed Product Backlog Items

このファイルには完了した PBI（Product Backlog Item）が保存されています。

---

## Completed PBIs

```yaml
product_backlog_archive:
  - id: PBI-001
    story:
      role: "Mac ユーザー"
      capability: "ウィンドウを切り替えたタイミングでアクティブウィンドウの名前を自動取得できる"
      benefit: "何の作業をしていたかを手動で記録する必要がなくなる"
    acceptance_criteria:
      - criterion: "AppleScript でアクティブウィンドウのアプリ名とウィンドウタイトルを取得できる"
        verification: "pytest tests/test_window_monitor.py::test_get_active_window -v"
      - criterion: "ウィンドウ切り替えを検知してイベントを発火できる"
        verification: "pytest tests/test_window_monitor.py::test_window_change_detection -v"
      - criterion: "バックグラウンドで常駐し、ウィンドウ変更を監視し続ける"
        verification: "pytest tests/test_window_monitor.py::test_background_monitoring -v"
    dependencies: []
    status: done

  - id: PBI-002
    story:
      role: "Mac ユーザー"
      capability: "ウィンドウ切り替え時に画面全体をキャプチャし、OCR でテキストを抽出できる"
      benefit: "画面に表示されている内容を自動で記録できる"
    acceptance_criteria:
      - criterion: "macOS の screencapture コマンドで画面全体をキャプチャできる"
        verification: "pytest tests/test_capture.py::test_screen_capture -v"
      - criterion: "Vision Framework を使って画像から日本語テキストを抽出できる"
        verification: "pytest tests/test_ocr.py::test_japanese_ocr -v"
      - criterion: "OCR 結果が空でない限り、有効なテキストを返す"
        verification: "pytest tests/test_ocr.py::test_ocr_returns_text -v"
    dependencies:
      - PBI-001
    status: done

  - id: PBI-003
    story:
      role: "Mac ユーザー"
      capability: "取得した情報を JSONL 形式でログ保存し、使用済みのキャプチャ画像を自動削除できる"
      benefit: "ディスク容量を節約しながら、必要な情報だけを蓄積できる"
    acceptance_criteria:
      - criterion: "ウィンドウ名、OCR テキスト、タイムスタンプを含む JSON を JSONL ファイルに追記できる"
        verification: "pytest tests/test_logger.py::test_jsonl_append -v"
      - criterion: "JSONL ファイルは日付ごとにローテーションされる"
        verification: "pytest tests/test_logger.py::test_daily_rotation -v"
      - criterion: "OCR 処理完了後にキャプチャ画像を削除する"
        verification: "pytest tests/test_capture.py::test_image_cleanup -v"
    dependencies:
      - PBI-002
    status: done

  - id: PBI-004
    story:
      role: "Mac ユーザー"
      capability: "数分間隔で Ollama を呼び出し、蓄積されたログから日報を自動生成できる"
      benefit: "一日の作業内容を要約した日報を手作業なしで作成できる"
    acceptance_criteria:
      - criterion: "設定された間隔で Ollama API を呼び出せる"
        verification: "pytest tests/test_ollama.py::test_scheduled_call -v"
      - criterion: "JSONL ログを読み込み、日報用のプロンプトを生成できる"
        verification: "pytest tests/test_ollama.py::test_prompt_generation -v"
      - criterion: "Ollama からの応答を日報ファイルとして保存できる"
        verification: "pytest tests/test_ollama.py::test_save_daily_report -v"
    dependencies:
      - PBI-003
    status: done

  - id: PBI-005
    story:
      role: "Mac ユーザー"
      capability: "auto-daily コマンドでアプリケーションを起動し、ウィンドウ監視から日報生成までの一連の処理を実行できる"
      benefit: "インストール後すぐにコマンド一つで利用を開始できる"
    acceptance_criteria:
      - criterion: "python -m auto_daily でアプリケーションを起動できる"
        verification: "pytest tests/test_main.py::test_module_execution -v"
      - criterion: "auto-daily コマンド（pyproject.toml の scripts）で起動できる"
        verification: "pytest tests/test_main.py::test_cli_entrypoint -v"
      - criterion: "起動後、ウィンドウ監視ループが開始される"
        verification: "pytest tests/test_main.py::test_main_starts_monitoring -v"
    dependencies:
      - PBI-004
    status: done

  - id: PBI-006
    story:
      role: "Mac ユーザー"
      capability: "環境変数 AUTO_DAILY_LOG_DIR でログの出力先ディレクトリを設定できる"
      benefit: "ログの保存場所を自分の好みや運用環境に合わせてカスタマイズできる"
    acceptance_criteria:
      - criterion: "AUTO_DAILY_LOG_DIR 環境変数でログ出力先を指定できる"
        verification: "pytest tests/test_config.py::test_log_dir_from_env -v"
      - criterion: "環境変数が未設定の場合はデフォルトディレクトリ (~/.auto-daily/logs/) を使用する"
        verification: "pytest tests/test_config.py::test_log_dir_default -v"
      - criterion: "指定されたディレクトリが存在しない場合は自動作成する"
        verification: "pytest tests/test_config.py::test_log_dir_auto_create -v"
    dependencies:
      - PBI-005
    status: done

  - id: PBI-007
    story:
      role: "Mac ユーザー"
      capability: "Ollama に渡すプロンプトをテキストファイルで自由にカスタマイズできる"
      benefit: "日報のフォーマットや指示内容を自分の業務スタイルに合わせて変更できる"
    acceptance_criteria:
      - criterion: "プロンプトテンプレートを外部ファイル (~/.auto-daily/prompt.txt) から読み込める"
        verification: "pytest tests/test_config.py::test_prompt_template_from_file -v"
      - criterion: "テンプレート内の {activities} プレースホルダーにアクティビティログが埋め込まれる"
        verification: "pytest tests/test_ollama.py::test_prompt_template_placeholder -v"
      - criterion: "テンプレートファイルが存在しない場合はデフォルトテンプレートを使用する"
        verification: "pytest tests/test_config.py::test_prompt_template_default -v"
    dependencies:
      - PBI-006
    status: done

  - id: PBI-008
    story:
      role: "開発者・利用者"
      capability: "README.md を読んでアプリケーションの概要、インストール方法、使い方を理解できる"
      benefit: "新規ユーザーがスムーズに導入・利用を開始できる"
    acceptance_criteria:
      - criterion: "README.md にプロジェクトの概要と機能一覧が記載されている"
        verification: "README.md ファイルの存在と内容を確認"
      - criterion: "インストール手順（pip install、Ollama セットアップ、macOS 権限設定）が記載されている"
        verification: "README.md のインストールセクションを確認"
      - criterion: "使用方法（コマンド例、環境変数設定）が記載されている"
        verification: "README.md の使用方法セクションを確認"
    dependencies:
      - PBI-005
    status: done

  - id: PBI-009
    story:
      role: "Mac ユーザー"
      capability: "シェルスクリプトを実行するだけでアプリケーションを起動できる"
      benefit: "複雑なコマンドを覚えなくても簡単にアプリを起動できる"
    acceptance_criteria:
      - criterion: "scripts/start.sh を実行するとアプリケーションが起動する"
        verification: "bash scripts/start.sh --help でヘルプが表示される"
      - criterion: "Ollama が起動していない場合はエラーメッセージを表示する"
        verification: "Ollama 停止状態で scripts/start.sh を実行しエラーを確認"
      - criterion: "スクリプトに実行権限が付与されている"
        verification: "ls -la scripts/start.sh で実行権限を確認"
    dependencies:
      - PBI-005
    status: done

  - id: PBI-010
    story:
      role: "Mac ユーザー"
      capability: "ウィンドウ切り替え時に自動的に画面キャプチャ、OCR、ログ保存が実行される"
      benefit: "手動操作なしで作業コンテキストが自動記録される"
    acceptance_criteria:
      - criterion: "ウィンドウ切り替え時に capture_screen() で画面がキャプチャされる"
        verification: "pytest tests/test_integration.py::test_capture_on_window_change -v"
      - criterion: "キャプチャ画像に対して perform_ocr() が実行され、テキストが抽出される"
        verification: "pytest tests/test_integration.py::test_ocr_on_capture -v"
      - criterion: "ウィンドウ情報と OCR 結果が append_log() でログに保存される"
        verification: "pytest tests/test_integration.py::test_log_on_window_change -v"
      - criterion: "処理完了後に cleanup_image() で画像が削除される"
        verification: "pytest tests/test_integration.py::test_cleanup_after_processing -v"
    dependencies:
      - PBI-001
      - PBI-002
      - PBI-003
    status: done

  - id: PBI-011
    story:
      role: "Mac ユーザー"
      capability: "ウィンドウ切り替えとは別に、30秒ごとに定期的に画面キャプチャとOCRが実行される"
      benefit: "長時間同じウィンドウで作業していても、作業内容が定期的に記録される"
    acceptance_criteria:
      - criterion: "30秒間隔で定期的にキャプチャ・OCR・ログ保存が実行される"
        verification: "pytest tests/test_scheduler.py::test_periodic_capture -v"
      - criterion: "ウィンドウ切り替えトリガーと定期トリガーが共存する"
        verification: "pytest tests/test_scheduler.py::test_coexistence_with_window_trigger -v"
      - criterion: "アプリケーション停止時に定期実行も停止する"
        verification: "pytest tests/test_scheduler.py::test_stop_periodic_capture -v"
    dependencies:
      - PBI-010
    status: done

  - id: PBI-012
    story:
      role: "Mac ユーザー"
      capability: "Slack ウィンドウ表示時にチャンネル名とワークスペース名を自動抽出できる"
      benefit: "どのチャンネルで作業していたかが日報に反映される"
    acceptance_criteria:
      - criterion: "ウィンドウタイトルからチャンネル名を抽出できる"
        verification: "pytest tests/test_slack_parser.py::test_channel_extraction -v"
      - criterion: "ウィンドウタイトルからワークスペース名を抽出できる"
        verification: "pytest tests/test_slack_parser.py::test_workspace_extraction -v"
      - criterion: "Slack コンテキストがログエントリに追加される"
        verification: "pytest tests/test_slack_parser.py::test_slack_context_in_log -v"
    technical_notes: |
      Slack macOS ウィンドウタイトルの一般的なフォーマット:
      - チャンネル: "#channel-name | Workspace Name" または "#channel-name - Workspace Name"
      - DM: "@username | Workspace Name"
      - スレッド: "Thread in #channel-name | Workspace Name"
      新規ファイル: src/auto_daily/slack_parser.py
    dependencies:
      - PBI-010
    status: done

  - id: PBI-013
    story:
      role: "Mac ユーザー"
      capability: "YAML設定でワークスペースごとのユーザー名を設定し、自分のメッセージを識別できる"
      benefit: "複数ワークスペースで自分の発言を正確に記録できる"
    acceptance_criteria:
      - criterion: "slack_config.yaml からワークスペースごとのユーザー名を読み込める"
        verification: "pytest tests/test_config.py::test_slack_username_config -v"
      - criterion: "OCR テキストから会話全体を抽出できる"
        verification: "pytest tests/test_slack_parser.py::test_conversation_extraction -v"
      - criterion: "ユーザー名で自分のメッセージをフィルタできる"
        verification: "pytest tests/test_slack_parser.py::test_my_message_filter -v"
    technical_notes: |
      ## YAML 設定ファイル
      - パス: ~/.auto-daily/slack_config.yaml
      - フォーマット:
        ```yaml
        workspaces:
          "Workspace Name":
            username: "your-username"
        ```

      ## 新規依存関係
      - PyYAML (pyyaml) を pyproject.toml の dependencies に追加

      ## 新規関数
      - config.py: get_slack_username(workspace: str) -> str | None
        - ワークスペース名からユーザー名を取得
        - 設定ファイルがない場合は None を返す

      - slack_parser.py: extract_conversations(ocr_text: str) -> list[Message]
        - OCR テキストから会話を抽出
        - Message = TypedDict with username, timestamp, content
        - パターン: "username  HH:MM" または "username  HH:MM AM/PM"

      - slack_parser.py: filter_my_messages(conversations: list[Message], username: str) -> list[Message]
        - 自分のメッセージをフィルタ

      ## 既存パターンの踏襲
      - config.py の get_prompt_template() と同様のファイル読み込みパターン
      - slack_parser.py の parse_slack_title() と同様の正規表現パターン
    story_points: 5
    dependencies:
      - PBI-012
    status: done

  - id: PBI-014
    story:
      role: "Mac ユーザー"
      capability: "コマンドラインから日報生成を実行できる"
      benefit: "任意のタイミングで蓄積されたログから日報を生成できる"
    acceptance_criteria:
      - criterion: "python -m auto_daily report で今日のログから日報を生成できる"
        verification: "pytest tests/test_main.py::test_report_command -v"
      - criterion: "--date オプションで過去の日付のログから日報を生成できる"
        verification: "pytest tests/test_main.py::test_report_with_date_option -v"
      - criterion: "生成された日報が ~/.auto-daily/reports/ に保存される"
        verification: "pytest tests/test_main.py::test_report_saves_to_reports_dir -v"
      - criterion: "日報生成後にファイルパスが標準出力に表示される"
        verification: "pytest tests/test_main.py::test_report_outputs_path -v"
    dependencies:
      - PBI-004
    technical_notes: |
      ## 実装方針
      - 既存の argparse に `report` サブコマンドを追加
      - OllamaClient と generate_daily_report_prompt() を活用
      - save_daily_report() で ~/.auto-daily/reports/ に保存
      - ログファイルは get_log_dir() から日付ベースで取得

      ## 新規関数
      - __init__.py: report_command(date_str: str | None) -> None
        - 日報生成のメインロジック
        - date_str が None なら今日の日付を使用
        - ログファイルが存在しない場合はエラーメッセージを表示
    story_points: 5
    status: done

  - id: PBI-015
    story:
      role: "Mac ユーザー"
      capability: ".env ファイルで Ollama の接続先やモデル名などの設定を管理できる"
      benefit: "設定を一元管理でき、環境ごとに異なる設定を簡単に切り替えられる"
    acceptance_criteria:
      - criterion: ".env ファイルから環境変数を読み込める"
        verification: "pytest tests/test_config.py::test_load_dotenv -v"
      - criterion: "OLLAMA_BASE_URL 環境変数で Ollama の接続先を設定できる"
        verification: "pytest tests/test_config.py::test_ollama_base_url_from_env -v"
      - criterion: "OLLAMA_MODEL 環境変数で使用するモデルを設定できる"
        verification: "pytest tests/test_config.py::test_ollama_model_from_env -v"
      - criterion: "AUTO_DAILY_CAPTURE_INTERVAL 環境変数でキャプチャ間隔を設定できる"
        verification: "pytest tests/test_config.py::test_capture_interval_from_env -v"
      - criterion: "各環境変数が未設定の場合はデフォルト値を使用する"
        verification: "pytest tests/test_config.py::test_env_defaults -v"
    technical_notes: |
      ## 新規依存関係
      - python-dotenv を pyproject.toml の dependencies に追加

      ## 新規設定項目とデフォルト値
      - OLLAMA_BASE_URL: "http://localhost:11434"
      - OLLAMA_MODEL: "llama3.2"
      - AUTO_DAILY_CAPTURE_INTERVAL: 30 (秒)

      ## 実装方針
      - config.py の先頭で load_dotenv() を呼び出し
      - .env ファイルのパス: プロジェクトルート or ~/.auto-daily/.env
      - 新規関数:
        - get_ollama_base_url() -> str
        - get_ollama_model() -> str
        - get_capture_interval() -> int

      ## 既存コードの修正
      - OllamaClient: base_url のデフォルトを get_ollama_base_url() から取得
      - PeriodicCapture: interval を get_capture_interval() から取得

      ## .env.example ファイル
      - リポジトリに .env.example を追加してサンプル設定を提供
      - .gitignore に .env を追加（まだなければ）
    story_points: 5
    dependencies:
      - PBI-006
    status: done

  - id: PBI-017
    story:
      role: "Mac ユーザー"
      capability: "report コマンドで正しいログファイルを参照して日報を生成できる"
      benefit: "蓄積したログから確実に日報を生成できる"
    acceptance_criteria:
      - criterion: "report コマンドが logger.py の get_log_filename() と同じ形式のファイルを参照する"
        verification: "pytest tests/test_main.py::test_report_uses_correct_log_filename -v"
      - criterion: "ログファイルが存在する場合に日報生成が成功する"
        verification: "pytest tests/test_main.py::test_report_with_existing_log -v"
    technical_notes: |
      ## バグの内容
      ログファイル名の形式が一致していない:
      - logger.py (生成時): "activity_YYYY-MM-DD.jsonl"
      - __init__.py (参照時): "YYYY-MM-DD.jsonl"

      ## 修正箇所
      __init__.py:51 の log_file 生成を修正:
      - 現在: log_file = log_dir / f"{target_date.isoformat()}.jsonl"
      - 修正後: logger.py の get_log_filename() を使用

      ## 修正方法
      from auto_daily.logger import get_log_filename
      log_file = log_dir / get_log_filename(datetime.combine(target_date, datetime.min.time()))

      または get_log_filename() を date 型も受け付けるように拡張
    story_points: 1
    dependencies:
      - PBI-014
    status: done

  - id: PBI-018
    story:
      role: "Mac ユーザー"
      capability: "プロジェクトルートの prompt.txt からプロンプトテンプレートを読み込める"
      benefit: "プロジェクトごとに異なるプロンプトを Git 管理できる"
    acceptance_criteria:
      - criterion: "プロジェクトルートの prompt.txt からプロンプトを読み込める"
        verification: "pytest tests/test_config.py::test_prompt_template_from_project_root -v"
      - criterion: "prompt.txt が存在しない場合はデフォルトテンプレートを使用する"
        verification: "pytest tests/test_config.py::test_prompt_template_default -v"
    technical_notes: |
      ## 変更内容
      .env の読み込みと同様に、プロジェクトルートの prompt.txt を優先的に読み込む。

      ## 修正箇所
      config.py: get_prompt_template() を修正
      - 現在: ~/.auto-daily/prompt.txt を読み込み
      - 変更後: カレントディレクトリの prompt.txt を読み込み

      ## 実装方針
      ```python
      def get_prompt_template() -> str:
          prompt_file = Path.cwd() / "prompt.txt"
          if prompt_file.exists():
              return prompt_file.read_text()
          return DEFAULT_PROMPT_TEMPLATE
      ```
    story_points: 1
    dependencies:
      - PBI-007
    status: done

  - id: PBI-019
    story:
      role: "Mac ユーザー"
      capability: "プロジェクトルートの slack_config.yaml から Slack 設定を読み込める"
      benefit: "プロジェクトごとに異なる Slack 設定を Git 管理でき、チームで設定を共有できる"
    acceptance_criteria:
      - criterion: "プロジェクトルートの slack_config.yaml から Slack ユーザー名を読み込める"
        verification: "pytest tests/test_config.py::test_slack_config_from_project_root -v"
      - criterion: "プロジェクトルートにファイルがない場合は ~/.auto-daily/slack_config.yaml にフォールバックする"
        verification: "pytest tests/test_config.py::test_slack_config_fallback_to_home -v"
      - criterion: "どちらにもファイルがない場合は None を返す"
        verification: "pytest tests/test_config.py::test_slack_username_config_file_not_found -v"
    technical_notes: |
      ## 変更内容
      .env や prompt.txt と同様に、プロジェクトルートの slack_config.yaml を優先的に読み込む。
      ホームディレクトリへのフォールバックも維持する（個人設定用）。

      ## 修正箇所
      config.py: get_slack_username() を修正
      - 現在: ~/.auto-daily/slack_config.yaml を読み込み
      - 変更後: まず Path.cwd() / "slack_config.yaml" をチェック
                存在しなければ ~/.auto-daily/slack_config.yaml にフォールバック

      ## 実装方針
      ```python
      def get_slack_username(workspace: str) -> str | None:
          # 1. プロジェクトルートをチェック
          project_config = Path.cwd() / "slack_config.yaml"
          if project_config.exists():
              config = yaml.safe_load(project_config.read_text())
              # ... parse and return

          # 2. ホームディレクトリにフォールバック
          home_config = Path.home() / ".auto-daily" / "slack_config.yaml"
          if home_config.exists():
              config = yaml.safe_load(home_config.read_text())
              # ... parse and return

          return None
      ```

      ## サンプルファイル
      slack_config.yaml.example をリポジトリルートに追加:
      ```yaml
      # Slack ワークスペースごとのユーザー名設定
      workspaces:
        "Your Workspace Name":
          username: "your-username"
        "Another Workspace":
          username: "another-username"
      ```
    story_points: 2
    dependencies:
      - PBI-013
    status: done

  - id: PBI-020
    story:
      role: "Mac ユーザー"
      capability: "スクリプトを実行して必要な macOS 権限（画面収録・アクセシビリティ）の設定画面を開ける"
      benefit: "手動で設定画面を探す手間なく、アプリに必要な権限を簡単に設定できる"
    acceptance_criteria:
      - criterion: "scripts/setup-permissions.sh を実行すると画面収録の設定画面が開く"
        verification: "bash scripts/setup-permissions.sh で設定画面が開くことを確認"
      - criterion: "アクセシビリティの設定画面が開く"
        verification: "bash scripts/setup-permissions.sh で設定画面が開くことを確認"
      - criterion: "現在の権限状態を確認できるオプション (--check) がある"
        verification: "bash scripts/setup-permissions.sh --check で権限状態が表示される"
      - criterion: "権限が不足している場合に警告メッセージを表示する"
        verification: "権限未設定状態でスクリプトを実行し警告を確認"
    technical_notes: |
      ## 必要な権限
      1. **画面収録 (Screen Recording)**
         - screencapture コマンドに必要
         - 設定画面: System Preferences > Privacy & Security > Screen Recording
         - 確認方法: CGPreflightScreenCaptureAccess() または実際にキャプチャを試行

      2. **アクセシビリティ (Accessibility)**
         - System Events 経由のウィンドウ情報取得に必要
         - 設定画面: System Preferences > Privacy & Security > Accessibility
         - 確認方法: AXIsProcessTrusted() を呼び出す

      ## 実装方針
      ```bash
      #!/bin/bash
      # scripts/setup-permissions.sh

      # 設定画面を開く
      open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
      open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

      # 権限チェック (--check オプション)
      # Python スクリプトを呼び出して権限状態を確認
      ```

      ## Python 権限チェックモジュール
      新規ファイル: src/auto_daily/permissions.py
      ```python
      import subprocess
      from ApplicationServices import AXIsProcessTrusted
      import Quartz

      def check_screen_recording_permission() -> bool:
          # CGPreflightScreenCaptureAccess() を使用
          pass

      def check_accessibility_permission() -> bool:
          return AXIsProcessTrusted()

      def request_permissions() -> None:
          # 設定画面を開く
          pass
      ```

      ## 既存スクリプトとの連携
      scripts/start.sh から権限チェックを呼び出し、不足時に setup-permissions.sh の実行を促す
    story_points: 3
    dependencies:
      - PBI-009
    status: done

  - id: PBI-021
    story:
      role: "開発者"
      capability: "LLM クライアントを抽象化して複数のバックエンド（Ollama、LM Studio）を統一的に扱える"
      benefit: "新しい LLM バックエンドを追加する際のコード変更を最小限に抑えられる"
    acceptance_criteria:
      - criterion: "LLM クライアントの Protocol/ABC が定義されている"
        verification: "pytest tests/test_llm_client.py::test_llm_protocol -v"
      - criterion: "既存の OllamaClient がプロトコルを実装している"
        verification: "pytest tests/test_llm_client.py::test_ollama_implements_protocol -v"
      - criterion: "AI_BACKEND 環境変数でバックエンドを切り替えられる"
        verification: "pytest tests/test_config.py::test_ai_backend_from_env -v"
      - criterion: "get_llm_client() ファクトリ関数が環境変数に応じたクライアントを返す"
        verification: "pytest tests/test_llm_client.py::test_get_llm_client_factory -v"
    technical_notes: |
      ## リファクタリング内容
      現在の ollama.py は Ollama API に直接依存している。
      複数バックエンドに対応するため抽象化レイヤーを導入する。

      ## 新規ファイル構成
      ```
      src/auto_daily/
        llm/
          __init__.py       # get_llm_client() ファクトリ
          protocol.py       # LLMClient Protocol 定義
          ollama.py         # OllamaClient 実装
          lm_studio.py      # (PBI-022で追加)
      ```

      ## Protocol 定義
      ```python
      # llm/protocol.py
      from typing import Protocol

      class LLMClient(Protocol):
          async def generate(self, prompt: str) -> str:
              """テキストを生成する"""
              ...

          async def generate_with_image(self, prompt: str, image_path: str) -> str:
              """画像付きでテキストを生成する（Vision モデル用）"""
              ...
      ```

      ## 環境変数
      - AI_BACKEND: "ollama" (default) | "lm_studio"
      - AI_MODEL: 使用するモデル名（バックエンド共通）

      ## 後方互換性
      - 既存の OllamaClient は llm/ollama.py に移動
      - ollama.py の他の関数（generate_daily_report_prompt, save_daily_report）は維持
    story_points: 5
    dependencies:
      - PBI-004
    status: done

  - id: PBI-025
    story:
      role: "Mac ユーザー"
      capability: "ログファイルを1時間単位で分割して保存できる"
      benefit: "ログファイルが肥大化せず、時間帯ごとのアクティビティを管理しやすくなる"
    acceptance_criteria:
      - criterion: "日付ディレクトリ logs/YYYY-MM-DD/ が自動作成される"
        verification: "pytest tests/test_logger.py::test_date_directory_creation -v"
      - criterion: "ログファイル名が activity_HH.jsonl 形式で生成される"
        verification: "pytest tests/test_logger.py::test_hourly_log_filename -v"
      - criterion: "時間が変わると新しいログファイルに書き込まれる"
        verification: "pytest tests/test_logger.py::test_hourly_rotation -v"
      - criterion: "既存の日単位ログとの後方互換性がある（移行期間中）"
        verification: "pytest tests/test_logger.py::test_legacy_daily_log_compat -v"
    technical_notes: |
      ## 変更内容
      ログファイルの粒度を1日から1時間に変更し、日付ごとのディレクトリに整理する。

      ## ディレクトリ構造
      ```
      ~/.auto-daily/
        └── logs/
            ├── 2025-12-25/           # 日付ディレクトリ
            │   ├── activity_09.jsonl  # 09:00-10:00 のログ
            │   ├── activity_10.jsonl  # 10:00-11:00 のログ
            │   └── ...
            └── 2025-12-26/
                └── ...
      ```

      ## 修正箇所
      logger.py を修正:
      - get_log_dir_for_date(date) -> Path: 日付ディレクトリを返す
      - get_log_filename(dt) -> str: activity_HH.jsonl 形式
      - append_log(): 日付ディレクトリを自動作成

      ## 実装方針
      ```python
      def get_log_dir_for_date(log_base: Path, dt: datetime | None = None) -> Path:
          if dt is None:
              dt = datetime.now()
          date_dir = log_base / dt.strftime('%Y-%m-%d')
          date_dir.mkdir(parents=True, exist_ok=True)
          return date_dir

      def get_log_filename(dt: datetime | None = None) -> str:
          if dt is None:
              dt = datetime.now()
          return f"activity_{dt.strftime('%H')}.jsonl"
      ```

      ## ヘルパー関数
      - get_log_files_for_date(date) -> list[Path]: 指定日のログファイル一覧
      - get_log_file_for_hour(date, hour) -> Path: 指定時間のログファイル
    story_points: 3
    dependencies:
      - PBI-003
    status: done

  - id: PBI-028
    story:
      role: "Mac ユーザー"
      capability: "OpenAI API を使って日報を生成できる"
      benefit: "クラウドベースの高性能 LLM で高品質な日報を生成できる"
    acceptance_criteria:
      - criterion: "OpenAIClient が LLMClient プロトコルを実装している"
        verification: "pytest tests/test_llm_client.py::test_openai_implements_protocol -v"
      - criterion: "AI_BACKEND=openai で OpenAI API を使用できる"
        verification: "pytest tests/test_llm_client.py::test_openai_backend -v"
      - criterion: "OPENAI_API_KEY 環境変数で API キーを設定できる"
        verification: "pytest tests/test_config.py::test_openai_api_key_from_env -v"
      - criterion: "OPENAI_MODEL 環境変数でモデル（gpt-4o, gpt-4o-mini 等）を指定できる"
        verification: "pytest tests/test_config.py::test_openai_model_from_env -v"
    technical_notes: |
      ## OpenAI API
      公式の openai Python SDK を使用する。
      - パッケージ: openai (pyproject.toml の dependencies に追加)
      - エンドポイント: https://api.openai.com/v1/chat/completions

      ## 実装
      ```python
      # llm/openai_client.py
      from openai import AsyncOpenAI

      class OpenAIClient:
          def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
              self.client = AsyncOpenAI(api_key=api_key)
              self.model = model

          async def generate(self, prompt: str, model: str | None = None) -> str:
              response = await self.client.chat.completions.create(
                  model=model or self.model,
                  messages=[{"role": "user", "content": prompt}],
              )
              return response.choices[0].message.content
      ```

      ## 環境変数
      - OPENAI_API_KEY: OpenAI API キー（必須）
      - OPENAI_MODEL: 使用するモデル（デフォルト: "gpt-4o-mini"）
      - OPENAI_BASE_URL: カスタムエンドポイント（オプション、Azure OpenAI 等）

      ## コスト意識
      - デフォルトは gpt-4o-mini（低コスト）
      - 高品質が必要な場合は gpt-4o を指定
    story_points: 3
    dependencies:
      - PBI-021
    status: done

  - id: PBI-030
    story:
      role: "Mac ユーザー"
      capability: "日報の保存先ディレクトリを環境変数やプロジェクト設定で変更できる"
      benefit: "日報をプロジェクトごとに管理したり、任意の場所に保存できる"
    acceptance_criteria:
      - criterion: "AUTO_DAILY_REPORTS_DIR 環境変数で日報の保存先を指定できる"
        verification: "pytest tests/test_config.py::test_reports_dir_from_env -v"
      - criterion: "環境変数が未設定の場合はデフォルトディレクトリ (~/.auto-daily/reports/) を使用する"
        verification: "pytest tests/test_config.py::test_reports_dir_default -v"
      - criterion: "指定されたディレクトリが存在しない場合は自動作成する"
        verification: "pytest tests/test_config.py::test_reports_dir_auto_create -v"
      - criterion: "プロジェクトルートに reports/ ディレクトリがある場合はそちらを優先する"
        verification: "pytest tests/test_config.py::test_reports_dir_from_project_root -v"
    technical_notes: |
      ## 変更内容
      PBI-006（ログ出力先設定）と同様のパターンで、日報の保存先をカスタマイズ可能にする。

      ## 優先順位
      1. プロジェクトルートの `reports/` ディレクトリ（存在する場合）
      2. `AUTO_DAILY_REPORTS_DIR` 環境変数
      3. デフォルト: `~/.auto-daily/reports/`

      ## 修正箇所
      config.py の get_reports_dir() を修正:
      ```python
      def get_reports_dir() -> Path:
          # 1. プロジェクトルートの reports/ をチェック
          project_reports = Path.cwd() / "reports"
          if project_reports.exists() and project_reports.is_dir():
              return project_reports

          # 2. 環境変数をチェック
          env_value = os.environ.get("AUTO_DAILY_REPORTS_DIR")
          if env_value:
              reports_dir = Path(env_value)
              reports_dir.mkdir(parents=True, exist_ok=True)
              return reports_dir

          # 3. デフォルト
          reports_dir = DEFAULT_REPORTS_DIR
          reports_dir.mkdir(parents=True, exist_ok=True)
          return reports_dir
      ```

      ## ユースケース
      - プロジェクトごとに日報を管理: リポジトリ内の `reports/` に保存
      - 共有フォルダに保存: Dropbox や Google Drive のパスを指定
      - 複数プロジェクトで共通: ~/.auto-daily/reports/ を使用

      ## .env ファイル例
      ```
      AUTO_DAILY_REPORTS_DIR=/Users/username/Documents/DailyReports
      ```
    story_points: 2
    dependencies:
      - PBI-006
    status: done

  - id: PBI-031
    story:
      role: "Mac ユーザー"
      capability: "Google カレンダーの iCal URL を設定して、指定日の予定を取得できる"
      benefit: "カレンダーの予定を日報生成に活用できる"
    acceptance_criteria:
      - criterion: "calendar_config.yaml から iCal URL を読み込める"
        verification: "pytest tests/test_calendar.py::test_load_calendar_config -v"
      - criterion: "iCal URL から指定日のイベント一覧を取得できる"
        verification: "pytest tests/test_calendar.py::test_fetch_events_from_ical -v"
      - criterion: "複数カレンダーのイベントをマージできる"
        verification: "pytest tests/test_calendar.py::test_merge_multiple_calendars -v"
      - criterion: "カレンダー設定がない場合は空のリストを返す"
        verification: "pytest tests/test_calendar.py::test_no_calendar_config -v"
    technical_notes: |
      ## 新規依存関係
      - icalendar: iCal 形式のパース（pyproject.toml に追加）

      ## 設定ファイル
      パス: プロジェクトルート または ~/.auto-daily/calendar_config.yaml
      ```yaml
      calendars:
        - name: "仕事"
          ical_url: "https://calendar.google.com/calendar/ical/xxx/private-xxx/basic.ics"
        - name: "個人"
          ical_url: "https://calendar.google.com/calendar/ical/yyy/private-yyy/basic.ics"
      ```

      ## 新規ファイル
      src/auto_daily/calendar.py:
      ```python
      from dataclasses import dataclass
      from datetime import date, datetime
      from pathlib import Path
      import httpx
      from icalendar import Calendar
      import yaml

      @dataclass
      class CalendarEvent:
          summary: str
          start: datetime
          end: datetime
          calendar_name: str

      def load_calendar_config() -> list[dict]:
          """カレンダー設定を読み込む"""
          # プロジェクトルート優先、なければホームディレクトリ
          ...

      async def fetch_events(ical_url: str, target_date: date) -> list[CalendarEvent]:
          """iCal URL から指定日のイベントを取得"""
          ...

      async def get_all_events(target_date: date) -> list[CalendarEvent]:
          """全カレンダーからイベントを取得してマージ"""
          ...
      ```
    story_points: 5
    dependencies:
      - PBI-004
    status: done

  - id: PBI-033
    story:
      role: "Mac ユーザー"
      capability: "アプリケーション起動時に macOS の必要な権限（画面収録・アクセシビリティ）が確認され、不足時に警告が表示される"
      benefit: "権限不足による動作不良を事前に検知し、スムーズにセットアップできる"
    acceptance_criteria:
      - criterion: "アプリ起動時に画面収録とアクセシビリティ権限を自動チェックする"
        verification: "pytest tests/test_permissions.py::test_check_all_permissions -v"
      - criterion: "権限が不足している場合、警告メッセージを表示して setup-permissions.sh の実行を促す"
        verification: "pytest tests/test_main.py::test_permission_warning_on_start -v"
      - criterion: "権限が揃っている場合はそのまま監視を開始する"
        verification: "pytest tests/test_main.py::test_start_with_permissions -v"
    technical_notes: |
      ## 統合箇所
      __init__.py の main() 関数で --start 時に permissions.py を呼び出す

      ## 実装内容
      - check_all_permissions() を __init__.py にインポート
      - main() の --start 処理で権限チェックを追加
      - 権限不足時: 警告メッセージ + setup-permissions.sh の案内 + exit(1)
      - 権限正常時: 従来通り監視を開始
    story_points: 2
    dependencies:
      - PBI-020
    sprint: 24
    status: done

  - id: PBI-016
    story:
      role: "Mac ユーザー"
      capability: "Ollama がインストールされていなくてもアプリケーションを起動できる"
      benefit: "まずログ収集だけを試したい場合や、Ollama を後から導入したい場合でも使い始められる"
    acceptance_criteria:
      - criterion: "Ollama 未接続でもアプリケーションが起動しウィンドウ監視が動作する"
        verification: "pytest tests/test_main.py::test_start_without_ollama -v"
      - criterion: "アプリケーション起動時に Ollama 未接続の場合は警告メッセージを表示する"
        verification: "pytest tests/test_main.py::test_start_warns_without_ollama -v"
      - criterion: "report コマンド実行時に Ollama 未接続の場合はエラーで終了する"
        verification: "pytest tests/test_main.py::test_report_fails_without_ollama -v"
      - criterion: "OLLAMA_BASE_URL で指定した接続先に接続できない場合もエラーで終了する"
        verification: "pytest tests/test_main.py::test_report_fails_with_invalid_ollama_url -v"
    technical_notes: |
      ## 実装方針
      - ollama.py に check_ollama_connection() -> bool 関数を追加
        - OLLAMA_BASE_URL への接続を試行し、成功可否を返す
      - __init__.py の start_command() を修正
        - 起動時に check_ollama_connection() を呼び出し
        - 接続不可の場合は警告（Warning）を表示して続行
      - __init__.py の report_command() を修正
        - 実行時に check_ollama_connection() を呼び出し
        - 接続不可の場合はエラーメッセージを表示して終了（sys.exit(1)）

      ## エラーメッセージ例
      - 警告: "Warning: Ollama is not available at {url}. Report generation will not work."
      - エラー: "Error: Cannot connect to Ollama at {url}. Please ensure Ollama is running."

      ## 挙動の変更
      - 現在: Ollama 未起動 → アプリ起動失敗
      - 変更後: Ollama 未起動 → 警告表示してアプリ起動成功、report コマンドのみエラー
    story_points: 3
    dependencies:
      - PBI-005
      - PBI-015
    sprint: 26
    status: done

  - id: PBI-022
    story:
      role: "Mac ユーザー"
      capability: "LM Studio を使って日報を生成できる"
      benefit: "Ollama 以外の選択肢があり、好みのツールで日報生成ができる"
    acceptance_criteria:
      - criterion: "LMStudioClient が LLMClient プロトコルを実装している"
        verification: "pytest tests/test_llm_client.py::test_lm_studio_implements_protocol -v"
      - criterion: "AI_BACKEND=lm_studio で LM Studio を使用できる"
        verification: "pytest tests/test_llm_client.py::test_lm_studio_backend -v"
      - criterion: "LM_STUDIO_BASE_URL 環境変数で接続先を設定できる"
        verification: "pytest tests/test_config.py::test_lm_studio_base_url_from_env -v"
    technical_notes: |
      ## 実装方針
      OpenAI SDK を使用し、base_url をオーバーライドして LM Studio に接続する。
      LM Studio は API キーが不要なので、api_key="not-needed" とする。
    story_points: 3
    dependencies:
      - PBI-021
    sprint: 27
    status: done
```
