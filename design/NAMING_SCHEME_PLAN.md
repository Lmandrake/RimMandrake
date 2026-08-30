<!-- status: live — the three-tier naming scheme plan. Ruled in principle by the owner 2026-08-30; execution gated on token budget (NAMING_SCHEME_EXECUTION_1). Drafted + self-reviewed by the Fable seat, surveys MEASURED same day. -->
# The Three-Tier Naming Scheme — RimMandrake / RimStarWars / RimUtinni

_Owner's ruling (2026-08-30, verbatim anchor): "RimMandrake is the global fully
generalizable stack. RimStarWars should be the collection for everything
generalizably within the Star Wars family. RimUtinni should be anything
specifically for this scenario… There WILL be other Star Wars scenarios we
build and we'd hate for things to get stuck in the wrong place. So the pit
traps would be RimMandrake, just to be clear."_

**Why this is not aesthetic:** (1) the world-freeze savegame bakes our
defNames as shortHashes — after the freeze, defName renames are effectively
impossible, so every week of new content raises the cost of doing this;
(2) `The Salvation.rid` / `MandrakeJawa.xtp` bake packageIds and gene
defNames at the one irreversible worldgen; (3) a second Star Wars scenario
reuses RimStarWars wholesale only if nothing campaign-specific leaked into it.

---

## 1. The tiers, with decision tests

| Tier | Definition | The test | Examples |
|---|---|---|---|
| **RimMandrake** | Fully generalizable to any RimWorld game | *Would a medieval-tribe player install this alone and understand it?* | Pits, Inhabited, WreckedMachines core, Visibility dial, art fixes for non-SW mods |
| **RimStarWars** | Generalizable within the Star Wars family — any future SW scenario | *Would a Hoth or Tatooine-smuggler campaign want this unchanged?* | Jawa xenotype/genes, Star Wars races, Droidworks platform, ion weapons, SW-mod fixes |
| **RimUtinni** | This scenario only — the Utinni campaign | *Does it name Ash'karr, the Kolyska, the Nine, this clan, or this story?* | The Salvation, planetary lore/art, Jawa_Doctrine, EmpirePursuit config, pawn flavor, faction slates |

**Tie-break rules (canonized here):**
- **A fix mod takes the tier of the mod it fixes** (Cerean mane fix → RimStarWars; saurid frill fix → RimMandrake).
- **Engine vs. content**: when a system splits into a generic engine and campaign content (Pits precedent, ratified), the engine takes the highest tier it honestly passes, the content pack takes its own tier. One mod may not straddle; split it.
- **Species vs. clan**: the Jawa *species* (genes, body, voice, eggs) is RimStarWars (owner-explicit); *this clan's* culture, faith, backstories, and doctrine are RimUtinni.
- **Doctrine is Utinni even when it patches SW content** (the ion-over-explosives *rule* is theology; the ion *weapons* are RimStarWars).
- **Non-shipping tooling is EXEMPT** (Utils, rimflow, JawaBench companion, the `jawa/*` GABP tool prefix, Spikes): the scheme governs shipping identity; renaming dev tooling breaks 56+ scripts and every skill doc for zero player value. Tooling keeps its names and paths.

## 2. The naming grammar

| Surface | Grammar | Examples |
|---|---|---|
| packageId | `mandrake.<tier>.<modname>`, lowercase — **author segment KEPT** (review finding 6: RimWorld resolves mods and MayRequire by packageId; third-party `rimstarwars.*`-style ids are plausible on Workshop and would collide silently; uniqueness beats prettiness) | `mandrake.rm.pits` · `mandrake.rsw.races` · `mandrake.rut.doctrine` |
| Mod display name | `<Tier>: <Name>` | `RimMandrake: Covered Pits` · `RimUtinni: The Salvation` |
| defName prefix | `RM_` · `RSW_` · `RUT_` | `RM_PitCover` · `RSW_JawaEyes_Amber` · `RUT_SalvationRite_Landing` |
| Folder | `src/<Tier>/<ModName>/` | `src/RimStarWars/Droidworks/` |
| C# namespace | `<Tier>.<ModName>` | `RimStarWars.Droidworks` |
| texPath root | `<Tier>/<ModName>/…` inside each mod | moves with its mod, nothing cross-references |

