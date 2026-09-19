## spec
`infrastructure/artpipe/pending/` was found fully drained (0 jobs) while the
daemon (`artpiped.py -N 3`, pid 699477, confirmed the sole instance via
`pgrep -af artpipe`) was live and idle. Refilled from the flora `art:"improve"`
channel of `SHEET_ORPHAN_CONSUMPTION_1`'s audit
(`Transient/sheet_orphan_audit_2026-09-12.md` §5): 145 APPLY rows / 134 distinct
defNames in `design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json`,
independently confirmed via `grep -F` against `infrastructure/artpipe/registry.jsonl`
to have **zero** prior generation attempts (waves 4-9 only ever drew from the
fauna improve pool; no WAVE10+ item existed for flora before this one). Excluded
the audit's 3 confirmed-superseded rows (`Plant_YellowGrass`/`Plant_YellowTallGrass`
— absent from every roster; the `the_pyrelands` row of `AB_HardyGrass`).

The 118-row NEW-ART/DEF commission ledger and the other 4 orphan channels
(fauna out, flora move, flora out, sizeBin rescale) were checked and
deliberately NOT touched here — `SHEET_ORPHAN_CONSUMPTION_1` records 5
findings (dupes already built, disagreeing decision files, an authority
conflict on the fauna cut list) that need an owner/BENCH call before any of
those channels are applied. This item only queues NEW ART GENERATION for
already-decided, unambiguous `improve` rows — it does not run
`apply_assignment_verdicts.py`, touch any roster JSON, or count as
consumption of that item's remaining channels.

Same "improve" semantics as waves 4-9 (`infrastructure/artpipe/README.md`):
full regen, non-SW names free to reinterpret the general kind, heavy black
outline required. Canvas defaulted to 256×256 (art-downscale-legibility
guard); the 3 `titan` sizeBin picks got 384×384 with an explicit
`oversize_reason`.

**14 of ~131 remaining eligible flora picked** (a slice, not the whole pool),
chosen for having an explicit owner design note in the decisions json to work
from: `AB_WildRadagast`, `AB_GlobularPlant`, `Plant_Fireweed`, `AB_GiantGamma`,
`AB_ToxicGamma`, `BMT_Plant_TreeTanglerootMangrove`, `AB_CrystalHorn`,
`BMT_Plant_TreeTwistingThornwood`, `AB_AgariluxPrime`, `AB_GiantAgarilux`,
`AB_FirevineTree`, `AB_GiantAgariTox`, `AB_LargeSlimyTree`, `AB_GreenRockFern`.

## verify
`fill_queue.py --input Transient/art_regen_flora_wave1_improve.json --channel
codex` dry-run: 14 jobs / 0 duplicates / 0 row errors. Filed for real: 14 job
files landed in `infrastructure/artpipe/pending/`. Daemon confirmed still the
sole `artpiped.py` process before and after filing; within seconds it claimed
3 of the 14 into `active/` (`agariluxprime_v1`, `crystalhorn_v1`,
`firevine_fireweed_v1`) — matching its `-N 3` worker count, proof it is
consuming the new queue.

## criteria
14 flora `art:"improve"` jobs sitting in pending/active, none colliding with
an existing pending/active/done/failed id, registry.jsonl shows 14
`registered`+`queued` pairs sourced `ART_REGEN_FLORA_WAVE1_QUEUE_1`.

## 2026-09-13 (offline subagent, dispatched by BENCH) — filed and confirmed running
Daemon was drained (0 pending). Filed 14 flora-improve jobs per the spec
above; dry-run clean, real fill clean, daemon picked 3 up within seconds.
Left `~117-120` flora improve rows + the 14-fauna wave-10 pool (named in
`ART_REGEN_WAVE9_QUEUE_1`) + the disputed 118-row ledger + the other
`SHEET_ORPHAN_CONSUMPTION_1` channels for a future wave. Not claiming this
exhausts the flora improve pool — a WAVE2 (flora) or WAVE10 (fauna) item is
still owed.
