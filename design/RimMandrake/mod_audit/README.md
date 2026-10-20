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
| `FACTS_REGEN_DELTA.md` | which stage-1 verdicts/severities the 2026-10-10 facts regeneration would change, by rule (flags only) | `facts_delta.py --before <old jsonl>` |
| `batches/batch_NN.json`, `batches/INDEX.md` | self-contained assessor inputs, grouped by routing category | `batches.py` |

## How to refresh the facts (all offline; no bridge, no game)

Tools live in `src/RimMandrake/Utils/modaudit/`. Caches are derived and live outside git in
`~/.cache/rm_modaudit/`. Run from the repo root, in this order:

```
python3 src/RimMandrake/Utils/modaudit/selftest_modaudit.py           # must print OK first
python3 src/RimMandrake/Utils/modaudit/universe.py                    # ~10 s: FULL.LATEST + our absent mods, all roots
python3 src/RimMandrake/Utils/modaudit/defscan.py                     # ~1 min: offline def + patch census
python3 src/RimMandrake/Utils/modaudit/diskfacts.py --budget 240      # resumable; re-run until it says DONE (~20 min total over /mnt/c); a SCHEMA bump re-walks every mod
python3 src/RimMandrake/Utils/modaudit/runtime.py [--log <archived Player log> --session <tps id prefix> --token <bridge token>]
python3 src/RimMandrake/Utils/modaudit/sources.py --budget 240 [--search]   # resumable; gh api, capped + cached
python3 src/RimMandrake/Utils/modaudit/assemble.py                    # writes facts/ (refuses on a failed sanity probe)
python3 src/RimMandrake/Utils/modaudit/batches.py                     # writes batches/
```

To re-collect one mod after it changed: `diskfacts.py --redo <packageId>`, then `assemble.py`.

**After a new full-list cold load**, point `runtime.py` at THAT session: its Player.log is archived by the next
launch to `D:\ClaudeWork\rimmandrake\scratch\playerlog_archive\Player.<launch time>.log`; the TPS session id and bridge
token are in that launch's receipt in `D:\ClaudeWork\rimmandrake\scratch\launch_receipts\`. The live `Player.log` belongs to
whatever is running now and is never the default.

## How to read a facts row (and what each number is NOT)

- **`class`** OURS = `mandrake.rm.*` / `mandrake.rsw.*` / `mandrake.rut.*` (or any About id under `src/`);
  CORE_DLC = `ludeon.rimworld*`; THIRD_PARTY = everything else.
