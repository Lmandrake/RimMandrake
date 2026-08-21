# Handoff — CHECK, 2026-08-21 16:10 PDT

## 🔴 THE GAME IS UP, AT THE MAIN MENU, AND THE BRIDGE IS YOURS

```
game        UP (owner stamped it 15:53). 578 mods, factioncontrol ABSENT.
bridge      CHECK holds it. 244 tools live: jawa 119, rimworld 107, rimbridge 18.
where       MAIN MENU. No world generated, no map. That is why the 21
            `needs: bridge` items have not been run - almost all of them want
            pawns, raids or a world to look at.
reach it    python.exe, NEVER python3. RimBridge binds Windows loopback and
            WSL2 is NAT-mode, so from WSL it is unreachable and the error says
            NOTHING about whether RimWorld is running.
```

```python
python.exe -c "import sys; sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
with RimBridge(h,p,t) as b: print(b._request('tools/list',{}))"
```

## What this load proved, and what it did not

Signatures were `EXPECTED_FAILURES_next_load.md` **§6** (⚠️ I first numbered it §3, which
was taken; it is §6 now). Harvest saved to
`observed/2026-08-21_harvest_2244load.txt` — read that, do not re-derive it.

| | |
|---|---|
| ✅ **S2 def dump** | **PASS.** New capture `2026-08-21T22:44:59Z`: 533 types, **78,813 defs** (+756 over the frozen 78,057), `defTypes` index present, **`AbilityDef` 612** — it read **0** before. The 824-collision fix works. |
| ⚠️ **S1 Inhabited** | **PARTIAL.** DLL landed, **zero** unknown-field errors. But 294 CharacterDefs on disk → **193 loaded, 101 discarded.** |
| ✅ **companion** | 244 tools; `jawa/faction_name_get`/`_set`/`faction_create` all present. |
| ⚠️ **S3 harvest** | **PARTIAL** — see below. |

### 🔑 Two written-down numbers were wrong and nobody had counted

- The roster expectation of **269** is wrong in both directions: **294** on disk, **193** loaded.
- The tool expectation of **115** `jawa/` tools is wrong: **119**.

### The 101 discards — FOUND, FIXED ON DISK, NOT IN THIS SESSION

Engine stack: `SkillGain.LoadDataFromXmlCustom → ParseIntPermissive → Single.Parse(null)`.
BUILD's root cause (`c6060ae`): **`SkillGain` takes the node NAME** — `<Shooting>5</Shooting>` —
**not `<li>`**. `CAST_SKILLS_EMPTY_LI_1` is **done**.
🔴 **Defs parse only at startup, so the RUNNING game still has 193 of 294.** The full cast
is not testable until the next load. Not a reason to reload — the 193 are fine for the
pawn, weapon, faction and world checks.

### From the harvest, not predicted

- `DEFS DISCARDED` **103** vs baseline 2 — fully attributed: our 101 + 2 benign.
- `cross-reference` **128** vs baseline 25.
- `stale saved data (Scribe)` **8** vs baseline 0 — all `guy762_*` GeneDefs (KotOR).
  ⚠️ Scribe ≠ cross-ref: a SAVED FILE holds a dead name, and no mod change fixes it.
- ⛔ **B59's megafauna YIELDS is UNMEASURED, not passed.** A no-op patch logs nothing, so
  the log cannot answer it. Settled on screen only. Recorded as UNMEASURED per
  `CHECK.md` "Numbers you report" — do not round it to a pass.

## 🔴 ONE THING IS THE OWNER'S AND IS STILL PENDING

`refresh.py` reports the capture **REPLACED**. Only he re-freezes:

```
python3 src/RimMandrake/Utils/refresh.py --freeze --by owner --freeze-id OFFICIAL-2026-08-21-2244
```

⚠️ **The `--freeze-id` is REQUIRED here.** The default ids from the capture DATE and both
captures are 2026-08-21, so the entry comes out with `"id"` == `"supersedes"` — an entry
that supersedes itself. Verified by dry run.
⛔ `freeze_dump.py` (which I wrote) **no longer exists** — BUILD folded it into
`refresh.py` at `9078a15`. Anything naming the standalone script is dead.

## The queue is smaller and now schedulable

- **53 open → 42.** `NEEDS_RESTAMP_THIRTYEIGHT_1` closed: 49 items read `needs: offline`
  at the migration default; now **bridge 21 · game-up 7 · offline 7 · owner 4 · harvest 2
  · deploy 1**. `rimflow why <ID>` gives a true answer now.
- 13 items merged into 3 umbrellas (`NEXT_LOAD_LOG_HARVEST_1`, `QUICKTEST_VISUAL_ROUND_1`,
  `FACTION_LABELS_ONE_LOOK_1`) and 4 hosts. Every absorbed clause was written into its
  successor's spec first. **One deliberate drop, named:** `B41`'s `raidsForbidden` — an
  absence cannot be observed in any bounded check.

### ⬜ The owner's review sheet is UNACTIONED and now STALE

`D:\Luke\dev\Rimworld\TRANSIENT_check_queue_review.html` — 53 rows, pre-filled
KEEP 26 / CUT 10 / MERGE 17. The 17 MERGEs are done; **the 10 CUTs are untouched and
waiting on him.** It still shows the pre-merge queue, so it is 13 rows stale. Regenerate
with `make_check_review.py --summaries TRANSIENT_check_queue_summaries.jsonl`.

## Convergence — the measured answer to his worry

69% of all items reach an end state; CHECK is the outlier at 36%. **The leak is not the
filing rate:** of 69 runs, 34 pass / **27 partial** / 8 fail, and only 2 items were ever
verified twice. A partial parks an item and nothing re-runs it.
⚠️ The ledger spans ONE day (migrated), so it cannot show a trend.

## Next, in order

1. **A dev quicktest map (~90 s) is the best value** — unlocks the largest block:
   `ROLE_KINDS_ARMED_5_OF_5_1`, `sixteen-authored-role-kinds…`, `CHEAPEST_WEAPON_IS_ABSURD_1`,
   `QUICKTEST_VISUAL_ROUND_1`. Owner had not chosen when this was written.
2. `W9` — generate and paint the world. The links CSV is pre-flighted: `lint_links.py`
   PASSES on 1,075 rows. Pass `expectTiles=21872`.
3. 🪤 **Hash every screenshot.** `rimworld/screenshot_cell_rect` photographs the TOP
   WINDOW, not the map — four `success: true` calls once gave four identical PNGs.
