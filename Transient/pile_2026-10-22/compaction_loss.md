# Compaction loss — BENCH session 5453bc27, auto-compacted 2026-10-23T00:21Z

Owner's question (2026-10-23 01:00Z): *"How much loss occurs when the context gets compacted? Should we
worry about this?"* This file MEASURES one compaction: what the ~10 h pre-compaction segment held that
neither the harness summary nor the disk kept.

## Method
- Segment: `compaction_check.py --extract` (1757 transcript lines, 14:36Z → 00:21Z; 200 assistant turns).
- Because the extract turned out to DROP owner words (see §2, first lesson), owner text was re-pulled from
  the raw jsonl `/home/mandrake/.claude/projects/-home-mandrake-rm-bench/5453bc27-3eb8-4e2e-b5ef-b3cc25266b27.jsonl`:
  7 typed messages (`queue-operation` content) + 12 answered AskUserQuestion results = 37 card answers, 6 write-ins.
- Compared against (a) the summary (the `## compaction summary` block), (b) disk: `OWNER.jsonl`/`BENCH.jsonl`
  ledger (~43 provenance events 14:44–23:23Z from this session), `infrastructure/state/lessons/20261022*`
  (75 files), `git log --since 2026-10-22` (280 commits), pinned `Transient/pile_2026-10-22/*`.

## 1. Owner words that exist ONLY in the transcript
**Count: 0.** Every typed owner message (7) and every card write-in (6) appears verbatim in summary §6.
All 37 card picks are on disk: 34 as `--by-card`/`--owner-said` ledger events, the day-shape picks (cap five,
small list, phone collections) in pinned `day_plan.md`, the "delete all 20" pick in `art/events/BENCH.jsonl`.

Words held by the summary but NOT on disk (they die with the next compaction or session end):
- *"Foundry also has some of the flowworks items. It's been told to prioritize them."* (15:47Z) — 0 hits on disk.
- *"Ok, I'd like you to make a deep plan now…"* (15:31Z) — only an ellipsized excerpt in `day_plan.md`.
- *"Make a subagent do web research on agent systems like Devin…"* (22:45Z) and *"Wake bench…"* (14:37Z) —
  only in the UNTRACKED `conversations/2026-10-22-1436-5453bc27.md`… which itself lacks the other four
  (§2), and partly in `harness_research/setup.md`.
- *"Are you using bridge right now?"* — trivial.
These are carried verbatim into the handoff written with this report, so they now reach disk.

## 2. Lessons / traps learned but not filed
**Count: 1 learned in-segment and left uncommitted; 2 newly measured by this audit.**
- `infrastructure/state/lessons/20261022T160123Z-BENCH-pushing-from-side-clone-bench-when.md` (helper pushed
  2b85094eb0 to the PUBLIC repo with the gmail committer from a side clone) was WRITTEN but never committed —
  `??` in git status 9 h later. An untracked file lives only in this clone. Committed with this report.
- NEW (filed 20261023T010455Z): the transcript extractors (`compaction_check.py --extract`,
  `conversations.py`) drop mid-turn owner messages and all card answers — the extract body lacked 4 of 6
  typed messages and 12 of 12 card answers. The summary happened to keep them; the extract would not have.
- NEW (filed 20261023T010455Z): "handoff at ~50% context" never fired — the seat cannot see its context fill.
All other in-segment lessons were filed as learned (DLL rebuild from HEAD 165125Z, card-blocks-orchestrator
232137Z, publish auto-rebuild 232612Z, plus helpers' ~30 that day).

## 3. Open work / promises missing from BOTH summary and disk
**Count: 0 missing from both.** The summary's §7 caught every open thread I could find in the segment.
Open threads held ONLY by the summary (not filed, not in any pinned file) — lost at the next compaction:
- `RSW_Rycrit` has no def and an empty texture folder (art helper 15:44Z: "I reported it but didn't file it").
- The pond-shallowing setting (on by default) means a real lake never uses the drain-order fix — "may need a
  ruling from you later" (22:33Z). Not filed; only a selftest name mentions shallow-first draining.
- The owner's spare test machine ("There is a machine we could use") — the bottleneck helper was told to skip it,
  BENCH promised to "fold it into the follow-up". Ledger holds his words; no item or follow-up exists.
- Owner's saved Mod Settings keep `joinFittings=false`, so the fittings he picked will NOT show in his game
  tonight unless switched on — not on `walk_tonight.md`.
- Propane 30% flash + gasoline cold/roof evaporation — listed in pinned `fuel_spill_research.md`, not queued.
- Scrapper shut gates C/D are never drawn (material path wins) — in a ledger note, not an item.
- Promise *"I'll report the walk rebuild as soon as it finishes"* — in the summary; the helper is still running.
All seven go into the handoff as pointers.

## 4. Errors or distortions in the summary
**Count: 0 material errors; 2 cosmetic.**
- Times in §1 are PDT without saying so, and "~16:05 card answers" was 16:13 PDT (23:13Z). Harmless.
- "Owner = Lukas (they/them pronoun default in prose…)" — an odd invented aside; project docs say "he".
- It does not flag that lesson 160123Z is uncommitted (§2) — an omission, not a falsehood.
Spot-checked against disk and correct: shas 8ead9dd3b1, fb5ad67f9c, e3af42b7a6, 443912e4df; belt figures
548/48/86 over 68 runs; 423 min in cards; 142 refusals / 45 today; walk-rebuild agent a95636a2fbad20c90 and
save `RM_fw_walkthrough_20261022b` (bridge held by BENCH, re-taken 01:03Z).

## Verdict
This compaction lost almost nothing that matters: **0 owner words, 0 open promises and 0 material summary
errors were lost outright**, because the seat wrote rulings to the ledger as it got them (~43 provenance
events) and the harness summary is unusually complete (it lists every owner message and card pick). What
remained at risk was a thin layer that lived ONLY in the summary: **4 owner sentences not on disk, 7 open
threads never filed, 1 lesson written but uncommitted** — exactly the material a handoff exists to carry,
and none was carried because the ~50% handoff never fired. Everything else the segment held (tool calls,
helper reports, re-reading files) was reasoning noise already distilled into commits. So: worry less about
the compaction itself and more about two habits — file the stray finding the moment it appears, and hand
off on a visible proxy instead of waiting to feel 50%. Second-order risk found: the extraction tools we
would use to *recover* from a compaction miss owner words that arrived mid-turn or by card; the summary
covered for them this time.
