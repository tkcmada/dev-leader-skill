# values.schema.md

Schema for the `values.yaml` consumed by `leader.template.md` and `dev-workflow.template.md`.

Every placeholder referenced in either template is documented here. The categories below match how the templates use them:

- **Scalars** — single string / enum values (`{{ var }}`).
- **Flags** — booleans gating `{% if %}` blocks.
- **Lists** — iterated via `{% for %}`. Each row's expected fields are documented.

Two ready-to-copy examples live under `examples/tanecon.values.yaml` and `examples/tottori.values.yaml`.

---

## Scalars

| Key | Required | Type | Meaning | Example |
|-----|----------|------|---------|---------|
| `project_name` | yes | string | Short project slug used in commit notification titles etc. | `tanecon2027` |
| `project_display_name` | yes | string | Human-friendly project name used in headings and intro text. | `tanecon2027 BBM` |
| `repo_slug` | yes | string | `owner/name` of the GitHub repo where issues live. | `tkcmada/tanecon2027` |
| `story_label` | yes | string | The label that marks an issue as an implementation story. Historically `type:dev`; new projects should standardize on `type:story`. | `type:story` |
| `push_branch` | yes | string | The branch the dev-workflow pushes to at [6]. | `main` |
| `remote_exec_prefix` | yes | string | Prefix prepended to every `gh` / `git` command. Empty string when running locally; e.g. `ssh pi4 'cd ~/<repo> && ` when commands must be run on another host. Note: when non-empty, callers must close the quote themselves at the end of the command. | `""` |
| `repo_path` | yes | string | Absolute or `~`-relative path to the project repo on the runtime host. | `~/tanecon2027` |
| `ticket_hierarchy` | yes | enum | One of `epic-story` (two layers: epic → story) or `flat-dev` (single implementation layer). | `epic-story` |
| `leader_description` | yes | string | The `description:` frontmatter line for the rendered leader SKILL.md. | `Software development lead persona for tanecon2027 BBM project. ...` |
| `dev_workflow_description` | yes | string | The `description:` frontmatter line for the rendered dev-workflow SKILL.md. | `Standard development workflow for tanecon2027 BBM (type:story). ...` |

### Notes on scalars

- `story_label` and `ticket_hierarchy` are independent: a project may use `epic-story` hierarchy with a `type:story` label, or `flat-dev` with `type:dev`. Templates branch on each separately.
- `remote_exec_prefix` is **concatenated literally** in front of commands. If non-empty, it must include the opening quote/escape syntax and the caller is responsible for the closing quote — typical patterns:
  - Local execution: `""` (empty).
  - Remote via SSH: `"ssh pi4 'cd ~/tottori-rover-2026 && "` (note the trailing space and unclosed quote intentionally absorbed by surrounding text in the template if appropriate). Projects that prefer to render strictly closed shell commands should keep `remote_exec_prefix` empty and run the renderer where commands execute.

---

## Flags

All flags are booleans. When `true`, the corresponding `{% if %}` block in the template is included; when `false`, it is dropped.

| Key | Default | Controls |
|-----|---------|----------|
| `retrospectives_enabled` | `false` | Whether the `memory/retrospectives/` directory, the standup "retrospective report" step, the `## Retrospective` section in leader, and the retrospective file format block are emitted. |
| `wrap_up_enabled` | `false` | Whether the `## Session Wrap Up` section is emitted in leader. |
| `bye_enabled` | `false` | Whether the `## Good Bye — End of Session` section, the standup "carry-over items" step, and related references are emitted in leader. |
| `recognition_phrases_enabled` | `false` | Whether the "Leader recognition phrases" table is emitted under `## Trigger`. When `true`, also populate the `recognition_phrases` list (see below). |
| `openspec_enabled` | `false` | Whether the `## Ordering with OpenSpec` section and the OpenSpec-related AC bullet are emitted in dev-workflow. |
| `notification_enabled` | `false` | Whether Pushover notification commands appear in [4] agent brief, [6] post-close, and the AC observability viewpoint. |
| `qa_skill_ref_enabled` | `false` | Whether [5] QA references an external `qa-testing` skill for project-specific verification checklists. |

---

## Lists

Each list is iterated with `{% for item in list %}`. The expected fields per item are listed under each entry.

### `available_agents`

The "Available Agents" table in leader.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `name` | yes | string | Agent name as invoked (shown in backticks). |
| `best_for` | yes | string | One-line description of when to pick this agent. |

