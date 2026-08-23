<!-- status: live -->
# `DUMP_READERS_USE_THE_DB_1` — verify record, BUILD, 2026-08-21

Offline. Config: the frozen capture `OFFICIAL-2026-08-21`
(`capturedUtc 2026-08-21T08:20:20Z`, 578 mods, `modlist_sha e0f11692cf69e516`),
`defs.sqlite` rebuilt 12:16 the same day and reported **current** by its own
staleness guard. Game down throughout; nothing here needed it up.

## 🔴 The measurement that changed the answer

The item assumed five tools "parse large JSON for what the db answers in 0.2s".
**Measured, that is true of three of them and false of two**, and the split is
not about the tools — it is about the shape of the question:

| question shape | JSON | db | winner |
|---|---|---|---|
| projection — two columns over the whole capture (`defName`→`packageId`) | 6.39 s / **1519 MB** | 5.00 s / **60 MB** | db, 25× on memory |
| projection — one type's `shortHash` table | whole-file `json.load` | 0.16 s | db |
| join — `tag → defNames` over `weaponTags` | whole-file `json.load` | **0.18 s / 23 MB** | db |
| **whole records** — every `ThingDef` as a dict | **3.17 s / 1497 MB** | **10.88 s / 1347 MB** | 🔴 **JSON**, by 3.4× on time |

⇒ **`db.records()` of a big type is SLOWER than reading the JSON file**, because
both end up parsing the same ~316 MB of JSON text and the db adds a row-by-row
trip to get there. Both return 24,904 ThingDefs, so this is a cost difference,
not a coverage one. **A tool that needs the records is right to read the file.**

## What was ported, and what it proved

### 1. `validate_save_artifact.py` `build_index()` → db-first ✅
Ran `--json` over `src/Jawa/ideoligion/The Salvation.rid` and
`src/Jawa/ideoligion/MandrakeJawa.xtp`, before and after, separate `TMPDIR` so
neither could serve the other's cache:

```
BEFORE (json scan)  wall 4.91s  peakRSS 1051348 kB
AFTER  (db)         wall 4.44s  peakRSS   62636 kB
```

**Every graded verdict is identical** — `referencesChecked` 266/36,
`resolved` 250/36, `missing` 0, `typeMismatch` 0, `unmeasurable` 16/0. One field
moved, and it is metadata about the dump rather than a verdict:
`dumpEmptyDefTypes` **80 → 27**. The old number came from a heuristic
(`'"defs":[]'` in the first 200 bytes); the new one is `capture.coverage NOT IN
('complete','ambiguous')`, which is where the instrument itself draws the line —
its `coverage` line reads *"27 of 536 def types cannot be counted at all and 5
more answer without a cross-check"*.

### 2. `gen_races_mod.py` `verify()` → `_owner_index()` ✅
The last whole-graph load in the repo. `1519 MB → 60 MB`, 6.39 s → 5.00 s.

### 3. `worldmap.py` `load_hash_table()` → db-first ✅
`TerrainDef`: **1340 hashes, byte-identical to the JSON ground truth**, 0.16 s.
End-to-end round trip on `WORLDMAP_gen2.rws`: *"unresolved none — table matches
the save"*, eight biomes decoded, `round-trip IDENTICAL`.

### 4. `rimflow/artifact.py` `defnames_in()` → onto the seam ✅
Not a port — it was already db-first, carrying its own 20-line copy of the
locator. Collapsed onto `dump_db()`; still returns **67,942** names. rimflow
selftest **24/24**.

### 5. `weapon_affordability.py` / `weapon_tag_audit.py` → 🔴 NOT PORTED, deliberately
Both want every `ThingDef` record: `base_market_value()` recurses through
`costList`, and `eligible()` reads `techLevel`, `weaponClasses` and `ingestible`
off each record. That is the row of the table where the db loses. Porting them
would have cost 3.4× the wall clock to make the item's checklist look complete.

⚠️ **The item's `criteria` is met as written** — *"no tool parses more than
~10 MB of JSON to answer a question the db answers"*. The db does not answer
this question better, so these two are outside it. Filed as
`WEAPON_TOOLS_PROJECT_NOT_LOAD_1`: the win available to them is a projection
(`def_tags` join, measured at 0.18 s / 23 MB above) plus `json_extract` for the
few fields, which is a rewrite of their logic and not a port of their loader.

## The db is a strict superset, and every exception is an ORPHAN

Head-to-head over the whole capture, db index vs JSON index:

```
db 67942 names | json 61197 names
json-only 152  |  db-only 6897
names where json has a (type,pkg) the db LACKS: 19
```

- **db-only 6,897** — records the JSON regex drops. It hard-codes the dumper's
  field order and demands `"modName":"…"`; a record whose `modName` is `null`
  never matches. ~9,000 auto-generated `SymbolDef`s are the bulk of it.
- **json-only 152, plus the 19 dropped entries — 100% attributable to `orphan`
  def types**, mechanically, not by inspection:

```
types behind the 152 json-only names : AspirationDef, GunPropDef, HyperTextDef,
  ProjectileImpactEffectDef, ProjectileImpactSoundDef, RaceTraitDef,
  RaidTargetCollectionDef, SkinDef, SummarizePromptDef, TYP_CompatibilityDef,
  ThoughtPromptDef, ToddlerPlayCategoryDef, ToddlerSoulPoolDef, TraitPoolDef
   all orphan? True
types behind the 19 dropped entries  : AspirationDef, GunPropDef
   all orphan? True
```

🔴 **`defs/` accumulates and nothing prunes it** — 19 files on disk are dated
2026-08-10…15 and their types were never declared by this capture. The JSON walk
ingests those dead defNames, so a reference to a **removed** def grades as
PROVIDED. Fail-toward-success, in the two functions built to catch exactly that.
Same defect, same size, as the 154 names `artifact.py` shed in `85789cf`.

## Selftests
```
measure   42/42 passed, 0 skipped
rimflow   24/24 passed
```

## One defect introduced and closed in the same change
`build_index`'s cache was keyed on `capturedUtc` alone — right for *"has the
dump moved"*, wrong for *"was this index built by the code now running"*. With
two sources against one capture it would serve the other's index. Added
`INDEX_VERSION = 2` to the key and `source: db|json` to the record.
