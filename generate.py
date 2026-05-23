#!/usr/bin/env python3
"""Render dev-leader-skill templates from a project-specific values.yaml.

Reads a values.yaml file and renders the canonical Jinja2 templates
(``leader.template.md`` and ``dev-workflow.template.md``) into the output
paths declared by the ``output_paths`` section of the values file.

Usage:
    python generate.py --values <path/to/values.yaml> [--repo-root <dir>] \
                       [--template-dir <dir>]

Exit code is non-zero on any failure (missing required keys, undefined
Jinja2 variables, IO errors, etc.).
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError


TEMPLATES = {
    # template filename -> key under values["output_paths"]
    "leader.template.md": "leader",
    "dev-workflow.template.md": "dev_workflow",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render dev-leader-skill templates from values.yaml.",
    )
    parser.add_argument(
        "--values",
        required=True,
        help="Path to the project's values.yaml file.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Base directory that output_paths are resolved against (default: cwd).",
    )
    parser.add_argument(
        "--template-dir",
        default=None,
        help="Directory containing the .template.md files "
        "(default: directory of this script).",
    )
    return parser.parse_args()


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_values(values_path: pathlib.Path) -> dict:
    if not values_path.is_file():
        die(f"values file not found: {values_path}")
    try:
        with values_path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        die(f"failed to parse YAML {values_path}: {exc}")
    if not isinstance(data, dict):
        die(f"values file did not contain a mapping at the top level: {values_path}")
    return data


def main() -> None:
    args = parse_args()

    script_dir = pathlib.Path(__file__).resolve().parent
    template_dir = (
        pathlib.Path(args.template_dir).resolve()
        if args.template_dir
        else script_dir
    )
    repo_root = pathlib.Path(args.repo_root).resolve()
    values_path = pathlib.Path(args.values).resolve()

    values = load_values(values_path)

    output_paths = values.get("output_paths")
    if not isinstance(output_paths, dict):
        die(
            "values.yaml is missing the required 'output_paths' mapping "
            "(expected keys: 'leader', 'dev_workflow')."
        )

    # Resolve every output up front so we can fail fast on missing entries.
    resolved: dict[str, pathlib.Path] = {}
    for tmpl_name, key in TEMPLATES.items():
        rel = output_paths.get(key)
        if not rel or not isinstance(rel, str):
            die(
                f"output_paths.{key} is missing or not a string "
                f"(required for template {tmpl_name})."
            )
        resolved[tmpl_name] = repo_root / rel

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    for tmpl_name, out_path in resolved.items():
        try:
            template = env.get_template(tmpl_name)
        except Exception as exc:  # TemplateNotFound, TemplateSyntaxError, ...
            die(f"failed to load template {tmpl_name} from {template_dir}: {exc}")

        try:
            rendered = template.render(**values)
        except UndefinedError as exc:
            die(
                f"undefined variable while rendering {tmpl_name}: {exc}. "
                "Add the missing key to values.yaml (see values.schema.md)."
            )

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            die(f"failed to write {out_path}: {exc}")

        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
