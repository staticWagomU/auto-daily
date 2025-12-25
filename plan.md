# AI-Agentic Scrum Dashboard

## Rules

### General Principles

1. **Single Source of Truth**: This dashboard is the only place for Scrum artifacts. All agents read from and write to this file.
2. **Git as History**: Do not add timestamps. Git tracks when changes were made.
3. **Order is Priority**: Items higher in lists have higher priority. No separate priority field needed.

### Product Backlog Management

1. **User Story Format**: Every PBI must have a `story` block with `role`, `capability`, and `benefit`.
2. **Ordering**: Product Owner reorders by moving items up/down in the YAML array.
3. **Refinement**: Change status from `draft` -> `refining` -> `ready` as stories mature.

### Definition of Ready (AI-Agentic)

**Ready = AI can complete it without asking humans.**

| Status | Meaning |
|--------|---------|
| `draft` | Initial idea. Needs elaboration. |
| `refining` | Being refined. AI may be able to make it `ready`. |
| `ready` | All information available. AI can execute autonomously. |

**Refinement process**:
1. AI attempts to refine `draft`/`refining` items autonomously (explore codebase, propose acceptance criteria, identify dependencies)
2. If AI can fill in all gaps -> change status to `ready`
3. If story is too big or unclear -> try to split it
4. If unsplittable item still needs human help -> keep as `refining` and document the question

**Prioritization**: Prefer `ready` items. Work on refinement when no `ready` items exist or while waiting for human input.

### Sprint Structure (AI-Agentic)

**1 Sprint = 1 PBI**

Unlike human Scrum where Sprints are time-boxed to amortize event overhead, AI agents have no such constraint. Scrum events are instant for AI, so we maximize iterations by:

- Each Sprint delivers exactly one PBI
- Sprint Planning = select top `ready` item from backlog
- Sprint Review/Retro = run after every PBI completion
- No fixed duration - Sprint ends when PBI is done

**Benefits**: Faster feedback, simpler planning, cleaner increments, easier rollback.

### Sprint Execution (TDD Workflow)

1. **One PBI per Sprint**: Select the top `ready` item. That's the Sprint Backlog.
2. **TDD Subtask Breakdown**: Break the PBI into subtasks. Each subtask produces commits through Red-Green-Refactor:
   - `test`: What behavior to verify (becomes the Red phase test)
   - `implementation`: What to build to make the test pass (Green phase)
   - `type`: `behavioral` (new functionality) or `structural` (refactoring only)
   - `status`: Current TDD phase (`pending` | `red` | `green` | `refactoring` | `completed`)
   - `commits`: Array tracking each commit made for this subtask
3. **TDD Cycle Per Subtask (Commit-Based)**:
   - **Red**: Write a failing test, commit it (`phase: red`), status becomes `red`
   - **Green**: Implement minimum code to pass, commit it (`phase: green`), status becomes `green`
   - **Refactor**: Make structural improvements, commit each one separately (`phase: refactor`), status becomes `refactoring`
   - **Complete**: All refactoring done, status becomes `completed`
4. **Multiple Refactor Commits**: Following Tidy First, make small, frequent structural changes. Each refactor commit should be a single logical improvement (rename, extract method, etc.).
5. **Commit Discipline**: Each commit represents one TDD phase step. Never mix behavioral and structural changes in the same commit.
6. **Full Event Cycle**: After PBI completion, run Review -> Retro -> next Planning.

### Impediment Handling

1. **Log Immediately**: When blocked, add to `impediments.active` right away.
2. **Escalation Path**: Developer -> Scrum Master -> Human.
3. **Resolution**: Move resolved impediments to `impediments.resolved`.

### Definition of Done

1. **All Criteria Must Pass**: Every required DoD criterion must be verified.
2. **Executable Verification**: Run the verification commands, don't just check boxes.
3. **No Partial Done**: An item is either fully Done or still in_progress.

### Status Transitions

```
PBI Status (in Product Backlog):
  draft -> refining -> ready

Sprint Status (1 PBI per Sprint):
  in_progress -> done
       |
    blocked

Subtask Status (TDD Cycle with Commits):
  pending ─┬─> red ─────> green ─┬─> refactoring ─┬─> completed
           │   (commit)  (commit) │    (commit)    │
           │                      │       ↓        │
           │                      │   (more refactor commits)
           │                      │       ↓        │
           │                      └───────┴────────┘
           │
           └─> (skip to completed if no test needed, e.g., pure structural)

Each status transition produces a commit:
  pending -> red:        commit(test: ...)
  red -> green:          commit(feat: ... or fix: ...)
  green -> refactoring:  commit(refactor: ...)
  refactoring -> refactoring: commit(refactor: ...) [multiple allowed]
  refactoring -> completed:   (no commit, just status update)
  green -> completed:    (no commit, skip refactor if not needed)

Sprint Cycle:
  Planning -> Execution -> Review -> Retro -> (next Planning)
```

### Agent Responsibilities

| Agent | Reads | Writes |
|-------|-------|--------|
| Product Owner | Full dashboard | Product Backlog, Product Goal, Sprint acceptance |
| Scrum Master | Full dashboard | Sprint config, Impediments, Retrospective, Metrics |
| Developer | Sprint Backlog, DoD | Subtask status, Progress, Notes, Impediments |
| Event Agents | Relevant sections | Event-specific outputs |

---

## Quick Status

```yaml
sprint:
  number: 20
  pbi: PBI-021
  status: done
  subtasks_completed: 4
  subtasks_total: 4
  impediments: 0
```

---

## 1. Product Backlog

### Product Goal

