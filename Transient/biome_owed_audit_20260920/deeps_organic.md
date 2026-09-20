# Biome owed-work audit — 9 sheets (2026-09-20)

Sheets assigned: the_rot.md, the_lantern_deeps.md, the_pyrelands.md,
the_twilight_deep.md, the_grey_deep.md, the_propane_lakes.md, the_webwork.md,
the_contagion.md, assailant_weapon_remnants.md

Method: extract Owed-style section(s) per sheet, split into individual work
items, classify FILED / UNFILED / DONE-BUT-UNRECORDED against
`infrastructure/state/items/*.md` and `infrastructure/state/items/closed/*.md`
plus defs/art/C# on disk.

Status: IN PROGRESS — filling section by section.

## the_rot.md

Owed section (§ after "## Owed") has one heading holding 6 bullets; the
"Engine feasibility pass" bullet is itself 7 sub-items. Examined 11 individual
work items total (5 top-level bullets + 6 engine sub-items; the "def tails
check" bullet is marked ✅ CLOSED in the sheet itself, not counted as owed).

1. **Heat-generating gene** — FILED/DONE (CONFIRMED). `ROT_WARM_MAT_1`
   (closed at `f4d8dbf2b`) built `RUT_Gene_Furnaceblood`
   (`src/RimUtinni/RotSporeKit/Defs/GeneDefs/RUT_RotSporeKit_Furnaceblood.xml`),
   `RM_MapComponent_WarmGround`, and `RUT_GrownFurnace`. Sheet's Owed line is
   stale — the gene existed before this audit.
2. **Guardian repertoire concretized per tea species** — UNCERTAIN (leaning
   UNFILED). Searched: "guardian repertoire", "tea species", "Wildsteam" +
   "guardian". No item or design-doc section found expanding the §7 tea-guard
   menu per species. `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (closed) covers
   general fauna/flora assignment sittings, not this specific expansion —
   its own prose doesn't mention guardians or tea species.
3. **Engine feasibility pass — health-share comp (C#, two variants)** —
   UNFILED (CONFIRMED no such comp exists). Searched: "health-share",
   "HealthShare", "SharedHealth", "Symbiont" (found only hediff/recipe defs,
   no shared-health C# comp), "CompHealthShare". No item names it either.
4. **...live-item viability clock (dies refrigerated, dies delayed)** —
   FILED/DONE (CONFIRMED). `ROT_LIVE_PREPARATIONS_1` (closed at `f4d8dbf2b`):
   `RM_Patch_LivePrepViability.cs` +
   `RUT_RotSporeKit_LivePreparations.xml` (vanilla `CompTemperatureRuinable`
   + `CompLifespan` on every live-prep item, with a strict/lenient Mod
   Settings toggle per ban 4).
5. **...heat-pushing produce comp** — FILED/DONE, same as #1
   (`RUT_GrownFurnace`, `ROT_WARM_MAT_1`).
6. **...milk ponds as terrain (donor Marsh patches re-skinned to not-water
   milk)** — UNFILED (CONFIRMED not built). Searched: "MilkPond", "milk
   pond" (TerrainDefs), "Marsh" reskin. `RUT_RotSporeKit_Terrain.xml` ships
   `RUT_MushroomFloor/Bridge/HeavyBridge/MoonlessCarpet/MycelialSoil/
   MycelialMatting` — mushroom bridges reference milk ponds as the thing
   they're built OVER, but no milk-pond terrain def exists anywhere in
   `src/RimUtinni`. `WATER_KINDS_TAXONOMY_1` and `FISH_BY_BIOME_1` (both
   closed) only classify milk ponds in DESIGN prose ("not-water"); neither
   builds the terrain. **The Rot has no rot-tagged standing liquid at all** —
   this is the closest analog to the Blue Desert pattern found in this set:
   a ratified design element (milk ponds, referenced by name in 4+ places)
   with no engine artifact.
7. **...Sheen weather def + compatibility hediff** — FILED/DONE (CONFIRMED).
   `RUT_RotSporeKit_SheenWeathers.xml` (205 lines),
   `RUT_RotSporeKit_SheenHediffs.xml` (109 lines),
   `RUT_HediffComp_SheenExposure.cs`, `RUT_SheenExposureLock.xml` game
   condition all exist and are substantial, referenced across several other
   items (`BMT_FAUNA_ABSORPTION_1`, `CAVERNS_PARITY_BUILD_1`,
   `MIASMA_MECHANICS_1`).
8. **...the rot-rate map condition** — UNFILED (CONFIRMED not built).
   Searched: "rot-rate", "RotRate", "rot clock", "RotClock". The sheet's own
   §3 "The rot clock" describes instant composting as a service, but no
   GameConditionDef or MapComponent implementing a map-wide rot-rate exists
   in `src/RimUtinni` or `src/RimMandrake`; no item names it.
9. **...the pale tree as a Royalty anima reskin with a restricted vanilla
   psycast set** — FILED but STALE STATE (flag). `ROT_PALE_TREE_1` shows
   `ready` (not closed) in rimflow, but `RUT_PaleTree.xml` is fully built
   (verified field-for-field against `Plant_TreeAnima` per its own header),
   art landed 2026-09-20 per `ROT_FLORA_FAUNA_VERDICTS_1`, and `rimflow show`
   itself warns 3 commits cite the item with none touching its item file —
   the ledger row appears to lag real state. The "restricted vanilla
   psycast set" audit is explicitly declined by an owner card baked into the
   XML comment ("No power whitelist: declined... needs C#, not built") —
   so that clause of the Owed bullet is correctly still open, but is a
   ruled-out non-goal, not an oversight.
10. **Roster admission tests at `BIOME_FAUNA_ASSIGNMENT_SITTING_1`** —
    FILED/DONE via that item (closed) plus the subsequent
    `ROT_FLORA_FAUNA_VERDICTS_1` (proposed/in-flight) which names hybrid
    verdicts explicitly.
11. **Wildsteam wiring — the sacred-grove relationship into
    `FACTION_SPEC.md`** — UNFILED (CONFIRMED). Searched: "sacred grove",
    "Wildsteam" + "Rot"/"MycoticJungle", grep of `FACTION_SPEC.md` itself for
    "sacred grove"/"Rot"/"MycoticJungle"/"pale tree" — zero hits. The 611-line
    `FACTION_SPEC.md` never mentions the Rot's sacred-grove relationship at
    all. `FACTION_ART_SPEC.md` and other docs reference Wildsteam's palette
    and lore generically, not this specific relationship.

## the_lantern_deeps.md

Owed section: 8 bullets, one splits into two (mindstone race naming vs. the
actual race build). Examined 9 items total.

1. `LANTERN_DEEPS_INJECTION_1` — FILED/DONE (closed `2eb08d1a4`).
2. `HORRORWASTES_BIOME_DISSOLVE_1` — FILED/DONE (closed `bb437a16`).
3. `CRYSTAL_MODS_INGEST_1` — FILED, superseded by `CRYSTAL_INGEST_EXECUTION_1`,
   which is itself FILED/DONE (closed `406dd95f4`). Chain intact.
4. `MECHANOID_ORIGIN_CANON_1` — FILED/DONE (closed 2026-09-11) — but this item's
   own `verify` clause is explicitly CANON/NAMING ONLY ("names ruled... design
   reviewed"), not a build. See #7 below for the gap this leaves.
5. `KYBER_TRADE_PLOT_1` — FILED, `ready`/BLOCKED (design spec written,
   implementation genuinely still owed per the item's own blocked reason:
   "Heat/Hutt-Interest GM blackboard (M4) unbuilt"). Matches the sheet's own
   "implementation still owed" note — not a discrepancy, sheet is accurate.
6. **Names ruling** — FILED/DONE via `MECHANOID_ORIGIN_CANON_1`
   (`RUT_Mindstone` kept, new race named `RUT_Kindled`, Forgotten Sentinels
   canon) — this is a NAMING ruling only, confirmed closed.
7. **Crystal-life authoring (art + C#: piezo/light-draw, Creep's accretion,
   Cleavers' fracture movement, Shard-mind animating dead gear)** — UNFILED
   (CONFIRMED). `LANTERN_DEEPS_INJECTION_1` itself states explicitly: "the
   crystal-life cast (Lantern, Creep, Cleavers, Chorus, Shard-minds,
   mindstone) is authored content — art + C# scoped separately" — i.e. it was
   deliberately deferred to a future item that was never filed. Searched:
   "Crystal-life authoring", "piezo", "Creep" + "accretion", "Cleaver" +
   "fracture", "ShardMind"/"Shard-mind", "RUT_Kindled", "RUT_Mindstone" —
   zero defs, zero C#, zero items beyond the deferral note itself. **The
   Kindled race that `MECHANOID_ORIGIN_CANON_1` ratified by name does not
   exist as a def anywhere in `src/RimUtinni` or `src/RimMandrake`** — no
   pawnkind, no mindstone findable item, no droid-mind crafting recipe. This
   is the sheet's largest playability gap: a named, owner-ratified new
   sapient race with zero engine representation.
8. **Roster admission for the non-crystal cave fauna at the sitting** —
   UNCERTAIN. `LANTERN_DEEPS_INJECTION_1` defers this to "the sitting"
   (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`, closed), but that item's own prose
   only proves general sheet review + assignment-prep infrastructure, not
   that Lantern Deeps' specific non-crystal fauna roster was actually
   admitted. Searched: "non-crystal cave fauna", "Lantern Deeps" inside
   `BIOME_FAUNA_ASSIGNMENT_SITTING_1.md` and `_assignment_prep.md` — did not
   open `_assignment_prep.md` (611 lines, another agent's territory/frozen
   prep doc) to confirm a per-species row; flagging as uncertain rather than
   claiming UNFILED without that read.

