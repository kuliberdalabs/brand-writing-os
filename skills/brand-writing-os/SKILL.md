---
name: brand-writing-os
description: Draft, edit, and audit evidence-backed brand writing using a client voice profile, approved claims ledger, source pack, and channel brief. Use for blog articles, thought leadership, newsletters, landing pages, case studies, social posts, email copy, or batch editorial work where the output must sound like a specific brand without inventing facts, quotes, prices, customer stories, or lived experience.
---

# Brand Writing OS

Produce publishable brand copy through one controlled path:

`brief + sources + brand profile + claims ledger -> draft -> voice edit -> evidence audit -> final`

## Protect the three boundaries

1. **Evidence:** Use a number, quote, result, client name, price, date, credential, or lived detail only when it appears in an approved source or claims ledger. Never create texture by inventing experience.
2. **Brand:** Use only the active client's profile and examples. Never borrow another person, company, or hidden operator persona.
3. **Authority:** Do not create or change commercial promises, legal positions, prices, guarantees, or public commitments. Flag missing decisions.

Treat fluent prose as unverified until the evidence audit passes.

## Gather the minimum inputs

Find or request:

- the deliverable and channel;
- the reader and desired action;
- a current brand profile;
- approved source material;
- a claims ledger when the copy contains proof, prices, quotes, or results;
- constraints such as length, deadline, CTA, SEO phrase, or publication format.

Use a neutral voice and label the gap if a profile is unavailable. Do not infer a founder's personal voice from a few generic prompts.

Read [profile-and-onboarding.md](references/profile-and-onboarding.md) when creating or updating a client profile. Read [sources-and-claims.md](references/sources-and-claims.md) whenever the task contains factual or commercial claims. Read [channel-patterns.md](references/channel-patterns.md) only for the requested channel. Read [editorial-rubric.md](references/editorial-rubric.md) before the final audit. Use [examples.md](references/examples.md) when the distinction between human detail and fabricated detail is unclear.

For Polish copy, also read [polish-language-pack.md](references/polish-language-pack.md) before the human edit. Its phrase list is a review aid; the client's profile and source evidence still govern the final wording.

## Execute the workflow

### 1. Freeze the brief

Write a compact internal brief with one reader, one main point, one desired action, source paths, and constraints. Resolve reversible ambiguity. Stop only when a missing business decision would materially change the output.

### 2. Build an evidence map

List every externally checkable claim the piece may need. Attach each claim to a source or an approved ledger entry. Separate:

- verified fact;
- attributed opinion;
- reasonable inference, explicitly framed as inference;
- unsupported claim, which must be removed or returned as a question.

Do not treat previous marketing copy as proof unless the ledger marks it approved and current.

### 3. Draft for meaning

Choose one controlling idea. Lead with the most useful fact, tension, observation, or outcome available in the evidence. Let the material determine the structure. Prefer concrete nouns and active verbs. Explain technical terms at the reader's altitude.

Do not optimize voice sentence by sentence while the argument is still unstable.

### 4. Apply the brand register

Use the profile's perspective, formality, vocabulary, rhythm, boundaries, and CTA policy. Preserve the writer's strongest natural lines. Apply house-style prohibitions only when the profile names them; do not impose universal punctuation bans or generic internet banlists.

For a batch, compare the openings, paragraph shapes, transitions, examples, and endings side by side. Recut repeated grammatical molds.

### 5. Run the human edit

Perform three ordered edits:

1. **Subtract:** remove throat clearing, inflated claims, vague abstractions, corporate filler, redundant summaries, and fake emphasis.
2. **Reshape:** break repeated sentence molds, uniform paragraph blocks, automatic list-of-three structures, mirrored contrast formulas, and recap endings when they do not serve the material.
3. **Restore voice:** vary cadence, use the profile's real vocabulary, and retain sourced details that make the text recognizable. Add no fact, anecdote, quote, or sensory detail during this pass.

Do not make clean prose artificially quirky. Correctness and trust outrank visible personality.

### 6. Audit before delivery

Use one combined gate for routine copy:

- trace every factual and commercial claim;
- confirm numbers, quotes, names, prices, and dates against sources;
- check brand voice and persona boundaries;
- check that the argument answers the brief;
- scan for placeholders and profile-specific forbidden patterns;
- confirm the CTA asks only for an approved action.

For a high-risk page or a batch, split the gate into two independent passes when possible:

- **Evidence pass:** claims, provenance, currency, omissions, and misleading implications.
- **Editorial pass:** voice, clarity, structure, batch repetition, and channel fit.

Do not let an editorial pass repair factual uncertainty by rewriting it more confidently.

Run the deterministic scanner as a supplement, never as proof of factual correctness:

```bash
python3 scripts/audit_copy.py draft.md \
  --profile path/to/brand-profile.json \
  --claims path/to/claims-ledger.json \
  --source path/to/source.md
```

For Polish drafts, add `--language pl` to flag common editorial tells as warnings.

### 7. Deliver with a short receipt

Return:

- the final copy;
- the sources used or their local paths;
- unresolved claims or decisions;
- audit status: `pass`, `pass with warnings`, or `blocked`.

Do not publish, send, or mutate a live account unless the current user explicitly authorizes that action and target.
