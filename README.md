# dev-leader-skill

Canonical Jinja2 templates for the **leader** and **dev-workflow** Claude skills, shared across dev projects.

This repository provides the source of truth for the `leader` and `dev-workflow` skill bodies. Individual development projects consume these templates as a git submodule, supply a project-specific `values.yaml`, and render them into their own `.claude/skills/<name>/SKILL.md`.

## Why this repo exists

Multiple dev projects (initially `tkcmada/tanecon2027` and `tkcmada/tottori-rover-2026`) historically maintained their own forks of the same `leader` / `dev-workflow` skills. Drift between the forks made every improvement a copy-paste exercise.

The templates here capture the **canonical** structure of both skills:

- Common sections (Persona, Orchestrator Constraint, Priority Heuristics, Recommendation Format, file formats, the 6-stage dev-workflow diagram, AC quality bar, etc.) live in one place.
- Project-specific differences (repo slug, branch name, ticket hierarchy, available agents, hardware verification examples, optional features such as Pushover notifications or OpenSpec integration) are abstracted into Jinja2 placeholders and `{% if %}` / `{% for %}` blocks.

## Related projects

- [`tkcmada/tanecon2027`](https://github.com/tkcmada/tanecon2027) — 種コン2027 BBM project
- [`tkcmada/tottori-rover-2026`](https://github.com/tkcmada/tottori-rover-2026) — tottori-rover-2026 project

## Layout

| Path | Purpose |
|------|---------|
| `README.md` | This file. |
| `leader.template.md` | Jinja2 template for the `leader` skill (English). |
| `dev-workflow.template.md` | Jinja2 template for the `dev-workflow` skill (English). |
| `values.schema.md` | Documentation of every placeholder: required/optional, type, meaning, example. |
| `examples/tanecon.values.yaml` | Sample values for the `tanecon2027` project. |
| `examples/tottori.values.yaml` | Sample values for the `tottori-rover-2026` project. |
| `generate.py` | Renderer script that turns a `values.yaml` into the two SKILL.md files. |
| `requirements.txt` | Python runtime dependencies (`jinja2`, `pyyaml`) used by `generate.py`. |

## How to use

The intended consumer workflow is:

1. **Add this repo as a submodule** in your project, e.g. under `.claude/skills/_shared/dev-leader-skill/`.
2. **Author a `values.yaml`** for your project, following `values.schema.md`. The `examples/` directory shows full, working values files you can copy and edit.
3. **Render the templates** with a Jinja2 renderer (provided by the `leader-generate` skill, implemented in a separate story) into `.claude/skills/leader/SKILL.md` and `.claude/skills/dev-workflow/SKILL.md`.
4. **Commit the rendered SKILL.md** files alongside the submodule pointer so the skills are usable without a render step at runtime.

The renderer (`generate.py`) ships in this repo — see "How to generate" below.

## How to generate

Install dependencies once:

```bash
pip install -r requirements.txt
```

Render the skills into your project (run from the consuming project's root, after this repo has been added as a submodule under e.g. `.claude/skills/dev-leader-skill/`):

```bash
python .claude/skills/dev-leader-skill/generate.py \
    --values .claude/skills/dev-leader-skill-values.yaml \
    --repo-root .
```

Flags:

- `--values <path>` (required): path to your project's `values.yaml`.
- `--repo-root <path>` (optional, defaults to `.`): base directory that `output_paths` are resolved against.
- `--template-dir <path>` (optional, defaults to the directory of `generate.py`): where the `.template.md` files live.

Outputs are written to the paths configured in the `output_paths` section of your `values.yaml` (see `values.schema.md`). `generate.py` runs Jinja2 with `StrictUndefined`, so any missing key in `values.yaml` will produce an explicit error instead of a silent blank.

## Conventions

- All template text, comments, and example values are in **English**.
- Placeholders use **Jinja2** syntax: `{{ var }}`, `{% if %}`, `{% for %}`, `{% macro %}`.
- Templates intentionally **omit** any `## Language` section; the consuming project decides the reply language separately.
- Templates intentionally **omit** any "derived from X" history notes; project-specific provenance belongs in the consuming repo, not in the canonical template.

## License

Not specified. Treat as personal/internal until a license is added.