## the_pyrelands.md

Owed section: 5 bullets, split into 11 individual items (canon sitting = 3,
cross-flow ledger = 4). Examined 11.

1. `PYRELANDS_MECHANICS_1` — the sheet text literally reads "(to file)" but
   this is STALE SHEET PROSE (flag, per CLAUDE.md's decay warning): the item
   IS filed and closed (`6946c1873`). The sheet was not updated after filing.
2. **Roster** (fire-hawks, furnace-beasts, three families, quickgrass/
   scorch-fruit) — FILED/DONE, CONFIRMED by volume: `PYRELANDS_FAUNA_WIRING_1`,
   `PYRELANDS_FIRE_WEB_COMMISSION_1`, `PYRELANDS_CREATURE_RERENDER_1`,
   `PYRELANDS_FLORA_LEAK_1`, `PYRELANDS_FACING_COMPLETE_1`, plus the art-wave
   items (`SCORCHFRUIT_ART_REGEN_1`, `EMBERGRASS_LEAFLESS_ALTS_1`) all exist —
   this sheet's flora/fauna owed work is the best-covered of the set, matching
   the briefing that Pyrelands already had its verdict pass + art wave.
3. **FireEcology deploy collision** — DONE/addressed (CONFIRMED). Read
   `src/RimMandrake/Utils/deploy_custom_mods.py:70-81` directly: it now hard
   `sys.exit`s on a duplicate mod folder name across tiers, citing this exact
   FireEcology precedent in its own comment. `MOD_NAMING_CONSOLIDATION_AUDIT_1`
   (closed) is the item that produced the consolidation.
4. **Canon sitting (Wednesday)**:
   a. Sun-Debt reconciliation line into `faction_religions.md` §4 — UNFILED
      (CONFIRMED). Read §4 (Deep Desert Tribes / the Sun-Debt) in full — no
      mention of the Pyrelands, fire, or flame harvest anywhere in that
      section. Searched: "Pyrelands", "flame harvest", "fire raid" against
      the whole file — zero hits.
   b. genetic-tech theme line into the Rakata spec — UNFILED (CONFIRMED).
      Searched `ANCIENTS_AS_RAKATA_SPEC.md` for "Pyrelands" — zero hits (the
      file does discuss genetic-tech revulsion generally, just never ties it
      to this biome).
   c. flame harvest/fire raids into the Tribes' dossier — UNFILED as a canon
      doc-line (CONFIRMED no Pyrelands text in `faction_religions.md`); the
      closest related item, `DESERT_TRIBES_FIRE_HARVEST_1` (a *scenario
      event* for tribes visiting to light fires), is filed but **DROPPED**,
      not done — so nothing satisfies this bullet either as canon prose or
      as a mechanic.
5. **Cross-flow ledger** (4 sub-items: R-H9 → `the_sump.md`; nightside mirror
   → `the_propane_lakes.md`; Kiln overlap → `sacred_sites_pass_1.md`;
   furnace-beast warmth routes → nightside travel canon) — UNCERTAIN across
   all 4. Searched "R-H9", "Kiln overlap", "furnace-beast" + "travel" in
   items and design docs; `sacred_sites_pass_1.md` does discuss the Kiln
   (§ "The Kiln (Zizzik/Mob'Unloo contest)") but I did not verify it
   specifically reconciles with the Pyrelands sheet's cross-flow note, nor
   did I check `the_sump.md`/`the_propane_lakes.md` for the other two links —
   this is a genuine gap in my coverage (budget), flagging UNCERTAIN rather
   than guessing.

## the_twilight_deep.md

Owed section: 5 bullets → 10 individual items (implementation-deferred
bullet = 5 named systems, canon sitting = 3, cross-flow ledger = 4; v2 full
settlement excluded as explicitly out-of-scope v2). Examined 12.

1. **Implementation deferred to diving mods** (roof/ceiling rendering,
   skylight drift, bottom-river currents, fishing/kelp economies, Compact
   dwelling gen, gardener set-piece) — PARTIALLY FILED. `TWILIGHT_DEEP_WATER_
   LAYER_1` (doing) and `LIQUID_TYPES_MOD_1` (doing) are both in-flight and
   cover the water-layer/current half; no item found for skylight drift,
   Compact dwelling gen or the gardener set-piece specifically. UNCERTAIN on
   those three — searched "skylight drift", "Compact dwelling", "gardener
   set-piece", found nothing, but this whole bullet is explicitly marked
   "deferred to the diving mods" in the sheet (i.e. deferred to a FUTURE
   framework decision), so absence may be intentional non-scope rather than
   a gap — flagging rather than calling it UNFILED outright.
2. **v2 Compact settlement** — correctly out of scope (marked 🔵 v2, plan of
   record), not owed work.
3. **Roster — "the generous pass"** — UNCERTAIN, leaning UNFILED. Searched
   "twilight deep" across all items: only `BIOME_FAUNA_ASSIGNMENT_SITTING_1`
   (general sitting) and `TWILIGHT_DEEP_WATER_LAYER_1` (water-layer
   blocker) reference this biome — no dedicated fauna/flora wiring item
   like the Rot's or Pyrelands' several-item chains. Given the sheet's own
   emphasis ("this biome alone populates richly"), the thin item trail is
   suspicious but I did not check the live def dump for actually-spawned
   Twilight Deep fauna, so not calling it CONFIRMED UNFILED.
4. **Canon sitting**:
   a. Compact's ark-keeper reveal into their faction dossier — UNFILED
      (CONFIRMED). Searched "ark-keeper" across `design/Jawa` — only the
      sheet itself and `README_BIOME_GRAMMAR.md` (which flags it 🔴 as
      still-important content) mention it; no faction dossier file for "the
      Compact" exists anywhere in `design/Jawa/worldbuilding`.
   b. mat-roof mechanism into `terminator_sea.md` canon — FILED/DONE
      (CONFIRMED). Read `terminator_sea.md:15`: "beneath the mat-roof, the
      crowding exception lives" — the scoping line is already there.
   c. skylight/roof physics into the hydrology doc — UNFILED (CONFIRMED).
      Searched `hydrology_and_fire_ecology.md` (the only hydrology doc in
      the tree) for "skylight", "roof physics", "Twilight" — zero hits.
5. **Cross-flow ledger** (the_grey_deep.md sister-underworld statuary/ark
   link; terminator_sea.md surface law — done, see 4b; the Miasma
   crèche-comparison; `LIQUID_TYPES_MOD_1` density-current grade) —
   UNCERTAIN on the grey_deep and Miasma links (not yet checked at time of
   writing — the_grey_deep.md is this sheet's own next section below and
   will cross-check there); `LIQUID_TYPES_MOD_1` is FILED/doing (see #1).

## the_grey_deep.md

Owed section: 4 bullets → 7 individual items. Examined 7.

⭐ **This sheet is a POSITIVE control, not a gap**: its first Owed bullet
literally states "no mechanics item filed" — but this is the sheet HONESTLY
self-reporting a deliberate owner deferral ("when they need it," 2026-09-07),
not a silent hole. Contrast with the Blue Desert pattern in the task brief:
that one was ratified-and-forgotten; this one is ratified-and-declared-
deferred. No defs exist anywhere for this biome's three named creatures
(`PillarMason`/`CrustedGiant`/`OssuaryShrimp` — searched all three names,
zero hits in `src/RimUtinni` or `src/RimMandrake`), which is exactly what
"deferred by ruling" should look like on disk.

1. **Implementation deferred by ruling** (murk visibility, pillar navigation
   + waymarks, brine-pool lethality + shore harvest, scrape-sign/glow-mark
   telegraphy, statuary salvage, shrimp evasion AI) — correctly UNFILED,
   by design (see above). Not counted as a defect.
2. **"The Twilight Deep... owed its own sitting"** — STALE SHEET PROSE
   (flag, CONFIRMED). `the_grey_deep.md` was last edited 2026-09-10; the
   Twilight Deep sheet it's asking to be sat on was already marked "✅ done
   2026-09-07" in `README_BIOME_GRAMMAR.md` three days earlier. This note
   asks for a sitting that had already happened when it was written.
3. **Roster — the three residents into the assignment pass;
   `sea_beasts_roster.md` pairing (the giant ↔ the Miasma's warden mothers)**
   — UNFILED (CONFIRMED for the pairing specifically). Read
   `sea_beasts_roster.md` in full (75 lines, RSW SeaBeasts roster) — zero
   mentions of "Grey Deep," "warden mother," or "giant"; it's a different,
   unrelated 18-creature roster. The underlying LORE connection already
   exists in prose (`the_miasma.md`'s own "warden mothers" section and
   `the_grey_deep.md`'s "bred at the Miasma's crèches" line both exist and
   agree), but no roster FILE or item performs the pairing itself.
   `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (closed) is the only item touching
   this biome by name and its own prose doesn't confirm a Grey-Deep-specific
   admission pass. Searched: "Grey Deep", "pillar-mason", "crusted giant",
   "ossuary shrimp", "warden mother" + "roster". Given #1, this may also be
   intentionally deferred rather than a true gap — UNCERTAIN on urgency,
   CONFIRMED on the literal absence.
4. **Cross-flow ledger** (`terminator_sea.md` surface/shore law;
   `the_miasma.md` crèche; preservation triptych `the_sump.md`/
   `the_scarlands.md`; `LIQUID_TYPES_MOD_1` brine grade; future dry-statuary
   archaeology) — PARTIALLY CONFIRMED: the Miasma crèche link is already
   written into both sheets' prose (see #3). `LIQUID_TYPES_MOD_1` is
   FILED/doing (see Twilight Deep section above). Did not check
   `the_sump.md`/`the_scarlands.md`/`terminator_sea.md` for this specific
   triptych/surface-law line — UNCERTAIN, not checked (budget).

## the_propane_lakes.md

🔴 **Correction to the task brief**: the brief states `RUT_Umbra` "has had no
flora/fauna pass at all" as if it were a second Blue Desert. Read the live
def, `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml`, in full —
**this is FALSE as stated**. `<wildAnimals>` carries 4 species
(`AA_Frostmite`, `AA_FrostboundBehemoth`, `AA_Terramorph`, `AA_Slurrypede`,
weights 0.02-0.35) and `<wildPlants>` carries 4 (`AB_CrystalHorn`,
`AB_CrystalFlower`, `AB_FrostLeaf`, `AB_RimeNodules`, weights 0.4-1.0) — both
non-empty, non-zero. The def's own header states these were "transplanted
from BiomeCast_Ashkarr.xml/BiomeFlora_Ashkarr.xml against
`rosters/the_propane_lakes.json`" with ban 1/ban 2 enforced by that JSON's
evictions — i.e. a roster/ban pass DID happen. **What's actually true**: the
species are still raw DONOR names (Alpha Animals/Alpha Biomes prefixes), not
renamed/verdict-passed campaign content the way the Rot's and Pyrelands'
rosters were — so Umbra is populated but has not been through the
naming/art/hybrid-verdict pass those sheets got. That's a real, lesser gap
(cosmetic/canon ownership, not "empty biome"), and it is NOT named anywhere
in this sheet's own Owed section — the Owed list is silent on flora/fauna
entirely.

Owed section: 7 bullets → 12 individual items (engine feasibility pass = 5,
cross-flow ledger = 2). Examined 12, plus the flora/fauna gap above (not
itself an Owed-list line item, so not counted in the 12, but reported
because it is real biome-completeness work with no item name to search for).

1. `ANCIENT_WAR_LAB_1` — FILED, `doing` (in progress, not stale).
2. `LIQUID_BIOMES_MAP_1` — FILED/DONE (closed `182c69842`); sheet's own text
   confirms "paint DONE," matches.
3. `TERRAMANUFACTURE_CANON_1` — FILED/DONE (closed `3c2993420`).
4. `MECHANOID_BIOME_PRESENCE_REVIEW_1` — FILED, superseded by
   `MECH_PRESENCE_ENFORCEMENT_1`, which is FILED/DONE (closed `023beee3`).
   Chain intact.
5. **The Frostling → `forsaken_crags.md` roster** — FILED/DONE (CONFIRMED).
   `forsaken_crags.md:254`: "The Frostling joins this roster (owner,
   2026-09-06: moved back from the propane...)" — line is present verbatim.
6. **Engine feasibility pass — aurora weather with radiation + GIC surge
   events** — UNFILED (CONFIRMED). Searched: "aurora" + "radiation", "GIC
   surge", "GameConditionDef" list under `UtinniPatches/Defs/
   GameConditionDefs/` (13 files, none Umbra-scoped — closest name match,
   `RUT_GradientSurge`, is unrelated: label "the breath-tide surge", not
   Umbra). No item names it either.
7. **...the tap building** — UNFILED (CONFIRMED). Searched "electrojet tap",
   "tap building". `RUT_TibannaTap_BeldonWiring.xml` exists but is
   `FORGE_MECHANICS_1`'s unrelated Tibanna-gas tap for a different biome
   (the Forge) — false-positive name collision, not this one.
8. **...fuel-snow weather** — UNCERTAIN. `RUT_Umbra.xml`'s own comment says
   SnowGentle/SnowHard are "reflavored per the sheet as 'fuel snow'... not
   literal water snow" — so the WEATHER-DEF reskin exists as flavor text on
   vanilla snow weather, but no new fuel-snow-specific mechanic (precipitation
   feeding crystal flora, described in SS4b) was found. Searched "fuel snow",
   "FuelSnow". Partial credit, not a clean DONE.
9. **...the lake terrain (flammable, off-gassing into saturation)** —
   UNFILED (CONFIRMED). Searched "off-gass", "Flammable" + "Propane",
   `AB_PropaneLake`/`AB_SolidPropane` terrain defs — no custom comp or patch
   adding flammability/off-gassing found; `RUT_PropaneLake.xml` is the
   worldmap BiomeDef only (paint layer), not local-map terrain behavior.
10. **...the crater event (map permanence)** — FILED, folded into
    `ANCIENT_WAR_LAB_1`'s own scope ("the crater ending as a permanent map
    change") — in progress, not a separate unfiled item as the sheet's
    phrasing might suggest.
11. **Cross-flow ledger — Umbra→crags tholins** — appears consistent
    (UNCERTAIN on completeness): `forsaken_crags.md:68/73/260` already
    discusses tholin-rime chemistry and variant mapping; did not verify it
    specifically cites Umbra as the warm-end source.
12. **...Blue Desert→Umbra haze/dead** — appears consistent (UNCERTAIN):
    `the_blue_desert.md` already has its own haze section (§ "The haze, and
    the 'snow'"); did not verify a two-way citation of Umbra specifically.

## the_webwork.md

Owed section: 6 bullets → 9 individual items (Roster = 4, cross-flow = 2, one
self-resolved). Examined 9.

1. `WEBWORK_MECHANICS_1` — FILED/DONE (closed `0167e7af`).
2. `SHOKKWEAVE_SOLE_SOURCE_1` — FILED, `doing` (in progress, matches sheet).
3. **Roster** — rides the full assignment pass — MOSTLY FILED/DONE.
   `WYYYSCHOKK_FERALISK_MERGE_1` (closed, cuts every donor 'lisk duplicate),
   `WEBWORK_KIT_BUILD_1` (closed, "the roster's web/anchor/gutter ThingDefs"),
   plus `BIOME_FAUNA_ASSIGNMENT_SITTING_1` cover most of this. One piece
   UNCERTAIN/leaning UNFILED: the bestiary clade naming ("nettik/chirrik/
   rothrik available for the guilds") and the explicit "donor density
   correction" — searched both terms across all items, zero hits.
4. **Wildsteam kit** (still-burner weapon + liquor fuel item + mandible
   bounty quest) — UNFILED (CONFIRMED). Searched: "still-burner", "mandible
   bounty", "Wildsteam" + "Webwork" — zero item or design-doc hits beyond
   the sheet's own line ("lands with their template/faction work" — no such
   faction-template item found naming this content).
5. **Egg economy** (item, offworld sale route, carried-eggs mark) — UNFILED
   (CONFIRMED). Searched: "egg economy", "carried-eggs", "Shokk" + "egg" —
   zero hits in items or design docs.
6. **Cross-flow ledger — the Contagion's UV cage** — UNCERTAIN, not checked
   against `the_contagion.md` yet (see that section below in this report).
7. **...the Greentide margin** — UNCERTAIN, not independently verified.
8. **...`VAPOR_EMITTER_PLACEMENT_1` owes nothing here** — self-resolved by
   the sheet's own text ("no steam sources — the Webwork's wet is silent"),
   not a work item at all. Correctly not owed.

## the_contagion.md

⚠️ **Could not confirm the task brief's "two owed-style sections" claim.**
Read the whole 252-line file; grepped case-insensitively for "owed", "TODO",
"not built", "unbuilt", "still needs", "remains to", "to file", and every
🔴/⚠️ inline marker. Result: exactly ONE `## Owed` heading exists (line 226,
running to EOF), and no other heading or inline marker in §§0-9 names
deferred work in owed-list form — §6's 🔴 lines are HARD BANS (permanent
rules), not owed work. `git log` on the file shows no recent consolidation
of two sections into one. Reporting this as UNCERTAIN/possibly-stale-brief
rather than inventing a second section; treated the single section as
authoritative.

Owed section: 9 bullets → 14 individual items (engine feasibility pass = 4,
plus 10 single-item bullets). Examined 14.

1. `CONTAGION_BIOME_PLACEMENT_1` — FILED/DONE (closed `c0f0b6024`).
2. **Art: the half-transformed tree** ("half plant" redo) — FILED, rides
   `TREE_GRAPHICS_OWNERSHIP_1`, which is `doing`/BLOCKED (14 recovered
   sweetline-tree art candidates await an owner pick) — matches the sheet's
   own "rides" framing, not a gap.
3. `WATER_KINDS_TAXONOMY_1` — FILED/DONE (closed, confirmed earlier in this
   report under the Rot section).
4. `MUTATION_MODIFIERS_SURVEY_1` — FILED/DONE (closed `f4a40fd1d`).
5. **The Unfinished — art line + C# spawner** (random stats, random
   `Hediff_AddedPart` limbs, short lifespan, goo-corpse) — UNFILED
   (CONFIRMED). Searched "The Unfinished" + "goo-corpse", "Hediff_AddedPart"
   + "Contagion" — only hit was `MUTATION_MODIFIERS_SURVEY_1`'s own survey
   text (which surveyed the MECHANISM generically, not built this specific
   creature). No spawner C#, no art, no item.
