# BMT_FAUNA_ABSORPTION_1 — donor corrected to biomesteam.*, ready to port

## Owner ruling, 2026-09-11 (question-card sitting)

Given the choice between (a) retargeting the item's donor to `biomesteam.*`
since the 71/41/30 figures are real and already ruled, (b) filing a fresh
keep-or-port sitting on the real `mlie.beastsoftherim`, or (c) leaving it
blocked — the owner picked **(a)**: the 71/41/30 figures are correct and
already ruled (`decisions_propagated.json`); the item named the wrong donor.

**Corrected scope for this item:** port the 71 `BMT_`-prefixed creatures (38
clean "in" + 30 "move" + `BMT_ChemSnail` resolved OUT per `biome_findings.md`
= 68 unique defNames landing; the "41 in" in the old queue line becomes 38
clean-in + `BMT_ChemSnail`'s conflict resolved as detailed below) from the
**`biomesteam`** family — `biomesteam.biomescaverns`, `biomesteam.biomescore`,
`biomesteam.biomespollutedlands` — into our own tier per the SWBestiary
donor-retirement pattern, then retire those three `biomesteam.*` mods.

`mlie.beastsoftherim` (the real 19-species/64-def donor) is UNAFFECTED by
this item — it stays exactly as it was in the Wave 2 stat-normalization audit
listing (its own keep-or-port sitting is separate, not required before this
item proceeds).

---

## FOUNDRY port pass, 2026-09-11 — 68/68 ported, retirement BLOCKED (see escalation)

Read directly from the three donor mods on disk (`BiomesTeam.BiomesCaverns`
2969748433, `BiomesTeam.BiomesCore` 2038000893, `BiomesTeam.BiomesPollutedLands`
3390196656 under the Steam workshop content folder) — not guessed, not
grepped from a stale dump. Cross-checked `decisions_propagated.json` (833
rows) against `biome_findings.md`: only one conflict exists system-wide
(`BMT_ChemSnail`, "in" at `the_cracked_lands` / "out" at `the_rot`) — see the
escalation below, this resolution is now in question.

**Port mechanics** (script-driven reference closure, not hand-typed): started
from the 68 target defNames, walked every `ParentName`, `Name=` (abstract
defs), leaf-text, and **dictionary-style XML tag** (`<butcherProducts><BMT_X>`
— the tag itself is the ref) reference until closed. Landed on **274** total
defs (68 species + 206 dependencies: bodies, eggs, leather/chitin/silk,
sounds, hediffs, damage types, life stages, one FactionDef for the pustule
hornet hive, one RulePackDef). Renamed `BMT_` → `RSW_` throughout (defName,
`Name=`, `ParentName=`, dictionary tag names, leaf-text refs — all four
reference shapes, verified zero leftover `BMT_`/`BiomesCore.` tokens outside
free-text tradeTags strings, which carry no def and were left alone).
Stripped every `modExtensions`/`comps`/`compClass`/`hediffClass`/`needClass`
field naming a C# class in `BiomesCore.*`, `BMT_PollutedLands.*`,
`PathfindingFramework.*` (inactive on this mod list) or
`VEF.AnimalBehaviours.*` (presence unconfirmed) — the creature keeps its
stats/body/art, not the donor-framework-only behaviour (pack defense,
lure-prey AI, filth trail, water-walker, dig-periodically, hermaphroditic-mate
job giver, corpse spawner, etc.); each def falls back to its vanilla base
class. Two non-resident adult forms (`RSW_RoyalRhino`, `RSW_ShatterjawBeetle`)
are ported as back-end `evolveIntoPawnKindDef` targets for their resident
larva/pupa stages — "out" for biome residency per the ruling, but required so
the vanilla evolve mechanism (confirmed vanilla, not donor C#) doesn't dangle.
440 texture files + all referenced sound-clip folders copied verbatim from
the donor's own `Textures`/`Sounds` trees, texPaths repathed to
`swanimals/BiomesTeam/<original path>` (audio to `Sounds/BiomesTeam/...`);
vanilla-Core reuse paths (`Things/...`, `World/...`) left untouched by design.

Output: `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/{ThingDefs_Races,
ThingDefs_Items,Bodies,SoundDefs,Support}/RSW_BiomesTeamPort_*.xml`.
`validate_patch.py --defs <Data> --defs <Workshop> --defs <Mods>`: **0
errors** on 4/5 files; the 5th (`ThingDefs_Items`) flagged 2 as ERROR
(`RSW_Filth_Acidic_Snail_Slime`/`RSW_Filth_Snail_Slime` reusing vanilla
`Things/Filth/Spatter`) — **verified false positive**: that exact path is
used by vanilla's own `Filth_Blood`/`Filth_BloodInsect`/`Filth_Slime`
(`Data/Core/Defs/ThingDefs_Misc/Filth_Various.xml`); the validator mis-treats
`Things/` as claimed by this mod because SWBestiary already carries other
content under `Textures/Things/...`. 3 WARN on `RSW_Yooka` reusing vanilla
`Dessicated_Alpaca` — expected caveat (validator can't see packed
asset-bundle textures), Alpaca is a real vanilla animal.

### Live wiring found and repointed (NOT part of the original brief — found
while checking for dangling donor references)

The three donor mods turned out to be **already load-bearing** in already-
shipped RimUtinni content, gated with `MayRequire="biomesteam.*"` — retiring
them blind would have silently dropped these from the live game. Repointed
every occurrence whose defName is one of the ruled 68, `BMT_X
MayRequire="biomesteam.*"` → `RSW_X MayRequire="mandrake.rsw.swbestiary"`
(mirrors the pattern `SandFishing_CrackedLands.xml` already uses for
`RSW_DuneCrawler`): **27 wildAnimals/butcherProducts entries across 12 hand-
authored files** (`RUT_CrackedLands/Miasma/AridShrubland/Desert/FeverWood/
Greentide/Scarlands/PoisonForest/TheRot/Webwork/Wasteland.xml` +
`RUT_RotSporeKit_MantisScythe.xml`'s `BMT_FungalMantisClaw` butcher product),
plus **26 rows in `design/Jawa/fauna/cast_assignment.csv`** (defName + `mod`
column repointed to `RimMandrake: SW — Bestiary`, reason field annotated).

## Owner rulings, 2026-09-11 card sitting (BENCH) — the two open calls are made

1. **Retirement STANDS.** The same-day conflict (00:03 "port then RETIRE" vs
   the ~00:18 Wave-4 "keep-and-suppress for … the Biomes-team family") is
   RULED: the specific correction wins — the three `biomesteam.*` mods RETIRE
   **after** the three escalation gates below clear and the RSW_ port is
   proven live. The Wave-4 record in
   `design/Jawa/mods/stat_normalization_audit_2026-09-09.md` now carries the
   exception. Does NOT change MVB/Alpha Animals keep-and-suppress.
2. **The 7 stragglers are CUT** (escalation §2's roster: `BMT_ChemSnail` at
   BOTH `the_cracked_lands` and `the_rot`, `BMT_CaveSpider`, `BMT_GiantSlug`,
   `BMT_GiantSnail`, `BMT_Pillbug`, `BMT_GlowBat`): delete their live biome
   entries (the `MayRequire`-gated wildAnimals/butcherProducts rows and the
   flier extraction) so nothing dangles at retirement. They are NOT added to
   the port. FOUNDRY executes with the rest of this item.

## ESCALATION — retirement is NOT safe yet, three open items

1. **GATE (1) IS MOOT, CLOSED 2026-09-20 (FOUNDRY) — `BiomeCast_Ashkarr.xml` is
   retired, not regenerated.** The "regenerate once the SWBestiary `RSW_` port
   deploys and the dump refreshes" framing this gate opened with was itself wrong:
   both preconditions were met this pass (SWBestiary's `BiomesTeamPort` defs
   deployed live, `Mods/SWBestiary/Defs/BiomesTeamPort/`, 7 files byte-matching
   the repo; the 2026-09-20T07-47-24Z capture resolves 395 `RSW_` PawnKindDefs),
   and regenerating against that fresh data still produced a file whose every
   xpath targets a biome defName painted on **zero** of Ash'karr's 21,872 tiles
   (independently re-measured off a fresh parse of `ASHKARR_WORLDMAP_tiles.csv`,
   not just the generator's own coverage check) — all 22 are pre-
   `BIOME_OWNERSHIP_WAVE_1` (2026-09-09) donor/vanilla names, superseded by
   `RUT_`-prefixed BiomeDefs that carry their own hardcoded `wildAnimals`
   natively. **Confirmed dead, not "very likely" — `BiomeCast_Ashkarr.xml` is now
   deleted** (design/, src/, and the deployed Steam Mods copy), full writeup at
   `infrastructure/state/items/closed/BIOME_CAST_PATCH_DEAD_NAMES_1.md`. There is
   nothing left to regenerate; do not re-open this gate on a future pass without
   reading that item first. `gen_cast_patch.py` itself was kept (a live,
   unrelated mechanism — `biome_wildbiomes_evictions.py` — imports one of its
   helper functions) and now refuses to write a dead cast file if re-run.
   **This file also carries zero `wildPlants` content and was never the source of
   any plant crossref error** — that mechanism belongs to
   `CUT_FALLOUT_GENERATED_DATA_1` (`BiomeFlora_Ashkarr.xml`/`biome_flora.py`), a
   separate item this pass also advanced (see its own notes).
   ⚠️ **A sibling generator is NOT safe the same way**: `animal_tolerances.py`
   (deployed as `AnimalTolerances_Ashkarr.xml`, 401 live `ComfyTemperatureMin/Max`
   operations on ~200 animals) has the identical dead pre-migration-name join,
   but because its xpath targets the animal's own def rather than a biome
   defName, regenerating it would silently **delete** a live hard-spawn-gate
   temperature safety net rather than no-op. Not fixed, not touched — flagged
   separately at `infrastructure/state/items/closed/ANIMAL_TOLERANCES_JOIN_BROKEN_1.md`.
2. **GATE (2) DONE — the 7 CUT stragglers have no live biome rows left.** Re-measured
   2026-09-26: no `BMT_ChemSnail/CaveSpider/GiantSlug/GiantSnail/Pillbug/GlowBat` row in
   any biome XML under `src/` (RUT_TheRot included); the only remaining mentions are
   comments, census CSVs under `design/`, and `PatchOperationConditional`-guarded
   `MegafaunaYield.xml` ops that no-op without the donor.
3. **GATE (3) DONE — `ROT_SPORECLOUD_PORT_1` closed at `f4d8dbf2b`**: `RUT_SporeCloud` runs
   on our own `GameCondition_EnvironmentalWeather`, live-proven by BENCH's Battery F
   2026-09-18 (unroofed pawns gain `RUT_SporesBuildup`, roofed and mechanoids do not).
   The Cracked Lands fish pair (`BMT_Rocktooth`/`BMT_Boneblade`, the last biomesteam refs
   in any `fishTypes`) is ported as `RSW_Rocktooth`/`RSW_Boneblade` at `9cfdb672c`
   (`RSW_BiomesTeamPort_Fish.xml`, art under `swanimals/BiomesTeam/`), deployed, and
   `RUT_CrackedLands` + the `RM_FloodedCanyon` mirror repointed.

## Retirement state, 2026-09-26 — two of three donors are already OFF the live list

`biomesteam.biomescaverns` (cut by `CAVERNS_PARITY_BUILD_1`) and
`biomesteam.biomespollutedlands` are inactive in the live 630-mod `ModsConfig.xml` and in
`ModsConfig.FULL.LATEST.xml`. Only **`biomesteam.biomescore`** remains active. A
dependents sweep over every active mod's v1.6 load folders found no other active mod
depending on it (About.xml) and no ungated def reference to its 212 defs in any active
mod or in `src/` (every hit is a comment, a `MayRequire`, or a conditional-guarded op).

**biomescore RETIRED 2026-09-27 (owner: "try to fix the savegame then retire the retirable"),
commit `51ede08fe`.**

- **Save scrubbed first, offline.** Backup:
  `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-biomescore-retire-20260927T055758Z` (sha256
  identical to the pre-edit save). Script `Transient/canonical_save_biomescore_scrub_2026-09-27.py`
  (binary mode, line surgery, never in place). Removed: the `biomesteam.biomescore` row from all
  three `<meta>` lists (positional, 617 → 616); the two map components
  `BiomesCore.SpecialTerrainList` / `BiomesCore.Locations.LocationGrid`; the 3 `BMT_HermeticArmor`
  + 1 `BMT_HermeticHelmet` Things (worn, world pawns) and the 4 `BMT_HermeticSuitHediff` hediffs
  that reference them; one `VAE_Footwear_Shoes` made of `BMT_Sharkskin` (never ported); plus every
  name-only reference to biomescore's 213 defNames — 37 `priceHistoryRecorders` key/value pairs
  (removed positionally, asserted aligned), 109 flat filter entries, 9 Work Tab
  `BC_HarvestAnimalProduct` rows, 2 auto-slaughter configs, 1 NPC contract, 2 tale `<app>` fields.
  Three worn apparel items had their `<stuff>` repointed to the identical ported material
  (`RSW_FragileChitin`, `RSW_WeakChitin`, `RSW_BiomesCore_CrabShell`). 543 lines / 16,937 bytes,
  CRLF preserved (0 bare LF), whole-file ElementTree parse OK. Re-census over all 213 donor
  defNames + `BiomesCore.*` classes: **0** (was 145 rows); controls `>Steel<` 917 and `>Human<` 864
  unchanged. Terrain grid (savemap, 629-mod dump) holds no donor terrain.
- **ModsConfig**: live 630 → **629**, FULL.LATEST recaptured (`modlist_swap.py --capture-full`),
  pre-edit copy `infrastructure/state/modlists/ModsConfig.PRESWAP.20260926_230202_pre_biomescore_retire.xml`.
  `retired_mods.json` lists it; the three `Biomes! Core` FindMod blocks (Armour_Leather,
  MegafaunaYield, PawnFlavorPhase2_ThoughtDef) deleted and deployed; `selftest_retired_mods` 0 failures.
  FlowWorks' `MayRequire="biomesteam.biomescore"` affordance rows stay by design (they degrade to absent).
- **OWED: live verification** — load the canonical save on the full 629 list, expect
  `compatible`/0 missing mods and no `Could not load reference` for any BMT_/BiomesCore name.
  Blocked by `BLUEDESERT_ORPHAN_LOAD_CRASH_1` (full-list cold load currently resets ModsConfig).
  Do this once that item closes, then close this one.

## Live verification attempted 2026-09-28 — NOT CLOSED, mixed result, needs a BENCH/owner call

`BLUEDESERT_ORPHAN_LOAD_CRASH_1` closed; picked this up. Mod-list level confirmed clean:
**614-mod live `ModsConfig.xml`, `biomesteam.biomescore`/`biomescaverns`/`biomespollutedlands`
all absent** (ElementTree-parsed). (Mod count has moved from 629→614 since this item's last
update via unrelated same-day retirements/consolidation — `THEY_MOD_REPLICATION_1` and the
`BAROQUE_BIOMES_WAVE1/2/3` biome-mod-unification waves — not a regression, just this project's
own fast pace; see `ModsConfig.FULL.LATEST.xml`.)

**Blocked, then unblocked, by an unrelated defect** (full root-cause + fix in
`GASDAMAGING_PARENTNAME_UNRESOLVED_1`, cross-referenced there in full — not duplicated here):
today's biome-mod-unification wave folded `mandrake.rm.creaturebehaviors` and
`mandrake.rm.environmentalhazards` into `mandrake.rm.biomes` but left four OTHER mods
(`mandrake.rm.shipvermin`, `mandrake.rut.rotsporekit`, `mandrake.rsw.swbestiary`,
`mandrake.rm.explosivegrowth`) still declaring `loadAfter`/`modDependencies` on the now-defunct
standalone packageIds, so they loaded before `mandrake.rm.biomes` and a `RotSporeKit` def
(`RUT_ChokingSpores`, unrelated to BMT_ content) got a null `thingClass`, crashing
`Game..ctor()` via `ReadingPolicyDatabase.GenerateStartingPolicies()` for EVERY fresh game
construction (LoadGame or quicktest) — this is why every `load_game_ready` call timed out at
`Entry`/`hasCurrentGame:false` with a stuck `Dialog_MessageBox`, regardless of mod content.
Fixed (4 `About.xml` loadAfter repoints + a live `ModsConfig.xml` reorder + a stale
`FlowWorks.dll` rebuild+redeploy — see that item for the commits). **This was NOT caused by,
and does not touch, any BMT_/BiomesCore content** — confirmed by reading the crash's own def
(`RUT_ChokingSpores`, a RotSporeKit gas def with no BMT_ lineage) and by the fact none of the
four affected mods are Biomes!Team donors.

**Once unblocked, the canonical save loaded successfully all the way to `programState: Playing`**
(not just `mapData`) with `ignoreModCompatibility: true` — first clean fresh-Game construction
this whole investigation. `rimworld/list_saves` still reports `missing_mods`/`compatible:false`
(616 recorded vs 614 active, 8 missing) — **none of the 8 are Biomes!Team donors**: `They!`,
`Cryptoforge`, and six RM_/RUT_ mods folded into `mandrake.rm.biomes` by today's consolidation
(their content is now reachable under the unified mod, just under a packageId the save's stale
meta list doesn't know about — expected drift, not a real absence).

**The `Could not load reference` sweep is mixed, not clean**, checked specifically for lines
AFTER the Scribe load actually starts (`"Loading game from file CANONICAL_ASHKARR_START_2026-09-12
with mods:"`, not the earlier def-load-time noise a prior pass on this item already
characterized as pre-existing/non-fatal on 2026-09-27):
- **104 distinct BMT_-prefixed defNames** (eggs/meat/corpses of ~20 creature species — Maxolotl,
  LandOctopus, BiliousVarog, BloodletterPetrel, CarrionVulture, FamineLocust, GastroToad,
  Glowtail, Megakrill, Megaroach, MucklurkerCatfish, MutatingTumorfish, Norphea,
  PustuleHornetQueen, Sacapillar, Screecher, SludgeCrawler, Swarmcaller, TaintedTurtle,
  TripleSnapper, SmogMoth, BarbedPangolin, BunkerBug, ColonyPustuleHornet, Creature_Mantrap and
  more) match, name-for-name, the SAME set already present in
  `infrastructure/state/logs/harvested/Player_fulllist_clean_after_sumpgate_20260927T063252Z.log`
  (2026-09-27, **pre-dating** this item's biomescore retirement work) — this is standing,
  already-precedented, non-fatal save debt, not something this item's own work introduced.
- **~14 ADDITIONAL distinct BMT_-prefixed defNames NOT in that 2026-09-27 reference set**:
  `Blueprint_`/`Frame_`/`Blueprint_Install_` variants of `BMT_Chinampa_{Granite,Limestone,
  Marble,Sandstone,Slate}`, `BMT_DenseSandWall`, `BMT_GlacialIceBuildable`,
  `BMT_IceDiggingSpot`, `BMT_IceWallBuildable`, `BMT_LavaGenerator`, `BMT_LightSandWall`,
  `BMT_MagmaPump`, `BMT_PontoonBridge`, `BMT_SandDiggingSpot` — all terrain/building content
  (thematically Polluted Lands/Caverns), never seen flagged before in this item's history.
  **Not chased further this pass** — reading which is genuinely new vs. an artifact of this
  session's different mod set (8 unrelated mods also inactive right now, forcing
  `ignoreModCompatibility`) needs a controlled comparison this session didn't have time for,
  and a fix (a caverns/pollutedlands-equivalent save scrub, mirroring biomescore's own careful
  backup+scrub+re-census procedure above) is exactly the kind of consequential action this
  item's own doctrine says to do carefully, not improvise blind.
- The broader 8-missing-mod noise (`VQE_`/`VWE_` Cryptoforge content, `They_`/`GiantAnt_Race`,
  `RUT_Lanternstone*`) is separately explained by those 8 mods' own today's-consolidation
  packageId drift (see above) and is NOT this item's concern.

**Not closing.** The mod-list-level retirement (this item's own literal remaining scope) is
clean. The save-content level shows two different signals: the LONG-STANDING BMT_ fauna debt is
precedented as acceptable elsewhere in this project and arguably satisfies this item's spirit;
the NEWLY-NOTICED BMT_ terrain/building debt does not have that precedent and is reported here
rather than assessed — a BENCH/owner call on whether that second set blocks closing, needs its
own scrub, or is itself pre-existing-and-fine (just never previously checked this specifically)
is owed before this item closes.

---

## Original escalation (superseded above, kept for provenance) — donor mod and creature count don't match

## What this pass found (measured, not guessed)

The queue line (`infrastructure/state/queue/FOUNDRY.md`) reads: *"Port the 71 cast
Beasts of the Rim creatures (41 in + 30 move per decisions_propagated) into our
tier per the SWBestiary donor-retirement pattern, then retire
mlie.beastsoftherim - owner ruled 2026-09-11 (Wave 2)."* Picking this up to
execute, the donor mod named and the 71-creature figure cited do not describe
the same mod. This is not "which 30 is ambiguous" — it is two different mods
under one item, so nothing was ported and nothing was retired this pass.

### The real `mlie.beastsoftherim` (verified against the actual Steam Workshop
folder, not a doc)

Workshop item `2194018641` (`packageId Mlie.BeastsoftheRim`, "Beasts of the Rim
(Continued)"), read directly from
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2194018641`:
**19 species, 64 total defs** (ThingDef + PawnKindDef pairs + eggs + leathers +
one wool), parsed from its own `1.6/Defs/**/*.xml` with `xml.etree` (not grepped
— this repo's own rule against blind scans applied even though the file set is
small): AlligatorMan, Armadillo, Bardelot, BlackBear, BlackBearMan, Giantala,
Worm (Giant Earthworm), Gigantelope, Jerbal, Mandrill, MandrillMan, Megasquid,
Neanderthal, Penguin, Rabbuck, Toraton, Yippa, Zarander, Zebra. **None of these
19 defNames carry a `BMT_` prefix, and none appear anywhere in
`decisions_propagated.json`.** (`design/Jawa/mods/stat_normalization_audit_
2026-09-09.md` cites "45 defs" for this mod from an earlier def-dump count —
close enough to be the same mod, still nowhere near 71, and the discrepancy
doesn't matter for the point below.)

### What `BMT_` actually is in this repo's own data

`design/Jawa/worldbuilding/data/beast_census.csv` (header: `defName,mod,
package_id,...`) is unambiguous: every `BMT_`-prefixed defName's `mod`/
`package_id` columns read **`Biomes! Caverns` / `biomesteam.biomescaverns`**,
**`Biomes! Polluted Lands` / `biomesteam.biomespollutedlands`**, or
**`biomesteam.biomescore`** — the "Biomes!" mod family by `biomesteam`, an
entirely different author from Mlie. `BMT` is this codebase's own census
abbreviation for "**B**io**m**es!**T**eam", not for "Beasts of the Rim" — the
initials coincide, the mods do not.

`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(generatedAt `2026-09-10T14:20:34Z`) confirms the same set: 124 `BMT_`-prefixed
rows, decision counts **41 in / 30 move / 53 out at the row level** — this is
exactly the queue line's own "41 in + 30 move" citation, and
`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`'s "BMT had 124
sitting rows (41 in / 30 move / 53 out)" line matches it precisely. At the
unique-defName level (121 names; 3 appear in 2 biome rows each) that's 38
clean "in" + 30 "move" + 1 conflicted (`BMT_ChemSnail`: "in" at
`the_cracked_lands`, "out" at `the_rot` — resolved to OUT by the later, more
current `biome_findings.md`, which lists it under `the_rot`'s departures) + 52
clean "out" = 53 out once resolved, matching the audit doc's own "53 out"
exactly. **So the 71/41/30 figures are real, measured, and fully traceable —
they just belong to `biomesteam.biomescaverns` / `biomesteam.biomescore` /
`biomesteam.biomespollutedlands`, not to `mlie.beastsoftherim`.**

Cross-checked directly: zero overlap between the 121 `BMT_` defNames in
`decisions_propagated.json` and the 19 real `mlie.beastsoftherim` defNames
above.

### Why this can't just be executed as written

`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`'s Wave 2 table (the
audit this item's own queue line cites as "owner ruled 2026-09-11, Wave 2")
lists `mlie.beastsoftherim | 45 defs` as one of nine keep-or-port mods —
`biomesteam.biomescaverns`/`biomescore`/`biomespollutedlands` are **not** on
that Wave 2 (or any wave's) retirement list at all; per `biome_findings.md`
they are live, currently-active donors that multiple biomes are actively
receiving `BMT_` arrivals from as of the 2026-09-10 sitting (e.g. `the_rot`
arrivals include `BMT_Thrumbungus`, `BMT_Yooka`; `the_scarlands` arrivals
include `BMT_CrystalFairyMole`, `BMT_MegaphoridLarva`, `BMT_Stoneback`, etc.).

Executing the item literally — port the 68 unique `BMT_` "in"/"move" species,
then retire `mlie.beastsoftherim` — would: (1) leave `mlie.beastsoftherim`'s
own real 19 species/64 defs completely unported, silently deleting them from
every biome and save the moment it's retired, the exact `WEAPONS_DONOR_
RETIREMENT_1`-style incident this project's own doctrine exists to prevent;
and (2) leave the actual `biomesteam.*` donors of the ported content fully
active and untouched, so the "port" would just duplicate content already live
under two different defName sets, retiring nothing.

## Not done this pass, deliberately

No defs generated, no art extracted, no `ModsConfig.xml` edit, no retirement —
`ModsConfig.xml` writes and mod retirements are this project's own "expensive
list" (`CHARTER.md`), and executing either on a self-contradictory brief is
strictly worse than waiting. This matches this item's own instruction to
escalate rather than guess when the "which 30" split is unclear — here the
ambiguity is one level up: which MOD.

## Escalation — needs an owner/BENCH call

1. **If the intent was the `biomesteam.*` "Biomes!" family** (which the
   measured 71/41/30 figures actually belong to): correct this item's donor
   mod name away from `mlie.beastsoftherim` to `biomesteam.biomescaverns` +
   `biomesteam.biomescore` + `biomesteam.biomespollutedlands`, confirm those
   three are actually intended for retirement (they appear nowhere in the
   ruled stat-normalization waves), and re-file/rename the item accordingly
   before any port work starts.
2. **If the intent was really `mlie.beastsoftherim`** (consistent with its
   Wave 2 audit listing): the 71/41/30/decisions_propagated figures do not
   apply to it at all — its own 19 species have never been through a
   keep-or-port sitting. A new review pass (`skills/review-sheets`, per this
   project's own established pattern for exactly this kind of call) is needed
   to decide which of its 19 species come along before any port/retirement
   work, not a straight "port 71 and retire."

No defs, patches, or `ModsConfig.xml` changes accompany this file — this is a
findings-only commit.