Example:
```yaml
available_agents:
  - name: general-purpose
    best_for: Investigation, shell commands, bug fixes, multi-step implementation
  - name: Explore
    best_for: Read-only codebase search — finding files, symbols, references
```

### `recognition_phrases`

Trigger phrases the leader treats as activations. Only emitted when `recognition_phrases_enabled` is `true`. May be empty in that case but is then a no-op table.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `phrase` | yes | string | The phrase shown in bold in the activation table. |
| `action` | yes | string | What the leader does when the phrase fires (markdown allowed). |

Example:
```yaml
recognition_phrases:
  - phrase: add epic ticket
    action: Create a `type:epic` + `status:open` issue ...
```

### `memory_dirs`

Rows of the memory layout block under `## Memory Location`.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `name` | yes | string | Directory name (without trailing slash; the template adds it). |
| `file_pattern` | yes | string | Files inside it, shown after the name (e.g. `index.md + YYYY-MM-DD.md`). |
| `purpose` | yes | string | One-line purpose. |

Example:
```yaml
memory_dirs:
  - name: daily
    file_pattern: index.md + YYYY-MM-DD.md
    purpose: daily work logs
  - name: decisions
    file_pattern: index.md + decision-NNN.md
    purpose: ADRs
```

### `applicable_subsystems`

Bullets listed under `## When to use this skill` in dev-workflow. Each entry is rendered as `- {{ item }}`.

Type: list of string.

Example:
```yaml
applicable_subsystems:
  - Writing / modifying code (Python, C/C++ firmware, shell, etc.)
  - Changing hardware-control code (ATmega firmware, AtomS3, I2C, UART, ToF, etc.)
  - Creating or significantly modifying skills (SKILL.md) or agent definitions
  - Modifying existing automation flows
  - Investigating / fixing bugs
```

### `subsystem_labels`

Optional subsystem labels mentioned in the [1] ticket creation step.

Type: list of string (full label names, e.g. `subsystem:atmega`).

### `user_story_actors`

Actor candidates inserted into the User Story template in [2a].

Type: list of string. Rendered joined with ` / `.

Example:
```yaml
user_story_actors:
  - Toku
  - BBM operator
  - leader
```

### `hardware_verification_examples`

Short tokens listed in the AC Gate "Hardware verification" row, e.g. peripherals to check after a firmware flash.

Type: list of string. Rendered joined with `, `.

### `hardware_safety_targets`

Hardware components the agent must handle safely (referenced in [4]).

Type: list of string. Rendered joined with `, `.

### `qa_verification_methods`

Rows of the "Verification means" table in [5] QA.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `method` | yes | string | The verification means (e.g. "File / code review"). |
| `example` | yes | string | A concrete example command or activity. |

Example:
```yaml
qa_verification_methods:
  - method: File / code review
    example: "`git diff` to confirm the change matches intent"
```

### `related_resources`

Bullets under `## Related resources` in dev-workflow.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `name` | yes | string | Resource name / title. |
| `ref` | yes | string | Pointer (path, URL, or wiki-style link). |

Example:
```yaml
related_resources:
  - name: Main skill
    ref: "[[leader]]"
  - name: GitHub Issues
    ref: tkcmada/tanecon2027
```

### `status_labels`

Status-to-emoji mapping shown in the "Show Task List" step of leader. Typically the same 5 rows across projects.

Fields:

| Field | Required | Type | Meaning |
|-------|----------|------|---------|
| `label` | yes | string | Full label (e.g. `status:done`). |
| `emoji` | yes | string | Emoji prefix (e.g. `✅`). |

Example:
```yaml
status_labels:
  - label: status:done
    emoji: "✅"
  - label: status:open
    emoji: "📋"
  - label: status:in-progress
    emoji: "🔄"
  - label: status:blocked
    emoji: "🚫"
  - label: status:action_required
    emoji: "⚠️"
```

### `ac_hardware_specific_bullets`

Extra hardware-specific bullets injected into the AC "Behavior / Performance" viewpoint.

Type: list of string. Each entry becomes one `- [ ] ...` bullet.

Example:
```yaml
ac_hardware_specific_bullets:
  - "Firmware change: ATmega or AtomS3 runs without resetting"
  - "Firmware change: WDT does not fire under normal load"
```

---

## Minimal required keys

The smallest valid `values.yaml` includes every scalar and every list (even if empty) plus all flags (which can default to `false`). See the examples for fully populated values.
