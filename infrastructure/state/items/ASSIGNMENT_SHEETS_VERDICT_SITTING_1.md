# ASSIGNMENT_SHEETS_VERDICT_SITTING_1 — the owner's override pass on the landed assignment

The "review after" half of BIOME_FAUNA_ASSIGNMENT_SITTING_1's land-now-review-after
ruling. The two sheets are built, prefilled with every landed call, committed at
`1bae4258`:

- `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\fauna_assignment_register.html`
  — 372 rows / 26 groups; 54 contested up top (Aerofleet/Fumerider, Mynock two-home,
  Beldon, dryads, Blurrg/Reek/Dewback flags, Muffalo homeless, 23 deliberately-open
  claims).
- `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\flora_assignment_register.html`
  — 313 rows; includes the 118-row NEW-ART/DEF ledger (commission / defer / drop —
  these verdicts CREATE the art queue).

## spec
Serve with `python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py
--sheet <sheet> --decisions <sheet-stem>.decisions.json` (sidecar owns the file). The
owner reviews; contested group first is the highest-value 20 minutes; the other ~300
rows are bulk-agreeable per group.

## verify
- `serve_sheet.py --decisions <file> --status` shows `touchedBySheet: true` — 🔴 a
  byte-identical prefill is NOT a review (the consumer refuses it).
- Overrides applied via `design/Jawa/worldbuilding/review/apply_assignment_verdicts.py`
  (report first, `--apply` writes rosters), then `_validate.py --cross` green, then the
  regeneration commands it prints (cast, patches, flora) rerun and committed.
- Overrides read as a GROUP before acting (the skill's rule) — eight scattered
  disagreements may be one rule the sheets didn't know.
- Freeze both decisions files when he says done.

## traps
- ⚠️ Sheet row-ids for confidence/new_defs entries are POSITIONAL (`c:`/`nd:` +
  index): if any roster's arrays shift before the owner reviews, regenerate the
  sheets first or verdicts land on the wrong entry (the applier errors on
  out-of-range, but an in-range shift is silent).
- A `move` verdict's note must name the target; a kept `purge:` row must name the
  defNames to restore — the applier refuses the whole apply otherwise, nothing
  partial is written.

## click-test PASSED 2026-09-09 (headless Linux Chrome in WSL)
Fauna sheet: decision button, note, and 54-row bulk-apply all fired — sidecar wrote
(savedBy/writeCount), header followed, reload agreed with the file; decisions file
restored byte-exact after the test (SHA-verified, git clean). Flora sheet loaded with
zero console errors. Sheets are READY to serve.
⚠️ Incident logged: the test agent force-killed the owner's Windows Chrome processes
chasing a dead CDP route (twice) before switching to Linux Chrome — his open browser
windows were closed ~this hour. Lesson filed to LESSONS_INBOX.
