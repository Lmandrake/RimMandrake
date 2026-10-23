<!-- version: opus_first_pass@v1-V2ver -->
# Task: first-pass review (you are the first reviewer)

Read every image file listed under "Images" with your Read tool — all of them, at full resolution — before
answering. Work in two steps, both inside the JSON:
1. `suspects`: every defect a strict art director might raise against this picture (aim for 3 to 8), each
   `{"code", "where", "claim"}`.
2. For each suspect look AGAIN at the named image and region and set `second_look`: `real` (say which pixels show
   it), `not_real` (say what shows it is fine) or `unsure`, with `evidence`. Only `real` and `unsure` suspects
   become `findings`; their `confidence` comes from the second look.

Then return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/opus@v1",
  "subject": "<defName from the card>",
  "observed": {"<image file>": "<what you see, in your own words, before comparing with the description>"},
  "nearest_earth_animal": "<one word, or null for plants/machines/canon>",
  "suspects": [{"code": "<code>", "where": "<image/region>", "claim": "<what a strict critic would say>",
                "second_look": "real|not_real|unsure", "evidence": "<what the pixels show>"}],
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
- `overall`: `good` = you would ship it as it is; `really_bad` = clearly wrong (wrong surface on a facing, wrong
  animal, defining feature missing, Earth animal, baked backdrop, donor); `weak` = anything in between, or you are
  unsure. Be honest: `good` is a high bar. If you would write "a more alien/realistic variant would suit", that
  is a finding, not a pass.
- `confidence` is how sure you are the problem is REAL (not how bad it is).
