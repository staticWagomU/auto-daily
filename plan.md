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
  number: 5
  pbi: PBI-005
  status: in_progress
  subtasks_completed: 1
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
sprint:
  number: 4
  pbi_id: PBI-004
  story: "Mac ユーザーとして、数分間隔で Ollama を呼び出し、蓄積されたログから日報を自動生成できる"
  status: in_progress

  subtasks:
    - id: ST-001
      test: "test_scheduled_call: 設定された間隔で Ollama API を呼び出せる"
      implementation: "OllamaClient クラスを実装"
      type: behavioral
      status: completed
      commits:
        - phase: red
          hash: 2d9a421
        - phase: green
          hash: 0b4e3e3

    - id: ST-002
      test: "test_prompt_generation: JSONL ログを読み込み、日報用のプロンプトを生成できる"
      implementation: "generate_daily_report_prompt() 関数を実装"
      type: behavioral
      status: completed
      commits:
        - phase: red
          hash: ad8b6f9
        - phase: green
          hash: e835661

    - id: ST-003
      test: "test_save_daily_report: Ollama からの応答を日報ファイルとして保存できる"
      implementation: "save_daily_report() 関数を実装"
      type: behavioral
      status: completed
      commits:
        - phase: red
          hash: e46e839
        - phase: green
          hash: 031f845

  notes: |
    Sprint 5 開始。PBI-005 のメインエントリーポイントを TDD で実装する。

sprint_5:
  number: 5
  pbi_id: PBI-005
  story: "auto-daily コマンドでアプリケーションを起動し、ウィンドウ監視から日報生成までの一連の処理を実行できる"
  status: in_progress

  subtasks:
    - id: ST-001
      test: "test_module_execution: python -m auto_daily でアプリケーションを起動できる"
      implementation: "__main__.py を作成し、main() を呼び出す"
      type: behavioral
      status: completed
      commits:
        - phase: red
          hash: d4d28a3
        - phase: green
          hash: pending

    - id: ST-002
      test: "test_cli_entrypoint: auto-daily コマンドで起動できる"
      implementation: "__init__.py に main() を追加し、pyproject.toml と整合させる"
      type: behavioral
      status: pending
      commits: []

    - id: ST-003
      test: "test_main_starts_monitoring: 起動後、ウィンドウ監視ループが開始される"
      implementation: "main() で WindowMonitor を起動する"
      type: behavioral
      status: pending
      commits: []

  notes: |
    ルートの main.py を削除し、パッケージ内に適切なエントリーポイントを実装する。
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