6. **Engine feasibility pass — the Burn as weather with radiation + UV
   damage to natives** — UNFILED (CONFIRMED, zero hits).
7. **...the jelly/rattle tells** — UNFILED (CONFIRMED, zero hits).
8. **...sun-sterilization of hauled water and mulch (timed item
   transformation in sunlight)** — UNFILED (CONFIRMED, zero hits).
9. **...mulch that infects fields** — UNFILED (CONFIRMED, zero hits).
10. **The green below — CypreJungle / Feralisk jungle / Desert Oasis want
    their own short definitions** — UNFILED (CONFIRMED). These three names
    appear widely as EXISTING biome/fauna-roster names across `design/Jawa`
    (census CSVs, palette JSON, etc.), but no dedicated short-definition
    sheet exists for any of them in `design/Jawa/worldbuilding/biomes/` the
    way the_contagion.md itself is one — unlike the 9 sheets in this audit,
    they have no `the_*.md`/named sheet of their own.
11. **Contagion-touched cure ruling** — UNFILED (CONFIRMED, zero hits for
    "Contagion-touched cure" or "cure ruling" in items; §7 of the sheet
    itself only states the HARD BAN that it never upgrades you, not a cure
    mechanism ruling).
12. **Doc hygiene: find and link the primary R-H rule list** — UNFILED
    (CONFIRMED, still open). Searched for a dedicated "R-H rules" document;
    only found scattered R-H citations inline in individual sheets (e.g.
    `wasteland.md:195` cites R-H1 directly) — no single primary list doc
    exists anywhere in `design/Jawa`, matching the sheet's own note that "the
    primary R-H rule list was not located this session."

## assailant_weapon_remnants.md

(pending)