Established sub-prefixes with real def counts (`Inhabited_`, `DW_`) MAY keep
their stem behind the tier prefix only if the migration cost of the tail
outweighs clarity — default is full conversion; the rename map decides per
mod and the owner signs the exceptions.

## 3. Tier assignment — all 32 mods (from the MEASURED census)

**RimMandrake (14):** RimMandrake_Pits (27 `RM_`, already clean — the
exemplar) · SacredGraffiti (core; the nine mark-styles extract to a RimUtinni
content pack) · WreckedMachines (core; Rekko-relic hooks extract to
RimUtinni) · StrandedQuest (**VERIFY in Phase 1**: read its 2 defs' quest
text — campaign flavor would make it RimUtinni) · Inhabited (297 defs) ·
PlanetPresetPrime · RimDefDump · JawaRules (**misnamed**; verify its 2 rules
are engine-level, then rename) · DesertVehicleReskin (**re-assigned by review
finding 1**: it redraws Alpha Vehicles — Neolithic draught animals for desert
reading — not SW content; fix-mod rule → the fixed mod is generic) ·
GravshipAstronautFix · PhytokinBarkHeadFix · ResearchKitEastFix ·
ToolBeltFix · SauridFrillFix.

**RimStarWars (10):** RimMandrake_StarWarsRaces (**511 defs — the largest
re-prefix, and currently carrying the top-tier name on SW content**) ·
Droidworks (176 `DW_`; campaign roster/curation extracts to RimUtinni) ·
JawaIonWeapons · JawaIkee · JawaVoice (**straddle, review finding 3**: the
Jawaese-bubble framework is RSW; the authored line corpus is campaign flavor
— skim the lines in Phase 1 and extract RUT content if they name the
clan/ship/gods) · Jawa_Armoury (SW gun rebalance; campaign armory-doctrine
patches extract to RimUtinni) · BlastDoorFrameAsyncFix · CereanManeFix ·
KotORBandolierNorthFix · MSEDroidFix.

**RimUtinni (6 + the future Salvation pack):** Jawa_Doctrine ·
JawaFactionSlate · JawaPlantGrowth (**VERIFY in Phase 1**: a generic growth
tweak would be RM) · EmpirePursuit (pursuer engine may generalize to
RimMandrake later; ship Utinni now) · Jawa_PawnFlavor (90 defs — today
misfiled under `src/RimMandrake/`) · AshkarrLandmarkArt.

**SPLIT (1):** Jawa_Patches (121 defs, 67 patches) — SW races/animals content
→ RimStarWars; campaign doctrine patches → RimUtinni. Needs per-file triage;
its own execution sub-item.

_Count reconciliation: 14+10+6+1 = 31 assigned vs the census's 32 About.xml
roots — the Phase 1 rename map enumerates every About.xml and reconciles the
delta exactly; no assignment ships on these lists alone._

**In-flight content (born correctly from today):** Covered Pits core → RM ·
trap primitive tier → RM (owner-explicit) · ion/capture absorption patches →
RSW · trap theology rows → RUT · Visibility dial → RM · **Ninefold: NAMED
DECISION** — the door ruling christened it "RimMandrake Ninefold" hours
before this tier scheme existed; the engine/content rule says the satiation
*engine* is RimMandrake (a pantheon engine a second scenario could reuse with
its own gods) and the Nine + Salvation content is RimUtinni. Recommended:
`rimmandrake.ninefold` engine + `rimutinni.salvation` content pack. Owner
confirms or collapses it to RimUtinni whole.

## 4. Blast radius and migration mechanics (MEASURED)

