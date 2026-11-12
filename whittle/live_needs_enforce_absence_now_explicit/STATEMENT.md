# LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: done statement

Item title: Enforce inferred live-mods needs at the gate (derived, never written into the proof), with an explicit live-without: opt-out for proofs that intend a mod's absence
Written by wc.py setup (no model) from the ledger criteria and `infrastructure/state/items/LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT.md`; the item file's spec and verify sections are the owner's words where it has them.

- Replay: at least 17 of the 20 R1/R2 items get the right mod added before repair; zero wrong additions.
- Negative control: zero additions on the last 50 PASS proofs, after the migration's `live-without:` lines.
- One week after landing: runs failing on a mod-list cause in `runs.jsonl`, against a baseline recounted first.
