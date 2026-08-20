# Doc audit — `design/`, 2026-08-20

**Question, the owner's words:** *"I mostly wanted an audit over all these .md files we
keep updating. They're expensive to keep in that way. I wonder if some of them are
redundant and could be collapsed."*

**Scope.** `design/` excluding the faction cluster (`design/**/faction*`,
`force_users_build_spec.md`, `FACTION_SPEC.md`, `pawnkind_roster.md`) — another worker
owns those. **ANALYSIS ONLY: nothing in the repo was changed by this audit.**

---

## 0. The measurement that answers the question

| | |
|---|---|
| `.md` under `design/` | **115 files, 45,474 lines** — 59% of the repo's 76,779 tracked doc lines |
| of those, **in scope** (non-faction) | **105 files, 37,777 lines** |
| doc-writes since the 2026-08-13 re-init (7 days) | **639** across **122** distinct design docs — ~91/day |
| of those, in scope (non-faction) | **514** |
| the single most-rewritten file in the repo | `design/V2_DREAMS.md` — **41 commits**, 1,794 lines |

🔑 **The expense is not the file count. It is that ~91 doc-writes a day are spread over
122 files with no index and no single owner per subject.** Where a subject is split
across four files, every ruling costs four edits — or, more often, costs one edit and
leaves three files wrong. That is what the duplication section below is actually
measuring.

⚠️ **A structural cause, cheap to fix:** `design/README.md` defines the tier rule
(`Jawa/` vs `RimMandrake/`, the promotion test) but **contains no index of the 115
documents**. An agent that cannot find the existing doc writes a new one. Six of the
duplications below have that shape.

---

## 1. The write-once files

**Correction to the brief's framing, and it matters.** The repo-wide figure is **75
files that still exist** with exactly one commit (2 of the 77 were deleted). But
`7e98004` — *"Repo re-initialised: option-B tier structure, history archived"*,
2026-08-13 — **added 204 `.md` files in a single commit**. For any file whose only
commit is `7e98004`, "write-once" means *imported at re-init and untouched for seven
days*. Their earlier history exists but was archived out of this repo.

⇒ **Write-once here measures dormancy since 2026-08-13, not that a doc was written
casually in one pass.** It cannot distinguish a doc that was refined for a week before
the re-init from one dashed off. The reference check does the deciding, exactly as the
brief instructed.

**Distribution of the 75:** `design/Jawa` 22 · `src/RimMandrake` 9 · `skills/skills-workspace` 7 ·
`infrastructure/output` 5 · `skills/rimworld-modding` 4 · `design/RimMandrake` 3 · rest ≤3 each.
**`design/` holds 25 of 75 — one third.**

### The 25 in-scope, classified

| class | count | files |
|---|---|---|
| **(a) finished — LEAVE** | **19** | the nine `INHABITED_CAST_*.md` · `INHABITED_SPECIES_TEXTURE.md` · `setting_physics.md` · `biome_terrain_palette.md` · `data/mech_control_axes.md` · `data/ideology_palette.md` · `ship_build/ship_build.md` · `agent_supersession_audit.md` · `yautja_mod_audit.md` · `parked_mod_concepts.md` · `jawa_dialogue_source_audit.md` |
| **(b) abandoned** | **2** | `design/RimMandrake/ollama.md` · `design/Jawa/build_plan.md` |
| **(c) absorbed** | **1** | `design/Jawa/first_live_access.md` |
| **(d) orphan** | **3** | `design/RimMandrake/coastal_mesa_rationale.md` · `design/Jawa/carbonite_trophy_mod.md` · `design/Jawa/art/graphic.md` |

🔴 **Only 6 of 25 are candidates for anything, and 3 of those are one-page files.
Write-once was a false lead — the corpus's cost is duplication, not dormancy.**

**Two findings inside the class-(a) group that reframe it:**