| # | Surface | Size | Mechanic |
|---|---|---|---|
| 1 | Live ModsConfig.xml | 24 active `mandrake.*` ids | scripted swap from the rename map, same session as redeploy — game DOWN |
| 2 | Our own `MayRequire` attrs | **167** | sed from map + a zero-tolerance checker (a wrong MayRequire is a silent no-op; nothing audits it today) |
| 3 | World-freeze savegames | 6 draft .rws; our BiomeDef/TerrainDef/FactionDefs bake as shortHashes | **renames MUST precede the final freeze.** Drafts do not "regenerate" by script — Ash'karr is hand-authored; the route is a bridge re-import from the CSV bundle (rimworld-world-editing), a game-up bridge-claimed window of its own. Alternative: declare current drafts sacrificial and re-import once, post-rename. (The worldbuilding CSVs/MDs themselves carry zero of our defNames — MEASURED — so the coupling is confined to .rws artifacts and mod XML.) |
| 4 | `The Salvation.rid` + `MandrakeJawa.xtp` | 17 packageId refs; `Jawa_*` gene defNames | regenerate via `build_salvation_rid.py` AFTER renames, BEFORE worldgen; validate with `validate_save_artifact.py` |
| 5 | Tooling scripts | 56 .py referencing our names; deploy discovers 2 src dirs | sed from map; extend deploy discovery to `src/<Tier>/` (3 dirs); tooling's own names exempt (§1) |
| 6 | Patches/xpaths naming our defNames | inside the 1,261-def rename | same map, same sed; validate_patch.py both `--live` and `--defs` after |
| 7 | Cherry Picker lists | **0 refs — clean** | none |
| 8 | canon.yml / queues / skills docs | 71 canon mentions (mostly lore, exempt); 22 skill files; 10 queue rows | hand-triaged sed — only packageId/defName/path citations migrate, lore words stay |
| 9 | texPaths | self-contained per mod | move with the mod; post-deploy magenta sweep for misses (texture binds by texPath, silently) |
| 10 | Def dump / fingerprints | whole dump stale after rename | `refresh.py` + re-fingerprint; every downstream census re-runs |

## 5. Phases

**Phase 0 — ACTIVE NOW (this document + same-day commits):** the scheme is
doctrine. **New-content rule: every new packageId, defName, namespace and
folder created from 2026-08-30 uses the tier grammar** — enforced by
CLAUDE.md and the memory file; the lint (Phase 1) makes it mechanical. This
stops the debt growing while execution waits on token budget.

**Phase 1 — prep (~1 short session, no game needed):** build
`Utils/naming_lint.py` (checks packageId grammar, defName prefix vs mod
tier, namespace, folder placement; wired as a refusing step in
`deploy_custom_mods.py` plan output + optional pre-commit hook). Generate
the **rename map** (`infrastructure/state/naming_rename_map.csv`: every old
defName/packageId/folder → new, with tier and confidence). Owner reviews the
§3 assignments + straddle splits — a review-sheet if he wants clicks.

**Phase 2 — the atomic migration (one focused session + one game-down window
+ one bridge window for the world re-import):** freeze other seats' writes to
`src/` with a MECHANISM, not an announcement (review finding 5): a rimflow
blocking item plus a temporary PreToolUse hook refusing `src/` writes that
lack the sprint tag — a peer FOUNDRY window mid-build otherwise ships against
half-renamed defs. The sweep explicitly includes queue files and design specs
citing old defNames/packageIds (FOUNDRY.md verifiably cites `Jawa_Armoury`-era
names today). Then apply
the map — `git mv` folders (history preserved), packageIds, defNames,
namespaces, MayRequire, xpaths, tool-script references; swap ModsConfig;
redeploy; `refresh.py`; regenerate .rid/.xtp; run naming_lint (zero
violations), the MayRequire checker (zero), validate_patch on every patch
mod, magenta sweep; 22-second minimal-list load + quicktest. **Estimate:
300–800k tokens PLUS one game-down window (redeploy + ModsConfig swap) PLUS
one game-up bridge window (world re-import)** — the token number alone
undersells the wall-clock shape (review finding 9). Mostly scripted;
verification dominates; executable by Opus 5 — the judgment lives in the
map, which Phase 1 fixes.

