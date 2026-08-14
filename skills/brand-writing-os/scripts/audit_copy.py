#!/usr/bin/env python3
"""Deterministic companion checks for Brand Writing OS.

The scanner catches mechanical risks. It does not replace semantic fact checking.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|TK)\b|\[(?:SOURCE|CITATION|CLAIM|VERIFY)(?::[^\]]*)?\]",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(
    r"(?<![\w])(?:\d{1,3}(?:[ .]\d{3})+|\d+)(?:[,.]\d+)?"
    r"(?:\s?(?:%|zł|PLN|EUR|USD|GBP|€|£|\$|min(?:ut(?:a|y)?)?|h|godzin(?:a|y)?|dni|dzień|tygodni(?:e)?|miesiąc(?:e|y)?|lat(?:a)?))?",
    re.IGNORECASE,
)
QUOTE_RE = re.compile(r"(?:[„“\"])([^\n\"”]{6,}?)(?:[”\"])")
URL_RE = re.compile(r"https?://\S+")
WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    file: str
    line: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan brand copy for deterministic editorial and evidence risks."
    )
    parser.add_argument("drafts", nargs="+", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--source", action="append", default=[], type=Path)
    parser.add_argument("--channel")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    return parser.parse_args()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def number_parts(value: str) -> tuple[str, str]:
    match = re.match(
        r"\s*((?:\d{1,3}(?:[ .]\d{3})+|\d+)(?:[,.]\d+)?)\s*(.*)\Z",
        value,
    )
    if not match:
        return normalize(value), ""
    numeric = match.group(1).replace(" ", "")
    if "." in numeric and "," in numeric:
        numeric = numeric.replace(".", "").replace(",", ".")
    elif "," in numeric:
        numeric = numeric.replace(",", ".")
    elif numeric.count(".") == 1 and len(numeric.rsplit(".", 1)[1]) == 3:
        numeric = numeric.replace(".", "")
    return numeric, normalize(match.group(2))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"Cannot read {path}: {error}") from error


def read_json(path: Path | None, label: str) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid {label} JSON at {path}:{error.lineno}: {error.msg}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def configured_list(mapping: dict[str, Any], key: str) -> list[str]:
    value = mapping.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Profile field '{key}' must be a list of strings")
    return value


def add_literal_issues(
    issues: list[Issue],
    text: str,
    path: Path,
    values: list[str],
    level: str,
    code: str,
) -> None:
    folded = text.casefold()
    for value in values:
        if not value:
            continue
        offset = folded.find(value.casefold())
        if offset >= 0:
            issues.append(
                Issue(level, code, str(path), line_number(text, offset), f"Matched profile value: {value!r}")
            )


def add_regex_issues(
    issues: list[Issue],
    text: str,
    path: Path,
    patterns: list[str],
    level: str,
    code: str,
) -> None:
    for pattern in patterns:
        try:
            match = re.search(pattern, text)
        except re.error as error:
            raise ValueError(f"Invalid profile regex {pattern!r}: {error}") from error
        if match:
            issues.append(
                Issue(level, code, str(path), line_number(text, match.start()), f"Matched profile regex: {pattern!r}")
            )


def add_replacement_issues(
    issues: list[Issue], text: str, path: Path, replacements: Any
) -> None:
    if replacements is None:
        return
    if not isinstance(replacements, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in replacements.items()
    ):
        raise ValueError("Profile field 'term_replacements' must map strings to strings")
    folded = text.casefold()
    for avoided, preferred in replacements.items():
        offset = folded.find(avoided.casefold())
        if offset >= 0:
            issues.append(
                Issue(
                    "warning",
                    "preferred-term",
                    str(path),
                    line_number(text, offset),
                    f"Profile prefers {preferred!r} instead of {avoided!r}",
                )
            )


def claim_string_list(entry: dict[str, Any], key: str, claim_id: str) -> list[str]:
    value = entry.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Claim {claim_id!r} field {key!r} must be a list of strings")
    return value


def active_claim_evidence(
    claims: dict[str, Any], claims_path: Path | None
) -> tuple[str, list[Issue]]:
    entries = claims.get("approved_claims", [])
    if not isinstance(entries, list):
        raise ValueError("Claims field 'approved_claims' must be a list")

    evidence_parts: list[str] = []
    issues: list[Issue] = []
    today = date.today()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Every approved claim must be a JSON object")
        claim_id = str(entry.get("id", "unnamed"))
        allowed_numbers = claim_string_list(entry, "allowed_numbers", claim_id)
        allowed_quotes = claim_string_list(entry, "allowed_quotes", claim_id)
        if entry.get("status") != "approved":
            continue
        valid_until = entry.get("valid_until")
        if valid_until:
            try:
                expiry = date.fromisoformat(valid_until)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Claim {claim_id!r} has invalid valid_until date") from error
            if expiry < today:
                issues.append(
                    Issue(
                        "warning",
                        "expired-claim",
                        str(claims_path or "claims-ledger"),
                        1,
                        f"Claim {claim_id!r} expired on {expiry.isoformat()}",
                    )
                )
                continue

        evidence_ref = entry.get("evidence")
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ValueError(f"Approved claim {claim_id!r} needs a non-empty evidence reference")

        parsed = urlparse(evidence_ref)
        local_evidence = ""
        evidence_available = False
        if parsed.scheme in {"http", "https"}:
            issues.append(
                Issue(
                    "warning",
                    "remote-evidence",
                    str(claims_path or "claims-ledger"),
                    1,
                    f"Claim {claim_id!r} uses remote evidence that this scanner did not fetch",
                )
            )
            evidence_available = True
        else:
            evidence_file = Path(evidence_ref.split("#", 1)[0])
            if not evidence_file.is_absolute() and claims_path is not None:
                evidence_file = claims_path.parent / evidence_file
            if evidence_file.is_file():
                local_evidence = read_text(evidence_file)
                evidence_parts.append(local_evidence)
                evidence_available = True
            else:
                issues.append(
                    Issue(
                        "error",
                        "missing-evidence",
                        str(claims_path or "claims-ledger"),
                        1,
                        f"Claim {claim_id!r} evidence file does not exist: {evidence_file}",
                    )
                )

        if not evidence_available:
            continue
        evidence_parts.append(str(entry.get("statement", "")))
        evidence_parts.extend(allowed_numbers)
        evidence_parts.extend(allowed_quotes)

        if local_evidence:
            local_normalized = normalize(local_evidence)
            for quote in allowed_quotes:
                if normalize(quote) not in local_normalized:
                    issues.append(
                        Issue(
                            "error",
                            "claim-evidence-mismatch",
                            str(claims_path or "claims-ledger"),
                            1,
                            f"Claim {claim_id!r} quote is absent from its evidence file",
                        )
                    )
            local_numbers = {
                number_parts(match.group(0).strip())
                for match in NUMBER_RE.finditer(local_evidence)
            }
            for allowed in allowed_numbers:
                allowed_numeric, allowed_unit = number_parts(allowed)
                supported = any(
                    allowed_numeric == evidence_numeric
                    and (
                        not allowed_unit
                        or allowed_unit == evidence_unit
                        or allowed_unit in local_normalized
                    )
                    for evidence_numeric, evidence_unit in local_numbers
                )
                if not supported:
                    issues.append(
                        Issue(
                            "warning",
                            "claim-evidence-number-mismatch",
                            str(claims_path or "claims-ledger"),
                            1,
                            f"Claim {claim_id!r} allowed number is not an exact token in its evidence: {allowed!r}",
                        )
                    )
    return "\n".join(evidence_parts), issues


def is_list_marker(text: str, start: int, token: str) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    suffix = text[start + len(token) : start + len(token) + 2]
    return not prefix.strip() and bool(re.match(r"[.)]\s", suffix))


def scan_draft(
    path: Path,
    text: str,
    profile: dict[str, Any],
    evidence: str,
    has_evidence: bool,
    channel: str | None,
) -> list[Issue]:
    issues: list[Issue] = []
    voice = profile.get("voice", {})
    boundaries = profile.get("boundaries", {})
    if voice and not isinstance(voice, dict):
        raise ValueError("Profile field 'voice' must be an object")
    if boundaries and not isinstance(boundaries, dict):
        raise ValueError("Profile field 'boundaries' must be an object")

    for match in PLACEHOLDER_RE.finditer(text):
        issues.append(
            Issue("error", "placeholder", str(path), line_number(text, match.start()), f"Unresolved marker: {match.group(0)!r}")
        )

    add_literal_issues(
        issues,
        text,
        path,
        configured_list(voice, "forbidden_phrases"),
        "error",
        "forbidden-phrase",
    )
    add_literal_issues(
        issues,
        text,
        path,
        configured_list(voice, "forbidden_characters"),
        "error",
        "forbidden-character",
    )
    add_literal_issues(
        issues,
        text,
        path,
        configured_list(boundaries, "forbidden_topics")
        + configured_list(boundaries, "forbidden_names"),
        "error",
        "persona-boundary",
    )
    add_regex_issues(
        issues,
        text,
        path,
        configured_list(voice, "forbidden_regex"),
        "error",
        "forbidden-pattern",
    )
    add_regex_issues(
        issues,
        text,
        path,
        configured_list(voice, "watch_regex"),
        "warning",
        "watch-pattern",
    )
    add_replacement_issues(issues, text, path, voice.get("term_replacements"))

    for required in configured_list(voice, "required_phrases"):
        if required.casefold() not in text.casefold():
            issues.append(Issue("warning", "missing-required-phrase", str(path), 1, f"Missing required phrase: {required!r}"))

    evidence_normalized = normalize(evidence)
    evidence_numbers = [number_parts(match.group(0).strip()) for match in NUMBER_RE.finditer(evidence)]
    masked = URL_RE.sub("", text)
    for match in NUMBER_RE.finditer(masked):
        token = match.group(0).strip()
        if is_list_marker(masked, match.start(), token):
            continue
        numeric, unit = number_parts(token)
        supported = any(
            numeric == evidence_numeric
            and (not unit or unit == evidence_unit or unit in evidence_normalized)
            for evidence_numeric, evidence_unit in evidence_numbers
        )
        if not supported:
            level = "error" if has_evidence else "warning"
            issues.append(
                Issue(level, "unverified-number", str(path), line_number(masked, match.start()), f"Number not found in supplied evidence: {token!r}")
            )

    for match in QUOTE_RE.finditer(text):
        quote = normalize(match.group(1))
        if len(quote) < 6 or quote in evidence_normalized:
            continue
        level = "error" if has_evidence else "warning"
        issues.append(
            Issue(level, "unverified-quote", str(path), line_number(text, match.start()), "Quoted text not found in supplied evidence")
        )

    channels = profile.get("channels", {})
    if channel and isinstance(channels, dict) and isinstance(channels.get(channel), dict):
        word_range = channels[channel].get("word_range")
        if isinstance(word_range, list) and len(word_range) == 2:
            word_count = len(WORD_RE.findall(text))
            minimum, maximum = word_range
            if isinstance(minimum, int) and word_count < minimum:
                issues.append(Issue("warning", "word-count", str(path), 1, f"{word_count} words; profile minimum is {minimum}"))
            if isinstance(maximum, int) and word_count > maximum:
                issues.append(Issue("warning", "word-count", str(path), 1, f"{word_count} words; profile maximum is {maximum}"))

    paragraphs = [
        len(WORD_RE.findall(block))
        for block in re.split(r"\n\s*\n", text)
        if block.strip() and not block.lstrip().startswith(("#", "- ", "* ", ">"))
    ]
    substantial = [count for count in paragraphs if count >= 12]
    if len(substantial) >= 5 and statistics.mean(substantial) >= 20:
        mean = statistics.mean(substantial)
        if mean and statistics.pstdev(substantial) / mean < 0.16:
            issues.append(Issue("warning", "uniform-paragraphs", str(path), 1, "Paragraph lengths are unusually uniform; review for a repeated template"))

    return issues


def opening(text: str) -> str:
    in_frontmatter = text.startswith("---\n")
    for raw in text.splitlines():
        line = raw.strip()
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if not line or line.startswith(("#", "```", "<!--")):
            continue
        return normalize(re.sub(r"^[>*_`\-\s]+", "", line))
    return ""


def batch_issues(drafts: list[tuple[Path, str]]) -> list[Issue]:
    issues: list[Issue] = []
    for index, (left_path, left_text) in enumerate(drafts):
        left = opening(left_text)
        if not left:
            continue
        for right_path, right_text in drafts[index + 1 :]:
            right = opening(right_text)
            if not right:
                continue
            left_words = left.split()
            right_words = right.split()
            shared_prefix = left_words[:3] == right_words[:3] and len(left_words) >= 3
            similarity = SequenceMatcher(None, left, right).ratio()
            if shared_prefix or similarity >= 0.72:
                issues.append(
                    Issue(
                        "warning",
                        "similar-openers",
                        str(right_path),
                        1,
                        f"Opening resembles {left_path} (similarity {similarity:.0%})",
                    )
                )
    return issues


def emit_text(issues: list[Issue], files: int) -> None:
    if not issues:
        print(f"PASS: {files} file(s), no deterministic issues found.")
    else:
        for issue in issues:
            print(f"{issue.level.upper()} {issue.file}:{issue.line} [{issue.code}] {issue.message}")
        errors = sum(issue.level == "error" for issue in issues)
        warnings = sum(issue.level == "warning" for issue in issues)
        print(f"SUMMARY: {files} file(s), {errors} error(s), {warnings} warning(s).")
    print("NOTE: semantic claim accuracy and brand fit still require the skill's editorial audit.")


def main() -> int:
    args = parse_args()
    try:
        profile = read_json(args.profile, "profile")
        claims = read_json(args.claims, "claims ledger")
        claim_evidence, claim_issues = active_claim_evidence(claims, args.claims)
        source_text = "\n".join(read_text(path) for path in args.source)
        evidence = "\n".join((claim_evidence, source_text))
        has_evidence = bool(args.claims or args.source)
        drafts = [(path, read_text(path)) for path in args.drafts]

        issues: list[Issue] = []
        issues.extend(claim_issues)
        for path, text in drafts:
            issues.extend(scan_draft(path, text, profile, evidence, has_evidence, args.channel))
        if len(drafts) > 1:
            issues.extend(batch_issues(drafts))
    except ValueError as error:
        print(f"CONFIG ERROR: {error}", file=sys.stderr)
        return 2

    issues.sort(key=lambda item: (item.file, item.line, item.level, item.code))
    if args.format == "json":
        print(json.dumps({"issues": [asdict(issue) for issue in issues]}, ensure_ascii=False, indent=2))
    else:
        emit_text(issues, len(drafts))

    has_error = any(issue.level == "error" for issue in issues)
    has_warning = any(issue.level == "warning" for issue in issues)
    return 1 if has_error or (args.strict and has_warning) else 0


if __name__ == "__main__":
    raise SystemExit(main())
