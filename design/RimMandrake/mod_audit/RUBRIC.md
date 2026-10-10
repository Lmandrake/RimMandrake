# Mod audit rubric

How an assessor turns one mod's measured facts into a forward plan. Read
[`SCENARIO_BRIEF.md`](SCENARIO_BRIEF.md) first (what the scenario is and the filters it implies), then this
file, then your `batches/batch_NN.json`. Whole-session context (TPS, memory, log probe) is in
`facts/session_context.json`. The full per-mod record is `facts/mod_facts.jsonl`; your batch file copies the
fields you need.

## 1. The five questions, per mod

| # | Question | Answer field(s) | Primary evidence |
|---|---|---|---|
| 1 | What does it add (content, functionality, art)? | `adds` | `description`, `defs_by_type`, `dll_flags`, `disk_by_kind`, `patches_mods` |
| 2 | Forward plan | `verdict`, `verdict_reason`, `replacement_path` | §2 below |
| 3 | Likely problems | `problems[]` | §3 below; `log_*`, `dll_flags`, `texture_decoded_mb_est`, `patched_by`, `patches_ours_refs` |
| 4 | Is source available? | `source` | `source_url`, `source_kind`, `source_confidence`, `ships_source` |
| 5 | Resonance / dissonance with the scenario | `fit`, `fit_reason` | `SCENARIO_BRIEF.md` §2 and §4, cited by section |

## 2. Verdict categories (exactly one per mod)

