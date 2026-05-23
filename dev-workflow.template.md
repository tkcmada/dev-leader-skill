---
name: dev-workflow
description: {{ dev_workflow_description }}
---

# dev-workflow — {{ project_display_name }} development task standard flow

{% macro gh_cmd(verb, args) -%}
{{ remote_exec_prefix }}gh {{ verb }} --repo {{ repo_slug }} {{ args }}
{%- endmacro %}

Issues labeled `{{ story_label }}` in `{{ repo_slug }}` are **always** processed by the 6-stage flow defined below.
{% if ticket_hierarchy == 'epic-story' %}
## Ticket hierarchy: epic / story

Development tasks are managed in a **two-layer epic → story hierarchy**.

```
type:epic ──(epic to story)──▶ {{ story_label }} ──(6-stage flow [1]–[6])──▶ implement & close
```

- **`{{ story_label }}` is the only implementation-unit ticket.** Single small tasks are also filed as `{{ story_label }}`, not as a separate "dev" type.
- A story can exist under an epic or on its own.
- The epic itself is **not** an implementation unit and does not go through the 6-stage flow. Close the epic once all child stories are `status:done`.

### type:epic — filing a coarse goal

- Trigger phrase **"add epic ticket"** creates a `type:epic` + `status:open` issue.
- At creation, a coarse goal statement is enough — refinement happens in "epic to story".
- "add epic ticket" and "epic to story" are **leader recognition phrases** (treated like "hi leader") and are handled by [[leader]].

### epic to story — refinement and story extraction

- Trigger phrase **"epic to story"** has the leader brainstorm with the user to refine the epic body. The refinement fills five sections:
  1. **Goal** — what we want to achieve
  2. **Use Case** — assumed usage
  3. **Failure Scenarios / Edge Cases**
  4. **Architecture** — design / approach
  5. **Acceptance Criteria**
- Once enough information has been gathered, create one or more `{{ story_label }}` issues.
  - Slice stories as **user-facing vertical slices** (e.g. "add a logging feature"). Do **not** slice by component (e.g. "ATmega side only").
  - Link the epic number from the story body. The epic keeps a list of its child stories.
- Each `{{ story_label }}` is then processed by the **6-stage flow [1]–[6]** below.
{% endif %}
## When to use this skill

A GitHub Issue in `{{ repo_slug }}` qualifies for this workflow if it does any of the following:

{% for sub in applicable_subsystems -%}
- {{ sub }}
{% endfor %}

Issues that do not qualify (routine task management, ops notes, etc.) are handled by the normal [[leader]] flow.
{% if openspec_enabled %}
## Ordering with OpenSpec

For changes large enough to require an OpenSpec proposal, the ordering is:

1. **Large change requiring an OpenSpec proposal** → first author and accept the proposal via `openspec` (see `@/openspec/AGENTS.md`).
2. Once the proposal is accepted, enter dev-workflow [1] Ticket creation (reference the proposal ID in the issue body under a `## Related OpenSpec` section).
3. Stages [2]–[6] then proceed as usual.

Small-to-medium changes that do not need an OpenSpec proposal go directly to dev-workflow [1].
{% endif %}
---

## 6-stage flow

```
[1] File a ticket
   ↓
[2] Refinement (decide AC)
   ↓
[3] AC Gate check  ← if fails, go back to [2]
   ↓ pass
[3.5] User approval  ← only for tasks where brainstorming was performed (skipped tasks pass through)
                    ← this approval also grants commit/push permission (see below)
   ↓ approved
[4] Automated implementation (background agent)
   ↓
[5] QA (leader verifies each AC){% if qa_skill_ref_enabled %} + reference qa-testing skill{% endif %}
   ↓
[6] Close the ticket
```

### [1] File a ticket

Create a new GitHub Issue.

