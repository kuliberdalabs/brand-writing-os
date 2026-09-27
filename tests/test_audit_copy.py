from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "brand-writing-os" / "scripts" / "audit_copy.py"
PROFILE_TEMPLATE = ROOT / "skills" / "brand-writing-os" / "assets" / "templates" / "brand-profile.example.json"
CLAIMS_TEMPLATE = ROOT / "skills" / "brand-writing-os" / "assets" / "templates" / "claims-ledger.example.json"


class AuditCopyTests(unittest.TestCase):
    def run_audit(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_supported_numbers_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            source = root / "source.md"
            claims = root / "claims.json"
            draft.write_text(
                "W pilocie średni czas obsługi spadł z 18 do 11 minut.\n",
                encoding="utf-8",
            )
            source.write_text(
                "Średni czas ręcznej obsługi spadł z 18 do 11 minut.\n",
                encoding="utf-8",
            )
            claims_payload = json.loads(CLAIMS_TEMPLATE.read_text(encoding="utf-8"))
            claims_payload["approved_claims"][0]["evidence"] = "source.md"
            claims_payload["approved_claims"][0]["allowed_numbers"] = ["18", "11 minut"]
            claims.write_text(json.dumps(claims_payload), encoding="utf-8")
            result = self.run_audit(
                str(draft),
                "--profile",
                str(PROFILE_TEMPLATE),
                "--claims",
                str(claims),
                "--source",
                str(source),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)

    def test_invented_claims_and_profile_breach_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            source = root / "source.md"
            draft.write_text(
                "TODO: Dodaj dowód. To rewolucyjne rozwiązanie oszczędza 40 godzin. "
                "Klient powiedział: „Nie wyobrażam sobie powrotu”.\n",
                encoding="utf-8",
            )
            source.write_text("Pilot dotyczył obsługi zgłoszeń.\n", encoding="utf-8")
            result = self.run_audit(
                str(draft),
                "--profile",
                str(PROFILE_TEMPLATE),
                "--source",
                str(source),
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertTrue(
                {"placeholder", "forbidden-phrase", "unverified-number", "unverified-quote"}.issubset(codes)
            )

    def test_warning_becomes_failure_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("Wynik wzrósł o 25 procent.\n", encoding="utf-8")
            normal = self.run_audit(str(draft))
            strict = self.run_audit(str(draft), "--strict")
            self.assertEqual(normal.returncode, 0)
            self.assertEqual(strict.returncode, 1)
            self.assertIn("unverified-number", normal.stdout)

    def test_polish_pack_reports_tells_with_correct_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text(
                "Nagłówek.\nW DZISIEJSZYCH CZASACH oferujemy kompleksowe rozwiązania.\n"
                "To dopiero początek.\n",
                encoding="utf-8",
            )
            result = self.run_audit(str(draft), "--language", "pl", "--format", "json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            tells = [issue for issue in payload["issues"] if issue["code"] == "polish-tell"]
            self.assertEqual([issue["line"] for issue in tells], [2, 2, 3])
            self.assertTrue(all(issue["level"] == "warning" for issue in tells))

    def test_polish_pack_is_opt_in_and_strict_can_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("Warto zauważyć, że terminarz jest gotowy.\n", encoding="utf-8")
            default = self.run_audit(str(draft))
            polish = self.run_audit(str(draft), "--language", "pl", "--strict")
            self.assertEqual(default.returncode, 0, default.stdout + default.stderr)
            self.assertNotIn("polish-tell", default.stdout)
            self.assertEqual(polish.returncode, 1)
            self.assertIn("polish-tell", polish.stdout)

    def test_polish_pack_does_not_flag_clean_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text(
                "Recepcja zapisuje wizyty w terminarzu. Wieczorem sprawdza jutrzejszy grafik.\n",
                encoding="utf-8",
            )
            result = self.run_audit(str(draft), "--language", "pl", "--strict")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_decimal_does_not_approve_a_different_whole_number(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            source = root / "source.md"
            draft.write_text("Proces trwał 15 h.\n", encoding="utf-8")
            source.write_text("Proces trwał 1.5 h.\n", encoding="utf-8")
            result = self.run_audit(str(draft), "--source", str(source))
            self.assertEqual(result.returncode, 1)
            self.assertIn("unverified-number", result.stdout)

    def test_batch_flags_repeated_opening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "one.md"
            second = root / "two.md"
            first.write_text("Zacznij od procesu, który blokuje zespół.\n\nDalszy tekst.\n", encoding="utf-8")
            second.write_text("Zacznij od procesu, który blokuje sprzedaż.\n\nInny tekst.\n", encoding="utf-8")
            result = self.run_audit(str(first), str(second), "--format", "json")
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertIn("similar-openers", {issue["code"] for issue in payload["issues"]})

    def test_invalid_profile_regex_is_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            profile = root / "profile.json"
            draft.write_text("Tekst.\n", encoding="utf-8")
            profile.write_text(
                json.dumps({"voice": {"forbidden_regex": ["("]}}),
                encoding="utf-8",
            )
            result = self.run_audit(str(draft), "--profile", str(profile))
            self.assertEqual(result.returncode, 2)
            self.assertIn("CONFIG ERROR", result.stderr)

    def test_null_claim_list_is_configuration_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            claims = root / "claims.json"
            draft.write_text("Tekst.\n", encoding="utf-8")
            claims.write_text(
                json.dumps(
                    {
                        "approved_claims": [
                            {
                                "id": "broken",
                                "status": "approved",
                                "evidence": "source.md",
                                "allowed_numbers": None,
                                "allowed_quotes": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_audit(str(draft), "--claims", str(claims))
            self.assertEqual(result.returncode, 2)
            self.assertIn("CONFIG ERROR", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_claim_evidence_blocks_even_when_number_is_allowlisted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            claims = root / "claims.json"
            draft.write_text("Zaoszczędziliśmy 999 godzin.\n", encoding="utf-8")
            claims.write_text(
                json.dumps(
                    {
                        "approved_claims": [
                            {
                                "id": "missing-source",
                                "status": "approved",
                                "evidence": "missing.md",
                                "allowed_numbers": ["999 godzin"],
                                "allowed_quotes": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_audit(str(draft), "--claims", str(claims), "--strict")
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-evidence", result.stdout)
            self.assertIn("unverified-number", result.stdout)

    def test_readme_workspace_layout_resolves_evidence_from_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".brand-writing-os"
            sources = root / "sources"
            config.mkdir()
            sources.mkdir()
            draft = root / "draft.md"
            source = sources / "pilot-summary.md"
            claims = config / "claims-ledger.json"
            draft.write_text("Czas spadł z 18 minut do 11 minut.\n", encoding="utf-8")
            source.write_text("Czas spadł z 18 minut do 11 minut.\n", encoding="utf-8")
            claims.write_text(
                json.dumps(
                    {
                        "approved_claims": [
                            {
                                "id": "layout",
                                "status": "approved",
                                "evidence": "../sources/pilot-summary.md",
                                "statement": "Czas spadł z 18 minut do 11 minut.",
                                "allowed_numbers": ["18 minut", "11 minut"],
                                "allowed_quotes": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_audit(
                str(draft),
                "--claims",
                str(claims),
                "--source",
                str(source),
                "--strict",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