| verdict | means | evidence REQUIRED to choose it |
|---|---|---|
| `KEEP` | stays for the foreseeable future | Fit is `resonant` or `neutral`, AND either something of ours depends on it (`patched_by_ours_refs` > 0, our `dependencies`/`load_after`, a `MayRequire` of ours) or it supplies something we have no plan to build (name the thing). For a framework/library: name at least one dependant in the universe. |
| `KEEP-TEMPORARILY-THEN-PHASE-OUT` | needed now, but we intend to own or drop what it does | Name **what holds it in today** (dependants, placed Things in the save, our patches into it) AND **the exit**: the item, port or absorption that ends the dependency (an existing ledger item ID, or "unfiled: <SUBJECT_INTENT_TWIST name>"). Star Wars IP donors sunsetting via `RSW_` ports land here. |
| `REPLACE-NOW-WITH-OUR-OWN` | build our replacement before the next release; the donor goes when it lands | A concrete scope of the replacement (which defs/mechanics, roughly how many: cite `defs_by_type`), a reason it cannot wait (dissonance, a measured problem, a ruling such as no-donor-art), and evidence we have not already built it (search `src/` first: CLAUDE.md "this project keeps having already built it"). |
| `ELIMINATE-COMPLETELY` | remove with no replacement | Fit is `dissonant` OR it duplicates something we own, AND a retirement-cost check: dependants (`patched_by`, other mods' `dependencies`), placed Things in the save (state UNMEASURED if you could not check), and `ParentName` order (does anything inherit from its abstract defs?). "Nothing depends on it" alone is not enough (SCENARIO_BRIEF §3). |

If the evidence for any verdict is missing, choose the most conservative verdict the evidence supports
(`KEEP-TEMPORARILY-THEN-PHASE-OUT` over `ELIMINATE-COMPLETELY`) and say what is missing in `open_questions`.
Our own mods (`class: OURS`) use the same four verdicts with the meanings *keep*, *merge-then-retire*
(phase-out into another of ours), *rewrite*, *delete*; for them `source` is trivially available and the
substance is overlap with other mods of ours, dependence on donors, and runtime problems.

## 3. Problem severity scales

Every problem is one entry `{kind, severity, basis, confidence, evidence}`. Severity is **0 none / 1 low /
2 medium / 3 high / U unmeasured**. `basis` is the number or the stated reason. A severity without a basis
is invalid.

| kind | 1 low | 2 medium | 3 high | where the number comes from |
|---|---|---|---|---|
| `tps` | a tick FLAG (`map_component_tick`, `comp_tick`, ...) but small content | tick FLAGs + many tickers likely on a map (creatures/buildings it spawns in numbers) | a measured cost (none exists yet: per-mod TPS is UNMEASURED) or a known heavy mechanic named in its description | `dll_flags`; `session_context.json` stage shares are SESSION-wide only |
| `memory` | `texture_decoded_mb_est` < 50 | 50-250 | > 250 | INFERRED proxy from PNG/DDS headers (w*h*4*1.33), never MEASURED per mod |
| `log_noise` | 1-2 distinct errors, or chatter < 50 lines | 3-9 distinct, or chatter 50-500 | >= 10 distinct, an exception during load/tick, or chatter > 500 | `log_errors_distinct`, `log_error_samples`, `log_chatter_lines` (attribution is CANDIDATE: read the samples before charging the mod) |
| `interaction` | patches vanilla/third-party defs only | patches defs of ours, or ours patch it heavily (`patches_ours_refs` / `patched_by_ours_refs` > 0) | patches the same defs our mods own with conflicting intent, or `incompatible_with` lists something in the universe | `patches_mods`, `patched_by`, `patch_findmod_names`, `incompatible_with` |
| `complexity` | XML-only | one DLL, no Harmony | Harmony + Prepatcher, many DLLs, or `static_ctors` > 20 | `dll_count`, `dll_flags`, `static_ctors` |
| `size` | `disk_mb` < 20 | 20-200 | > 200 | `disk_mb`, `disk_by_kind` |
| `maintenance` | source verified, pushed in the last year | source unverified / no 1.6 in `supported_versions` | no source, archived repo, or author gone (last push > 2 years) | `source_*`, `supports_1_6` |

## 4. Confidence (every claim carries one)

- **MEASURED**: read off an instrument in the facts record (a count, a flag, a parsed field) or off a file
  you opened. Cite the field or path.
- **INFERRED**: reasoned from measured facts (e.g. memory from texture estimate; "creature pack" from
  `defs_by_type`). Say what it was inferred from.
- **UNVERIFIED**: a claim you could not check (a source URL the network refused; a save-placement question).

## 5. Forbidden shortcuts

1. **Do not judge from the name alone.** Read `description` and `defs_by_type` (CLAUDE.md "Is there a mod that
   does X": a packageId is an author's slug, not a description of behaviour).
2. **Do not claim "heavy", "laggy" or "bloated" without a number or a stated reason.** Per-mod TPS and memory
   are UNMEASURED; say so and use the proxies with their labels.
3. **Do not treat a CANDIDATE log attribution as guilt.** Read the sample; a `def`-only attribution names the
   mod that DECLARES the def, which may be the victim of someone else's patch.
4. **Do not read `def_total` as "what is in the game".** It is declared XML before patches and MayRequire; a
   Cherry Picker cut or a `MayRequire` can remove it at runtime.
5. **Do not call a mod unused because nothing in `patched_by` names it.** Edges are a lower bound (xpaths
   without a defName add none). Search `src/` for its packageId, defNames and `MayRequire` before saying so.
6. **Do not resolve a §5 contradiction of the brief inside a verdict.** Mark the mod `open_questions` and cite
   the contradiction.
7. **Zero is a claim.** `log_error_occurrences: 0` is MEASURED only when `runtime_scope` says the mod was in the
   measured session; otherwise it is `null` and means UNMEASURED.
8. **Never invent a ledger item.** Cite an existing ID (`rimflow show <ID>`) or write `unfiled:` plus a proposed
   `SUBJECT_INTENT_TWIST` name (design/RimMandrake/ticket_naming_2026-10-10.md).

## 6. Output: `assessments/batch_NN.jsonl` (one JSON object per mod)

```json
{
  "packageId": "author.mod",
  "batch": 3,
  "assessor": "<agent/model id>",
  "assessed_utc": "2026-10-11T00:00:00Z",
  "facts_generated": "<facts/session_context.json universe_generated>",
  "adds": {"content": "...", "functionality": "...", "art": "...", "confidence": "MEASURED|INFERRED"},
  "verdict": "KEEP | KEEP-TEMPORARILY-THEN-PHASE-OUT | REPLACE-NOW-WITH-OUR-OWN | ELIMINATE-COMPLETELY",
  "verdict_reason": "one paragraph, citing fields and brief sections",
  "verdict_confidence": "MEASURED | INFERRED | UNVERIFIED",
  "holds_it_in": ["dependants / our patches / save placement (UNMEASURED if not checked)"],
  "replacement_path": "item ID or 'unfiled: NAME' or null",
  "problems": [{"kind": "log_noise", "severity": 2, "basis": "4 distinct errors, e.g. ...",
                "confidence": "MEASURED", "evidence": "log_error_samples[0]"}],
  "source": {"available": "yes | no | unverified", "url": "...", "kind": "github|...", "license": "...",
             "last_push": "...", "confidence": "MEASURED|INFERRED|UNVERIFIED"},
  "fit": "resonant | neutral | dissonant",
  "fit_reason": "cite SCENARIO_BRIEF.md section(s)",
  "retirement_cost": {"dependants": [...], "save_placement": "UNMEASURED|none|...", "parentname_risk": "..."},
  "open_questions": ["for the checker / owner card"],
  "card_worthy": false
}
```

`card_worthy: true` marks a mod whose verdict needs the owner (a ruling gap, a contradiction, or a
REPLACE/ELIMINATE of something a design doc names). The second checker re-derives every MEASURED claim from
the facts record and may only downgrade confidence or flag; it never silently changes a verdict.

## 7. Human record template (one section per mod, generated from the assessment)

```markdown
### <name> (`<packageId>`)
**Verdict:** <verdict> (<confidence>) · **Fit:** <fit> · **Source:** <url or none> (<kind>, <license>)
**Adds:** <content / functionality / art, one line each>
**Why:** <verdict_reason>
**Problems:** <kind sev basis> · ... (U = unmeasured)
**Holds it in / exit:** <holds_it_in> -> <replacement_path>
**Open:** <open_questions>
<sub>facts: batch NN · mod_facts.jsonl <facts_generated> · assessed by <assessor> <date></sub>
```

## 8. Worked examples (from the real facts record)

Built from `facts/mod_facts.jsonl` of 2026-10-10 by the stage-0 author (batch numbers as generated that day; a refresh may renumber), to show the shape and the evidence
discipline. They are illustrations, not rulings; the stage-1 assessor of the owning batch re-assesses them.

### Example 1: Harmony (`brrainz.harmony`), batch `frameworks_libraries`

```json
{"packageId": "brrainz.harmony", "batch": 1, "assessor": "stage0-example",
 "adds": {"content": "none (def_total 0)", "functionality": "the runtime patching library every Harmony mod calls (dll_flags: harmony; 0Harmony.dll + HarmonyMod.dll loaded)",
          "art": "none (2 images, 0.9 MB est)", "confidence": "MEASURED"},
 "verdict": "KEEP",
 "verdict_reason": "Load-order position 2 and a dependency of many universe mods, including our own (dependants_ours lists mandrake.rm.aftermath, .bazaar, .biomes, .explosivegrowth, .explosiveknockback, .flowworks ...). Removing it removes every Harmony mod. No plan exists to replace it and none should.",
 "verdict_confidence": "MEASURED",
 "holds_it_in": ["dependants (About.xml modDependencies) incl. our own mods"], "replacement_path": null,
 "problems": [{"kind": "log_noise", "severity": 0, "basis": "0 error occurrences in the 550-mod session", "confidence": "MEASURED", "evidence": "log_error_occurrences"},
              {"kind": "tps", "severity": "U", "basis": "per-mod TPS UNMEASURED; it is the patch mechanism, cost lands on the patching mods", "confidence": "UNVERIFIED", "evidence": "tps_cost"}],
 "source": {"available": "yes", "url": "https://github.com/pardeike/HarmonyRimWorld", "kind": "github", "license": "MIT", "last_push": "2026-08-16", "confidence": "MEASURED"},
 "fit": "neutral", "fit_reason": "Infrastructure; brief §4 test 1-2 (something of ours depends on it).",
 "retirement_cost": {"dependants": ["(most code mods)"], "save_placement": "none (no defs)", "parentname_risk": "none"},
 "open_questions": [], "card_worthy": false}
```

### Example 2: Star Wars Animal Collection (`mlie.starwarsanimalcollection`), batch `star_wars_donors`

```json
{"packageId": "mlie.starwarsanimalcollection", "batch": 6, "assessor": "stage0-example",
 "adds": {"content": "1,578 declared defs: SoundDef 589, ThingDef 454, PawnKindDef 160, BodyDef 102, IdeoIconDef 90 (defs_by_type) - a Star Wars creature roster",
          "functionality": "XML only (dll_count 0); 54 patch ops into Core/Odyssey/biome mods",
          "art": "in AssetBundles (disk_by_kind.assetbundles 32.3 MB), so texture_decoded_mb_est (5.0) UNDERSTATES it: the header census cannot see inside bundles",
          "confidence": "MEASURED"},
 "verdict": "KEEP-TEMPORARILY-THEN-PHASE-OUT",
 "verdict_reason": "Genuine Star Wars IP (brief §2 tiers; §4 test 7), so its future is RSW_ ports routed through Utinni patches. What holds it in today is MEASURED: our mods reference its defNames 3,439 times (patched_by_ours_refs: mandrake.rut.patches 1,838, mandrake.rut.doctrine 624, mandrake.rsw.swbestiary 498 ...) and two of ours declare it a hard dependency (dependants_ours: mandrake.rsw.shokk, mandrake.rsw.swbestiary). The absorption item MLIE_FAUNA_ABSORPTION_1 is CLOSED, yet these edges remain, so the exit is not finished.",
 "verdict_confidence": "MEASURED",
 "holds_it_in": ["dependants_ours: mandrake.rsw.shokk, mandrake.rsw.swbestiary", "3,439 xpath defName references from our patches", "placed creatures in the campaign save: UNMEASURED"],
 "replacement_path": "MLIE_FAUNA_ABSORPTION_1 (closed) / STARWARS_DONOR_SUNSET_1 (closed); remaining edges: unfiled: MLIE_DONOR_EDGES_STILL_BITE",
 "problems": [{"kind": "interaction", "severity": 2, "basis": "patched_by_ours_refs 3,439", "confidence": "MEASURED", "evidence": "patched_by"},
              {"kind": "memory", "severity": "U", "basis": "art is in 32.3 MB of AssetBundles; decoded size not measurable from headers", "confidence": "INFERRED", "evidence": "disk_by_kind"},
              {"kind": "log_noise", "severity": 0, "basis": "0 error occurrences", "confidence": "MEASURED", "evidence": "log_error_occurrences"}],
 "source": {"available": "yes", "url": "https://github.com/emipa606/StarWarsAnimalCollection", "kind": "github", "license": "MIT", "last_push": "2026-06-07", "confidence": "MEASURED"},
 "fit": "resonant", "fit_reason": "Star Wars creatures fit the setting (brief §1, §4 test 3) but as IP they belong in the RSW_ tier via ports (§2, §3); donor art is not kept (§4 test 8).",
 "retirement_cost": {"dependants": ["mandrake.rsw.shokk", "mandrake.rsw.swbestiary"], "save_placement": "UNMEASURED", "parentname_risk": "check our defs inheriting its abstract bases before removal"},
 "open_questions": ["Why do 3,439 references remain after the absorption item closed? A checker should split them into ported-twin wiring vs live dependence."],
 "card_worthy": true}
```

### Example 3: Worldbuilder (`ferny.worldbuilder`), batch `code_tweaks_qol_ui`

```json
{"packageId": "ferny.worldbuilder", "batch": 5, "assessor": "stage0-example",
 "adds": {"content": "8 defs (ScenPartDef 3, SoundDef 2, FeatureDef 1, ThingDef 1, WorldObjectDef 1)",
          "functionality": "world customisation editor ('This mod allows to customize worlds.'); one DLL with Harmony and a settings screen (dll_flags); 16 static ctors",
          "art": "35 images, 78.4 MB decoded estimate (INFERRED)", "confidence": "MEASURED"},
 "verdict": "KEEP-TEMPORARILY-THEN-PHASE-OUT",
 "verdict_reason": "It is an authoring tool for the one hand-made world (design/Jawa/worldbuilding/fall_line_major_region_label.md says labels were authored with it), and players never generate or edit worlds (brief §2: no worldgen; players receive the frozen savegame). It is needed while the world is being authored and painted (the planet is painted once, at the end), and has no player-facing purpose after that. Nothing in the universe depends on it (dependants: []).",
 "verdict_confidence": "INFERRED",
 "holds_it_in": ["world authoring until the final paint pass", "its FeatureDef/WorldObjectDef may be referenced by the world save: UNMEASURED"],
 "replacement_path": "unfiled: WORLDBUILDER_RETIRE_AFTER_PAINT_ONCE",
 "problems": [{"kind": "log_noise", "severity": 1, "basis": "1 distinct error: 'Exception in ConfigErrors() of CannibalPirate: NullReferenceException' (frame evidence; the deploy log names a Worldbuilder IsMemeAllowedFor postfix)", "confidence": "MEASURED", "evidence": "log_error_samples[0]"},
              {"kind": "complexity", "severity": 2, "basis": "Harmony DLL, 16 static ctors", "confidence": "MEASURED", "evidence": "dll_flags, static_ctors"}],
 "source": {"available": "yes", "url": "https://github.com/fernyrepos/Worldbuilder", "kind": "github", "license": null, "last_push": "2026-09-12", "confidence": "MEASURED"},
 "fit": "neutral", "fit_reason": "Tooling for the owner's authoring, not player content; brief §2 (no worldgen) makes it dissonant only if exposed to players.",
 "retirement_cost": {"dependants": [], "save_placement": "UNMEASURED (world features in the frozen world)", "parentname_risk": "none known"},
 "open_questions": ["design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md says ferny.Worldbuilder is NOT in activeMods, but FULL.LATEST lists it at position 372: doc or list is stale (do not resolve here)."],
 "card_worthy": true}
```
