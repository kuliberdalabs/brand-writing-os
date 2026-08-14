#!/usr/bin/env python3
"""Validate the portable structure without third-party dependencies."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "brand-writing-os"
SKILL_FILE = SKILL / "SKILL.md"


def fail(message: str) -> int:
    print(f"INVALID: {message}")
    return 1


def main() -> int:
    if not SKILL_FILE.is_file():
        return fail(f"missing {SKILL_FILE}")

    text = SKILL_FILE.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter:
        return fail("SKILL.md needs YAML frontmatter")

    fields = {}
    for line in frontmatter.group(1).splitlines():
        if ":" not in line:
            return fail(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"}:
        return fail("frontmatter must contain only name and description")
    if fields["name"] != SKILL.name:
        return fail("skill name must match its directory")
    if not re.fullmatch(r"[a-z0-9-]{1,63}", fields["name"]):
        return fail("skill name must use lowercase letters, digits, and hyphens")
    if len(fields["description"]) < 80:
        return fail("description is too short to trigger reliably")
    if "TODO" in text or "[TODO" in text:
        return fail("unresolved TODO in SKILL.md")

    for relative in re.findall(r"\]\((references/[^)]+)\)", text):
        if not (SKILL / relative).is_file():
            return fail(f"missing referenced file: {relative}")

    for json_file in (SKILL / "assets" / "templates").glob("*.json"):
        try:
            json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            return fail(f"invalid JSON in {json_file}: {error}")

    for script in (SKILL / "scripts").glob("*.py"):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as error:
            return fail(f"invalid Python in {script}: {error}")

    openai_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    interface: dict[str, str] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf'^  {key}: "([^"]+)"$', openai_yaml, re.MULTILINE)
        if not match:
            return fail(f"agents/openai.yaml needs a quoted {key}")
        interface[key] = match.group(1)
    if not 25 <= len(interface["short_description"]) <= 64:
        return fail("agents/openai.yaml short_description must be 25-64 characters")
    if f"${fields['name']}" not in interface["default_prompt"]:
        return fail("agents/openai.yaml default prompt must mention the skill")

    print("Skill is valid!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
