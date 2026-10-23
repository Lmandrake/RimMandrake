<!-- version: opus_first_pass@v1-V3own -->
# Task: first-pass review (you are the first reviewer)

Read every image file listed under "Images" with your Read tool — all of them, at full resolution — before
answering. Then return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/opus@v1",
  "subject": "<defName from the card>",
  "observed": {"<image file>": "<what you see, in your own words, before comparing with the description>"},
  "nearest_earth_animal": "<one word, or null for plants/machines/canon>",
  "owner_would": "keep|keep_with_note|redo",
  "owner_note": "<the note you expect him to write, or null>",
  "checklist": {"<ITEM_ID>": {"status": "ok|fail|unreadable|n/a", "seen": "<what in the picture decided it>"}},
  "findings": [
    {"code": "<reason code from the card>", "where": "<image/facing>", "seen": "<what you saw>",
     "quote": "<the rule it breaks, quoted>", "confidence": 0.0, "model_severity": "blocking|polish",
     "fix": "<one positive sentence for the generator>"}
  ],
  "overall": "good|weak|really_bad",
  "needs_call_why": "<null, or why a second reviewer should look>",
  "proposals": []
}

- `checklist` has one entry for EVERY item listed on the card, keyed by its ID.
- Every checklist item you answer `fail` also appears as a finding with that item's code.
- `overall` follows `owner_would`: `good` for keep / keep_with_note, `really_bad` for redo, `weak` only
  when you cannot predict him.
- `confidence` is how sure you are the problem is REAL (not how bad it is).