```yaml
product_goal:
  statement: "ウィンドウ切り替え時に作業コンテキストを自動キャプチャし、Ollama を活用して日報を自動生成することで、ユーザーの日報作成の手間を削減する"
  success_metrics:
    - metric: "アプリケーションの安定稼働"
      target: "24時間連続稼働でクラッシュなし"
    - metric: "OCR 精度"
      target: "日本語テキストの認識率 90% 以上"
    - metric: "日報生成成功率"
      target: "Ollama 呼び出しの成功率 95% 以上"
  owner: "@scrum-team-product-owner"
```

### Backlog Items

```yaml
product_backlog:
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
    status: draft

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
      ## LM Studio API
      LM Studio は OpenAI 互換 API を提供する。
      - デフォルト URL: http://localhost:1234
      - エンドポイント: /v1/chat/completions

      ## 実装
      ```python
      # llm/lm_studio.py
      class LMStudioClient:
          def __init__(self, base_url: str = "http://localhost:1234"):
              self.base_url = base_url

          async def generate(self, prompt: str) -> str:
              # OpenAI 互換 API を使用
              async with httpx.AsyncClient() as client:
                  response = await client.post(
                      f"{self.base_url}/v1/chat/completions",
                      json={
                          "messages": [{"role": "user", "content": prompt}],
                          "temperature": 0.7,
                      },
                  )
                  return response.json()["choices"][0]["message"]["content"]
      ```

      ## 環境変数
      - LM_STUDIO_BASE_URL: "http://localhost:1234" (default)
    story_points: 3
    dependencies:
      - PBI-021
    status: draft

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
    status: ready

  - id: PBI-029
    story:
      role: "Mac ユーザー"
      capability: "OpenAI Vision API（GPT-4o）を使って OCR を実行できる"
      benefit: "高精度なクラウドベースの画像認識で文脈を理解した OCR ができる"
    acceptance_criteria:
      - criterion: "OpenAIVisionOCR が OCRBackend プロトコルを実装している"
        verification: "pytest tests/test_ocr.py::test_openai_vision_implements_protocol -v"
      - criterion: "OCR_BACKEND=openai で OpenAI Vision を使用できる"
        verification: "pytest tests/test_ocr.py::test_openai_vision_backend -v"
      - criterion: "画像を Base64 エンコードして GPT-4o に送信できる"
        verification: "pytest tests/test_ocr.py::test_openai_vision_image_encoding -v"
      - criterion: "OCR_MODEL 環境変数で Vision モデルを指定できる"
        verification: "pytest tests/test_config.py::test_ocr_model_openai_from_env -v"
    technical_notes: |
      ## OpenAI Vision API
      GPT-4o / GPT-4o-mini の Vision 機能を使用して画像からテキストを抽出する。

      ## 実装
      ```python
      # ocr/openai_vision.py
      import base64
      from openai import AsyncOpenAI

      class OpenAIVisionOCR:
          def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
              self.client = AsyncOpenAI(api_key=api_key)
              self.model = model

          async def perform_ocr(self, image_path: str) -> str:
              with open(image_path, "rb") as f:
                  image_data = base64.b64encode(f.read()).decode("utf-8")

              response = await self.client.chat.completions.create(
                  model=self.model,
                  messages=[{
                      "role": "user",
                      "content": [
                          {"type": "text", "text": "この画像に含まれるすべてのテキストを抽出してください。"},
                          {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                      ]
                  }],
              )
              return response.choices[0].message.content
      ```

      ## 環境変数
      - OPENAI_API_KEY: API キー（PBI-028 と共有）
      - OCR_MODEL: Vision モデル（デフォルト: "gpt-4o-mini"）
      - OCR_BACKEND: "openai" で有効化

      ## Apple Vision との比較
      | 項目 | Apple Vision | OpenAI Vision |
      |------|--------------|---------------|
      | 速度 | 高速（ローカル） | 中速（API）|
      | コスト | 無料 | 従量課金 |
      | 精度 | 高（日本語◎） | 非常に高 |
      | 文脈理解 | なし | あり |

      ## 注意点
      - API 呼び出しごとにコストが発生
      - 大量の画像処理には不向き（Apple Vision を推奨）
      - 日本語テキストの抽出精度は非常に高い
    story_points: 5
    dependencies:
      - PBI-023
      - PBI-028
    status: draft

  - id: PBI-023
    story:
      role: "開発者"
      capability: "OCR バックエンドを抽象化して複数の方式（Apple Vision、AI Vision）を統一的に扱える"
      benefit: "新しい OCR 方式を追加する際のコード変更を最小限に抑えられる"
    acceptance_criteria:
      - criterion: "OCR バックエンドの Protocol/ABC が定義されている"
        verification: "pytest tests/test_ocr.py::test_ocr_protocol -v"
      - criterion: "既存の Vision Framework OCR がプロトコルを実装している"
        verification: "pytest tests/test_ocr.py::test_apple_vision_implements_protocol -v"
      - criterion: "OCR_BACKEND 環境変数でバックエンドを切り替えられる"
        verification: "pytest tests/test_config.py::test_ocr_backend_from_env -v"
      - criterion: "get_ocr_backend() ファクトリ関数が環境変数に応じたバックエンドを返す"
        verification: "pytest tests/test_ocr.py::test_get_ocr_backend_factory -v"
    technical_notes: |
      ## リファクタリング内容
      現在の ocr.py は Apple Vision Framework に直接依存している。
      AI Vision モデル対応のため抽象化レイヤーを導入する。

      ## 新規ファイル構成
      ```
      src/auto_daily/
        ocr/
          __init__.py       # get_ocr_backend() ファクトリ
          protocol.py       # OCRBackend Protocol 定義
          apple_vision.py   # Apple Vision Framework 実装
          ai_vision.py      # (PBI-024で追加)
      ```

      ## Protocol 定義
      ```python
      # ocr/protocol.py
      from typing import Protocol

      class OCRBackend(Protocol):
          def perform_ocr(self, image_path: str) -> str:
              """画像からテキストを抽出する"""
              ...
      ```

      ## 環境変数
      - OCR_BACKEND: "apple" (default) | "ai_vision"

      ## 後方互換性
      - 既存の perform_ocr() 関数は維持（内部でファクトリを使用）
    story_points: 3
    dependencies:
      - PBI-002
    status: draft

  - id: PBI-024
    story:
      role: "Mac ユーザー"
      capability: "Ollama/LM Studio の Vision モデルを使って OCR を実行できる"
      benefit: "より高精度な文脈理解が可能な AI ベースの OCR を選択できる"
    acceptance_criteria:
      - criterion: "AIVisionOCR が OCRBackend プロトコルを実装している"
        verification: "pytest tests/test_ocr.py::test_ai_vision_implements_protocol -v"
      - criterion: "OCR_BACKEND=ai_vision で AI Vision を使用できる"
        verification: "pytest tests/test_ocr.py::test_ai_vision_backend -v"
      - criterion: "OCR_MODEL 環境変数で使用する Vision モデルを指定できる"
        verification: "pytest tests/test_config.py::test_ocr_model_from_env -v"
      - criterion: "画像を Base64 エンコードして Vision モデルに送信できる"
        verification: "pytest tests/test_ocr.py::test_ai_vision_image_encoding -v"
    technical_notes: |
      ## AI Vision OCR の仕組み
      Ollama/LM Studio の Vision 対応モデル（llava, llama3.2-vision 等）を使用して
      画像からテキストを抽出する。

      ## 実装
      ```python
      # ocr/ai_vision.py
      class AIVisionOCR:
          def __init__(self, llm_client: LLMClient):
              self.llm_client = llm_client

          def perform_ocr(self, image_path: str) -> str:
              prompt = "この画像に含まれるすべてのテキストを抽出してください。"
              return await self.llm_client.generate_with_image(prompt, image_path)
      ```

      ## Ollama Vision API
      ```json
      {
        "model": "llava",
        "prompt": "この画像のテキストを抽出してください",
        "images": ["<base64 encoded image>"]
      }
      ```

      ## 環境変数
      - OCR_MODEL: Vision モデル名（例: "llava", "llama3.2-vision"）
      - OCR_BACKEND と AI_BACKEND の組み合わせで動作

      ## 注意点
      - AI Vision OCR は LLM クライアントに依存するため、PBI-021 が前提
      - Apple Vision より遅いがコンテキスト理解力が高い
    story_points: 5
    dependencies:
      - PBI-021
      - PBI-023
    status: draft

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
    status: ready

  - id: PBI-026
    story:
      role: "Mac ユーザー"
      capability: "1時間ごとにログを要約して保存できる"
      benefit: "長時間の作業でもコンテキストが溢れず、効率的に日報を生成できる"
    acceptance_criteria:
      - criterion: "python -m auto_daily summarize で現在の時間のログを要約できる"
        verification: "pytest tests/test_main.py::test_summarize_command -v"
      - criterion: "日付ディレクトリ summaries/YYYY-MM-DD/ が自動作成される"
        verification: "pytest tests/test_summarize.py::test_summary_date_directory -v"
      - criterion: "要約が summaries/YYYY-MM-DD/summary_HH.md として保存される"
        verification: "pytest tests/test_summarize.py::test_summary_file_format -v"
      - criterion: "スケジューラーで1時間ごとに自動的に要約が生成される"
        verification: "pytest tests/test_scheduler.py::test_hourly_summary_scheduler -v"
      - criterion: "--hour オプションで特定の時間の要約を生成できる"
        verification: "pytest tests/test_main.py::test_summarize_with_hour_option -v"
    technical_notes: |
      ## 新規コマンド
      ```bash
      # 現在の時間のログを要約
      python -m auto_daily summarize

      # 特定の時間を指定
      python -m auto_daily summarize --date 2025-12-25 --hour 14
      ```

      ## ディレクトリ構造
      ```
      ~/.auto-daily/
        ├── logs/
        │   └── 2025-12-25/
        │       ├── activity_09.jsonl
        │       ├── activity_10.jsonl
        │       └── ...
        └── summaries/
            └── 2025-12-25/           # 日付ディレクトリ
                ├── summary_09.md      # 09:00-10:00 の要約
                ├── summary_10.md      # 10:00-11:00 の要約
                └── ...
      ```

      ## 要約用プロンプト
      ```
      以下の1時間分のアクティビティログを簡潔に要約してください。
      重要なタスク、作業内容、成果を箇条書きで記載してください。

      {activities}
      ```

      ## スケジューラー統合
      - PeriodicCapture と同様に SummaryScheduler を作成
      - 毎時0分（または設定可能な間隔）で前の時間のログを要約

      ## 新規ファイル
      - src/auto_daily/summarize.py: 要約生成ロジック
      - 要約用プロンプトテンプレート: summary_prompt.txt

      ## ヘルパー関数
      - get_summary_dir_for_date(date) -> Path: 要約の日付ディレクトリ
      - get_summary_filename(hour) -> str: summary_HH.md 形式
    story_points: 5
    dependencies:
      - PBI-025
      - PBI-004
    status: draft

  - id: PBI-027
    story:
      role: "Mac ユーザー"
      capability: "時間単位の要約を集約して日報を生成できる"
      benefit: "コンテキスト制限を回避しながら、1日全体を俯瞰した日報を作成できる"
    acceptance_criteria:
      - criterion: "report コマンドが要約ファイルから日報を生成する"
        verification: "pytest tests/test_main.py::test_report_from_summaries -v"
      - criterion: "要約がない時間帯はスキップされる"
        verification: "pytest tests/test_main.py::test_report_skips_missing_summaries -v"
      - criterion: "要約がまだ生成されていないログは直接読み込む（フォールバック）"
        verification: "pytest tests/test_main.py::test_report_fallback_to_logs -v"
      - criterion: "日報生成前に未要約のログを自動で要約するオプション (--auto-summarize)"
        verification: "pytest tests/test_main.py::test_report_auto_summarize -v"
    technical_notes: |
      ## ディレクトリ構造
      ```
      ~/.auto-daily/
        ├── logs/
        │   └── 2025-12-25/
        │       ├── activity_09.jsonl
        │       └── ...
        ├── summaries/
        │   └── 2025-12-25/
        │       ├── summary_09.md
        │       ├── summary_10.md
        │       └── ...
        └── reports/
            └── daily_report_2025-12-25.md  # 最終的な日報
      ```

      ## 処理フロー
      ```
      1. 指定日の要約ファイル一覧を取得
         summaries/2025-12-25/summary_*.md

      2. 各要約を読み込んで結合
         09:00-10:00: [要約1]
         10:00-11:00: [要約2]
         ...

      3. 結合した要約から日報を生成
         「以下の時間帯ごとの要約をもとに、1日の日報を作成してください」
      ```

      ## プロンプト構造
      ```
      以下は今日の作業の時間帯ごとの要約です。
      これらをもとに、1日の日報を作成してください。

      ## 09:00-10:00
      {summary_09}

      ## 10:00-11:00
      {summary_10}

      ...

      ## 日報フォーマット
      1. 今日の作業内容
      2. 進捗・成果
      3. 課題・問題点
      4. 明日の予定
      ```

      ## フォールバック動作
      要約がない時間帯のログがある場合：
      1. --auto-summarize: 自動で要約を生成してから日報作成
      2. --include-raw: ログを直接含める（コンテキスト注意）
      3. デフォルト: 警告を表示してスキップ

      ## コンテキスト削減効果
      - 従来: 1日分のログ（数百KB〜数MB）
      - 変更後: 時間単位の要約（各1-2KB × 8-10時間 = 10-20KB）
    story_points: 5
    dependencies:
      - PBI-026
    status: draft

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
    status: ready

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

      ## iCal URL の取得方法（ドキュメント用）
      1. Google カレンダーを開く
      2. 設定 → カレンダーを選択
      3. 「カレンダーの統合」セクション
      4. 「秘密のアドレス（iCal 形式）」をコピー
    story_points: 3
    dependencies: []
    status: ready

  - id: PBI-032
    story:
      role: "Mac ユーザー"
      capability: "日報生成時にカレンダー予定と作業ログを照合して、差分と補完情報を含めた日報を作成できる"
      benefit: "予定と実績の差分が明確になり、予定情報で作業内容を補完した精度の高い日報ができる"
    acceptance_criteria:
      - criterion: "予定と作業ログを時間軸で照合できる"
        verification: "pytest tests/test_calendar.py::test_match_events_with_logs -v"
      - criterion: "予定にあるが作業ログがない項目を「未着手」として検出できる"
        verification: "pytest tests/test_calendar.py::test_detect_unstarted_events -v"
      - criterion: "作業ログにあるが予定にない項目を「予定外作業」として検出できる"
        verification: "pytest tests/test_calendar.py::test_detect_unplanned_work -v"
      - criterion: "日報生成プロンプトにカレンダー情報と差分が含まれる"
        verification: "pytest tests/test_calendar.py::test_calendar_in_report_prompt -v"
      - criterion: "report コマンドに --with-calendar オプションがある"
        verification: "pytest tests/test_main.py::test_report_with_calendar_option -v"
    technical_notes: |
      ## 照合ロジック
      ```python
      @dataclass
      class MatchResult:
          matched: list[tuple[CalendarEvent, list[LogEntry]]]  # 予定と対応するログ
          unstarted: list[CalendarEvent]  # 予定あり、ログなし
          unplanned: list[LogEntry]  # ログあり、予定なし

      def match_events_with_logs(
          events: list[CalendarEvent],
          logs: list[LogEntry],
          tolerance_minutes: int = 30
      ) -> MatchResult:
          """予定とログを時間軸で照合"""
          # イベントの時間帯とログのタイムスタンプを比較
          # tolerance_minutes の余裕を持って照合
          ...
      ```

      ## 日報プロンプトへの統合
      ```
      ## 今日の予定
      - 09:00-10:00: チームミーティング
      - 14:00-15:00: コードレビュー
      - 16:00-17:00: 1on1

      ## アクティビティログ
      {activities}

      ## 予定と実績の照合
      ### 予定通り実施
      - 09:00-10:00: チームミーティング（ログあり）

      ### 未着手の予定
      - 16:00-17:00: 1on1（ログなし）

      ### 予定外の作業
      - 11:00-12:00: 緊急バグ対応

      ## 指示
      上記の情報をもとに日報を作成してください。
      予定と実績の差分についてもコメントしてください。
      ```

      ## コマンドオプション
      ```bash
      # カレンダー情報を含めて日報生成
      python -m auto_daily report --with-calendar

      # デフォルトでカレンダー統合を有効にする環境変数
      AUTO_DAILY_USE_CALENDAR=true
      ```

      ## 作業内容の補完
      - 予定の「summary」を使ってログの文脈を補完
      - 例: 「Zoom」アプリのログ → 予定「チームミーティング」と紐付け
      - 例: 「Slack」で #dev-team チャンネル → 予定「開発打ち合わせ」と紐付け
    story_points: 5
    dependencies:
      - PBI-031
      - PBI-004
    status: draft
```

### Definition of Ready

```yaml
definition_of_ready:
  criteria:
    - criterion: "AI can complete this story without human input"
      required: true
      note: "If human input needed, split or keep as refining"
    - criterion: "User story has role, capability, and benefit"
      required: true
    - criterion: "At least 3 acceptance criteria with verification commands"
      required: true
    - criterion: "Dependencies are resolved or not blocking"
      required: true
```

---

## 2. Current Sprint

```yaml
sprint_20:
  number: 20
  pbi_id: PBI-021
  story: "LLM クライアントを抽象化して複数のバックエンド（Ollama、LM Studio）を統一的に扱える"
  status: done

  sprint_goal:
    statement: "LLM クライアントの Protocol を定義し、既存の OllamaClient をリファクタリングすることで、将来の LM Studio 対応を可能にする"
    success_criteria:
      - "LLMClient Protocol が定義されている"
      - "既存の OllamaClient がプロトコルを実装している"
      - "AI_BACKEND 環境変数でバックエンドを切り替えられる"
      - "get_llm_client() ファクトリ関数が環境変数に応じたクライアントを返す"
    stakeholder_value: "新しい LLM バックエンドを追加する際のコード変更を最小限に抑えられる"

  subtasks:
    - id: ST-001
      test: "test_llm_protocol: LLMClient Protocol が generate() メソッドを定義している"
      implementation: |
        新規ファイル src/auto_daily/llm/__init__.py と protocol.py を作成:
        - typing.Protocol を使用して LLMClient を定義
        - generate(prompt: str, model: str) -> str メソッドを定義
      type: behavioral
      status: completed
      commits: []

    - id: ST-002
      test: "test_ollama_implements_protocol: OllamaClient が LLMClient プロトコルを実装している"
      implementation: |
        既存の OllamaClient を llm/ollama.py に移動:
        - async def generate(self, prompt: str, model: str) -> str を維持
        - Protocol の型チェックを通過することを確認
      type: behavioral
      status: completed
      commits: []

    - id: ST-003
      test: "test_ai_backend_from_env: AI_BACKEND 環境変数でバックエンドを設定できる"
      implementation: |
        config.py に get_ai_backend() を追加:
        - AI_BACKEND 環境変数を読み取る
        - デフォルト: "ollama"
      type: behavioral
      status: completed
      commits: []

    - id: ST-004
      test: "test_get_llm_client_factory: get_llm_client() が環境変数に応じたクライアントを返す"
      implementation: |
        llm/__init__.py に get_llm_client() を追加:
        - AI_BACKEND に応じて適切なクライアントをインスタンス化
        - "ollama" -> OllamaClient を返す
        - 未知のバックエンド -> ValueError
      type: behavioral
      status: completed
      commits: []

  notes: |
    ## 新規ファイル構成
    ```
    src/auto_daily/
      llm/
        __init__.py       # get_llm_client() ファクトリ
        protocol.py       # LLMClient Protocol 定義
        ollama.py         # OllamaClient 実装（移動）
    ```

    ## Protocol 定義
    ```python
    from typing import Protocol

    class LLMClient(Protocol):
        async def generate(self, prompt: str, model: str) -> str:
            """テキストを生成する"""
            ...
    ```

    ## 環境変数
    - AI_BACKEND: "ollama" (default) | "lm_studio" (PBI-022で追加)

    ## 後方互換性
    - 既存の ollama.py から OllamaClient を llm/ollama.py に移動
    - generate_daily_report_prompt, save_daily_report は ollama.py に維持
    - 既存のインポート (from auto_daily.ollama import OllamaClient) は維持
```

### Impediment Registry

```yaml
impediments:
  active: []

  resolved: []
```

---

## 3. Definition of Done

```yaml
definition_of_done:
  checks:
    - name: "Tests pass"
      run: "pytest tests/ -v --tb=short"
    - name: "Lint clean"
      run: "ruff check . && ruff format --check ."
    - name: "Types valid"
      run: "ty check src/"
```

---

## 4. Completed Sprints

```yaml
completed:
  - sprint: 1
    pbi_id: PBI-001
    story: "ウィンドウ切り替え時にアクティブウィンドウの名前を自動取得できる"
    subtasks_completed: 3
    commits:
      - accfa9e  # test: add failing test for get_active_window
      - 6eda581  # feat: implement get_active_window function
      - ce4ab41  # test: add failing test for window change detection
      - 2701c0c  # feat: implement WindowMonitor class
      - cdaeae6  # test: add failing test for background monitoring
      - 3441b04  # feat: implement background monitoring

  - sprint: 2
    pbi_id: PBI-002
    story: "ウィンドウ切り替え時に画面全体をキャプチャし、OCR でテキストを抽出できる"
    subtasks_completed: 3
    commits:
      - d2f5ea6  # test: add failing test for screen capture
      - eea2e47  # feat: implement capture_screen function
      - 2239d8d  # test: add failing test for Japanese OCR
      - f4b866d  # feat: implement perform_ocr using Vision Framework
      - c12c6fd  # test: add failing test for OCR validation
      - 73db59a  # feat: implement validate_ocr_result function

  - sprint: 3
    pbi_id: PBI-003
    story: "取得した情報を JSONL 形式でログ保存し、使用済みのキャプチャ画像を自動削除できる"
    subtasks_completed: 3
    commits:
      - beaad54  # test: add failing test for JSONL log append
      - 2e28cd2  # feat: implement append_log for JSONL logging
      - 205e639  # test: add test for daily log file rotation
      - 0fdb573  # test: add failing test for image cleanup
      - e4b30c3  # feat: implement cleanup_image function

  - sprint: 4
    pbi_id: PBI-004
    story: "数分間隔で Ollama を呼び出し、蓄積されたログから日報を自動生成できる"
    subtasks_completed: 3
    commits:
      - 2d9a421  # test: add failing test for Ollama API call
      - 0b4e3e3  # feat: implement OllamaClient.generate()
      - ad8b6f9  # test: add failing test for prompt generation
      - e835661  # feat: implement generate_daily_report_prompt
      - e46e839  # test: add failing test for daily report save
      - 031f845  # feat: implement save_daily_report

  - sprint: 5
    pbi_id: PBI-005
    story: "auto-daily コマンドでアプリケーションを起動し、ウィンドウ監視から日報生成までの一連の処理を実行できる"
    subtasks_completed: 3
    commits:
      - d4d28a3  # test: add failing test for module execution
      - a41c0be  # feat: implement module execution entrypoint
      - 1e85225  # test: add test for CLI entrypoint
      - f806654  # test: add failing test for monitoring startup
      - b83f676  # feat: implement --start flag for window monitoring

  - sprint: 6
    pbi_id: PBI-006
    story: "環境変数 AUTO_DAILY_LOG_DIR でログの出力先ディレクトリを設定できる"
    subtasks_completed: 3
    commits:
      - 8571baf  # test: add failing tests for config module (PBI-006)
      - b9e65ab  # feat: implement config module with log directory setting

  - sprint: 7
    pbi_id: PBI-007
    story: "Ollama に渡すプロンプトをテキストファイルで自由にカスタマイズできる"
    subtasks_completed: 3
    commits:
      - 602dc59  # test: add failing tests for prompt template feature (PBI-007)
      - 8522ce8  # feat: implement prompt template customization (PBI-007)

  - sprint: 8
    pbi_id: PBI-008
    story: "README.md を読んでアプリケーションの概要、インストール方法、使い方を理解できる"
    subtasks_completed: 3
    commits:
      - 5ca9d12  # docs: add comprehensive README with install and usage guide (PBI-008)

  - sprint: 9
    pbi_id: PBI-009
    story: "シェルスクリプトを実行するだけでアプリケーションを起動できる"
    subtasks_completed: 3
    commits:
      - db7e591  # feat: add start.sh script for easy application launch (PBI-009)

  - sprint: 10
    pbi_id: PBI-010
    story: "ウィンドウ切り替え時に自動的に画面キャプチャ、OCR、ログ保存が実行される"
    subtasks_completed: 4
    commits:
      - 4d4a1be  # test: add failing integration tests for window change processing (PBI-010)
      - 4cdf8bb  # feat: implement processor module for window change pipeline (PBI-010)
      - 58c0e64  # feat: integrate processor into main event loop (PBI-010)

  - sprint: 11
    pbi_id: PBI-011
    story: "ウィンドウ切り替えとは別に、30秒ごとに定期的に画面キャプチャとOCRが実行される"
    subtasks_completed: 3
    commits:
      - c13eda6  # test: add failing tests for periodic capture scheduler (PBI-011)
      - 77b3f3c  # feat: implement PeriodicCapture scheduler (PBI-011)
      - 0196a16  # feat: integrate periodic capture into main loop (PBI-011)

  - sprint: 12
    pbi_id: PBI-012
    story: "Slack ウィンドウ表示時にチャンネル名とワークスペース名を自動抽出できる"
    subtasks_completed: 3
    commits:
      - e78dc2d  # test: add failing tests for Slack parser (PBI-012)
      - 7e93ed7  # feat: implement Slack window title parser (PBI-012)

  - sprint: 13
    pbi_id: PBI-013
    story: "YAML設定でワークスペースごとのユーザー名を設定し、自分のメッセージを識別できる"
    subtasks_completed: 3
    commits:
      - 7de7f83  # test: add failing tests for Slack username config (PBI-013)
      - 81ae895  # feat: implement get_slack_username for YAML config (PBI-013)
      - 84b91b1  # test: add failing tests for conversation extraction (PBI-013)
      - de6da01  # feat: implement extract_conversations for OCR text (PBI-013)
      - f1a60d6  # test: add failing tests for my message filter (PBI-013)
      - 50e81e3  # feat: implement filter_my_messages function (PBI-013)

  - sprint: 14
    pbi_id: PBI-014
    story: "コマンドラインから日報生成を実行できる"
    subtasks_completed: 4
    commits:
      - 0209694  # test: add failing tests for report command (PBI-014)
      - 5d1eacd  # feat: implement report command for CLI (PBI-014)

  - sprint: 15
    pbi_id: PBI-015
    story: ".env ファイルで Ollama の接続先やモデル名などの設定を管理できる"
    subtasks_completed: 5
    commits:
      - 356797d  # feat: add .env file support for configuration management (PBI-015)

  - sprint: 16
    pbi_id: PBI-017
    story: "report コマンドで正しいログファイルを参照して日報を生成できる"
    subtasks_completed: 2
    commits:
      - db7a2e6  # fix: use correct log filename format in report command (PBI-017)

  - sprint: 17
    pbi_id: PBI-018
    story: "プロジェクトルートの prompt.txt からプロンプトテンプレートを読み込める"
    subtasks_completed: 2
    commits: []

  - sprint: 18
    pbi_id: PBI-019
    story: "プロジェクトルートの slack_config.yaml から Slack 設定を読み込める"
    subtasks_completed: 3
    commits:
      - e25bc39  # feat: load slack_config.yaml from project root instead of home (PBI-019)
      - 969585d  # docs: complete Sprint 18 - PBI-019 slack config project root support

  - sprint: 19
    pbi_id: PBI-020
    story: "スクリプトを実行して必要な macOS 権限（画面収録・アクセシビリティ）の設定画面を開ける"
    subtasks_completed: 6
    commits: []

  - sprint: 20
    pbi_id: PBI-021
    story: "LLM クライアントを抽象化して複数のバックエンド（Ollama、LM Studio）を統一的に扱える"
    subtasks_completed: 4
    commits: []
```

---

## 5. Retrospective Log

```yaml
retrospectives:
  - sprint: 1
    what_went_well:
      - "TDD サイクル（Red-Green）が順調に回った"
      - "AppleScript による macOS API 連携が問題なく動作した"
      - "3つのサブタスクすべてを完了できた"
    what_to_improve:
      - "Refactor フェーズをスキップしたが、コードは十分シンプルだった"
    action_items:
      - "次スプリントでは必要に応じて Refactor フェーズを活用する"

  - sprint: 2
    what_went_well:
      - "Vision Framework の OCR が日本語・英語を正常に認識できた"
      - "screencapture コマンドのラップが順調に動作した"
      - "PyObjC の型エラーを ty 設定で適切に除外できた"
    what_to_improve:
      - "ty の設定形式の調査に時間がかかった"
    action_items:
      - "新しいツールの設定は事前にドキュメントを確認する"

  - sprint: 3
    what_went_well:
      - "JSONL ログ保存が効率的に実装できた"
      - "日付ローテーションは既存実装でカバーされていた"
      - "画像クリーンアップ機能がシンプルに実装できた"
    what_to_improve:
      - "ST-002 のテストが既に Green の状態だった（実装先行）"
    action_items:
      - "複数のサブタスクで共通する機能は事前に整理する"

  - sprint: 4
    what_went_well:
      - "Ollama API クライアントを httpx で非同期実装できた"
      - "プロンプト生成が JSONL ログをうまく活用している"
      - "日報保存機能がシンプルかつ堅牢に実装できた"
    what_to_improve:
      - "特になし - TDD サイクルが順調に回った"
    action_items:
      - "PBI-004 完了により、コア機能がすべて揃った"

  - sprint: 5
    what_went_well:
      - "ST-001 の実装が ST-002 もカバーし、効率的だった"
      - "argparse で CLI が簡潔に実装できた"
      - "ルートの main.py を削除し、パッケージ構造がクリーンになった"
    what_to_improve:
      - "特になし - 3つのサブタスクがスムーズに完了"
    action_items:
      - "アプリケーションが python -m auto_daily --start で起動可能に"

  - sprint: 6
    what_went_well:
      - "3つのテストを1つの実装でカバーでき、効率的だった"
      - "config モジュールの責務が明確に分離されている"
      - "Path クラスの mkdir(parents=True, exist_ok=True) が便利"
    what_to_improve:
      - "特になし - シンプルな機能を TDD で実装完了"
    action_items:
      - "今後の設定項目も config モジュールに追加していく"

  - sprint: 7
    what_went_well:
      - "PBI-006 のパターンを踏襲し、効率的に実装できた"
      - "config モジュールへの機能追加がスムーズだった"
      - "テンプレートのプレースホルダー置換が Python の str.format() で簡潔に実装"
    what_to_improve:
      - "特になし - TDD サイクルがスムーズに回った"
    action_items:
      - "プロンプトテンプレート機能を README に記載する"

  - sprint: 8
    what_went_well:
      - "Sprint 7 のアクションアイテム（README にプロンプトテンプレート記載）を完遂"
      - "README.md に必要な情報（概要、インストール、使用方法、設定）を網羅的に記載"
      - "ドキュメンテーションタスクでもスプリント構造を維持できた"
    what_to_improve:
      - "特になし - シンプルなドキュメント作成タスクがスムーズに完了"
    action_items:
      - "PBI-009（起動スクリプト）を次スプリントで対応"

  - sprint: 9
    what_went_well:
      - "Sprint 8 のアクションアイテム（起動スクリプト）を完遂"
      - "Ollama 起動チェックで事前エラー検知を実装"
      - "色付き出力で UX を向上"
    what_to_improve:
      - "特になし - シンプルなスクリプト作成がスムーズに完了"
    action_items:
      - "Product Backlog の次の ready アイテムを確認し、必要に応じて新規 PBI を追加"

  - sprint: 10
    what_went_well:
      - "processor.py でパイプライン処理を単一責任で実装できた"
      - "TDD サイクル（Red-Green）が順調に回った"
      - "統合テストで各モジュールの連携を検証できた"
      - "アプリケーションが実際に動作するようになった"
    what_to_improve:
      - "特になし - 統合タスクがスムーズに完了"
    action_items:
      - "実際にアプリを起動して E2E テストを実施"
      - "Ollama 日報生成のスケジュール機能を検討"

  - sprint: 11
    what_went_well:
      - "PeriodicCapture クラスで定期実行を独立したコンポーネントとして実装"
      - "threading.Event().wait() で stop() の応答性を向上"
      - "ウィンドウ切り替えと定期実行が干渉せず共存"
      - "TDD サイクルが順調に回った"
    what_to_improve:
      - "特になし - シンプルな機能追加がスムーズに完了"
    action_items:
      - "定期キャプチャ間隔を環境変数でカスタマイズ可能にする"
      - "Ollama 日報生成の定期実行を検討"

  - sprint: 12
    what_went_well:
      - "TypedDict で型安全な Slack コンテキスト構造を実装"
      - "正規表現で複数のウィンドウタイトルフォーマットに対応"
      - "1つの実装で3つのサブタスクを効率的にカバー"
      - "TDD サイクルが順調に回った"
    what_to_improve:
      - "特になし - シンプルなパーサー実装がスムーズに完了"
    action_items:
      - "processor.py に Slack コンテキスト統合を検討"
      - "PBI-013 で Slack ユーザー名設定機能を追加"

  - sprint: 13
    what_went_well:
      - "Sprint 12 のアクションアイテム（Slack ユーザー名設定機能）を完遂"
      - "既存の config.py パターン（get_prompt_template）を踏襲し、効率的に実装"
      - "PyYAML による YAML 設定読み込みがシンプルに実装できた"
      - "Message TypedDict で型安全な会話構造を実装"
      - "TDD サイクル（Red-Green）が全サブタスクで順調に回った"
    what_to_improve:
      - "特になし - PBI-012 からの自然な拡張がスムーズに完了"
    action_items:
      - "processor.py に Slack 会話抽出とフィルタリングを統合"
      - "日報生成時に自分のメッセージを活用する機能を検討"

  - sprint: 14
    what_went_well:
      - "既存の OllamaClient, save_daily_report() を活用して効率的に実装"
      - "argparse のサブコマンド構造を導入して CLI を拡張"
      - "4つのサブタスクを1つの Red-Green サイクルでカバーできた"
      - "TDD サイクル（Red-Green）が順調に回った"
    what_to_improve:
      - "特になし - シンプルな CLI 拡張がスムーズに完了"
    action_items:
      - "日報生成時に Slack の自分のメッセージを含める機能を検討"
      - "日報の出力フォーマットをカスタマイズ可能にする"

  - sprint: 15
    what_went_well:
      - "python-dotenv で .env ファイル読み込みを実装"
      - "既存の config.py パターンを踏襲し、効率的に実装"
      - "5つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - シンプルな設定拡張がスムーズに完了"
    action_items:
      - ".env.example ファイルを追加してサンプル設定を提供"

  - sprint: 16
    what_went_well:
      - "バグの根本原因（ログファイル名形式の不一致）を正確に特定"
      - "get_log_filename() を再利用することでコードの一貫性を確保"
      - "既存テストも正しい形式に更新し、回帰を防止"
      - "TDD サイクル（Red-Green）がスムーズに回った"
    what_to_improve:
      - "PBI-014 のテスト作成時に logger.py のファイル名形式を考慮すべきだった"
    action_items:
      - "新規機能追加時は既存モジュールとの整合性をより意識する"

  - sprint: 17
    what_went_well:
      - "Path.cwd() でプロジェクトルートの prompt.txt を読み込む実装がシンプル"
      - "既存の test_prompt_template_from_file を削除し、新しいテストに置き換え"
      - "test_prompt_template_default も os.chdir() を使うように更新"
      - "TDD サイクル（Red-Green）がスムーズに回った"
    what_to_improve:
      - "特になし - シンプルな仕様変更がスムーズに完了"
    action_items:
      - "README.md を更新して prompt.txt の読み込み先を明記する"

  - sprint: 18
    what_went_well:
      - "PBI-018（prompt.txt）と同じパターンを踏襲し、効率的に実装"
      - "ホームディレクトリへのフォールバック機能を維持"
      - "既存テスト test_slack_username_config_file_not_found も更新して両方のパスをテスト"
      - "TDD サイクル（Red-Green）がスムーズに回った"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "slack_config.yaml.example はすでにリポジトリに存在することを確認"

  - sprint: 19
    what_went_well:
      - "ctypes を使って ApplicationServices の AXIsProcessTrusted にアクセスする方法を発見"
      - "pyobjc の制限（一部 API が直接インポートできない）に対応"
      - "6つのサブタスクをすべて完了し、権限チェック機能を実装"
      - "シェルスクリプトと Python モジュールの連携が適切に動作"
      - "TDD サイクル（Red-Green）がスムーズに回った"
    what_to_improve:
      - "pyobjc の API 可用性を事前に確認すべきだった（ApplicationServices は直接インポート不可）"
    action_items:
      - "macOS ネイティブ API 使用時は ctypes フォールバックを検討する"

  - sprint: 20
    what_went_well:
      - "typing.Protocol を使った抽象化で構造的サブタイピングを実現"
      - "既存の OllamaClient を llm/ パッケージに移動し、後方互換性を維持"
      - "get_llm_client() ファクトリパターンで柔軟なバックエンド切り替えを実装"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "テストのパッチ先（httpx.AsyncClient）が OllamaClient の移動により変更されたことへの対応"
    action_items:
      - "モジュール移動時はテストのモックパスも確認する"
      - "PBI-022（LM Studio 対応）は Protocol の上に実装可能"
```

---

## 6. Agents

```yaml
agents:
  product_owner: "@scrum-team-product-owner"
  scrum_master: "@scrum-team-scrum-master"
  developer: "@scrum-team-developer"

events:
  planning: "@scrum-event-sprint-planning"
  review: "@scrum-event-sprint-review"
  retrospective: "@scrum-event-sprint-retrospective"
  refinement: "@scrum-event-backlog-refinement"
```
