# Brand Writing OS

Evidence-first brand writing for AI agents.

Brand Writing OS is a portable Agent Skill that keeps brand voice and factual
claims in the same publishing workflow. It helps an agent draft, edit, and
audit copy without inventing numbers, quotes, prices, customer stories, or
personal experience.

Most brand-voice prompts answer only: "How should this sound?" Brand Writing
OS also asks: "What is this allowed to claim, and where is the evidence?"

## What it includes

- a compact workflow from brief and sources to an audited final draft;
- a private brand profile for voice, vocabulary, boundaries, and channel rules;
- a claims ledger that links approved proof to its underlying evidence;
- channel guidance for articles, newsletters, landing pages, case studies,
  email, and social posts;
- a dependency-free scanner for mechanical claim and editorial risks;
- a Polish language pack with editorial guidance and optional scanner warnings;
- an anonymous, reproducible before/after demo.

The core is an Agent Skill, not an npm library or hosted service. The
`package.json` is only a task runner for validation and tests.

## Install

Requirements:

- Node.js 22.20 or newer for `skills@1.5.19`;
- Python 3.10 or newer for the deterministic scanner.

Run from the project where the skill should be available:

```bash
DO_NOT_TRACK=1 npx --yes skills@1.5.19 add \
  https://github.com/kuliberdalabs/brand-writing-os/tree/main \
  --skill brand-writing-os \
  -a codex -a claude-code -y
```

## Quick start

Copy the public templates into a private project directory:

```bash
mkdir -p .brand-writing-os
cp .agents/skills/brand-writing-os/assets/templates/brand-profile.example.json \
  .brand-writing-os/brand-profile.json
cp .agents/skills/brand-writing-os/assets/templates/claims-ledger.example.json \
  .brand-writing-os/claims-ledger.json
cp .agents/skills/brand-writing-os/assets/templates/article-brief.example.md \
  .brand-writing-os/article-brief.md
```

Add `.brand-writing-os/` to the client project's ignore rules when it contains
confidential material. Keep source files such as approved transcripts, product
data, or pilot results in the client's private workspace.

Then ask the agent:

```text
Use $brand-writing-os with .brand-writing-os/brand-profile.json,
.brand-writing-os/claims-ledger.json, .brand-writing-os/article-brief.md,
and the approved files in sources/ to draft and audit the article.
```

The skill returns the copy, sources used, unresolved decisions, and one of
three audit states: `pass`, `pass with warnings`, or `blocked`.

## Polish language pack in 0.2.0

For Polish copy, the skill loads
[`polish-language-pack.md`](skills/brand-writing-os/references/polish-language-pack.md)
for phrase, rhythm, and structure review. Its examples are explicitly
illustrative. The pack keeps evidence and client voice rules from the core
workflow.

To include built-in Polish phrase checks in a direct scan, add `--language pl`:

```bash
python3 .agents/skills/brand-writing-os/scripts/audit_copy.py draft.md \
  --language pl --strict
```

These checks emit `polish-tell` warnings. Review each match in context; the
scanner does not rewrite the draft or decide whether a phrase is appropriate.
Without `--language pl`, existing scans keep their previous behavior.

## Evidence workflow

```text
brief + approved sources + brand profile + claims ledger
                         |
                         v
draft -> voice edit -> evidence audit -> final copy + audit receipt
```

The brand profile controls register and boundaries. The claims ledger records
which proof is approved, its source, its scope, and any restrictions. The
ledger is an allowlist, not a replacement for evidence.

## Reproducible before/after demo

Run:

```bash
npm run demo
```

The unsafe draft in `demo/unsafe-draft.md` claims `60%`, `99%`, and includes a
quote that does not appear in its source. The scanner must block it with
`unverified-number` and `unverified-quote`. The corrected draft preserves only
the four-week pilot result supported by `demo/source.md` and must pass in
strict mode.

Expected summary:

```text
UNSAFE: BLOCKED (unverified-number, unverified-quote)
CORRECTED: PASS
DEMO: PASS
```

## Run the scanner directly

```bash
python3 .agents/skills/brand-writing-os/scripts/audit_copy.py draft.md \
  --profile .brand-writing-os/brand-profile.json \
  --claims .brand-writing-os/claims-ledger.json \
  --source sources/interview.md \
  --channel blog \
  --strict
```

The scanner deterministically checks configured phrases and boundaries,
placeholders, numeric and quotation provenance, evidence file availability,
word ranges, repeated paragraph shapes, and similar batch openings.
With `--language pl`, it also flags selected Polish editorial tells.

It does **not** prove semantic accuracy, establish legal or regulatory
compliance, decide whether an inference is fair, or determine whether prose
truly sounds like a person. The agent must still perform the evidence and
editorial review described in `SKILL.md`. Human approval remains appropriate
for high-risk or externally published work.

## Private Brand Packs

The OSS repository provides the engine and anonymous templates. A real Brand
Pack belongs in the client's private workspace and can contain:

- accepted writing or speaking samples;
- the configured brand profile;
- claims and their evidence;
- current offers, prices, credentials, and CTA rules;
- client-specific evaluations and approval history.

Do not contribute Brand Packs, client evidence, personal data, or confidential
voice samples to this public repository.

## Professional implementation

The OSS core is self-service. Kuliberda Labs can prepare a private Brand Pack,
configure the claims and evidence ledger and channels, run evaluations, and
fit the workflow to a team. Learn more at [kuliberda.ai](https://kuliberda.ai).

## Validate the repository

```bash
npm run check
```

This runs the portable structure validator, scanner regression suite, and
public demo. The skill folder can also be checked with `quick_validate.py`
from OpenAI's `skill-creator` skill.

## License

Brand Writing OS is licensed under the [MIT License](LICENSE). Third-party
attributions are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
The MIT license covers this public repository; it does not make separately
held client data or private Brand Packs part of the project.
