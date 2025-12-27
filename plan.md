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
  number: 45
  pbi: PBI-046b
  status: in_progress
  subtasks_completed: 0
  subtasks_total: 2
  impediments: 0
  note: "マイクアクセス権限と音声認識権限のチェック機能を追加"
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

> **Note**: 完了した PBI は [plan-archive.md](./plan-archive.md) に移動されています。

```yaml
product_backlog:
  # --- Active PBIs (draft/refining/ready) ---

  # === リファクタリング PBIs ===

  - id: PBI-045
    story:
      role: "開発者"
      capability: "pytest-xdist を使ってテストを並列実行できる"
      benefit: "テスト実行時間が短縮され、開発サイクルが高速化する"
    acceptance_criteria:
      - criterion: "pytest-xdist が dev 依存関係に追加されている"
        verification: "grep -n 'pytest-xdist' pyproject.toml"
      - criterion: "pytest -n auto でテストが並列実行できる"
        verification: "pytest tests/ -n auto --tb=short"
      - criterion: "全テストがパスする（並列実行時も）"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      pytest-xdist を導入してテストを並列実行する。
      現在 20 個のテストファイルがあり、並列化による速度向上が期待できる。

      ## 実装手順

      ### 1. 依存関係の追加
      - pyproject.toml の dev 依存に pytest-xdist を追加
      - uv sync で依存関係をインストール

      ### 2. 動作確認
      - pytest -n auto でテストを実行
      - 並列実行時に問題がないことを確認

      ### 注意事項
      - テスト間で共有状態がある場合は修正が必要
      - ファイル I/O を伴うテストでは一時ディレクトリの分離を確認
    story_points: 1
    dependencies: []
    status: done

  - id: PBI-039
    story:
      role: "開発者"
      capability: "deprecated な append_log() を削除し、エラー処理を統一できる"
      benefit: "コードベースがクリーンになり、保守性が向上する"
    acceptance_criteria:
      - criterion: "logger.py から append_log() が削除されている"
        verification: "! grep -n 'def append_log(' src/auto_daily/logger.py"
      - criterion: "capture.py のエラー出力が logging.debug() を使用している"
        verification: "grep -n 'logger.debug' src/auto_daily/capture.py"
      - criterion: "calendar.py が具体的な例外をキャッチしている"
        verification: "grep -n 'httpx.HTTPError' src/auto_daily/calendar.py"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -v --tb=short"
    technical_notes: |
      ## フェーズ1: デッドコード削除とエラー処理の統一

      ### /tidy:first（構造的改善）
      - capture.py に import logging を追加、logger インスタンス作成
      - processor.py から不要コメント削除 (# Step 1: 等)

      ### 修正実施（振る舞いの変更）
      - logger.py から append_log() (93-136行) を完全削除
      - tests/test_logger.py から append_log 関連テストを削除
      - capture.py: sys.stderr → logging.debug()
      - calendar.py: Exception → 具体的例外 (httpx.HTTPError, ValueError, KeyError)

      ### /tidy:after（片付け）
      - 未使用の import を削除（sys, warnings など）
    story_points: 2
    dependencies: []
    status: done

  - id: PBI-040
    story:
      role: "開発者"
      capability: "processor.py と scheduler.py の重複したキャプチャ処理を統合できる"
      benefit: "コードの重複が80%削減され、変更時の修正箇所が1箇所になる"
    acceptance_criteria:
      - criterion: "capture_pipeline.py が存在し、共通パイプライン関数を提供している"
        verification: "test -f src/auto_daily/capture_pipeline.py"
      - criterion: "processor.py が capture_pipeline を使用している"
        verification: "grep -n 'from auto_daily.capture_pipeline' src/auto_daily/processor.py"
      - criterion: "scheduler.py が capture_pipeline を使用している"
        verification: "grep -n 'from auto_daily.capture_pipeline' src/auto_daily/scheduler.py"
      - criterion: "scheduler.py の threading.Event() がインスタンス変数化されている"
        verification: "grep -n '_stop_event' src/auto_daily/scheduler.py"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -v --tb=short"
    technical_notes: |
      ## フェーズ2: キャプチャパイプラインの統合

      ### /tidy:first（構造的改善）
      - capture_pipeline.py を新規作成（共通パイプライン関数を抽出）
      - scheduler.py の threading.Event() をインスタンス変数化

      ### 修正実施（振る舞いの変更）
      - processor.py を capture_pipeline を使用するよう変更
      - scheduler.py を capture_pipeline を使用するよう変更
      - tests/test_capture_pipeline.py を新規作成

      ### /tidy:after（片付け）
      - processor.py / scheduler.py から重複コードを削除
      - 未使用の import を削除

      ### capture_pipeline.py の設計
      ```python
      @dataclass
      class CaptureContext:
          window_info: dict[str, str]
          log_dir: Path
          extract_slack_context: bool = False

      def execute_capture_pipeline(context: CaptureContext) -> bool:
          """キャプチャ→OCR→ログの共通パイプライン"""
          ...
      ```
    story_points: 3
    dependencies:
      - PBI-039
    status: done

  - id: PBI-041
    story:
      role: "開発者"
      capability: "ollama.py の2つのプロンプト生成関数で重複するログ処理を統合できる"
      benefit: "ログ読み込み処理の重複が解消され、保守性が向上する"
    acceptance_criteria:
      - criterion: "ollama.py に _load_log_entries() ヘルパー関数が存在する"
        verification: "grep -n 'def _load_log_entries' src/auto_daily/ollama.py"
      - criterion: "ollama.py に _format_activities() ヘルパー関数が存在する"
        verification: "grep -n 'def _format_activities' src/auto_daily/ollama.py"
      - criterion: "generate_daily_report_prompt() がヘルパー関数を使用している"
        verification: "grep -A5 'def generate_daily_report_prompt' src/auto_daily/ollama.py | grep '_load_log_entries'"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -v --tb=short"
    technical_notes: |
      ## フェーズ3: ollama.py のプロンプト生成重複解消

      ### /tidy:first（構造的改善）
      - _load_log_entries() ヘルパー関数を抽出
      - _format_activities() ヘルパー関数を抽出

      ### 修正実施（振る舞いの変更）
      - generate_daily_report_prompt() 簡略化
      - generate_daily_report_prompt_with_calendar() 簡略化

      ### /tidy:after（片付け）
      - 重複コードの削除確認
    story_points: 2
    dependencies:
      - PBI-039
    status: done

  - id: PBI-042
    story:
      role: "開発者"
      capability: "テストコードの重複を解消し、共有フィクスチャを導入できる"
      benefit: "テストの保守性が向上し、新規テスト作成が容易になる"
    acceptance_criteria:
      - criterion: "tests/conftest.py が存在し、共通フィクスチャを定義している"
        verification: "test -f tests/conftest.py && grep -n 'def log_base' tests/conftest.py"
      - criterion: "test_llm_client.py の Protocol テストがパラメータ化されている"
        verification: "grep -n 'pytest.mark.parametrize' tests/test_llm_client.py"
      - criterion: "test_logger.py が共通フィクスチャを使用している"
        verification: "grep -n 'log_base' tests/test_logger.py || true"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -v --tb=short"
    technical_notes: |
      ## フェーズ4: テスト基盤の改善

      ### /tidy:first（構造的改善）
      - tests/conftest.py を新規作成（共通フィクスチャ定義）

      ### 修正実施（振る舞いの変更）
      - test_llm_client.py の Protocol テストをパラメータ化 (28-78行)
      - test_logger.py で共通フィクスチャを使用
      - test_scheduler.py で共通フィクスチャを使用

      ### /tidy:after（片付け）
      - 各テストファイルから重複フィクスチャを削除

      ### conftest.py のフィクスチャ
      ```python
      @pytest.fixture
      def log_base(tmp_path: Path) -> Path:
          """ログ用の一時ディレクトリ"""
          log_dir = tmp_path / "logs"
          log_dir.mkdir()
          return log_dir

      @pytest.fixture
      def sample_window_info() -> dict[str, str]:
          """サンプルのウィンドウ情報"""
          return {"app_name": "Test App", "window_title": "Test Window"}
      ```
    story_points: 3
    dependencies:
      - PBI-039
      - PBI-040
      - PBI-041
    status: done

  - id: PBI-043
    story:
      role: "開発者"
      capability: "__init__.py の長い関数を分割して責務を明確化できる"
      benefit: "可読性と保守性が向上し、テストが容易になる"
    acceptance_criteria:
      - criterion: "cli.py が存在し、CLI パーサーを定義している"
        verification: "test -f src/auto_daily/cli.py && grep -n 'argparse' src/auto_daily/cli.py"
      - criterion: "report.py が存在し、レポート生成ロジックを定義している"
        verification: "test -f src/auto_daily/report.py && grep -n 'async def' src/auto_daily/report.py"
      - criterion: "monitor.py が存在し、モニタリング起動ロジックを定義している"
        verification: "test -f src/auto_daily/monitor.py && grep -n 'def start' src/auto_daily/monitor.py"
      - criterion: "__init__.py の main() が50行以下になっている"
        verification: "wc -l src/auto_daily/__init__.py | awk '{if ($1 < 100) print \"OK\"; else print \"NG\"}'"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -v --tb=short"
    technical_notes: |
      ## フェーズ5: __init__.py の長い関数の分割

      ### /tidy:first（構造的改善）
      - cli.py を新規作成（CLI パーサーを抽出）
      - report.py を新規作成（レポート生成ロジックを抽出）
      - monitor.py を新規作成（モニタリング起動ロジックを抽出）

      ### 修正実施（振る舞いの変更）
      - __init__.py から新モジュールをインポートし、main() を簡略化
      - tests/test_cli.py を新規作成

      ### /tidy:after（片付け）
      - __init__.py から移動済みコードを削除
      - 未使用の import を削除

      ### 分割後の __init__.py
      ```python
      from auto_daily.cli import create_parser
      from auto_daily.report import report_command, summarize_command
      from auto_daily.monitor import start_monitoring

      def main() -> None:
          load_env()
          parser = create_parser()
          args = parser.parse_args()

          if args.command == "report":
              asyncio.run(report_command(...))
          elif args.command == "summarize":
              asyncio.run(summarize_command(...))
          elif args.start:
              start_monitoring()
          else:
              print(f"auto-daily v{__version__}")
      ```
    story_points: 5
    dependencies:
      - PBI-039
      - PBI-040
      - PBI-041
      - PBI-042
    status: done

  - id: PBI-044
    story:
      role: "開発者"
      capability: "prompt.txt と summary_prompt.txt をバージョン管理から除外し、サンプルファイルを参照できる"
      benefit: "カスタマイズしたプロンプトが他の開発者のリポジトリと競合せず、各自の環境に合わせた設定を維持できる"
    acceptance_criteria:
      - criterion: ".gitignore に prompt.txt と summary_prompt.txt が追加されている"
        verification: "grep -E '^prompt\\.txt$|^summary_prompt\\.txt$' .gitignore | wc -l | grep -q 2"
      - criterion: "prompt.txt.example が存在し、デフォルトテンプレートと同じ内容を含む"
        verification: "test -f prompt.txt.example && grep -q '{activities}' prompt.txt.example"
      - criterion: "summary_prompt.txt.example が存在し、デフォルトテンプレートと同じ内容を含む"
        verification: "test -f summary_prompt.txt.example && grep -q '{log_content}' summary_prompt.txt.example"
      - criterion: "prompt.txt と summary_prompt.txt がリポジトリから削除されている"
        verification: "! git ls-files --error-unmatch prompt.txt summary_prompt.txt 2>/dev/null"
      - criterion: "既存の config.py のフォールバック機構が引き続き動作する"
        verification: "pytest tests/test_config.py -v -k 'prompt'"
    technical_notes: |
      ## 背景
      カスタマイズ可能なファイル（prompt.txt, summary_prompt.txt）がバージョン管理に含まれていると、
      ユーザー固有の変更がコミットされたり、プル時にコンフリクトが発生する可能性がある。
      既に config.py には DEFAULT_PROMPT_TEMPLATE と DEFAULT_SUMMARY_PROMPT_TEMPLATE が定義されており、
      ファイルがない場合のフォールバックは実装済み。

      ## 実装手順
      1. prompt.txt.example と summary_prompt.txt.example を作成（現在のファイル内容をコピー）
      2. .gitignore に prompt.txt と summary_prompt.txt を追加
      3. git rm --cached で既存ファイルをリポジトリから削除（ローカルには残す）
      4. CLAUDE.md または README に使用方法を記載

      ## 使用方法（ユーザー向け）
      ```bash
      # カスタマイズしたい場合
      cp prompt.txt.example prompt.txt
      cp summary_prompt.txt.example summary_prompt.txt
      # 編集して使用
      ```
    story_points: 1
    dependencies: []
    status: done

  # === 音声認識機能 PBIs（PBI-046 を分割）===
  # 元の PBI-046 を7つの小さな PBI に分割

  - id: PBI-046a
    story:
      role: "開発者"
      capability: "pyobjc-framework-Speech と pyobjc-framework-AVFoundation を依存関係に追加できる"
      benefit: "音声認識機能の開発に必要なフレームワークが利用可能になる"
    acceptance_criteria:
      - criterion: "pyobjc-framework-Speech が pyproject.toml に追加されている"
        verification: "grep -n 'pyobjc-framework-Speech' pyproject.toml"
      - criterion: "pyobjc-framework-AVFoundation が pyproject.toml に追加されている"
        verification: "grep -n 'pyobjc-framework-AVFoundation' pyproject.toml"
      - criterion: "uv sync でエラーなくインストールできる"
        verification: "uv sync"
      - criterion: "Speech と AVFoundation が import できる"
        verification: "python3 -c 'from Speech import SFSpeechRecognizer; from AVFoundation import AVAudioEngine; print(\"OK\")'"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      音声認識機能に必要な pyobjc フレームワークを依存関係に追加する。

      ## 追加するパッケージ
      ```toml
      "pyobjc-framework-Speech; sys_platform == 'darwin'",
      "pyobjc-framework-AVFoundation; sys_platform == 'darwin'",
      ```

      ## 依存チェーン（既存でカバー済み）
      - pyobjc-core（既存）
      - pyobjc-framework-Cocoa（既存）
      - pyobjc-framework-Quartz（既存）
      - pyobjc-framework-CoreMedia（AVFoundation が必要、自動インストール）
    story_points: 1
    dependencies: []
    status: done

  - id: PBI-046b
    story:
      role: "Mac ユーザー"
      capability: "マイクアクセス権限と音声認識権限がチェックできる"
      benefit: "権限が不足している場合に明確なエラーメッセージが表示される"
    acceptance_criteria:
      - criterion: "check_microphone_permission() 関数が実装されている"
        verification: "grep -n 'def check_microphone_permission' src/auto_daily/permissions.py"
      - criterion: "check_speech_recognition_permission() 関数が実装されている"
        verification: "grep -n 'def check_speech_recognition_permission' src/auto_daily/permissions.py"
      - criterion: "check_all_permissions() に microphone と speech_recognition が含まれる"
        verification: "grep -n 'microphone\\|speech_recognition' src/auto_daily/permissions.py"
      - criterion: "権限チェックのテストが実装されている"
        verification: "pytest tests/test_permissions.py -v --tb=short -k 'microphone or speech'"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      既存の permissions.py パターンに従い、マイクと音声認識の権限チェックを追加。

      ## 実装方針
      ```python
      def check_microphone_permission() -> bool:
          """Check if microphone permission is granted."""
          # AVAudioSession.sharedInstance().recordPermission を使用
          ...

      def check_speech_recognition_permission() -> bool:
          """Check if speech recognition permission is granted."""
          # SFSpeechRecognizer.authorizationStatus() を使用
          ...
      ```

      ## テスト方針
      既存の mock patch パターンを踏襲し、macOS API をモック化。
    story_points: 1
    dependencies:
      - PBI-046a
    status: ready

  - id: PBI-046c
    story:
      role: "開発者"
      capability: "SpeechRecognizer クラスでマイク入力から音声認識ができる"
      benefit: "音声認識の基本機能が独立したモジュールとして利用可能になる"
    acceptance_criteria:
      - criterion: "speech.py に SpeechRecognizer クラスが実装されている"
        verification: "grep -n 'class SpeechRecognizer' src/auto_daily/speech.py"
      - criterion: "start() メソッドで音声認識を開始できる"
        verification: "grep -n 'def start' src/auto_daily/speech.py"
      - criterion: "stop() メソッドで音声認識を停止できる"
        verification: "grep -n 'def stop' src/auto_daily/speech.py"
      - criterion: "認識結果をコールバックで受け取れる"
        verification: "grep -n 'on_result\\|callback' src/auto_daily/speech.py"
      - criterion: "スレッドセーフな実装になっている"
        verification: "grep -n 'threading\\|Lock' src/auto_daily/speech.py"
      - criterion: "テストが実装されている"
        verification: "pytest tests/test_speech.py -v --tb=short"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      Apple Speech Framework を使用した音声認識モジュールを作成。

      ## クラス設計
      ```python
      class SpeechRecognizer:
          def __init__(
              self,
              on_result: Callable[[str, float, bool], None],
              language: str = "ja-JP",
          ):
              ...

          def start(self) -> None:
              """Start speech recognition."""
              ...

          def stop(self) -> None:
              """Stop speech recognition."""
              ...

          def is_running(self) -> bool:
              """Check if recognition is running."""
              ...
      ```

      ## 使用する macOS API
      - SFSpeechRecognizer: 音声認識エンジン
      - SFSpeechAudioBufferRecognitionRequest: 認識リクエスト
      - AVAudioEngine: マイク入力キャプチャ

      ## スレッド設計
      - 音声認識は別スレッドで実行
      - threading.Lock で状態管理
      - コールバックはメインスレッドから呼び出し
    story_points: 2
    dependencies:
      - PBI-046a
      - PBI-046b
    status: ready

  - id: PBI-046d
    story:
      role: "Mac ユーザー"
      capability: "音声認識結果が JSONL ログに記録される"
      benefit: "音声での作業内容も自動的にログに保存される"
    acceptance_criteria:
      - criterion: "append_log_speech() 関数が logger.py に実装されている"
        verification: "grep -n 'def append_log_speech' src/auto_daily/logger.py"
      - criterion: "音声ログエントリに type='speech' が含まれる"
        verification: "grep -n \"type.*speech\" src/auto_daily/logger.py"
      - criterion: "transcript, confidence, is_final フィールドが記録される"
        verification: "grep -n 'transcript\\|confidence\\|is_final' src/auto_daily/logger.py"
      - criterion: "テストが実装されている"
        verification: "pytest tests/test_logger.py -v --tb=short -k speech"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      既存の logger.py に音声認識結果を記録する関数を追加。

      ## ログフォーマット
      ```json
      {
        "type": "speech",
        "timestamp": "2024-01-15T10:30:00.123456",
        "transcript": "認識されたテキスト",
        "confidence": 0.95,
        "is_final": true,
        "language": "ja-JP"
      }
      ```

      ## 実装
      ```python
      def append_log_speech(
          log_base: Path,
          transcript: str,
          confidence: float,
          is_final: bool,
          language: str = "ja-JP",
      ) -> Path | None:
          """Append speech recognition result to hourly log."""
          ...
      ```

      ## 既存との統合
      - 同じ時間ごとの JSONL ファイルに追記
      - type フィールドで window/speech を区別
    story_points: 1
    dependencies: []
    status: ready

  - id: PBI-046e
    story:
      role: "Mac ユーザー"
      capability: "--enable-speech オプションで音声認識を有効化できる"
      benefit: "コマンドラインから簡単に音声認識機能をオン/オフできる"
    acceptance_criteria:
      - criterion: "--enable-speech フラグが cli.py に追加されている"
        verification: "grep -n 'enable-speech\\|enable_speech' src/auto_daily/cli.py"
      - criterion: "python -m auto_daily --help で --enable-speech が表示される"
        verification: "python -m auto_daily --help | grep -i speech"
      - criterion: "テストが実装されている"
        verification: "pytest tests/test_cli.py -v --tb=short -k speech"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      既存の CLI パーサーに音声認識オプションを追加。

      ## 実装
      ```python
      parser.add_argument(
          "--enable-speech",
          action="store_true",
          help="Enable speech recognition while monitoring",
      )
      ```

      ## 動作
      - --start と組み合わせて使用
      - --enable-speech 単体では警告を表示
    story_points: 1
    dependencies: []
    status: ready

  - id: PBI-046f
    story:
      role: "Mac ユーザー"
      capability: "モニタリング中に音声認識が自動的に動作する"
      benefit: "ウィンドウ監視と同時に音声も記録され、より完全な作業ログが得られる"
    acceptance_criteria:
      - criterion: "monitor.py が SpeechRecognizer をインポートしている"
        verification: "grep -n 'from.*speech import\\|import.*speech' src/auto_daily/monitor.py"
      - criterion: "--enable-speech 時に音声認識が開始される"
        verification: "grep -n 'speech.*start\\|SpeechRecognizer' src/auto_daily/monitor.py"
      - criterion: "終了時に音声認識が停止される"
        verification: "grep -n 'speech.*stop' src/auto_daily/monitor.py"
      - criterion: "認識結果が logger に記録される"
        verification: "grep -n 'append_log_speech' src/auto_daily/monitor.py"
      - criterion: "テストが実装されている"
        verification: "pytest tests/test_monitor.py -v --tb=short -k speech"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      既存の monitor.py に音声認識機能を統合。

      ## 統合ポイント
      - start_monitoring() で SpeechRecognizer を初期化
      - --enable-speech フラグをチェック
      - 認識結果を append_log_speech() で記録
      - シグナルハンドリングで停止

      ## 依存関係
      - PBI-046c: SpeechRecognizer クラス
      - PBI-046d: append_log_speech() 関数
      - PBI-046e: --enable-speech フラグ
    story_points: 1
    dependencies:
      - PBI-046c
      - PBI-046d
      - PBI-046e
    status: ready

  - id: PBI-046g
    story:
      role: "Mac ユーザー"
      capability: "日報生成時に音声ログが考慮される"
      benefit: "会議や通話の内容も日報に反映され、より正確な作業記録が得られる"
    acceptance_criteria:
      - criterion: "report.py が音声ログを読み込む"
        verification: "grep -n \"type.*speech\\|speech.*log\" src/auto_daily/report.py"
      - criterion: "generate_summary_prompt() に音声トランスクリプトが含まれる"
        verification: "grep -n 'transcript\\|speech' src/auto_daily/report.py"
      - criterion: "日報テンプレートに音声セクションが追加されている"
        verification: "grep -n '音声\\|会議\\|通話' src/auto_daily/config.py"
      - criterion: "テストが実装されている"
        verification: "pytest tests/test_report.py -v --tb=short -k speech"
      - criterion: "全テストがパスする"
        verification: "pytest tests/ -n auto -v --tb=short"
    technical_notes: |
      ## 概要
      既存の report.py を拡張し、音声ログを日報生成に統合。

      ## 変更箇所
      - _load_logs_as_entries(): type='speech' エントリも読み込み
      - generate_summary_prompt(): 音声トランスクリプトをプロンプトに含める
      - config.py: 日報テンプレートに音声セクションを追加

      ## プロンプト例
      ```
      ### 音声記録（会議・通話）
      - 10:30: "今日のスプリントレビューについて..."
      - 11:15: "実装方針を確認..."
      ```
    story_points: 1
    dependencies:
      - PBI-046d
      - PBI-046f
    status: ready

  # === 既存 PBIs ===

  - id: PBI-037
    story:
      role: "Mac ユーザー"
      capability: "要約生成プロンプトにより具体的なガイドラインを含めてカスタマイズできる"
      benefit: "作業の目的・成果を推測した高精度な要約が得られる"
    acceptance_criteria:
      - criterion: "デフォルトプロンプトに作業目的の推測ガイドラインが含まれる"
        verification: "grep -n '目的' src/auto_daily/config.py"
      - criterion: "同一アプリの連続操作をまとめる指示が含まれる"
        verification: "grep -n 'まとめる' src/auto_daily/config.py"
      - criterion: "除外すべき情報（ノイズ）の指示が含まれる"
        verification: "grep -n '除外' src/auto_daily/config.py"
      - criterion: "Slack 会話の要約形式が指定されている"
        verification: "grep -n 'Slack' src/auto_daily/config.py"
    technical_notes: |
      ## 現状の課題
      現在の summary_prompt.txt は汎用的すぎて、LLM が具体的な出力を生成しにくい。

      ## 改善版プロンプト
      ```
      以下の1時間分のアクティビティログを簡潔に要約してください。

      ## ガイドライン
      - 作業の「目的」と「成果」を推測して記述する
      - 同じアプリの連続操作はまとめる
      - OCR テキストから具体的なファイル名、関数名、議論トピックを抽出する
      - 「〇〇を確認」より「〇〇の△△を修正するために確認」のように文脈を補完する
      - Slack の会話は「誰と」「何について」話したかを要約する

      ## 除外すべき情報
      - システム通知やポップアップの内容
      - パスワードやトークンと思われる文字列
      - 繰り返し同じ内容のキャプチャ

      ## アクティビティログ
      {log_content}

      ## 出力フォーマット
      ### 主な作業
      - [作業1]: [目的/成果]
      - [作業2]: [目的/成果]

      ### コミュニケーション
      - [相手/チャンネル]: [トピック]

      ### 使用ツール
      [アプリ名のリスト]
      ```

      ## 実装箇所
      - config.py: DEFAULT_SUMMARY_PROMPT_TEMPLATE を更新
      - summary_prompt.txt (example): サンプルファイルを更新
    story_points: 2
    dependencies:
      - PBI-035
    status: done

  - id: PBI-038
    story:
      role: "Mac ユーザー"
      capability: "OCR テキストからノイズ（UI 要素、ゴミ文字）を自動除去できる"
      benefit: "要約や日報の精度が向上し、無関係な情報がログに含まれなくなる"
    acceptance_criteria:
      - criterion: "OCR 結果からシステム通知やメニューバー要素を除去する"
        verification: "pytest tests/test_ocr.py::test_filter_system_ui_noise -v"
      - criterion: "パスワードやトークンと思われる文字列を除去する"
        verification: "pytest tests/test_ocr.py::test_filter_sensitive_strings -v"
      - criterion: "連続する記号や意味のない文字列を除去する"
        verification: "pytest tests/test_ocr.py::test_filter_garbage_characters -v"
      - criterion: "フィルタリングがデフォルトで有効になっている"
        verification: "pytest tests/test_ocr.py::test_filtering_enabled_by_default -v"
      - criterion: "OCR_FILTER_NOISE 環境変数でフィルタリングを無効化できる"
        verification: "pytest tests/test_config.py::test_ocr_filter_noise_from_env -v"
    technical_notes: |
      ## 現状の課題
      OCR 結果には以下のノイズが含まれることがある：
      - macOS メニューバーの要素（時計、バッテリー、Wi-Fi など）
      - システム通知やバナー
      - 記号の羅列や意味不明な文字列
      - API キーやパスワードと思われる長い英数字文字列

      ## 実装方針
      ```python
      # ocr/filters.py
      import re
      from typing import Callable

      class OCRFilter:
          """OCR テキストのノイズを除去するフィルター"""

          def __init__(self):
              self.filters: list[Callable[[str], str]] = [
                  self._filter_menu_bar,
                  self._filter_sensitive_strings,
                  self._filter_garbage_chars,
                  self._filter_repeated_lines,
              ]

          def filter(self, text: str) -> str:
              """すべてのフィルターを適用"""
              for f in self.filters:
                  text = f(text)
              return text.strip()

          def _filter_menu_bar(self, text: str) -> str:
              """メニューバー要素を除去"""
              patterns = [
                  r'^\s*\d{1,2}:\d{2}\s*(AM|PM)?\s*$',  # 時計
                  r'^\s*\d{1,3}%\s*$',  # バッテリー
                  r'^\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*$',  # 曜日
              ]
              lines = text.split('\n')
              return '\n'.join(
                  line for line in lines
                  if not any(re.match(p, line) for p in patterns)
              )

          def _filter_sensitive_strings(self, text: str) -> str:
              """パスワードやトークンを [REDACTED] に置換"""
              # 32文字以上の英数字文字列（API キーなど）
              text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[REDACTED]', text)
              # Bearer トークン
              text = re.sub(r'Bearer\s+[A-Za-z0-9._-]+', 'Bearer [REDACTED]', text)
              return text

          def _filter_garbage_chars(self, text: str) -> str:
              """意味のない記号の連続を除去"""
              # 3つ以上の記号が連続
              text = re.sub(r'[^\w\s]{3,}', '', text)
              return text

          def _filter_repeated_lines(self, text: str) -> str:
              """完全に同じ行の繰り返しを1つにまとめる"""
              lines = text.split('\n')
              seen = set()
              result = []
              for line in lines:
                  if line.strip() and line not in seen:
                      seen.add(line)
                      result.append(line)
                  elif not line.strip():
                      result.append(line)
              return '\n'.join(result)
      ```

      ## 環境変数
      - OCR_FILTER_NOISE: "true" (default) | "false"

      ## 統合箇所
      - ocr/__init__.py: perform_ocr() の戻り値にフィルターを適用
      - config.py: get_ocr_filter_noise() を追加

      ## 後方互換性
      - フィルタリングはデフォルト有効
      - 環境変数で無効化可能
    story_points: 3
    dependencies:
      - PBI-023
    status: done

  - id: PBI-036
    story:
      role: "Mac ユーザー"
      capability: "ログファイルが日付ごとのディレクトリ（logs/YYYY-MM-DD/）に保存される"
      benefit: "日ごとのログが整理され、管理・検索がしやすくなる"
    acceptance_criteria:
      - criterion: "processor.py が append_log_hourly() を使用している"
        verification: "grep -n 'append_log_hourly' src/auto_daily/processor.py"
      - criterion: "ログが logs/YYYY-MM-DD/activity_HH.jsonl に保存される"
        verification: "pytest tests/test_processor.py::test_log_in_date_directory -v"
      - criterion: "既存の append_log() は後方互換のため残すが非推奨とする"
        verification: "grep -n 'deprecated' src/auto_daily/logger.py"
    technical_notes: |
      ## 問題
      現在 processor.py は旧方式の append_log() を使用しており、
      ログが logs/ 直下に activity_YYYY-MM-DD.jsonl として保存されている。

      本来は新方式の append_log_hourly() を使用し、
      logs/YYYY-MM-DD/activity_HH.jsonl に保存されるべき。

      ## 修正箇所
      1. processor.py
         - append_log → append_log_hourly に変更
         - 関数シグネチャの違いに対応（slack_context パラメータ）

      2. logger.py
         - append_log() に deprecation 警告を追加

      ## 新旧ディレクトリ構造
      ```
      # 旧（現状）
      ~/.auto-daily/
        └── logs/
            ├── activity_2025-12-25.jsonl
            └── activity_2025-12-26.jsonl

      # 新（期待）
      ~/.auto-daily/
        └── logs/
            └── 2025-12-25/
                ├── activity_09.jsonl
                ├── activity_10.jsonl
                └── ...
      ```

      ## 影響範囲
      - processor.py: process_window_change()
      - logger.py: append_log_hourly() に slack_context を追加する必要があるかも
      - scheduler.py: PeriodicCapture も確認が必要
    story_points: 2
    dependencies: []
    status: done

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
    status: done

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
          __init__.py       # get_ocr_backend() ファクトリ、後方互換 perform_ocr()
          protocol.py       # OCRBackend Protocol 定義
          apple_vision.py   # Apple Vision Framework 実装
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
      - OCR_BACKEND: "apple" (default) | "openai" (PBI-029で追加)

      ## 後方互換性
      - 既存の perform_ocr() 関数は維持（内部でファクトリを使用）
      - 現在の ocr.py を ocr/apple_vision.py に移動
      - ocr/__init__.py で perform_ocr() をエクスポート
    story_points: 3
    dependencies:
      - PBI-002
    status: done

  - id: PBI-024
    story:
      role: "Mac ユーザー"
      capability: "Ollama の Vision モデル（llava 等）を使って OCR を実行できる"
      benefit: "より高精度な文脈理解が可能な AI ベースの OCR を選択できる"
    acceptance_criteria:
      - criterion: "OllamaVisionOCR が OCRBackend プロトコルを実装している"
        verification: "pytest tests/test_ocr.py::test_ollama_vision_implements_protocol -v"
      - criterion: "OCR_BACKEND=ollama で Ollama Vision を使用できる"
        verification: "pytest tests/test_ocr.py::test_ollama_vision_backend -v"
      - criterion: "OCR_MODEL 環境変数で Vision モデルを指定できる（デフォルト: llava）"
        verification: "pytest tests/test_config.py::test_ocr_model_ollama_from_env -v"
      - criterion: "画像を Base64 エンコードして Ollama Vision API に送信できる"
        verification: "pytest tests/test_ocr.py::test_ollama_vision_image_encoding -v"
    technical_notes: |
      ## Ollama Vision OCR の仕組み
      Ollama の Vision 対応モデル（llava, llama3.2-vision 等）を使用して画像からテキストを抽出する。

      ## Ollama Vision API
      ```bash
      POST /api/generate
      {
        "model": "llava",
        "prompt": "この画像のテキストを抽出してください",
        "images": ["<base64 encoded image>"],
        "stream": false
      }
      ```

      ## 実装（openai_vision.py のパターンを踏襲）
      ```python
      # ocr/ollama_vision.py
      import base64
      import httpx

      class OllamaVisionOCR:
          def __init__(self, base_url: str | None = None, model: str | None = None):
              self.base_url = base_url or get_ollama_base_url()
              self.model = model or get_ocr_model()  # デフォルト: "llava"

          def perform_ocr(self, image_path: str) -> str:
              with open(image_path, "rb") as f:
                  image_data = base64.b64encode(f.read()).decode("utf-8")

              response = httpx.post(
                  f"{self.base_url}/api/generate",
                  json={
                      "model": self.model,
                      "prompt": "この画像に含まれるすべてのテキストを抽出してください。",
                      "images": [image_data],
                      "stream": False,
                  },
                  timeout=120.0,
              )
              return response.json()["response"]
      ```

      ## 環境変数
      - OLLAMA_BASE_URL: Ollama サーバー URL（既存設定を共有）
      - OCR_MODEL: Vision モデル名（デフォルト: "llava"）
      - OCR_BACKEND: "ollama" で有効化

      ## Apple Vision との比較
      | 項目 | Apple Vision | Ollama Vision |
      |------|--------------|---------------|
      | 速度 | 高速（ローカル） | 中速（ローカル LLM）|
      | コスト | 無料 | 無料（GPU 負荷） |
      | 精度 | 高 | モデル依存 |
      | 文脈理解 | なし | あり |
    story_points: 3
    dependencies:
      - PBI-023
    status: done

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
    status: done

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

      ## 実装ファイル
      - src/auto_daily/__init__.py: report コマンドを拡張
      - src/auto_daily/summarize.py: 要約読み込み関数を追加
    story_points: 5
    dependencies:
      - PBI-026
    status: done

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
      ```python
      # __init__.py に追加
      from auto_daily.permissions import check_all_permissions

      def main():
          ...
          if args.start:
              # 権限チェック
              perms = check_all_permissions()
              if not perms["screen_recording"]:
                  print("⚠️ Screen recording permission is required.")
                  print("Run: bash scripts/setup-permissions.sh")
              if not perms["accessibility"]:
                  print("⚠️ Accessibility permission is required.")
                  print("Run: bash scripts/setup-permissions.sh")
              if not all(perms.values()):
                  print("Please grant permissions and restart.")
                  sys.exit(1)
              ...
      ```
    story_points: 2
    dependencies:
      - PBI-020
    status: done

  - id: PBI-034
    story:
      role: "Mac ユーザー"
      capability: "Slack ウィンドウのキャプチャ時にチャンネル情報がログに自動記録される"
      benefit: "どのチャンネルで作業していたかが日報に反映され、より詳細なコンテキストが得られる"
    acceptance_criteria:
      - criterion: "processor.py でウィンドウ情報に Slack コンテキストを追加する"
        verification: "pytest tests/test_processor.py::test_slack_context_added -v"
      - criterion: "ログエントリに channel, workspace, dm_user, is_thread フィールドが含まれる"
        verification: "pytest tests/test_logger.py::test_slack_fields_in_log -v"
      - criterion: "Slack 以外のアプリでは追加フィールドは空（None）になる"
        verification: "pytest tests/test_processor.py::test_non_slack_no_context -v"
    technical_notes: |
      ## 統合箇所
      processor.py の process_window_change() 関数で slack_parser.py を呼び出す

      ## 実装内容
      ```python
      # processor.py に追加
      from auto_daily.slack_parser import parse_slack_title

      def process_window_change(old_window, new_window, log_dir):
          ...
          # Slack コンテキストを抽出
          slack_context = None
          if new_window["app_name"] == "Slack":
              slack_context = parse_slack_title(new_window.get("title", ""))

          # ログに追加
          append_log(
              ...,
              slack_context=slack_context,
          )
      ```

      ## ログフォーマット拡張
      ```json
      {
        "timestamp": "...",
        "app_name": "Slack",
        "window_title": "#dev-team | Company",
        "ocr_text": "...",
        "slack_context": {
          "channel": "dev-team",
          "workspace": "Company",
          "dm_user": null,
          "is_thread": false
        }
      }
      ```
    story_points: 3
    dependencies:
      - PBI-012
      - PBI-013
    status: done

  - id: PBI-035
    story:
      role: "Mac ユーザー"
      capability: "要約生成に使うプロンプトをテキストファイルでカスタマイズできる"
      benefit: "自分の仕事スタイルに合った要約形式を定義でき、日報の質が向上する"
    acceptance_criteria:
      - criterion: "プロジェクトルートの summary_prompt.txt からプロンプトを読み込める"
        verification: "pytest tests/test_config.py::test_summary_prompt_template_from_file -v"
      - criterion: "summary_prompt.txt が存在しない場合はデフォルトプロンプトを使用する"
        verification: "pytest tests/test_config.py::test_summary_prompt_template_default -v"
      - criterion: "{log_content} プレースホルダーがログ内容で置換される"
        verification: "pytest tests/test_main.py::test_summary_prompt_placeholder -v"
      - criterion: "summarize コマンドがカスタムプロンプトを使用する"
        verification: "pytest tests/test_main.py::test_summarize_uses_custom_prompt -v"
    technical_notes: |
      ## 実装パターン
      PBI-007（日報用 prompt.txt）と同じパターンを踏襲する。

      ## config.py に追加
      ```python
      DEFAULT_SUMMARY_PROMPT_TEMPLATE = """以下の1時間分のアクティビティログを簡潔に要約してください。
      重要なタスク、作業内容、成果を箇条書きで記載してください。

      {log_content}

      要約:"""

      def get_summary_prompt_template() -> str:
          """Get the prompt template for hourly summarization.

          Reads from summary_prompt.txt in the current working directory.
          Falls back to DEFAULT_SUMMARY_PROMPT_TEMPLATE if not found.

          Returns:
              Prompt template string with {log_content} placeholder.
          """
          prompt_file = Path.cwd() / "summary_prompt.txt"

          if prompt_file.exists():
              return prompt_file.read_text()

          return DEFAULT_SUMMARY_PROMPT_TEMPLATE
      ```

      ## __init__.py の変更
      ```python
      from auto_daily.config import get_summary_prompt_template

      def generate_summary_prompt(log_content: str) -> str:
          template = get_summary_prompt_template()
          return template.format(log_content=log_content)
      ```

      ## カスタマイズ例（summary_prompt.txt）
      ```
      以下のアクティビティログを要約してください。

      ## フォーマット
      - 主な作業内容
      - 使用したツール/アプリ
      - 重要なコミュニケーション

      {log_content}

      要約:
      ```

      ## 日報用プロンプトとの違い
      | 項目 | 日報（prompt.txt） | 要約（summary_prompt.txt） |
      |------|-------------------|---------------------------|
      | プレースホルダー | {activities} | {log_content} |
      | 入力 | フォーマット済みログ | 生ログ（JSONL） |
      | 出力 | 構造化日報 | 箇条書き要約 |
    story_points: 2
    dependencies:
      - PBI-007
      - PBI-026
    status: done
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
sprint_45:
  number: 45
  pbi_id: PBI-046b
  story: "マイクアクセス権限と音声認識権限がチェックできる"
  status: in_progress

  sprint_goal:
    statement: "既存の permissions.py に権限チェック関数を追加し、音声認識に必要な権限状態を確認できるようにする"
    success_criteria:
      - "check_microphone_permission() 関数が実装されている"
      - "check_speech_recognition_permission() 関数が実装されている"
      - "check_all_permissions() に microphone と speech_recognition が含まれる"
      - "全テストがパスする"
    stakeholder_value: "権限不足時に明確なエラーメッセージを表示でき、ユーザー体験が向上する"

  subtasks:
    - id: ST-001
      test: "check_microphone_permission() と check_speech_recognition_permission() のテスト"
      implementation: |
        tests/test_permissions.py に以下を追加:
        - test_check_microphone_permission_granted/denied
        - test_check_speech_recognition_permission_granted/denied
        - test_check_all_permissions に microphone/speech_recognition を追加
      type: behavioral
      status: pending
      commits: []

    - id: ST-002
      test: "DoD 検証: 全テストパスと lint/type チェック"
      implementation: |
        以下を実行して確認:
        - pytest tests/ -n auto -v --tb=short
        - ruff check . && ruff format --check .
        - ty check src/
      type: verification
      status: pending
      commits: []

  notes: |
    ## 背景
    PBI-046（音声認識機能）の2番目のタスク。
    音声認識を実装する前に、マイクと音声認識の権限チェック機能を追加する。

    ## 実装方針
    既存の permissions.py のパターン（screen_recording, accessibility）に従う:
    - AVAudioSession.sharedInstance().recordPermission でマイク権限チェック
    - SFSpeechRecognizer.authorizationStatus() で音声認識権限チェック
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

  - sprint: 24
    pbi_id: PBI-033
    story: "アプリケーション起動時に macOS の必要な権限（画面収録・アクセシビリティ）が確認され、不足時に警告が表示される"
    subtasks_completed: 3
    commits: []

  - sprint: 25
    pbi_id: PBI-034
    story: "Slack ウィンドウのキャプチャ時にチャンネル情報がログに自動記録される"
    subtasks_completed: 3
    commits: []

  - sprint: 26
    pbi_id: PBI-016
    story: "Ollama がインストールされていなくてもアプリケーションを起動できる"
    subtasks_completed: 4
    commits: []

  - sprint: 27
    pbi_id: PBI-022
    story: "LM Studio を使って日報を生成できる"
    subtasks_completed: 3
    commits: []

  - sprint: 28
    pbi_id: PBI-023
    story: "OCR バックエンドを抽象化して複数の方式を統一的に扱える"
    subtasks_completed: 4
    commits: []

  - sprint: 29
    pbi_id: PBI-029
    story: "OpenAI Vision API（GPT-4o）を使って OCR を実行できる"
    subtasks_completed: 4
    commits: []

  - sprint: 30
    pbi_id: PBI-032
    story: "日報生成時にカレンダー予定と作業ログを照合して、差分と補完情報を含めた日報を作成できる"
    subtasks_completed: 5
    commits: []

  - sprint: 31
    pbi_id: PBI-024
    story: "Ollama の Vision モデル（llava 等）を使って OCR を実行できる"
    subtasks_completed: 4
    commits: []

  - sprint: 32
    pbi_id: PBI-026
    story: "1時間ごとにログを要約して保存できる"
    subtasks_completed: 5
    commits: []

  - sprint: 33
    pbi_id: PBI-027
    story: "時間単位の要約を集約して日報を生成できる"
    subtasks_completed: 4
    commits: []

  - sprint: 34
    pbi_id: PBI-035
    story: "要約生成に使うプロンプトをテキストファイルでカスタマイズできる"
    subtasks_completed: 4
    commits: []

  - sprint: 35
    pbi_id: PBI-036
    story: "ログファイルが日付ごとのディレクトリ（logs/YYYY-MM-DD/）に保存される"
    subtasks_completed: 3
    commits: []

  - sprint: 36
    pbi_id: PBI-037
    story: "要約生成プロンプトにより具体的なガイドラインを含めてカスタマイズできる"
    subtasks_completed: 2
    commits: []

  - sprint: 37
    pbi_id: PBI-038
    story: "OCR テキストからノイズ（UI 要素、ゴミ文字）を自動除去できる"
    subtasks_completed: 5
    commits: []

  - sprint: 38
    pbi_id: PBI-040
    story: "processor.py と scheduler.py の重複したキャプチャ処理を統合できる"
    subtasks_completed: 5
    commits:
      - 4b8e35a  # refactor: extract common capture pipeline to deduplicate code
      - 72f0013  # docs(scrum): start Sprint 38 for PBI-040
      - 4e08785  # refactor(scheduler): use instance variable for stop event
      - fb86849  # refactor(processor): use capture_pipeline to eliminate duplication
      - 13fbaa0  # refactor(scheduler): use capture_pipeline to eliminate duplication
      - bceec74  # chore(scrum): complete Sprint 38 - capture pipeline integration (PBI-040)

  - sprint: 39
    pbi_id: PBI-041
    story: "ollama.py の2つのプロンプト生成関数で重複するログ処理を統合できる"
    subtasks_completed: 2
    commits:
      - e1e6d3b  # docs(scrum): start Sprint 39 for PBI-041
      - 110c3a9  # refactor(ollama): extract helper functions to eliminate duplication

  - sprint: 40
    pbi_id: PBI-042
    story: "テストコードの重複を解消し、共有フィクスチャを導入できる"
    subtasks_completed: 4
    commits:
      - 4ba02d9  # refactor(test): introduce shared fixtures to eliminate duplication

  - sprint: 41
    pbi_id: PBI-043
    story: "__init__.py の長い関数を分割して責務を明確化できる"
    subtasks_completed: 5
    commits:
      - 4583501  # refactor: extract CLI, report, and monitor modules from __init__.py

  - sprint: 42
    pbi_id: PBI-044
    story: "prompt.txt と summary_prompt.txt をバージョン管理から除外し、サンプルファイルを参照できる"
    subtasks_completed: 4
    commits:
      - 53bd4a0  # build: move prompt templates to .example files
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

  - sprint: 24
    what_went_well:
      - "既存の permissions.py モジュールを活用して効率的に実装"
      - "PBI-020 で実装した check_all_permissions() をそのまま統合"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "3つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - シンプルな統合タスクがスムーズに完了"
    action_items:
      - "次は PBI-034（Slack コンテキストのログ記録）を実装"

  - sprint: 25
    what_went_well:
      - "既存の slack_parser.py と parse_slack_title() を活用して効率的に実装"
      - "processor.py への統合が最小限の変更で完了"
      - "logger.py への slack_context 追加が後方互換性を維持"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "3つのサブタスクをすべて完了"
    what_to_improve:
      - "TypedDict と dict の型互換性に注意が必要（Any 型での回避）"
    action_items:
      - "次の ready な PBI を確認して実装を進める"

  - sprint: 26
    what_went_well:
      - "llm/ollama.py に check_ollama_connection() を追加し、接続チェック機能を実装"
      - "httpx.get() を使用したシンプルな同期接続チェック"
      - "start コマンドでは警告のみ、report コマンドではエラー終了という適切な動作分離"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - シンプルな機能追加がスムーズに完了"
    action_items:
      - "次の ready な PBI（PBI-022 LM Studio 対応など）を確認して実装を進める"

  - sprint: 27
    what_went_well:
      - "OpenAI SDK を再利用して LM Studio クライアントを効率的に実装"
      - "OpenAI 互換 API なので base_url のオーバーライドのみで動作"
      - "既存の llm/ パッケージ構造を踏襲し、スムーズに追加"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "3つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "次の draft PBI をリファインメントして ready にする"

  - sprint: 28
    what_went_well:
      - "LLM クライアント抽象化（PBI-021）と同じパターンを踏襲して効率的に実装"
      - "既存の ocr.py を ocr/ パッケージに再編成"
      - "後方互換性を維持（perform_ocr() 関数を維持）"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "PBI-029（OpenAI Vision OCR）の実装を進める"

  - sprint: 29
    what_went_well:
      - "OCR 抽象化（PBI-023）と同じパターンを踏襲して効率的に実装"
      - "OpenAI SDK の multimodal 機能（Vision API）をシンプルに活用"
      - "Base64 エンコードとメディアタイプ自動検出を実装"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "次の draft PBI をリファインメントして ready にする"

  - sprint: 30
    what_went_well:
      - "PBI-031 で実装した CalendarEvent, get_all_events() を効果的に活用"
      - "LogEntry, MatchResult dataclass で照合結果を型安全に構造化"
      - "match_events_with_logs() で時間ベースの照合を柔軟に実装"
      - "generate_daily_report_prompt_with_calendar() でカレンダー統合プロンプトを生成"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "5つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "次の draft PBI をリファインメントして ready にする"

  - sprint: 31
    what_went_well:
      - "openai_vision.py のパターンを踏襲して効率的に実装"
      - "既存の httpx を使用した OllamaClient と同様のパターンで Vision API を実装"
      - "OCR バックエンド抽象化（PBI-023）の上に自然に追加"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "次の draft PBI（PBI-026 要約機能など）をリファインメントして ready にする"

  - sprint: 32
    what_went_well:
      - "既存の logger.py と scheduler.py のパターンを踏襲して効率的に実装"
      - "summarize サブコマンドと HourlySummaryScheduler を追加"
      - "config.py に get_summaries_dir() を追加して設定を統一"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "5つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "PBI-027（要約を使った日報生成）をリファインメントして ready にする"

  - sprint: 33
    what_went_well:
      - "PBI-026 で実装した summarize.py を効果的に活用"
      - "get_summaries_for_date() と generate_daily_report_prompt_from_summaries() を追加"
      - "report コマンドに --auto-summarize オプションを追加"
      - "ST-001 の実装が ST-002、ST-003 の要件も満たしており効率的"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してシンプルに完了"
    action_items:
      - "次の draft PBI をリファインメントして ready にする"

  - sprint: 34
    what_went_well:
      - "PBI-007（prompt.txt）と同じパターンを踏襲して効率的に実装"
      - "config.py に DEFAULT_SUMMARY_PROMPT_TEMPLATE と get_summary_prompt_template() を追加"
      - "generate_summary_prompt() で template.format() を使用した置換を実装"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "4つのサブタスクをすべて完了"
    what_to_improve:
      - "テストで使用するログファイル形式（hourly vs daily）の不整合に注意"
    action_items:
      - "Product Backlog の整理（完了した PBI を確認）"

  - sprint: 35
    what_went_well:
      - "processor.py と scheduler.py の append_log → append_log_hourly 移行がスムーズに完了"
      - "append_log_hourly() に slack_context パラメータを追加して機能拡張"
      - "warnings.warn() による deprecation 警告を実装"
      - "TDD サイクル（Red-Green）がスムーズに回った"
      - "3つのサブタスクをすべて完了"
    what_to_improve:
      - "既存テスト（test_integration.py）のモック更新が必要だった点に注意"
    action_items:
      - "append_log を使用している他のコードがないか確認"

  - sprint: 36
    what_went_well:
      - "PBI-035（カスタムプロンプト機能）をベースに効率的に実装"
      - "DEFAULT_SUMMARY_PROMPT_TEMPLATE の改善で LLM への指示が明確化"
      - "目的・成果の推測、ノイズ除外、Slack 要約のガイドラインを追加"
      - "2つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - シンプルなプロンプト改善がスムーズに完了"
    action_items:
      - "実際の要約結果を確認して、プロンプトの効果を評価"

  - sprint: 37
    what_went_well:
      - "OCRFilter クラスで複数のフィルターを組み合わせたパイプライン設計"
      - "正規表現パターンでメニューバー要素、センシティブ情報、ゴミ文字を効率的に除去"
      - "get_ocr_filter_noise() で既存の環境変数パターンを踏襲"
      - "perform_ocr() へのフィルター統合が最小限の変更で完了"
      - "5つのサブタスクをすべて完了"
    what_to_improve:
      - "特になし - 既存パターンを活用してスムーズに完了"
    action_items:
      - "実際の OCR 結果でフィルターの効果を確認"
      - "必要に応じてフィルターパターンを追加・調整"

  - sprint: 38
    what_went_well:
      - "capture_pipeline.py を新規作成し、processor.py と scheduler.py の重複コードを約80%削減"
      - "CaptureContext dataclass でキャプチャのコンテキスト情報を明確に構造化"
      - "execute_capture_pipeline() で共通パイプライン（キャプチャ→OCR→ログ）を統一"
      - "scheduler.py の threading.Event() をインスタンス変数化してテスタビリティを向上"
      - "Tidy First アプローチで構造変更と振る舞い変更を分離してコミット"
    what_to_improve:
      - "特になし - 計画通りにリファクタリングを完了"
    action_items:
      - "今後の機能追加時は capture_pipeline を拡張して重複を防ぐ"

  - sprint: 39
    what_went_well:
      - "_load_log_entries() と _format_activities() ヘルパー関数を抽出"
      - "generate_daily_report_prompt() と _with_calendar() の重複ログ処理を統合"
      - "関数の責務が明確になり、可読性が向上"
    what_to_improve:
      - "特になし - 小規模なリファクタリングで効率的に完了"
    action_items:
      - "今後のプロンプト生成機能追加時はヘルパー関数を活用"

  - sprint: 40
    what_went_well:
      - "tests/conftest.py を新規作成し、共通フィクスチャ（log_base, sample_window_info）を定義"
      - "test_llm_client.py の Protocol テストをパラメータ化して重複を削減"
      - "pytest の fixture と parametrize を活用した効率的なテスト構造"
    what_to_improve:
      - "test_logger.py の既存テストはシンプルで共通フィクスチャ不要だった"
    action_items:
      - "新規テスト作成時は conftest.py のフィクスチャを積極的に活用"

  - sprint: 41
    what_went_well:
      - "cli.py、report.py、monitor.py の3モジュールを抽出し責務を分離"
      - "__init__.py の main() を50行以下に簡略化"
      - "純粋な構造的リファクタリングで既存テストがすべてパス"
      - "モジュール分離により将来のテスト追加が容易に"
    what_to_improve:
      - "特になし - Tidy First の原則に従いスムーズに完了"
    action_items:
      - "各モジュールの単体テストを将来的に追加検討"

  - sprint: 42
    what_went_well:
      - ".example パターンでカスタマイズ可能ファイルとバージョン管理を分離"
      - "config.py の既存フォールバック機構により追加実装不要"
      - ".gitignore と git rm --cached で既存ファイルを適切に除外"
      - "全テスト（165件）がパスし、既存機能への影響なし"
    what_to_improve:
      - "特になし - シンプルな設定変更がスムーズに完了"
    action_items:
      - "CLAUDE.md に .example ファイルの使用方法を追記"
      - "他のカスタマイズ可能ファイル（calendar_config.yaml等）も同様のパターンを踏襲済み"
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