- **Command**: `{{ gh_cmd("issue create", '--title "..." --body "..." --label "status:open,' + story_label + '"') }}`
- **Labels**: `status:open` + `{{ story_label }}` + any relevant subsystem labels ({% for sl in subsystem_labels %}`{{ sl }}`{% if not loop.last %}, {% endif %}{% endfor %}).
- **Title**: short, verb-led summary.
- **Required body sections**:
  ```markdown
  ## Overview
  (1–2 sentences on what to achieve)

  ## Background
  (Why this task is needed, related issues, trigger{% if openspec_enabled %}, related OpenSpec proposal ID if any{% endif %})

  ## Next Action
  Owner: leader / agent / user
  Action: (what to do next, 1–2 lines)
  ```

AC may be undefined at this stage (it is set in the next phase).

### [2] Refinement (Brainstorming → AC)

Refinement runs in **two phases**:

#### [2a] Brainstorming — align direction with the user

**Required for important / complex tasks.** Trivial fixes may skip.

| Required when… | Can skip when… |
|---------------|---------------|
| Creating a new skill or agent | Trivial bug fix (within one function) |
| Estimated effort ≥ 30 min | Doc / comment edits |
| Spans multiple files or components | Refactor that follows an existing pattern |
| Introduces a new capability | Renames, typos |
| Impacts a running service | Dependency version bumps only |
| Changes hardware behavior (firmware reflash, wiring) | Adding tests or logs only |

**Procedure:**

1. Explore the design space creatively (invoke `[[superpowers:brainstorming]]` if available).
2. Append the **5-section structured template** below to the issue body.
3. Compress unknowns into **1–3 questions max** — avoid drip-feeding.
4. Always present each question with **multiple concrete options (2–4)** — see "Options principle" below.
5. Once aligned, finalize the sections.

#### Options principle

Brainstorming questions must **always offer 2–4 concrete options**. Use a form similar to `AskUserQuestion`: each option has a `label` (short headline) and a `description` (trade-off).

**Why:**
- Open-ended questions ("how do you want to implement this?") push the design space back to the user and increase their cognitive load.
- Options make the leader's design proposals visible — the user just accepts or rejects.
- If you have a recommendation, place it first and append "(recommended)" to its label.

**Good example:**

> Q: What I2C polling interval?
> - 10 ms (recommended) — good balance of latency and WDT headroom
> - 5 ms — higher responsiveness, more CPU
> - 20 ms — lower load, slight peripheral delay
> - Event-driven — large refactor, out of scope this time

**Bad example:**

> Q: How many ms?
> (forces the user to pick a number; trade-offs are invisible)

**Exceptions:**
- For free-form numeric or date values where options are hard to enumerate, present 3–4 representative options plus a "free input" fallback.
- If the user explicitly says "you decide" or "your call", do not ask — the leader picks the best option and proceeds.

**5-section structured template:**

```markdown
## Agreed design (brainstorming result)

### 1. User Story
As a [actor, e.g. {% for actor in user_story_actors %}{{ actor }}{% if not loop.last %} / {% endif %}{% endfor %}],
I want [what to achieve],
so that [value gained / problem solved].

### 2. Goals & Non-Goals
**Goals**:
- (goal 1)
- (goal 2)

**Non-Goals** (explicitly out of scope this time):
- (item)

### 3. Approach comparison
| Option | Outline | Pros | Cons |
|--------|---------|------|------|
| A | ... | ... | ... |
| B | ... | ... | ... |

**Chosen**: B
**Why**: (why B over A)

### 4. Edge Cases & Failure Modes
- (edge case 1 and behavior)
- (fallback behavior, recovery, etc.)

### 5. AC candidates
AC candidates derived from the alignment (will be finalized in [2b]):
- (...)
```

**User Story examples:**

Bad:
> "Save encoder settings"
> (Who? What problem does it solve?)

Good:
> As a Rover operator, I want EncoderDriver4ch settings persisted in ATmega EEPROM, so that channel direction/scale survives unintended WDT resets and I don't have to reconfigure mid-run.

#### [2b] Write Acceptance Criteria

