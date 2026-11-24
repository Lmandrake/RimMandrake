<!-- version: opus_first_pass@v3 -->
# Task: first-pass review (you are the first reviewer)

Before you answer, read every image file listed under "Images" with your Read tool. Read all of them at full
resolution. Then return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/opus@v1",
  "subject": "<defName from the card>",
  "observed": {"<image file>": "<what you see, in your own words, before comparing with the description>"},
  "nearest_earth_animal": "<one word, or null for plants/machines/canon>",
  "checklist": {"<ITEM_ID>": {"status": "ok|fail|unreadable|n/a", "seen": "<what in the picture decided it>"}},
  "findings": [
    {"code": "<reason code from the section Reason codes>", "where": "<image/facing>", "seen": "<what you saw>",
     "quote": "<the rule it breaks, quoted>", "confidence": 0.0, "model_severity": "blocking|polish",
     "fix": "<one positive sentence for the generator>"}
  ],
  "overall": "good|weak|really_bad",
  "needs_call_why": "<null, or why a second reviewer should look>",
  "proposals": []
}

- The card is the section "The card". `nearest_earth_animal` is null for a plant, for a machine, and for a canon subject
  (its card has a section "Canon — Must show").
- `checklist` has one entry for EVERY item under "Checklist". The key of each entry is the item's ID.
- If you answer a checklist item `fail`, also write a finding. Its `code` is the reason code that the item names after
  "fails as".
- `overall` has one of three values:
  - `good` = the owner would keep the picture, perhaps with a polish note (size, more variants, a little more realism).
  - `really_bad` = the owner would redo the picture. Reasons: wrong surface on a facing, wrong animal, defining feature
    missing, reads as an Earth animal, baked backdrop, donor (art borrowed from another mod or from vanilla).
  - `weak` = you cannot tell which.
- Polish wishes are findings with a polish code, or go in `proposals`. Polish wishes do not stop `good`.
- `confidence` is the chance that the owner, looking at the picture, would name the same problem. `confidence` does not
  say how bad the problem is.
