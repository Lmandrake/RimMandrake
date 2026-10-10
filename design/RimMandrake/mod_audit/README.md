# Mod audit: every mod in the full game list, once and for all

Owner order, 2026-10-10: a thorough analysis of **every** mod in the large game list, kept as a long-term
record. Per mod: (1) what it adds, (2) a forward plan (`KEEP` / `KEEP-TEMPORARILY-THEN-PHASE-OUT` /
`REPLACE-NOW-WITH-OUR-OWN` / `ELIMINATE-COMPLETELY`), (3) likely problems (TPS, memory, complexity, size, log
noise, interactions with our mods), (4) whether source is available, (5) resonance or dissonance with the
scenario.

## The programme

| stage | what | who | output |
|---|---|---|---|
| 0 | evidence pipeline + scenario brief + rubric + batches | FOUNDRY (this directory) | `facts/`, `SCENARIO_BRIEF.md`, `RUBRIC.md`, `batches/` |
| 1 | batch assessment, one agent per batch | assessor agents | `assessments/batch_NN.jsonl` |
| 2 | second checker: re-derive every MEASURED claim from `facts/`, flag, downgrade confidence | checker agent | `assessments/batch_NN.check.jsonl` |
| 3 | GPT review of the contested and card-worthy rows | `gpt_consult.py` (high effort) | `reviews/` |
| 4 | question cards to the owner for rows marked `card_worthy` | BENCH with the owner | owner rulings, then the record |
| 5 | the human record: one markdown section per mod (template in `RUBRIC.md` §7) | generated | `RECORD.md` |

Assessors work **from measured facts, never guesses**. The rubric's forbidden shortcuts (§5) are the contract.

## Files

| path | what | regenerate |
|---|---|---|
| `SCENARIO_BRIEF.md` | the scenario's identity and the filters it implies; every line sourced; §5 lists contradictions between docs (unresolved on purpose) | by hand, when owner rulings change |
| `RUBRIC.md` | verdict definitions, evidence required, severity scales, confidence, forbidden shortcuts, assessment JSON schema, record template, worked examples | by hand |
| `facts/universe.json` | the universe: every packageId, its class (OURS / THIRD_PARTY / CORE_DLC), membership, all on-disk roots | `universe.py` |
| `facts/mod_facts.jsonl` | one JSON object per mod: everything measured about it | `assemble.py` |
| `facts/mod_facts.csv` | flat view of the same rows for a spreadsheet | `assemble.py` |
| `facts/session_context.json` | the measured session: log probe, unattributed errors, TPS stage profile, process memory | `assemble.py` |
| `batches/batch_NN.json`, `batches/INDEX.md` | self-contained assessor inputs, grouped by routing category | `batches.py` |

## How to refresh the facts (all offline; no bridge, no game)

Tools live in `src/RimMandrake/Utils/modaudit/`. Caches are derived and live outside git in
`~/.cache/rm_modaudit/`. Run from the repo root, in this order:

```
python3 src/RimMandrake/Utils/modaudit/selftest_modaudit.py           # must print OK first
python3 src/RimMandrake/Utils/modaudit/universe.py                    # ~10 s: FULL.LATEST + our absent mods, all roots
python3 src/RimMandrake/Utils/modaudit/defscan.py                     # ~1 min: offline def + patch census
python3 src/RimMandrake/Utils/modaudit/diskfacts.py --budget 240      # resumable; re-run until it says DONE (~25 min total over /mnt/c)
python3 src/RimMandrake/Utils/modaudit/runtime.py [--log <archived Player log> --session <tps id prefix> --token <bridge token>]
python3 src/RimMandrake/Utils/modaudit/sources.py --budget 240 [--search]   # resumable; gh api, capped + cached
python3 src/RimMandrake/Utils/modaudit/assemble.py                    # writes facts/ (refuses on a failed sanity probe)
python3 src/RimMandrake/Utils/modaudit/batches.py                     # writes batches/
```

To re-collect one mod after it changed: `diskfacts.py --redo <packageId>`, then `assemble.py`.

**After a new full-list cold load**, point `runtime.py` at THAT session: its Player.log is archived by the next
launch to `D:\Luke\dev\_rmscratch\playerlog_archive\Player.<launch time>.log`; the TPS session id and bridge
token are in that launch's receipt in `D:\Luke\dev\_rmscratch\launch_receipts\`. The live `Player.log` belongs to
whatever is running now and is never the default.

## How to read a facts row (and what each number is NOT)

- **`class`** OURS = `mandrake.rm.*` / `mandrake.rsw.*` / `mandrake.rut.*` (or any About id under `src/`);
  CORE_DLC = `ludeon.rimworld*`; THIRD_PARTY = everything else.
- **`membership`** `FULL.LATEST` (in the canonical list) or `OURS_ABSENT_INSTALLED` (ours, deployed, not in the
  list; see `Transient/foundry_full_latest_gap_proposal_20261010.md` for the owner's add-after-clean-load ruling).
- **`def_total`, `defs_by_type`** declared in the mod's own XML, inheritance resolved, **before** patches and
  `MayRequire`. Not "what the running game has".
- **`patch_ops_all`, `patches_mods`, `patched_by`** from xpath defNames; an xpath with no defName adds no edge, so
  edges are a **lower bound**. `patches_ours_refs` / `patched_by_ours_refs` are the interaction counts with our mods.
- **`dll_flags`** string presence in an assembly (`HarmonyLib`, `DoSettingsWindowContents`, `MapComponentTick`,
  ...). A FLAG, never a count, and not proof the code path runs.
- **`texture_decoded_mb_est`** w*h*4*1.33 from PNG/DDS headers: an INFERRED memory proxy, not a measurement.
- **`log_*`** from the 550-mod session of 2026-10-10. `null` = the mod was not in that session (UNMEASURED);
  `0` = measured zero. Attribution is CANDIDATE: read `log_error_samples` before charging a mod.
- **`static_ctors`** how many `[StaticConstructorOnStartup]` types the LoadTracer saw from the mod's assemblies.
- **`tps_cost`, `memory_cost`** UNMEASURED per mod. The TPS record attributes time to engine stages (see
  `session_context.json` `tps.stage_share`); `jawa/map_comp_timing` (`91f9c0a14`) can name MapComponents when run.
- **`source_*`** `MEASURED` = a repo the mod itself links, verified by `gh api`; `INFERRED` = linked but
  unverified, or a `--search` name match (confirm before relying on it); `steam-only` = no link found.
- **`prior_verdict_2026_08_30`** the earlier whole-list pass (`design/Jawa/mods/outgrown_audit_2026-08-30.*`),
  which did not open its framework rows one by one; context, not authority.

## Known gaps (state, 2026-10-10)

- Per-mod TPS and memory: UNMEASURED (instrument does not exist at mod granularity yet).
- Texture memory proxy cannot see inside AssetBundles (e.g. `mlie.starwarsanimalcollection` ships its art in 32 MB of
  bundles); read `disk_by_kind.assetbundles` beside `texture_decoded_mb_est`. Core/DLC art lives in `resources.assets`, also unseen.
- Log attribution covers 100 of 344 error blocks of the measured session; the rest (152 are one vanilla-worded
  `Tried to calculate chance for father ...` line with no trace) are listed in `session_context.json` `unattributed_top`.
- Player.log warnings: UNMEASURED (no consistent prefix); only error openers are counted.
- Placed Things in the campaign save per mod: not collected (needed for any ELIMINATE; `rimworld-savegame` skill).
- `vlvop.tormentmaster.expansion`: in FULL.LATEST, installed in neither root, so it has no facts beyond its id.