- **Nine of the 19 are `design/Jawa/bridge/INHABITED_CAST_*.md`, and every one was
  committed TODAY (2026-08-20).** They are cast 01–09, one per faction, numbered, with
  distinct content per file (the Hutt Cartel's Kessek Refinery; the Jawa Trade Moot's
  sandcrawler *Tukkat-Nur*; the Wildsteam Clan's Stairs of Var Ullu). **This is an
  active workstream one day old, not nine redundant files.** Write-once here means
  "written this morning". They would have scored identically to an abandoned doc.
- **`ship_build/ship_build.md` and `data/ideology_palette.md` are MACHINE-GENERATED**
  (`rimbench/shipbuild.py` and `Utils/ideology_palette.py`, both carrying
  "regenerate, never hand-edit" headers). One commit is exactly what a derived artifact
  looks like. ⚠️ But `design/README.md` says plainly: *"Anything a machine generates. If
  a script writes it, it is not design."* **Both violate the tier rule they sit under.**

---

## 2. Subject clusters with 3+ documents

### 🔴 2.1 The gravship — 11 documents, and they CONTRADICT each other

This is the worst cluster in `design/`, and the problem is not redundancy — it is that
the same constant is maintained in four places and the four have drifted.

Genuinely distinct, each answering its own question, keep all six:
`gravship_pursuer_mechanism.md` (who pursues) · `hiding_the_gravship.md` (the hide verb) ·
`ship_legacy_armoury.md` (lasers as inherited tech, 86 lines, overlaps nothing) ·
`art/gravship_wear_pass.md` (colour and silhouette) · `gravship_flight_invariants.md`
(launch validator) · `Gravship_Campaign_Planning_Discussion_2026-08-02.md` (the pre-Jawa brief).

**The overlap is the four geometry docs**, a real chain — `ship_designs.md` (topology)
→ `ship_deck_plan.md` (wing map) → `ship_build/ship_build.md` (tile sheet) →
`row8_build_order.md` (execution) — that restates the same constant set three to four
times each.

| constant | disagreeing homes |
|---|---|
| 🔴 **Grav-field extender count** | **7** in `ship_designs.md:15`/`:90` and `ship_deck_plan.md:136`; **8** in `ship_build/ship_build.md:84` and `row8_build_order.md` |
| 🔴 **Heatsinks** | **4** (`ship_deck_plan.md:122`) vs **8** (`ship_build.md:254`) vs **6** (`ship_bridge.json` / row8 D3) |
| 🔴 **Radii** | **34 / 30 / 12** in `ship_designs.md:103`, `row8_build_order.md:102-110`, `gravship_flight_invariants.md` §6 — but `ship_deck_plan.md` still says **19 / 16 / 6** |
| 🔴 **Tile cap** | `ship_designs.md:101` says **6,632** and `ship_designs.md:113` says **4,800** — *inside one file* |
| **Engine support** | **632.79541** in `row8_build_order.md:112`, superseded to **4500** in `gravship_flight_invariants.md` |
| #15 stat block (4,057 / 4,800 tiles, cargo 1,443, factory 1,182, shuttle 420) | `ship_designs.md:15`+`:504` · `ship_deck_plan.md` · `ship_build.md:20` · `row8_build_order.md:312` |
| Zone roster A–F/G/H/K/M/R/S/T/U/W, "hot wings B and E outboard" | `ship_deck_plan.md` §2 · `ship_build.md` §Zone map · `row8_build_order.md` §6.2 |
| Heat doctrine (9.9-tile banks, 500% burst) | `ship_deck_plan.md:123`/`:167` · `ship_distinctive_features.md:127-131` |
| "~170 pre-rusted `Ancient*` wreck props" | `ship_deck_plan.md:458` · `gravship_wear_pass.md:28` |
| Floors-survive-export finding | `gravship_flight_invariants.md` §7 · `row8_build_order.md` §7 |

🔑 **`row8_build_order.md` §6.4 is already a hand-written reconciliation table for
exactly these conflicts.** The duplication is known, was patched by adding a twelfth
document rather than by removing the second copy, and is still unresolved.

**Verdict: real division of labour for 6 docs, same subject written four times for the
geometry chain.** One of those four must become the sole home of every ship constant.

### 🔴 2.2 Mod curation — 15 documents, five of them "cherrypick", and it is not a pipeline

- `cherrypick_inbox.md` → `cherrypick_resolved.md` **is** a real pipeline (resolved:3
  names inbox as its input; 15 shared identifiers pass through). ⚠️ It leaks: inbox §E's
  **29 biome verdicts never arrive**, and `cherrypick_resolved.md` §4 still says "no
  verdicts yet".
- **resolved → `cherry_picker_killlist.md` is empty in both directions** — 5 shared
  tokens, all of them def *type* names (`PawnKindDef`, `FactionDef`), not defNames. The
  killlist is an **older parallel list (2026-08-02) that grew its own competing
  "§0 THE INBOX" on 2026-08-12**. That is a second inbox beside the first.
- `outer_rim_cherrypick_list.md` is **not a cut list at all** — an additive shopping
  list of Outer Rim defs to lift into a sub-mod. Filed in the wrong cluster by its name.
- `CHERRYPICK_AGENDA.md` is referenced by no design doc; the only mention repo-wide is
  `infrastructure/state/queue/HUMAN.md:26`, saying it **"is stale and will waste his time."**

**Verdict: one working pipeline plus two orphans plus a misnamed file.** Not four
divisions of labour.

### 2.3 Droids and machines — 8 documents, one omnibus that is known-wrong

`restraining_bolt_technical.md` (IL-level spec), `droid_chassis_coverage.md` (silhouette
procurement) and `data/mech_control_axes.md` (93-row data) are genuinely distinct.

🔴 **`design/Jawa/droid_ruling.md` is a 658-line omnibus that `droid_taxonomy.md` was
written to correct — and the correction was never merged.** `V2_DREAMS.md` B19 already
records that it *"states a mechanism that is not in the defs"*. It still heads a section
"**JDS droids blow up, and that is the point**" under a banner reading *"🔴 OWNER'S
RULING — CLOSED … read this before anything below it"*, and `V2_DREAMS.md` §1 still
cites it. The real mechanism measured in `droid_taxonomy.md` (no `deathAction`, no
`CompExplosive`, no DLL — it is `fleshType Mechanoid` → `deathOnDownedChance 1.0`) has
had no content edit merged since 2026-08-13. `droid_taxonomy.md` files the correction
as **"Not my file"**; nobody picked it up.

**⇒ The most authoritative-looking doc in the cluster is the wrong one. This is the
single highest-value fix in the audit and it is not a deletion.**

### 2.4 Ideoligion — 6 in-scope documents, one holding a dead second religion

Real split between `jawa_xenotype_and_religion.md` §2.0b (pantheon lore) and
`divine_satiation_engine.md` (mechanics), enforced by per-god pointers.
`review/religions_repair_sheet.md` covers the 11 NPC religions — different subject.

🔴 **But §2.1–§2.6 of `jawa_xenotype_and_religion.md` is a complete second, incompatible
ideoligion spec** — "The Articles of Passage", memes Nomad + Tunneler, relic "The First
Fusioncutter" — against `ideoligion/APPROVED.md`'s "The Salvation"
(`AM_Structure_Scavenger · Trader · VME_Scrapper · VME_Nomad`, Founding Ion Blaster).
Only a top banner marks it stale; the six dead sections are still there in full.

`divine_satiation_engine.md` is a **live but unimplemented** spec — no `.cs` anywhere
contains "satiation" — re-anchored by the 2026-08-15 ruling, so design-only, not dead.

### 2.5 Planet / worldmap / biomes — 23 documents, two hubs

`ASHKARR_WORLD_DEFINITION.md` (25 referrers) and `desert_world_design.md` (26) are the
hubs and are doing their job. See §3 for the worldgen-ruling status and §4 for the
duplications.

### 2.6 LLM / voice — 7 documents for work that is parked and unbuilt

`src/` implements **none** of it: no Ollama client, no TTS, no RimTalk hook. What is
built is the deterministic lane — `src/Jawa/JawaVoice/` (11 SpeakUp XMLs, ~5,900 lines)
generated by `src/RimMandrake/Utils/jawaese.py`.

🔴 **`llm_stack_assessment.md`'s premise is factually dead.** It reasons from "28 LLM
mods installed and ACTIVE"; the live `ModsConfig.xml` has **582 mods and zero RimTalk
packageIds** — only `kilokio.rimai.framework/.core`, `jpt.speakup`, `depscian.rimtunes`.
`llm_voice_preauthoring.md` Part B targets **RimDialogue**, which `required_mods.md`
verified does not exist.

🔴 **None of the five `RimMandrake/` LLM docs contains the string "v2" or "2026-08-15".**
The owner's ruling *"All in-game LLM generation is [v2]"* lives only at
`design/Jawa/worldbuilding/the_forgotten_war.md:427` and `V2_DREAMS.md:1066` — and it
**contradicts `design/Jawa/build_plan.md:13`**, which is unmarked.

### 2.7 Art pipeline — 7 documents, a real division of labour

**No collapse warranted.** Each owns something distinct: `SALVAGE_PALETTE.md` is a
**generated** deconstruction-yield census (`🔴 GENERATED FILE. Do not hand-edit`, from
`design/Jawa/art/salvage_filter.py`) and contains no hex codes at all — "palette" is a
misnomer, not a duplicate · `c7_directional_triage.md` is a v2-tagged defect register ·
`gravship_wear_pass.md` is the wear brief · `graphics_overhaul_protocol.md` is the
method · `mods/repurposed_graphics.md` is a licensing register.

- ✅ **`design/Jawa/art/codex_imagegen_origin_plan.md` is already gone** — moved to
  `infrastructure/disposing/` and deleted today in `9181ed0`, because *"the imagegen route
  shipped as the `generating-images` skill"*. Class **(c) absorbed, already actioned.**
- 🔴 **`design/Jawa/art/graphic.md` should follow it.** It is a one-shot ChatGPT prompt
  ("Art request — Gamorrean head sprites… upload this file to ChatGPT together with the
  whole `seed/` folder"). `skills/generating-rimworld-sprites/SKILL.md` now teaches the
  same ground generically **plus** a validator (`scripts/validate_sprite.py`) that
  `graphic.md` predates. One inbound ref. Class **(c) absorbed → delete.**
- 🔴 **The cluster's real defect is a missing ruling, not a surplus doc.** The standing
  **art freeze** — *"stop fixing art until the owner can verify the art doesn't work;
  the gate is the owner's own eyes… the PREMISE is what is suspect"* — lives only in
  `design/V2_DREAMS.md:358` and `src/DEPLOY_HOLD.txt:44`, **and in none of the art docs
  it gates**. `c7_directional_triage.md` is parked by that freeze and never says so.

### 🔴 2.8 Bridge / INHABITED — 13 documents, and the capability roster exists eight times

**Ground truth, counted from source** —
`grep -ho '"jawa/[a-z_]*"' src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs | sort -u | wc -l`
= **106 tools.**

| file | claims | verdict |
|---|---|---|
| `infrastructure/state/observed/LIVE.md` | **106** | ✅ correct |
| `skills/rimbridge-companion/SKILL.md:18` | "91 tools already ship" | stale by 15 |
| 🔴 `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md:14` | "Already built: **57** tools" | **stale by 49** |
| `skills/rimbridge/references/capability-matrix.md` | 20 `jawa/` + stock | frozen 2026-08-11 |
| `skills/rimbridge/references/{pawn,map,world}-authoring.md` | 14 / 15 / 25 | world-authoring's header contradicts its own 27-item block |

Concrete divergence: `jawa/pawn_psychic`, `pawn_pregnancy`, `pawn_mental`, `pawn_romance`
exist in source and in `LIVE.md` and are **absent** from `pawn-authoring.md`. Worse,
`BRIDGE_CAPABILITY_ROSTER.md` still lists `pawn_mental_state`, `add_gas`/`clear_gas`,
`create_zone`, `build_batch`, `prefab_capture` and `set_pawn_age` as **unbuilt proposals
to cull** — **all six are built and proven** (`669be9e`).

⇒ **`LIVE.md` is the only correct copy and it is derived from source.** The design-tier
roster is not a second opinion, it is a stale one.

**The nine `INHABITED_CAST_*.md` are a deliberate series and share almost no boilerplate.**
Measured: the format-spec block appears in **2 of 9** files; seven carry zero.
🔑 **The defect is the opposite of duplication — cast 01 is doing double duty as the
format spec.** `INHABITED_CAST_HUTT.md:25-48` carries "The format — it is a PAWN, not a
portrait", the pawn schema and a verified `TraitDef` list, material whose proper home
already exists at `INHABITED_DESIGN.md` §5.8 "THE ATTACHMENT FORMAT". Both files
independently carry the **⛔ never-`Pyromaniac`** ruling
(`INHABITED_CAST_HUTT.md:41` and `INHABITED_DESIGN.md` §5.8) — a *ruling* in two places.

**`design/RimMandrake/rimbridge.md`** (12 refs): §0–§2c are unique **provenance**
(RimBridgeServer identity, MIT licence, Workshop ID) — keep; §3–§5 are superseded by
`skills/rimbridge/SKILL.md` — retire. ⛔ **§6 holds a scope ruling found nowhere else:**
the bridge is an *authoring* tool and *"must not become a way for the colony to
self-upgrade."*

---

## 3. `V2_DREAMS.md` — is it working as a parking lot?

**41 commits, 1,794 lines — the most-rewritten document in the repo.**

### ✅ On the worldgen ruling it is working, and better than the brief expected

The ruling is the **first thing in the file** (lines 3–27, verbatim quote plus the
OUT/IN split), and the file **strikes rather than parks**, exactly as instructed:

| item | state |
|---|---|
| "Programmatic worldgen" (line 1091) | **⛔ DEAD, 2026-08-15 — "was: parked in full"** |
| "Retired from v1 — worldgen is manual" (line 732) | **🔴 DEAD, NOT PARKED** |
| `~~B2 ocean-shaping mod~~ · ~~C15 seed sweep~~ · ~~C16 score the ocean~~ · ~~D2 throwaway worlds~~ · ~~D4 half ocean~~` (line 748) | struck through, ⛔ DEAD, with the deleted artifacts named (`JawaSeaShaper`, `sea_seed_sweep.py`, `worldgen_sea_spec.md`) |
| `~~gand-and-chagrian-missing-artwork~~` (1765) | ⛔ WITHDRAWN |

It even draws the **hard distinction correctly** at lines 1442–1444: *"WORLDgen is OUT
of every version … LOCAL map generation (the 250×250 colony map) is not covered by the
worldgen ban"* — so `## v2 concept: iteratable map generation against validator
criteria` (1424) survives **deliberately**, not by oversight.

⇒ **Nothing dead-by-the-worldgen-ruling is still parked as live. Do not strike anything
further on those grounds.**

### 🔴 Where it is NOT working as a parking lot

**It declares:** *"An append-only register of deferred work. It is not a queue. Nothing
in here is scheduled, assigned, or owed."*

**Three things in it are scheduled, and two carry deadlines:**

1. **Line 864** — *"🔴 **THIS IS NOT A FREE v2 DECISION — IT HAS A v1 DEADLINE.**
   `GiantAnt_Faction` sits on `WORLDGEN_FACTION_CHECKLIST.md` Section 2, marked untick.
   A faction absent at world creation can never be added later."* A **v1 deadline**, in
   the file that says nothing here is owed.
2. **Line 1548, B66** — *"🔴 Two generator defects, one regenerate — **RIDE THIS WINDOW
   or lose a load**"*, 188 lines, carrying a live 2026-08-15 owner ruling (*"Remove any
   genes from our implementation of the xenotypes that aren't supported"*).
3. **Line 1335, C42** — *"⚠️ **This one bakes at world creation**"*.

🔑 **The one-hand-made-frozen-world rule makes "parked" mean something it does not mean
elsewhere: a v2 item that must be decided at the world screen is a v1 item.** Three of
them are sitting where the file's own header says nobody will look until v1 has shipped.
**These three should leave `V2_DREAMS.md` for a v1 surface. That is the fix, and it is
the file's real defect — not the worldgen items.**

### 🔴 It is carrying drained queue plumbing, including completed work

The file was created by draining `queue/BUILD.md`, `CHECK.md`, `DECIDE.md` and
`TODO_v2.md` **verbatim**, `spec:` / `verify:` / `criteria:` fields and all. Consequences:

- **One subject appears four times.** Scrapfields `minSpacing` 4→1 is **B3** (line 56),
  **C3** (180), **C32** (295) and **D-R4** (305) — the original queue's build /
  check / deploy / decide split, imported wholesale into a file that has no queue.
- **Completed items are parked as if pending.** B3's own body reads *"verify: `-> VERIFIED
  in sync`; deployed `JawaScrapfields.xml` carries `minSpacing 1`"*, and C32's heading is
  literally *"Scrapfields `minSpacing 1` **is deployed**"*. Done work occupying the
  deferred register.
- ~380 of 1,794 lines (21%) are B*/C*/D* entries in queue format with deploy commands and
  `Player.log` line numbers — operational detail with no operational home.

**Verdict: working as a parking lot for its worldgen discipline, failing as one on
three counts** — deadlined items filed as undeadlined, one subject in four entries, and
completed work still parked.

---

## 4. Duplication across design docs — the master list

🔴 = the two copies **disagree**. Those are not redundancy, they are defects: a reader
who lands on the wrong copy acts on a wrong number.

### 4.1 Contradictions (fix these; deleting a file is not the fix)

| fact | copy A | copy B | note |
|---|---|---|---|
| 🔴 **Tidal-lock axis** | `ASHKARR_WORLD_DEFINITION.md:52-78` — **point-keyed**, `effectiveLat = acos(cos x · cos y)`, read from `PlanetTypeDef.cs`; correlation **−0.98 arc / +0.10 latitude** | `tidally_locked_world.md:152` — *"🔴 Correction: **LATITUDE IS THE AXIS**"*, table at `:158-166` | **The single highest-risk defect in `design/`.** ASHKARR §10 item 4 declares it CLOSED; `tidally_locked_world.md` carries **no banner**, and **running code reads it**: `src/RimMandrake/Utils/ashkarr_settle.py` and `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml`. Same file also supplies a *live* arc-aware faction table cited by `ASHKARR:212` — so it is half-current, half-superseded |
| 🔴 Lock is a POINT vs a BAND | `ASHKARR:27-31,52-78` | `tidally_locked_world.md:152` | same root cause |
| 🔴 Grav-extender count | **7** — `ship_designs.md:15,90` · `ship_deck_plan.md:136` | **8** — `ship_build.md:84` · `row8_build_order.md` | |
| 🔴 Heatsinks | **4** `ship_deck_plan.md:122` | **8** `ship_build.md:254` / **6** row8 D3 | three-way |
| 🔴 Radii | **34/30/12** `ship_designs.md:103`, row8`:102-110`, `gravship_flight_invariants.md` §6 | **19/16/6** `ship_deck_plan.md` | |
| 🔴 Tile cap | **6,632** `ship_designs.md:101` | **4,800** `ship_designs.md:113` | *inside one file* |
| 🔴 Scald outflow | **~32,000** `ASHKARR:137` | **~5000** `the_one_map.md:148` | |
| 🔴 `AB_GelatinousSuperorganism` | **CUT** `biome_terrain_palette.md:100` | on the terminator — `the_one_map.md:135`, `ASHKARR:200` | |
| 🔴 `Savanna` / `TropicalRainforest` | **blacklisted** `ASHKARR:207` | weighted **4** and **1** — `biome_and_fauna_roster.md:141,172` | roster has 1 referrer; almost nobody reads the file holding the conflict |
| 🔴 Dynamic AI Sculptures | **✅ ACCEPTED** `mods/mod_config_rulings.md:25` | **FORBIDDEN** `mods/forbidden_mods.md:213` | `required_mods.md:1514` marks it superseded; `mod_config_rulings.md` contains **zero** supersession markers anywhere |
| 🔴 KotOR Weapons | backbone — `mods/armoury_keeplist.md:137` | *"DECLINE for the lean stack"* `required_mods.md:651` | unmarked |
| 🔴 Anomaly DLC | *"⛔ BENCHED"* `required_mods.md:541` | owner: *"I did NOT agree to that anomaly ruling"* — `cherrypick_inbox.md` §A | |
| 🔴 `RG_BoilingForest` cut | `REGROWTH_BOILING_LIFT_SPEC.md:3` · `CHERRYPICK_AGENDA.md:109` · `V2_DREAMS.md:1533` | *"Hold until we can explore it"* `cherrypick_inbox.md:183` | **four** homes |
| 🔴 `MemeCountRangeAbsolute` | slider to **8** — `ideoligion/APPROVED.md` | `IntRange(1,4)` — `review/religions_repair_sheet.md` §0 | |
| 🔴 Bolt goodwill curve | `offset = −2.5×N`, clamp −100, 5-row table — `restraining_bolt_doctrine.md` | `maxGoodwill = 100 − 2.5N`, floor −70, **ceiling not offset**, 4-row table — `restraining_bolt_technical.md` | **doctrine has no pointer to technical**, and doctrine is the doc cited by `faction_religions_spec.md` and `skills/rimworld-ideoligion/references/rubric.md` |
| 🔴 JDS droid explosion mechanism | `droid_ruling.md` §6 — under a *"OWNER'S RULING — CLOSED, read this before anything below it"* banner | `droid_taxonomy.md` — measured: no `deathAction`, no `CompExplosive`, no DLL; it is `fleshType Mechanoid` → `deathOnDownedChance 1.0` | already filed as `V2_DREAMS.md` B19; `droid_taxonomy.md` files it as **"Not my file"** and nobody picked it up |
| 🔴 Bridge tool count | **106** (source; `LIVE.md`) | **57** `BRIDGE_CAPABILITY_ROSTER.md:14` · **91** `skills/rimbridge-companion/SKILL.md:18` | plus six built tools still listed as *unbuilt proposals to cull* |
| 🔴 Cherrypick state | *"the cherrypick is **FROZEN** for v1"* `forbidden_mods.md:261` | nine open `☐ PASS` rows — `CHERRYPICK_AGENDA.md` | |
| 🔴 Save-bake model | *"SUPERSEDED 2026-08-19 — there is no bake step"* `Custom_World.md:60` | *"Bake the scenario into a starting save… Distribute save + mod-list"* `Custom_World.md:82`, `:108` | *inside one file*, live instructions contradicting their own banner |
| 🔴 LLM timing | all in-game LLM generation is `[v2]` — `the_forgotten_war.md:427`, `V2_DREAMS.md:1066` | `design/Jawa/build_plan.md:13` | build_plan unmarked |
| 🔴 `VEE_*` landmarks | audited + banned `ASHKARR:719-720` | *"unaudited"* `tile_augmentation_catalogue.md:58,275` | |
| Water fraction | **8.6%** `the_one_map.md:130` | **8.1%** `ASHKARR:725` | drift |
| Biome roster size | **57** `biome_and_fauna_roster.md:112` · **66→36** `biome_review_comments.md:3` · **26** `tidally_locked_world.md:397` · 14-row census `ASHKARR:190` | | no shared denominator |
| Mod-list size | *"575 frozen"* `CHERRYPICK_AGENDA.md:53` | live `ModsConfig.xml` = **582** | |
| Ideology palette currency | `data/ideology_palette.md` dumped 2026-08-14 against **585** mods | live list is **582** | generated, stale |

### 4.2 Agreeing duplicates (cheap redundancy, real maintenance tax)

| fact | homes |
|---|---|
| **21,872 tiles / sub7 / cov 1.0** | `ASHKARR:41,284,420,474` · `the_one_map.md:24` · `WORLDMAP_BRIDGE_SURFACE.md:222,253` · `worldgen_interactive_def.md:21` — **4 files, 7 sites** |
| #15 stat block (4,057 / 4,800, cargo 1,443, factory 1,182, shuttle 420) | `ship_designs.md:15,504` · `ship_deck_plan.md` · `ship_build.md:20` · `row8_build_order.md:312` |
| Zone roster A–W, "hot wings B and E outboard" | `ship_deck_plan.md` §2 · `ship_build.md` §Zone map · `row8_build_order.md` §6.2 |
| Heat doctrine (9.9-tile banks, 500% burst) | `ship_deck_plan.md:123,167` · `ship_distinctive_features.md:127-131` |
| "~170 pre-rusted `Ancient*` wreck props" | `ship_deck_plan.md:458` · `gravship_wear_pass.md:28` |
| Floors-survive-export | `gravship_flight_invariants.md` §7 · `row8_build_order.md` §7 |
| **Verbatim identical paragraph** | `tidally_locked_world.md:490` ≡ `water_doctrine.md:223` |
| Named waters | `ASHKARR:95-97` · `the_one_map.md:131` |
| Rain-only-on-peaks | `hydrology_and_fire_ecology.md:75` · `ASHKARR:130` |
| Owner's "POWER DENSITY explodes" ruling + `explodeOnKilled`/`KillFinalize` | `droid_ruling.md` §6 · `droid_taxonomy.md` (verbatim) · `explosion_energy_model.md` — **three** homes |
| Three-droid-family verdict table | `droid_ruling.md` · `droid_taxonomy.md` |
| "Twelve factions, four already about machines, no thirteenth" | `what_the_machines_are.md` · `droid_chassis_coverage.md` |
| "THE NINE NOW LIVE IN THE SHIP" (owner, verbatim) | `jawa_xenotype_and_religion.md:590` · `divine_satiation_engine.md:706` · `the_forgotten_war.md` |
| Nine-god roster + epithets | `jawa_xenotype_and_religion.md` §2.0b · `divine_satiation_engine.md` §8 · `ideoligion/the_salvation_description.md` |
| The 400-word Salvation description | `Utils/build_salvation_rid.py` · `Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` · `The Salvation.rid` ×2 — **4 hand-maintained copies** |
| ⛔ never-`Pyromaniac` ruling | `INHABITED_CAST_HUTT.md:41` · `INHABITED_DESIGN.md` §5.8 |
| Sanguophage/Dirtmole/Highmate/Waster + the five reflavors | `cherry_picker_killlist.md` §2 · `required_mods.md:715` |
| VFE-Insectoids 2 strip · VGE `GR_*` strip · `OuterRim_A280Blaster` | `forbidden_mods.md:77,70` · `required_mods.md:453,455` · killlist |
| Droid Depot bolt-targeting bug | `droid_ruling.md` §8.2 · `restraining_bolt_technical.md` §5 |
| Scrapfields `minSpacing` 4→1 | `V2_DREAMS.md` **B3, C3, C32 and D-R4** — four entries, one file |
| "Faction Filter never existed" banner | byte-identical line 1 of `cherry_picker_killlist.md`, `outer_rim_cherrypick_list.md`, `forbidden_mods.md`, `world_interest_and_mech_danger.md` |

✅ **Not duplicated, and worth saying so:** the terrain palette is single-sourced at
`biome_terrain_palette.md:244-262`. The cross-reference *banners* (⭐ "the water cycle is
specced in…", ⭐ "the planet's HISTORY is in…") that appear in 3–4 files each are
**pointers, not copies** — that is the corpus working correctly, and it is the pattern
the fixes below should extend.

### 4.3 Dangling references — 28 `.md` filenames cited from `design/` that exist nowhere

`TODO_v2.md` (4 citing files) · `worldgen_sea_spec.md` (3) · `RimMaster.md` (2) ·
`MODLIST.md` · `faction_dossiers.md` · `candidate_factions.md` · `kolyska_ship_name.md` ·
`races.md` · `live_mod_inventory.md` · `_ideoligions.md` · `Alien_Bestiary_SW_Naming_v1.md` ·
`in_game_verification_checklist.md` · `resource_catalogue.md` · plus GABP-side names
(`tool-reference.md`, `lua-frontend-design.md`, `semantic-state-design.md`, `windows.md`,
`companion-dll-guide.md`, `architecture.md`, `autonomy.md`, `faq.md`, `borrowed-vacuum.md`,
`Event.md`, `SAVE_FORMAT.md`, `CHANGELOG.md`, `CREDITS.md`, `TODO.md`).

⚠️ **`design/README.md` cites `MODLIST.md` and then admits in the next paragraph that it
does not exist** — the file already models the right behaviour. The other 27 do not.

### 4.4 Two more orphans found outside the write-once set

- **`design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md`** — **0 inbound references**, yet
  edited 2026-08-20. Its own header claims it is load-bearing for R-H3's fire ecology,
  and nothing — no doc, no queue, no state file — points back at it. 🔑 **The more
  interesting orphan: `coastal_mesa_rationale.md` is dead and stationary;
  `PLANT_GROWTH_SPEC.md` is alive and unreachable.**
- **`design/Jawa/mods/world_interest_and_mech_danger.md`** (2026-08-03) §1 still
  recommends adopting Reinforced Mechanoids 2, Total Warfare and Mechanoid Invaders —
  flatly killed by *"Mechanoids are OFF"*. **No banner**, and still cited from
  `setup_checklist.md` and `desert_world_design.md`.

---

## 5. Target shape

🔑 **The honest headline: very little should be deleted.** Of the **105** in-scope documents the
audit found **3 clear deletions and about 5 merges**. The corpus is not bloated with
redundant files — it is **bloated with second copies of numbers inside otherwise
justified files**, and that is what makes it expensive to keep updating.

⛔ **Nothing below deletes an owner ruling that is not recorded elsewhere,
`the_one_map.md`, or measured evidence carrying commit hashes.** Every ruling listed as
single-homed in §2 and by the cluster passes is explicitly preserved.

### Tier 1 — costs ~2 hours, removes the defects, deletes almost nothing

These are the fixes that pay for themselves immediately, because each one is currently a
*wrong answer* a reader can act on.

| # | action | cost | saving |
|---|---|---|---|
| 1 | 🔴 **Banner `tidally_locked_world.md:152-166`** as superseded by `ASHKARR:52-78`, keeping the live arc-aware faction table | 10 min | stops **running code** (`ashkarr_settle.py`, `JawaWorld_BiomeMix.xml`) being reasoned about from the wrong axis. **Do this first.** |
| 2 | 🔴 **Merge `droid_taxonomy.md`'s measured mechanism into `droid_ruling.md` §6**, or demote §6's "CLOSED" banner | 20 min | retires `V2_DREAMS` B19 and stops the most authoritative-looking droid doc being the wrong one |
| 3 | 🔴 **Fix `BRIDGE_CAPABILITY_ROSTER.md`**: 57 → 106, and un-list the six built tools it still calls unbuilt proposals | 15 min | 8 disagreeing rosters → 1 correct one + pointers to `LIVE.md` |
| 4 | 🔴 **Reconcile the ship constants once** into `ship_deck_plan.md`, and replace every restatement in `ship_designs.md` / `ship_build.md` / `row8_build_order.md` with a pointer. Resolve extenders 7-vs-8, heatsinks 4/6/8, radii, and the 6,632-vs-4,800 cap inside `ship_designs.md` | 45 min | ~10 duplicated constants → 1; `row8` §6.4's reconciliation table becomes unnecessary |
| 5 | **Banner `mod_config_rulings.md:25`** (Dynamic AI Sculptures) and `world_interest_and_mech_danger.md` §1 (mechs are OFF) | 10 min | two unmarked live contradictions closed |
| 6 | **Delete §2.1–§2.6 of `jawa_xenotype_and_religion.md`** — the dead "Articles of Passage" ideoligion — keeping §2.0b's pantheon | 10 min | −~200 lines, removes a complete second religion spec |
| 7 | **Add an index to `design/README.md`** — one line per document, grouped by the 8 subjects in §2 | 30 min | 🔑 **the structural fix.** Six of the duplications above exist because the writer could not find the existing home |

### Tier 2 — the collapses, ~1 hour

| # | action | saving |
|---|---|---|
| 8 | **LLM/voice 7 → 3.** Keep `jawa_dialogue_source_audit.md` (10 refs; cited by `jawaese.py` and `JawaVoice/About.xml` — genuinely shipped) and `jawa_crew_personas.md` (8 refs). Fold `ollama.md` + `rimtalk_analysis.md` + `llm_stack_assessment.md` + `music_protocol.md` + `llm_voice_preauthoring.md` into **one `[v2]`-bannered doc**, preserving `ollama.md` §2.3's `D:\dev\` install-root rule | −4 files, ~−700 lines; and it finally records the `[v2]` ruling in the tier it governs |
| 9 | **Cherrypick 5 → 2.** Keep the working `cherrypick_inbox.md` → `cherrypick_resolved.md` pipeline (and drain inbox §E's 29 stranded biome verdicts into it). Fold `cherry_picker_killlist.md`'s §0 second inbox into the first; rename `outer_rim_cherrypick_list.md` to say it is an *additive* list; retire `CHERRYPICK_AGENDA.md`, which `queue/HUMAN.md:26` already calls *"stale and will waste his time"* | −2 files, one inbox instead of two |
| 10 | **Lift `INHABITED_CAST_HUTT.md:25-48`** (the format spec + `TraitDef` list + Pyromaniac ruling) into `INHABITED_DESIGN.md` §5.8, which already has the right home for it | cast 01 stops being load-bearing for casts 02–09 |
| 11 | **Delete `design/Jawa/art/graphic.md`** — absorbed by `skills/generating-rimworld-sprites/`, which also ships a validator it predates. Delete `design/RimMandrake/coastal_mesa_rationale.md` (0 refs, dead script path). Retire `rimbridge.md` §3–§5, keeping §0–§2c provenance and **§6's authoring-not-self-upgrade ruling** | −2 files |
| 12 | **Move the two generated files out of `design/`** — `ship_build/ship_build.md` and `data/ideology_palette.md` both carry "regenerate, never hand-edit" headers, and `design/README.md` says *"Anything a machine generates … is not design."* Regenerate `ideology_palette.md` against the live 582-mod list while moving it | tier rule enforced; the ship tile sheet stops looking like a design authority when it is three revisions behind row8's D1–D5 |
| 13 | **Record the art freeze in `c7_directional_triage.md`**, which is parked by it and never says so | one ruling reaches the doc it governs |
| 14 | **File `PLANT_GROWTH_SPEC.md`** — either give it a referrer/queue entry or mark it parked | an alive-but-unreachable doc becomes reachable |

### Tier 3 — `V2_DREAMS.md`

| # | action | saving |
|---|---|---|
| 15 | 🔴 **Move the three deadlined items OUT.** `GiantAnt_Faction` (line 864, *"IT HAS A v1 DEADLINE"*), **B66** (line 1548, *"RIDE THIS WINDOW or lose a load"*) and **C42** (line 1335, *"bakes at world creation"*) are scheduled work in a file whose header says nothing here is scheduled and that is *"drained only when v1 has shipped."* Under the one-frozen-world rule, **a v2 item that must be decided at the world screen is a v1 item.** | the file's header becomes true again |
| 16 | **Collapse B3 + C3 + C32 + D-R4** into one scrapfields entry and mark it done — B3's own body says `VERIFIED in sync` and C32's heading says *"is deployed"* | 4 entries → 1; removes completed work from the deferred register |
| 17 | **Strike nothing further on worldgen grounds.** ✅ The ruling is already applied correctly and the local-map-generation carve-out at lines 1442–1444 is deliberate | — |

### What this adds up to

| | before | after |
|---|---|---|
| in-scope `design/` documents | **105** | **~96** (−9: 3 deleted, 4 merged into 1, 2 moved out of the tier) |
| in-scope `design/` lines | **37,777** | **~36,100** (−4.4%) |
| 🔴 **contradictions between docs** | **21** | **0** |
| duplicated constants maintained by hand | **~25** | **~5** |
| dangling `.md` citations | **28** | 0, once banners name the survivor |
| the actual saving | | 🔑 **not lines — it is that a ruling stops costing four edits.** On the 7-day rate of 514 in-scope doc-writes, the ship constants alone accounted for the same numbers being rewritten in four files |

🔑 **The one-sentence answer to the owner's question:** *some* documents are redundant,
but far fewer than the file count suggests — the expense is not 105 files, it is
**21 places where two files answer the same question differently**, and the cheapest
durable fix is an index in `design/README.md` plus one owner per constant.

---

## Method and caveats

- Inbound references counted with `grep -rl` over `*.md *.py *.xml *.cs`, excluding
  `vendor/`, `research/`, `infrastructure/disposing/` and self-references.
- **Write-once verified under `git log --follow`** for every in-scope design doc —
  the 2026-08-19 path rewrite noted by `infrastructure/output/audit_2026-08-20_docs.md`
  does **not** split their history; the counts hold.
- ⚠️ **`7e98004` ("Repo re-initialised … history archived", 2026-08-13) added 204 `.md`
  in one commit.** Commit counts in this repo measure activity *since* that date only.
- Cluster reads were performed by five parallel subagents; every claim carrying a line
  number was read from the file, not inferred.
- Bridge tool count measured from source:
  `grep -ho '"jawa/[a-z_]*"' src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs | sort -u | wc -l` → 106.
- ⛔ **Nothing in the repo was modified. This report is the only file written.**
