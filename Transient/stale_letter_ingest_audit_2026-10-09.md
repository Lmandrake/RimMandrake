# Stale-letter ingest audit, 2026-10-09 (BENCH helper)

Instrument: `Transient/stale_letter_audit.py` (read-only). For every ruling/rejected event in
`infrastructure/state/art/events/BENCH.jsonl` since 2026-10-08 20:00 PDT it takes the event's click time (`at`), finds the
snapshot version current then (every git version of the sheet's snapshot, by its `built`), and checks the recorded
picture shas against that version's row/column (for carried rows: the `carriedFrom` row). Limit: a rebuild that was
never committed between two commits is invisible.

## Events audited
177 ruling events resolved from a decisions file + 28 rejected + 12 carried rulings + 5 no-column (holds/redo markers)
+ 67 install events (each checked against its ruling's shas) + 40 purge events (purge shas are written explicitly in
the decisions file, not resolved from a letter, so snapshot-independent).

## Result
- RULINGS: no wrong one. All 177 plain keep rulings (the Greentide ingest included) match the snapshot current at click. The Greentide rebuild at 22:29 PDT re-lettered only F,G,K -> L,M;
  no ruling used those letters. Beldon H/J were clicked 19:36 PDT, ~11 min before the first committed snapshot containing
  them (19:47); their pictures are identical in every later version, so not wrong.
  Carried rows (renamed rows, `carriedFrom`; abyss/warscar/twilightsea/scald rulings) all match the OLD row's pictures.
- INSTALLS: 67 of 67 install events install a sha named by their ruling. Nothing to reverse.
- PURGES: not letter-resolved; nothing to reverse.
- REJECTED (the bug 2 of enact_py_review): **28 wrong events, 10 rows.** They name the art that was LIVE at ingest time
  (the regen that replaced the rejected art), not what was IN GAME when he clicked redo. Rows (sheet): RM_PaddleVine 1,
  RM_Aveluthia 3 (abyss); RM_Hessal 3 (greysea); AA_ShockGoat 3, RSW_CaveLemming 3, Tauntaun 3 (nightsideice);
  RM_LivingBolt 3 (rustcathedral); RM_Thuum 3 (thescald); RM_Blinker 3 (lanterndeeps); RSW_Scurrier 3 (deep_desert).
  Ingested 2026-10-09 01:18-01:26 PDT. The CORRECT rejected events (old IN GAME shas) already exist for all ten rows
  (earlier ingests, same ruling ids), so nothing needs adding; the 28 are spurious extras.
- Consequence: `rejection_refusal` now refuses a mechanical install of 7 of those live pictures over their own path
  (PaddleVine d04e02..., ShockGoat x3, Tauntaun x3). Hessal and Scurrier are owner-kept, so unaffected.

## Repair
The ledger is append-only and has NO retract/supersede for `rejected` events (only `release` for keeps and `purge`).
Not hand-edited. Needs a decision: add a `retract` event type honoured by `Index` (small change in artledger.py), then
retract the 28 ids (list: `python3 Transient/stale_letter_audit.py` + group by ruling_id, or filter BENCH.jsonl for
type=rejected, ts >= 2026-10-09T01:18, via *.decisions.json). Until then the effect is limited to mechanical installs.

## Guard preview (enact, no --apply)
The new ab6bed31a guard now flags rows on re-run: abyss 22, deep_desert 16, greentide 38, twilightsea 12, warscar 4,
rustcathedral 3, thescald 3. It is OVER-conservative: it cannot see that carried rows were remapped by identical
pictures, and flags rows (e.g. Greentide Plant_Grass C,D,E) whose recorded pictures I verified correct above. The owner
will have to re-confirm those rows or the guard needs a carried-row/identical-picture exemption.
