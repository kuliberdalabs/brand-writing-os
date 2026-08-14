#!/usr/bin/env python3
"""Run the public Brand Writing OS before/after demonstration."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
SCANNER = ROOT / "skills" / "brand-writing-os" / "scripts" / "audit_copy.py"


def audit(draft: str, *, strict: bool = False) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCANNER),
        str(DEMO / draft),
        "--profile",
        str(DEMO / "profile.json"),
        "--claims",
        str(DEMO / "claims-ledger.json"),
        "--source",
        str(DEMO / "source.md"),
        "--format",
        "json",
    ]
    if strict:
        command.append("--strict")
    return subprocess.run(command, text=True, capture_output=True, check=False)


def issue_codes(result: subprocess.CompletedProcess[str]) -> set[str]:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Scanner did not return JSON: {result.stdout or result.stderr}") from error
    return {issue["code"] for issue in payload.get("issues", [])}


def main() -> int:
    unsafe = audit("unsafe-draft.md")
    unsafe_codes = issue_codes(unsafe)
    expected = {"unverified-number", "unverified-quote"}
    if unsafe.returncode != 1 or not expected.issubset(unsafe_codes):
        print(
            "UNSAFE: unexpected result "
            f"(exit={unsafe.returncode}, codes={', '.join(sorted(unsafe_codes)) or 'none'})",
            file=sys.stderr,
        )
        return 1
    print(f"UNSAFE: BLOCKED ({', '.join(sorted(expected))})")

    corrected = audit("corrected-draft.md", strict=True)
    corrected_codes = issue_codes(corrected)
    if corrected.returncode != 0 or corrected_codes:
        print(
            "CORRECTED: unexpected result "
            f"(exit={corrected.returncode}, codes={', '.join(sorted(corrected_codes)) or 'none'})",
            file=sys.stderr,
        )
        return 1
    print("CORRECTED: PASS")
    print("DEMO: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