**Phase 3 — content splits (per-item):** Jawa_Patches triage; extract the
straddle packs (SacredGraffiti marks, WreckedMachines relics, Droidworks
campaign layer, Armoury doctrine patches). Each is a small FOUNDRY item off
this plan.

**Phase 4 — deliberately NOT planned:** tooling renames/moves and `design/`
tree restructuring. Exempt (§1) and stable paths are worth more than purity;
`design/Jawa/` stays (lore vocabulary is legal there; a second scenario gets
its own `design/<name>/`).

**Hard ordering constraint:** rename map → migration → regenerate .rid/.xtp
→ **only then** any world freeze. The freeze is the deadline that makes this
urgent.

## 6. Enforcement (what "enforce it on the whole thing" means mechanically)

1. `naming_lint.py` — the machine gate; refusal wired into deploy from
   Phase 1 (warn-mode until Phase 2 lands, then hard). One added rule
   (review finding 8): shipped mod XML/C# may not reference exempt-tooling
   identifiers (JawaBench namespace, `jawa/*` tool names) — the exemption
   must never leak into shipping content.
2. CLAUDE.md carries the three-line rule (committed with this plan).
3. The memory file `rimmandrake-moniker-for-mods` upgraded to the tri-tier
   scheme (done same day) so every future session knows it cold.
4. Queue items about new mods name their tier in the title.
5. The rename map CSV is the single source of truth during migration —
   patch a curated artifact, never re-derive (per project doctrine).

## 7. Named decisions for the owner (short list)

1. **Ninefold**: RM engine + RUT Salvation pack (recommended), or all-RUT?
2. **Sub-prefix survivals**: may `Inhabited_` (297) and `DW_` (176) keep
   their stems behind the tier grammar, or full conversion? (Recommended:
   keep `Inhabited_` as-is inside an RM mod — it already reads as a product
   name; convert `DW_` → `RSW_DW_`? No — recommended full `RSW_` for
   Droidworks, it's pre-freeze cheap and the split (§3) rewrites half of it
   anyway.)
3. **JawaRules**: verify-then-rename to RimMandrake, or is it doctrine?
4. **Display-name format**: `RimMandrake: Covered Pits` (recommended) vs
   bare names with tier only in packageId.

## 8b. Review round 2 — adversarial fork, all nine findings folded in

DesertVehicleReskin re-tiered to RimMandrake (its target mod is generic — my
census reasoning was wrong) · StrandedQuest and JawaPlantGrowth carry Phase-1
VERIFY flags (assignments were unverified guesses) · JawaVoice added to the
straddle list (framework RSW, line corpus possibly RUT) · the world-draft
"regeneration" hand-wave replaced with the real route (bridge re-import,
game-up window) and the sacrificial-drafts alternative · Phase 2's write
freeze got a mechanism (rimflow blocking item + temporary hook) and the sweep
now names queue/spec files citing old names · **the packageId grammar changed:
author segment kept (`mandrake.rm.*`)** — dropping it risked silent Workshop
collisions on exactly the surface (MayRequire) that fails silently · §3
counts corrected with an honest 31-vs-32 reconciliation note · an
exemption-leak lint rule added · the Phase 2 estimate now states its two
game-window costs, not just tokens.

## 8. Review log (the improve pass, same sitting)

Findings from the self-review, folded in above: the game-DOWN requirement on
blast item 1 was missing (ModsConfig swaps while the game runs are the
stale-writer trap — added); the multi-seat collision risk during Phase 2 was
missing (write-freeze announcement added); `git mv` named explicitly so
folder history survives; the tooling exemption was originally per-file and
is now a tier rule (§1) — it deletes 56 files' worth of fake work from
Phase 2; the Ninefold contradiction with the same-day door ruling was
surfaced instead of silently resolved; Cherry Picker checked and found
CLEAN rather than assumed dirty; and the estimate was re-based on the
MEASURED counts (1,261 defs · 167 MayRequire · 24 live ids · 56 scripts)
rather than gut feel.