Take the "AC candidates" from brainstorming and detail them down to the level of verification commands. See "AC perspectives" below for the checklist of viewpoints.

Update the issue body:
```markdown
## Acceptance Criteria

- [ ] (concrete done-condition 1)
  - Verify: (command or procedure)
- [ ] (concrete done-condition 2)
  - Verify: (...)
```

### [3] AC Gate check

The leader (or the assigned agent) self-checks the AC. **All items must pass — otherwise return to [2].**

| Gate item | Check |
|-----------|-------|
| Brainstorming complete | For important / complex tasks, the [2a] 5 sections (User Story / Goals & Non-Goals / Approach comparison / Edge Cases / AC candidates) are present in the issue body |
| Specificity | No vague phrasing like "works", "supports", "improves" |
| Verifiability | Each item is objectively checkable by a human or a command |
| Coverage | No gaps versus the stated goal |
| Verification means | Test / command / procedure is included for each item |
| Impact scope | Service restart / regression check is covered (if an existing service is modified) |
| Failure paths | Edge cases / error behavior are addressed (when relevant) |
| Hardware verification | If firmware changes, post-flash verification is included ({% for ex in hardware_verification_examples %}{{ ex }}{% if not loop.last %}, {% endif %}{% endfor %}) |

If the gate passes, decide the next step:

- **Task with brainstorming** → go to [3.5] User approval
- **Task that skipped brainstorming** → go directly to [4] Automated implementation; set `status:in-progress` and post a start marker

### [3.5] User approval (brainstorming tasks only)

For tasks where AC was set via interactive brainstorming, **always obtain explicit user approval before starting implementation**.

**Important**: The project's "do not auto-commit unless explicitly told" rule is **overridden** by this [3.5] approval. The approval grants "permission to start implementation **and** to commit/push at [6]". Unless explicitly opted out at approval time, the workflow may proceed to commit & push at [6] automatically.

**Procedure:**

1. Present a summary of the AC and the implementation plan.
2. Ask for approval with options (state explicitly that approval covers commit/push):
   - "Approve — implement & auto commit/push at [6]" (recommended)
   - "Approve — implement, but I will review the commit manually"
   - "Modify AC" (return to [2b])
   - "Restart brainstorming" (return to [2a])
   - "Hold / later"
3. On "Approve", flip the label to `status:in-progress`, post a start marker, and proceed to [4].
4. **Do not start implementation without approval.**
{% if notification_enabled %}
**Exception**: If the user has previously said "no need to re-approve" or "go ahead automatically", you may skip approval (log that fact in the issue).
{% endif %}

### [4] Automated implementation

Launch a background agent (`general-purpose` etc.). Include in the agent brief:

- Issue number (`{{ repo_slug }}#NNN`)
- All AC items
- Constraints (do not push, do not touch unrelated files, do not break existing tests, etc.)
- Comment format on completion
{% if notification_enabled %}- Pushover notification command (if applicable)
{% endif %}- Safe hardware-handling steps (when applicable; targets: {% for t in hardware_safety_targets %}{{ t }}{% if not loop.last %}, {% endif %}{% endfor %})