- **`membership`** `FULL.LATEST` (in the canonical list) or `OURS_ABSENT_INSTALLED` (ours, deployed, not in the
  list; see `Transient/foundry_full_latest_gap_proposal_20261010.md` for the owner's add-after-clean-load ruling).
- **`def_total`, `defs_by_type`** declared in the mod's own XML, inheritance resolved, **before** patches and
  `MayRequire`. Not "what the running game has".
- **`dependants`** every mod that would lose something if this one went, ALL edge kinds; **`dependants_detail`**
  `[{packageId, kinds, refs}]` with kinds `hard_dep` (modDependencies), `hard_dep_v1.6` (modDependenciesByVersion
  v1.6), `load_after` (loadAfter/forceLoadAfter, +ByVersion v1.6), `patch_xpath`, `findmod` (FindMod name = About
  name), `mayrequire` (any element of Defs/Patches), `class_ref` (XML names a type in this mod's LOADED DLLs, read from
  the .NET TypeDef table), `def_ref` (CANDIDATE: XML names a defName only this mod declares). Core/DLC is never a
  dependant. **`dependants_hard`** = the old modDependencies-only list. A patch selecting a def by `text()=` or `@Class`
  makes no edge (lower bound).
- **`cherry_picker_cut_defs`, `cherry_picker_shell`** declared defs on the LIVE Cherry Picker list (settings = intent
  for the next load); shell = >= 90% of its player-facing defs (ThingDef, PawnKindDef, BackstoryDef, ...) cut.
- **`defs_xml_files_total` / `_loaded` / `defs_outside_loaded_dirs`** Defs XML anywhere vs under the 1.6 contentDirs;
  the outside list excludes older version folders (`defs_xml_files_older_versions`) and Source: what remains is
  LoadFolders/compat-gated content `def_total` did not count.
- **`patch_ops_all`, `patches_mods`, `patched_by`** from xpath defNames; an xpath with no defName adds no edge, so
  edges are a **lower bound**. `patches_ours_refs` / `patched_by_ours_refs` are the interaction counts with our mods.
- **`dll_flags`** string presence in an assembly (`HarmonyLib`, `DoSettingsWindowContents`, `MapComponentTick`,
  ...). A FLAG, never a count, and not proof the code path runs.
- **`texture_decoded_mb_est`** w*h*4*1.33 from PNG/DDS headers of images under a `Textures/` folder and no
  source-like folder (Source, src, .vs, obj, bin, packages, About): an INFERRED memory proxy, not a measurement.
  `texture_decoded_mb_est_all_images` counts every png/dds (`largest_images_not_loaded` shows what was dropped); a mod
  that loads images by its own code (RimThemes `Themes/`, Worldbuilder presets) is undercounted by the Textures figure.
- **`log_*`** from the 550-mod session of 2026-10-10. `null` = the mod was not in that session (UNMEASURED);
  `0` = measured zero. Attribution is CANDIDATE: read `log_error_samples` before charging a mod.
- **`static_ctors`** how many `[StaticConstructorOnStartup]` types the LoadTracer saw from the mod's assemblies.
- **`tps_cost`, `memory_cost`** UNMEASURED per mod. The TPS record attributes time to engine stages (see
  `session_context.json` `tps.stage_share`); `jawa/map_comp_timing` (`91f9c0a14`) can name MapComponents when run.
- **`source_*`** `MEASURED` = a repo the mod itself links, verified by `gh api`; `INFERRED` = linked but
  unverified, or a `--search` name match (confirm before relying on it); `steam-only` = no link found.
  `assemble.py` re-judges every cached record offline (`sources.reselect`): shared-library repos (pardeike/Harmony
  except for Harmony itself, rwmt/Publicise, MonoMod/*), wiki repos and search hits whose repo name does not resemble
  the mod are REJECTED (`source_rejected`), a NOT_FOUND repo is never the source, and found-nothing reads INFERRED
  with `source_note` "no source found (searched: ...)".
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

## Merge and outputs (stage 2.5, 2026-10-11)

| path | what | regenerate |
|---|---|---|
| `MASTER_REGISTRY.jsonl` / `.csv` | one row per mod: final decision, status (AGREED / CHANGED_BY_CHECKER / DISPUTED), severities, checker-corrected source and dependants, card / ticket / action ids, evidence paths | `merge_checks.py` (selftest: `selftest_merge_checks.py`) |
| `merge_inputs.json` | hand-made: spot-checks of the primary sources checkers cited (a verdict change is taken only when CONFIRMED), card / measurement / action / answered-by-ruling maps | by hand |
| `OWNER_CARDS.md` | the owner cards: 8 ANSWERED (C01-C04, C07-C10), 15 open, 2 new from the GPT review (C24, C25), plus the questions already answered by a ruling | by hand |
| `ACTIONS_NOW.md` | no-decision actions and measurement tickets (proposed names, not yet filed) | by hand |
| `GPT_PACKAGE.md` | the whole picture for a GPT review (<= 250 KB) | `gpt_package.py` |
| `review_amendments.json` | hand-made verdict amendments from reviews (`reviews`) and the owner's card rulings (`owner_rulings`); `old` must match the checker-merged verdict or the merge refuses | by hand; consumed by `merge_checks.apply_amendments` |
| `OWNER_RULINGS.md` | the owner's card decisions, append-only | by hand, the same sitting as the card |
| `GPT_REVIEW_DISPOSITION.md` | ACCEPT / REJECT / DEFER for every finding of the 2026-10-10 GPT review, and the 30 re-examined verdicts | by hand |

## How to maintain this record

The record has three layers. Keep them apart, because each has a different owner:

1. **Facts** (`facts/`) are regenerated by machines and never hand-edited.
2. **Judgements** (`assessments/`, `checks/`, `merge_inputs.json`, `review_amendments.json`) are written by hand or by agents, with
   evidence.
3. **Decisions** (`OWNER_RULINGS.md`) are the owner's.

`MASTER_REGISTRY.*` is a disposable view of all three. GPT's maintainability advice (review §1, "Structure the permanent record")
is the same rule: human decisions are kept separate from regenerated facts, and generated reports are views.

**Rules that keep the record honest:**

- **A verdict is a target, not a readiness.** ELIMINATE means "headed out". Whether it can be unticked *today* depends on its gates:
  save census, edge review and replacement (`ACTIONS_NOW.md`).
- **Edges are not equal.** `hard_dep`, unguarded class or def refs and serialized types block. `load_after`, guarded `MayRequire`/FindMod
  and older-version folders do not. Until `MODAUDIT_CLASSREF_FIX_GUARDED_EDGES` lands, `class_ref` over-reports. Two known false
  edges: `biomesteam.coreframework` ← Fossils/MVB (both guarded), and JecsTools ← Armoury (our own `CompExtraSounds` namespace).
- **Texture figures are estimates**, from image headers, never measured memory. Savings are marginal (full stack minus the cluster),
  measured. Never add up per-mod proxies.
- **Patch counts are migration cost, never a reason to keep** (GPT §1: sunk cost).
- **Source is not permission.** A public repo without a licence grants no reuse right. Read LICENSE at the deployed revision before
  porting anything (`DONOR_LICENCES_VERIFY_BEFORE_PORT`).
- **A verdict change needs primary evidence opened by the person making it.** Agreement between checkers or reviewers shares their
  instrument and is not evidence. That is why `merge_checks.py` takes a checker's verdict only with a CONFIRMED spot-check, and
  `review_amendments.json` only with a cited path.

**Routine refresh (offline, run from the repo root):**

```
python3 src/RimMandrake/Utils/modaudit/selftest_modaudit.py && python3 src/RimMandrake/Utils/modaudit/selftest_merge_checks.py
# refresh facts as in "How to refresh the facts" above (universe -> defscan -> diskfacts -> runtime -> sources -> assemble)
python3 src/RimMandrake/Utils/modaudit/facts_delta.py --before <old mod_facts.jsonl>   # which verdicts the new facts would move
python3 src/RimMandrake/Utils/modaudit/merge_checks.py --check                          # counts only; refuses a stale amendment
python3 src/RimMandrake/Utils/modaudit/merge_checks.py                                  # rewrite MASTER_REGISTRY.jsonl/.csv
python3 src/RimMandrake/Utils/modaudit/gpt_package.py                                   # only before a new GPT pass
```

**When something changes:**

| event | do |
|---|---|
| The owner answers a card | Append it to `OWNER_RULINGS.md` (a click is "decision taken by question card"; quote only what he typed). Add `owner_rulings` entries to `review_amendments.json`, re-run `merge_checks.py`, and mark the card ANSWERED in `OWNER_CARDS.md`. If it retires something now, add it to the next RETIREMENT WAVE in `ACTIONS_NOW.md`. |
| A review or checker proposes a verdict change | Open the cited primary source yourself. Then add a `reviews` entry: status CHANGED only on your own evidence, otherwise DISPUTED / REJECTED / CONSISTENT. Write the disposition beside it. |
| A mod is unticked or added | Edit FULL.LATEST, re-run `universe.py` and then the chain. A retired mod's row disappears from the universe, so record the retirement in the item first. |
| A new full-list cold load | Point `runtime.py` at that session's archived log (see above). Re-measure log attribution and the TPS stage profile. |
| A tool's number disagrees with a doc | Trust neither. Re-measure, and write which direction the evidence runs. |

**Re-measure before trusting (these decay):**

- FULL.LATEST membership: 551 + 38 ours-absent = 589 rows. The last session loaded 550, because `vlvop.tormentmaster.expansion`
  is listed but not installed.
- Cherry Picker cut counts.
- Live Config settings: the Config file is not the in-memory value (`MOD_SETTINGS_HARVEST_EFFECTIVE_VALUES`).
- Placed things in the save.
- Per-mod TPS and memory: UNMEASURED until F1-F3.
- Source URLs (`sources.py --search` hits are INFERRED).
- `FACTS_REGEN_DELTA.md`, which still joins assessor verdicts, not the registry, until `FACTS_DELTA_REWIRE_TO_MASTER_REGISTRY` lands.
