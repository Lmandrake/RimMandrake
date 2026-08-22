# NEXT_LOAD_LOG_HARVEST_1
Everything the next Player.log must be asked, in one pass

Created by CHECK 2026-08-21 to absorb three items that each wanted the SAME artifact —
one `Player.log` from one load — and each of which would otherwise have parked
separately waiting for it.

## spec

🔑 **These are log GREPS, not interactions.** Nothing here needs the bridge, a map, or a
pawn. They need a load to have happened and its log to be unmined, which is exactly what
`needs: harvest` means. Filing them apart made three items look like three loads.

**Absorbed, with every original clause carried — a merge that loses a criterion is a cut
wearing a merge's name:**

| absorbed | what its log line must show |
|---|---|
| `B59` (the MegafaunaYield fix) | Megafauna butcher yields are the intended ones, AND the ~50 patch operations sequenced after the previously-aborted one apply again |
| `PRELOAD_PREDICTIONS_578_1` | JawaBench and Inhabited each print their init line; a failure is attributable to the right assembly rather than to "the load broke" |
| `BIOMESKIT_SNOWY_DESERT_TEXTURES_1` | the 148 missing-texture errors are ReGrowth's absent snow variants, NOT damage our repaint caused |

⚠️ **`RT_PROBE_LOAD_ABORTS_ON_578_1` is NOT absorbed and must not be.** It is also
`needs: harvest`, but it is a live blocker with its own fail run on the record, and
folding a blocker into a routine harvest is how a blocker stops being visible.

⛔ **Do not add "and also check…" to this item at collection time.** It is a fixed list
written before the load. An item that grows while the log is being read is an item whose
criteria were chosen after seeing the answer.

## verify

One pass over the newest `Player.log` after the next load, recording the three readings
above together. Harvest the whole log at once — `skills/rimworld-load-round`.

## criteria

- ✅ **PASS** when all three readings are recorded with their actual log lines quoted.
- ❌ **FAIL** if any one of the three cannot be answered from the log — that is a real
  answer about that clause, not a reason to defer the item.
- ⛔ **NOT in scope:** fixing anything the log reveals. A finding here spawns work; it
  does not reopen this item.

---

## COLLECTED — CHECK, 2026-08-22 10:35

Harvested against `Player.log` last written **2026-08-22 08:40:10**, RimWorld
1.6.4871 rev591, 578 active mods, state EXITED. One pass, the fixed list, nothing
added at collection time.

**❌ VERDICT: FAIL.** Two of the three clauses cannot be answered from a log at
all. Per this item's own criteria that is a real answer, not a deferral.

### 1. `B59` — MegafaunaYield · ❌ UNANSWERABLE BY CONSTRUCTION
The harvest tool reported `303` against baseline 0. **That number was false.** It
greps the mod name `Jawa Doctrine Patches`, which hits the load-time patch-file
manifest, not errors:
```
[Source: Jawa Doctrine Patches]
[File: C:\...\Mods\Jawa_Doctrine\Patches\MegafaunaYield.xml]
```
Corrected in `harvest_log.py` this session; the check now reads **0**.

But the clause is unanswerable regardless, and the tool's own header already said
so: MegafaunaYield.xml's 6 ops are `PatchOperationConditional` inside
`PatchOperationFindMod`, **both of which return true on no match**. A patch that
matched nothing logs exactly what one that worked logs. ⇒ **butcher yields are an
ON-SCREEN check, and no log will ever close this.**

### 2. `PRELOAD_PREDICTIONS_578_1` — per-assembly attribution · ❌ HALF MISSING
```
[Inhabited] ready: 2 patches, 193 characters, 0 places, 0 casts.
[RimBridge] Applied 56 optional Harmony patch classes.
```
- **Inhabited: present, and the count is a finding.** 193 against **294**
  `Inhabited.CharacterDef`s on disk. 294 − 101 skills-carrying = 193, exact.
  This is the game's own confirmation of `CAST_ROSTER_SKILLS_DISCARDED_1`.
  ⚠️ `0 places, 0 casts` is NOT a defect — there are no `InhabitedPlaceDef` or
  `InhabitedCastDef` files on disk. Checked, ruled out.
- **JawaBench: zero lines. It has no startup instrument at all** — every `Log`
  call in it is a `Log.Warning` inside a `catch`. So attribution, which is the
  entire point of this clause, is NOT achieved: a JawaBench that never loaded
  and one that is perfectly healthy produce identical logs.
  ⇒ spawned `JAWABENCH_HAS_NO_INIT_LINE_1` (BUILD).

### 3. `BIOMESKIT_SNOWY_DESERT_TEXTURES_1` · ⚠️ ANSWERED SIDEWAYS
**Zero** texture-path failures, against baseline 0 — confirmed two independent
ways (the tool's `tex` bucket, and a direct probe for `Could not load
UnityEngine`/`Failed to find any texture`/`texture at path`, all 0).
The 148 errors did not recur. So the clause as WRITTEN — "they are ReGrowth's,
not ours" — cannot be confirmed, because there is nothing left to attribute.
✅ The thing actually at stake **is** answered: **no texture damage from our
repaint.** ⚠️ Caveat carried: this bucket fires only when ALL directions are
missing, so a partial set stays silent.

### Spawned by this harvest
- `CAST_ROSTER_SKILLS_DISCARDED_1` (BUILD) — 101 of 294 cast defs discarded.
- `JAWABENCH_HAS_NO_INIT_LINE_1` (BUILD) — no companion startup line.
- `harvest_log.py` fixed: patch-file manifest no longer counted. Three checks
  were reporting confident false REDs (303 / 5252 / 2224 → 0 / 0 / 2).