The agent must post a result comment on the issue when it finishes (ending with `<!-- leader-bot -->` or the agent's identifier).

### [5] QA (AC verification)

When the agent reports completion, **the leader itself** verifies each AC item.{% if qa_skill_ref_enabled %} Project-specific verification perspectives live in the `qa-testing` skill — consult it for firmware / I2C / WDT / encoder checklists.{% endif %}

| Verification means | Example |
|--------------------|---------|
{% for qv in qa_verification_methods -%}
| {{ qv.method }} | {{ qv.example }} |
{% endfor %}
Record per-AC results as a table on the issue:

```markdown
## QA results
| AC | Result | Verification |
|----|--------|--------------|
| ... | ✅ | ... |
<!-- leader-bot -->
```

**If any item is ❌**:
- If the AC was insufficient, return to [2] Refinement.
- If the implementation is buggy, send the agent back to [4] with a fix task.

### [6] Close the ticket

Once all AC are ✅ (and [3.5] approval covered commit/push):

1. **Diff review**: run `{{ remote_exec_prefix }}git diff` to confirm the final diff matches intent.
2. **Commit**: one or a few commits per issue.
   - Commit messages in English, subject + body, **include the issue number**.
   - Example: `Fix #NNN: <summary>`
3. **Direct push to `{{ push_branch }}`** (no PR workflow):
   - `{{ remote_exec_prefix }}git push origin {{ push_branch }}`
4. **Update the issue**:
   - `{{ gh_cmd("issue edit", "<num> --add-label status:done --remove-label status:in-progress") }}`
   - Post a result comment (must end with `<!-- leader-bot -->`)
   - `{{ gh_cmd("issue close", "<num>") }}`
{% if notification_enabled %}5. **Pushover notification** (if available): `~/butler/scripts/notify.sh "✓ {{ project_name }} #N <title>" "<summary>"`
{% endif %}

---

## AC perspectives

When writing AC, sweep through the following viewpoints. **You do not need every viewpoint to apply**, but do not skip any viewpoint that does apply.

### 1. Functional
- [ ] The main use case works end-to-end
- [ ] I/O contract (type, format, range) is satisfied
- [ ] Existing functionality is preserved (no breaking changes)

### 2. Behavior / Performance
- [ ] Latency / processing time is within budget
- [ ] Memory / storage usage is within limits
{% for b in ac_hardware_specific_bullets -%}
- [ ] {{ b }}
{% endfor %}

### 3. Error / Edge cases
- [ ] Expected error cases behave gracefully (no crash, logged)
- [ ] Behavior is defined for empty / invalid / timed-out inputs
- [ ] Existing failure modes are not regressed

### 4. Observability / Operations
- [ ] Necessary information is logged
- [ ] Failures are surfaced to the user (GitHub comment{% if notification_enabled %}, Pushover{% endif %}, etc.)
- [ ] Configuration changes (if any) are documented

### 5. Verification means
- [ ] Each AC item states **how to verify it**
- [ ] Verification commands are concrete (copy-pasteable)
- [ ] Expected output / state is stated

### 6. Documentation (when applicable)
- [ ] CLAUDE.md / SKILL.md / agent definitions are updated as needed
- [ ] Paths to related skills / scripts are correct
{% if openspec_enabled %}- [ ] OpenSpec proposal `## Status` is updated (if applicable)
{% endif %}

### Good vs bad AC examples

Bad:
```
- [ ] Fix the bug
- [ ] Improve it
- [ ] Make performance better
```

Good:
```
- [ ] `ssh pi4 hostname` returns `pi4` without prompting for a password
- [ ] `~/.ssh/config` contains a `Host pi4` entry with HostName/User/IdentityFile set
- [ ] `python3 raspi_test_PiHAT.py --duration 180` keeps reg19=0 and reg22=0 for 3 minutes
```

---

## Commit conventions

| Item | Policy |
|------|--------|
| Granularity | One issue = one (or a few) commits |
| Message | English, subject + body, includes `#N` |
| Push | Direct push to `{{ push_branch }}` (no PR workflow) |
| Approval gate | **[3.5] user approval doubles as commit/push permission** |
| Agent diff review | The leader always runs `git diff` before committing |
| On failure | Do not amend existing commits — create a new commit |
| Exception | If the user said "I will commit myself" at approval time, stop just before commit in [6] and present the diff |

### Commit message example

```
Fix #234: Persist encoder settings in non-volatile storage

Settings currently live only in RAM and are wiped on unintended resets,
forcing manual reconfiguration mid-run. Persist them with a magic byte
for invalidation and reload on boot.

Verified: settings survive 5 forced resets.
```

---

## Related resources

{% for r in related_resources -%}
- {{ r.name }}: {{ r.ref }}
{% endfor -%}
