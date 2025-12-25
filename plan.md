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
  number: 11
  pbi: PBI-011
  status: in_progress
  subtasks_completed: 0
  subtasks_total: 3
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
    status: ready
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
sprint_11:
  number: 11
  pbi_id: PBI-011
  story: "ウィンドウ切り替えとは別に、30秒ごとに定期的に画面キャプチャとOCRが実行される"
  status: in_progress

  subtasks:
    - id: ST-001
      test: "test_periodic_capture: 30秒間隔で定期的にキャプチャが実行される"
      implementation: "PeriodicCapture クラスを作成し、スケジューラを実装"
      type: behavioral
      status: pending
      commits: []

    - id: ST-002
      test: "test_coexistence_with_window_trigger: ウィンドウ切り替えと定期トリガーが共存する"
      implementation: "メインループで両方のトリガーを起動"
      type: behavioral
      status: pending
      commits: []

    - id: ST-003
      test: "test_stop_periodic_capture: アプリ停止時に定期実行も停止する"
      implementation: "stop() メソッドでスケジューラを停止"
      type: behavioral
      status: pending
      commits: []

  notes: |
    ウィンドウ切り替えトリガーに加えて、30秒間隔の定期実行を追加。
    長時間同じウィンドウで作業していても記録が取れるようになる。
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
