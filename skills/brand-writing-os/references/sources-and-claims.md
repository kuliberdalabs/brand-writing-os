# Sources and claims

## Source priority

Use the closest current source of truth. Prefer, in order:

1. approved contracts, product data, current pricing sources, and signed-off client records;
2. primary research, official documentation, and direct transcripts;
3. accepted internal briefs and approved case studies;
4. reputable secondary sources;
5. previous marketing copy only as a lead to verify.

Check dates and scope. A true historical price can still be a false current claim.

## Claims ledger

Use `assets/templates/claims-ledger.example.json` for repeatable proof. Each entry needs:

- a stable identifier;
- the exact proposition that has been approved;
- evidence location;
- owner and status;
- allowed numbers and quotations;
- an expiry date when the claim can become stale;
- channel or wording restrictions when necessary.

The ledger is an allowlist, not a source replacement. Keep the underlying evidence available.
Resolve local `evidence` paths relative to the claims-ledger file. For example,
if the ledger is `.brand-writing-os/claims-ledger.json` and evidence is stored
in `sources/pilot-summary.md`, write `../sources/pilot-summary.md#section`.

## Drafting rules

- Keep exact numbers exact. Do not round or combine metrics without permission.
- Attribute opinions and forecasts.
- Describe an inference as an inference.
- Do not transform correlation into causation.
- Do not broaden one customer's result into a general guarantee.
- Do not create a quote from notes, a paraphrase, or a composite customer.
- Do not add a time, place, sensory detail, or first-person experience unless it is in the source.
- Do not infer prices, statutory dates, certifications, or legal obligations from memory.

## Claim audit

For every checkable sentence, ask:

1. What exact proposition will the reader take away?
2. Which source supports that proposition?
3. Does the source support the same subject, scope, date, and strength?
4. Did editing introduce stronger certainty or causality?
5. Would the sentence remain honest if a client saw the evidence beside it?

Remove, narrow, attribute, or block anything that fails.
