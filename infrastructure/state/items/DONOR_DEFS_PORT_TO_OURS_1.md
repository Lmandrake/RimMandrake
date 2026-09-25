# DONOR_DEFS_PORT_TO_OURS_1 — everything becomes ours

## the ruling

Owner, 2026-09-20, verbatim: *"Everything should be moved t our own thing defs."*

Said while approving the desert graphics, immediately after seeing that the
desert family's 109-species roster is **3 ours to 99 donor**. It is the general
form of what `CAVERNS_PARITY_BUILD_1` already did for one donor in one biome.

## the scale, MEASURED 2026-09-20

Every owned `RUT_*` BiomeDef's `<wildPlants>`/`<wildAnimals>`, parsed by each
entry's `MayRequire` packageId. Full table and method:
`infrastructure/state/facts/biome_rosters.md`.

| entries | donor |
|---:|---|
| **160** | `mlie.starwarsanimalcollection` |
| **102** | `sarg.alphaanimals` |
| 21 | `neronix17.outerrim.droiddepot` |
| 8 | `vanillaexpanded.vgeneticse` |
| 7 | `oskarpotocki.vfe.insectoid2` |
| 6 | `sarg.alphabiomes` |
| 4 | `who.vfee.isopodageneline` |
| 3 | `sarg.alphamemes` |
| 2 each | `mlie.horrors`, `biomesteam.biomescaverns` |
| 1 each | `lingluo.cockroach`, `regrowth.botr.core` |

🔑 **Two mods carry 262 of ~330 borrowed roster entries.** Any plan that is not
mostly about those two is aimed at the tail. `RM_TheRot` is the only biome where
we already own more than we borrow (21 vs 8) — it is the benchmark for what
"done" looks like.

## the pattern to copy — it already exists twice

- **`RSW_FungalWeevil`** and **`RSW_FungalMantis`** — ported out of
  `BMT_FungalWeevil`/`BMT_FungalMantis`, wired into `RUT_TheRot.xml` under our
  own defNames (lines 131, 138). This is the shape: re-author as ours, wire the
  new name, drop the donor name from the roster.
- **`CAVERNS_PARITY_BUILD_1`** — the whole-biome version, for `Biomes! Caverns`.
  It closed having made the Lantern Deeps generate from owned defs only, verified
  with the donor ABSENT from the mod list. Read it before planning this.

## naming

Per `design/NAMING_SCHEME_PLAN.md`, three tiers: **RimMandrake** (any RimWorld
game) / **RimStarWars** (any Star Wars scenario) / **RimUtinni** (this campaign),
prefixes `RM_`/`RSW_`/`RUT_`. A ported creature is almost always `RSW_`. ⚠️ The
rename gate is long closed — `NAMING_SCHEME_EXECUTION_1` ended 2026-08-31 — so a
rename here is owed work, never something to defer to it.

🔑 **Porting and renaming are separate jobs.** A ported def keeps whatever name
it had unless `NONCANON_BEAST_RENAME_1` says otherwise; do not silently
re-christen things while porting, or neither ruling can be checked.

## spec

⛔ **Do not start porting 300 defs.** This needs a plan and an owner sitting on
the order first. What is owed before any porting:

1. **A census of what porting actually means per donor.** A creature is a
   ThingDef + PawnKindDef + art + sometimes comps and a BodyDef. Some donors are
   a straight copy with a rename; some carry C# that would have to be reimplemented
   or dropped. Grade each donor's entries by that cost.
2. **A keep/cut pass first.** Porting a species we would have cut is pure waste —
   and the desert sheet shows the roster was never keep/cut ruled at all. Cutting
   is cheaper than porting, so the cut list comes first.
3. **Order by the table above**, not by biome.
4. **A per-donor retirement test**, the `CAVERNS_PARITY_BUILD_1` shape: the donor
   ABSENT from `ModsConfig.xml` and the biome still generating.

## Watch out

- 🔴 **Never infer a def's owner from its defName prefix.** `mlie.starwarsanimalcollection`
  ships BARE defNames (`Bantha`, `Kreetle`, `Scavrat`, `Shyrack`, `Gorg`,
  `Gutkurr`, `Jamel`, `Rat`), so a prefix rule buckets the single largest donor as
  vanilla Core. A census did exactly that this session. Read `MayRequire`.
- ⚠️ **19 desert-family entries carry NO `MayRequire` guard at all** (`AB_HardyGrass`,
  `AB_Aaklac`, `AB_DessertTree`, four `RG_Plant_*`, and others). Those break on
  the donor's removal with no graceful degrade — they are the first things this
  ruling fixes, not the last.
- ⚠️ A roster can name a species from a donor **already retired** — the Rot names
  17 `BMT_` defs from a mod absent from the 621-mod list
  (`ROT_ROSTER_DEAD_DONOR_NAMES_1`). Those need dropping, not porting.
- ⛔ Vanilla Core and DLC defs (`Ludeon.*`) are NOT donors. Leave them.
- 🔴 A texture binds by `texPath`, not defName — a ported def with the donor's
  old texPath renders the donor's art or nothing.

## verify

Per donor: it is absent from `ModsConfig.xml` and every biome that used it still
generates, with its roster intact under our own defNames. Confirmed from a
post-load def dump, never from the patch files.

## criteria

The shipped game's biome rosters name our defs. Removing any third-party content
mod changes nothing a player can see.

## FOUNDRY, 2026-09-24: folding in a stray 2026-09-20 census that never landed here

Commit `78b63a97` (2026-09-20, Opus) wrote `Transient/donor_port_twin_census.md`
citing this item in its message but never touched this file — found this pass
while checking why the queue flagged this item's prose as possibly stale. The
work is real and worth keeping; folding it in rather than leaving it to rot in
`Transient/`.

**Scope**: this is a twin-duplication census of the desert family's 109-row roster
only (`DESERT_FAMILY_PORT_EXECUTION_1`'s frozen sheet), not the full-roster
donor-cost census this item's own spec step 1 asks for — it answers "how bad is
the current live-duplication problem," not "what does porting each donor's
entries actually cost." Both are still owed.

**MEASURED** (against the 618-mod dump, 2026-09-20T20:14:27Z, fingerprint-matched
to the live `ModsConfig.xml` at capture time): of the desert sheet's 75
structurally-twin-eligible rows (bare donor-style names), **66 are live
identical-label twins** — both the donor ThingDef and our `RSW_` port exist,
same label, simultaneously. 7 rows are genuinely unported yet (`Rat`,
`Terrorworm`, `Plant_Brambles`, `Plant_Bush`, `Plant_HealrootWild`,
`Plant_Ripthorn`, `Plant_ShrubLow`). 2 are near-miss twins failing only on
pluralization (`Shaak`/`shaaks`, `Skalder`/`skalders`). All from
`mlie.starwarsanimalcollection`.

**Not a defect** — confirmed against `MLIE_FAUNA_ABSORPTION_1` (closed, moved to
`items/closed/`), whose own design keeps the donor active through every wave
and only retires it after a full donor-off cold load. That item's last logged
pass (2026-09-18) had 26 of 91 Wave-C species still remaining — so the 66 live
twins are exactly that in-progress state, not new damage.

**The one real gap this surfaced**: `sarg.alphaanimals` (102 roster entries,
the SECOND-largest donor named in this item's own table) has **no retirement
plan at all** — no `ALPHA_ANIMALS_*` item exists anywhere in `items/` or
`items/closed/`. `MLIE_FAUNA_ABSORPTION_1` and `BMT_FAUNA_ABSORPTION_1` cover
the other two large donors; Alpha Animals' 102 entries have never been scoped
as a wave. That is real unfiled work, not yet filed as its own item here —
whoever plans the porting order (spec step 1/3) should treat it as a third
wave alongside the other two, not a tail item.

Files: `Transient/donor_port_twin_census.md` (the full method + per-donor
active-state table, kept as-is; this section is the summary, not a
duplicate).

Still `proposed` — the census does not authorize porting; spec step 1's
full per-donor cost grading and step 2's keep/cut pass are both still
unstarted, and `⛔ Do not start porting 300 defs` stands.

## FOUNDRY, 2026-09-24: spec steps 1 and 2, the offline prep the owner sitting needs

Read-only research pass. Nothing ported, nothing renamed, no def/XML touched.
Method and full data below so the sitting doesn't have to re-derive it.

### 1. Per-donor porting cost — MEASURED against each donor's own source

**`mlie.starwarsanimalcollection`** — not present as a mod folder on this
machine's Steam Workshop cache, but fully vendored at
`vendor/mod_sources/StarWarsAnimalCollection_src` (repo already had it). **Full
census, all 160 ThingDefs** in `1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`:

- **No `Assemblies/` or `Source/` folder in the mod at all — it is pure XML,
  zero required C#.**
- Every comp used across all 160 entries is a stock RimWorld class:
  `CompProperties_EggLayer` (×71), `CompProperties_Milkable` (×16),
  `CompProperties_Shearable` (×12), `CompProperties_CanBeDormant`/
  `WakeUpDormant` (×9 each). One render node,
  `PawnRenderNodeProperties_BulbfreakTentacle` (3 uses, one species — Beldon),
  is a **vanilla Anomaly DLC class** reused for a tentacle look, not custom.
- Two entries carry a `MayRequire`-guarded soft extension
  (`pathfinding.framework`'s `MovementExtension`, `Mlie.XNDNocturnalAnimals`'s
  `ExtendedRaceProperties`) — both optional, both degrade to nothing if
  absent.
- **GRADE: LOW, essentially uniform across all 160/160.** Straight
  ThingDef+PawnKindDef copy-with-rename + art-copy job, the `RSW_FungalWeevil`
  shape exactly. Nothing here needs reimplementing.

**`sarg.alphaanimals`** — vendored nowhere in this repo; measured live from the
Steam Workshop cache (content id `1541721856`, packageId confirmed from its own
`About.xml`). Of this donor's **102 roster entries** (per this item's own
2026-09-20 table), **66 were matched and graded directly** — the ones that
appear as literal `<li MayRequire="sarg.alphaanimals">` rows inside our own
`RUT_*.xml` BiomeDef files. The remaining ~36 are wired through
`UtinniPatches/Patches/WildAnimals_*.xml` injection patches and were **not**
individually graded this pass — flagging this as a sample, not full coverage,
per the task's own allowance. (The donor's whole 141-ThingDef races library
uses the same comp vocabulary uniformly, so the ungraded remainder likely
splits the same way, but that's an inference, not a measurement.)

- **Every one of the 66 graded entries carries `VEF.AnimalBehaviours.AnimalStatExtension`
  at minimum** — this donor's entire cast rides on Vanilla Expanded Framework's
  "Animal Behaviours" module (packageId `vanillaexpanded.vfecore`), not on
  vanilla Core comps.
- 🔑 **`vanillaexpanded.vfecore` is already a permanent, load-bearing
  dependency of our OWN content** — `src/RimStarWars/SWBestiary` (the
  BiomesTeamPort races/items/bodies/sounds), `src/RimStarWars/Armoury`, and
  `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml` all reference
  `VEF.*` classes directly today. So referencing `VEF.AnimalBehaviours` comps
  on our own ported ThingDefs is **not new C# work** — it's XML authored
  against a framework we already keep regardless of Alpha Animals' fate.
  **61 of 66 graded entries (92%) are this shape — GRADE MEDIUM**: copy +
  rename + re-verify the VEF comp block, not a zero-risk port but not
  reimplementation either.
- **5 of 66 additionally use `AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher`**
  — `AA_Agaripawn`, `AA_Agaripod`, `AA_DecayDrake`, `AA_MycoidColossus`,
  `AA_Thermadon`. That class lives in Alpha Animals' own private
  `AlphaBehavioursAndEvents.dll`, which disappears the moment the donor mod
  folder is dropped. **GRADE HIGH**: needs either reimplementing that comp in
  our own C#, or accepting the cosmetic loss (a growth-stage graphics
  refresher — plausibly droppable, but that's a call for the sitting, not this
  pass).
- Full grade table (66 entries, name / grade / comp classes) is in the
  session's working notes; the counts above are the load-bearing numbers.

**Portability gap worth naming**: Star Wars Animal Collection's source is
vendored in-repo; Alpha Animals' is not. A future pass done from a machine
without this Steam Workshop cache (e.g. RimSage's own index did not have
either donor loaded this session, likely stale/mod-set-mismatched) cannot
re-derive the Alpha Animals numbers above without vendoring its source too.

### 2. Keep/cut ruling status — repo-wide check, not desert-only

Checked every biome whose `RUT_*` BiomeDef references either donor (22 biomes)
against its `design/Jawa/worldbuilding/biomes/rosters/*.json` `fauna[].action`
field and any biome-specific fauna-roster sitting doc.

🔴 **The `action: "keep"/"adjust-keep"/"import"` field inside every roster
JSON — including the desert's — is NOT an owner ruling.** This item's own
history already established that the desert roster (which carries 13 `keep`
and 4 `import` actions on donor rows in `desert.json` right now) was ruled by
the owner as "never keep/cut ruled at all." That verdict generalizes: these
fields are a working/proposed categorization, not a sat decision, **repo-wide**.
Do not mistake a JSON `action` field for a ruling anywhere in this roster set.

The only two donor-touched biomes with an **actual dated owner ruling**
(RULED CUT / RULED KEEP, per-row, carded or typed, in a dedicated
`*_fauna_roster_*.md` sitting doc) are:

| biome | sitting doc | donor rows ruled |
|---|---|---|
| **Sump** | `sump_fauna_roster_2026-09-24.md` | `AA_TarGuzzler`→`RM_Gulveth`, `AA_Bumbledrone`→`RM_Thrummel`, `AA_BumbledroneHierophant`→`RM_ThrummelWarden`, `AA_BumbledroneQueen`→`RM_ThrummelBroodmother` — all RULED replace, 2026-09-24 |
| **Webwork** | `webwork_fauna_roster_2026-09-23.md` | `Wyyyschokk`, `Kreetle`, `Shyrack` (`mlie.starwarsanimalcollection`), `RSW_JewelBeetle` — all RULED CUT, 2026-09-23/24 |

Two more biomes have a sitting in progress with behaviour-level rulings landed
but donor rows only **PROPOSED**, not yet carded:

| biome | doc | state |
|---|---|---|
| Miasma | `miasma_fauna_roster_2026-09-23.md` | structural rulings landed (tier, warden mother, stranded); fauna-row dispositions marked PROPOSED, execution explicitly "by nobody here" |
| Fever Wood | `fever_wood_fauna_roster_2026-09-23.md` | behaviour rulings landed (borer galleries, thornbug contract); no per-donor-row RULED CUT/KEEP table yet |

**Every other donor-touched biome has no keep/cut ruling of any kind found** —
Arid Shrubland, Contagion, Cracked Lands, Forsaken Crags, Greentide, Grey Sea,
Nightside Ice, Poison Forest, Propane Lake, Scarlands, Slime, The Forge, The
Rot, Twilight Sea, Wasteland, Weeping Stones, and Desert (confirmed, matches
this item's existing finding). **Fuel Snows and Umbra have no
`rosters/*.json` at all** — even the unruled working categorization is
missing for those two.

Per-biome donor-row and eviction counts (from each roster JSON, `action`
field distribution — working categorization, not rulings) are in the
session's working notes; available on request rather than reproduced here to
keep this section a decision table, not a dump.

### 3. Ordering table (by entries, cost as a column — not a recommendation)

| donor | roster entries | measured cost | keep/cut state |
|---:|---|---|---|
| 160 | `mlie.starwarsanimalcollection` | **LOW**, 160/160 measured, pure XML, zero required C# | 2 of its touched biomes (Webwork) have a dated CUT ruling; the rest do not |
| 102 | `sarg.alphaanimals` | **MEDIUM** (61/66 sampled) / **HIGH** (5/66 sampled, private-assembly comp) | 1 of its touched biomes (Sump) has a dated replace ruling; the rest do not |

Not concluded here: which donor goes first is the owner sitting's call per
this item's own spec (`⛔ Do not start porting 300 defs`). The facts above are
what step 1 and step 2 were owed before that sitting; both are now available
rather than abstract.

## census: Alpha Animals (AA_) donor — FOUNDRY, 2026-09-24

Read-only research, step 1 of this item's own spec, for the `sarg.alphaanimals`
donor specifically. Nothing ported, renamed, cut or edited; no Cherry Picker,
roster or live/deployed file touched. Supersedes the sampled 66/66-of-102 note
in the "spec steps 1 and 2" section above for this donor — this pass is full
coverage of what's currently live, derived fresh rather than reused from that
session's un-committed working notes.

**Coverage: 66 of 67 currently-live `AA_`-referencing biome-roster entries,
100% of the resolvable ones.** One entry (`VFEI2_BlackSwarmling`, see below)
is not an Alpha Animals def at all and is excluded from the table and count.

### Method — MEASURED, not scanned

1. **Live roster membership**: fresh `xml.etree.ElementTree` parse of all 26
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`, walking each
   `BiomeDef`'s `<wildAnimals>`/`<wildPlants>` children and keeping every
   entry whose `MayRequire="sarg.alphaanimals"` — the same element-keyed
   method as `facts/biome_rosters.md`, re-run fresh rather than trusting that
   file's 2026-09-20 snapshot. Also checked every `UtinniPatches/Patches/`
   file for `AA_`-referencing `PatchOperationAdd`/`Replace` blocks
   (`WildAnimals_CrackedLands.xml`, `WildAnimals_Greentide.xml`,
   `WildAnimals_Pyrelands.xml`) — all three patch either duplicate what the
   BiomeDef XML already carries directly, or (Pyrelands) only mention `AA_`
   names in historical comments for a port already completed
   (`PYRELANDS_DONOR_PORT_4`); no patch adds an `AA_` def invisible to the
   direct BiomeDef scan.
   **Result: 67 unique defNames, 97 (defName, biome) pairs** — drift since
   the 2026-09-20 snapshot (102 pairs, 69 unique) is real, not measurement
   noise: `AA_AnimaColossus`, `AA_AuroraSylph` and `AA_Skyeel` are newly live
   (not in the 09-20 census); `AA_DesertAve`, `AA_FissionMouse`,
   `AA_Gigantelope`, `AA_MammothWorm` and `AA_Needleroll` are no longer live
   (evicted or ported since). Per `BIOME_SPECIFIC_FAUNA_LAW_1`, evictions are
   stopped project-wide as of 2026-09-22 — these five are read as prior
   ports/cuts, not a live eviction sweep.
2. **Per-def cost grading**: donor mod resolved live from the Steam Workshop
   cache at `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1541721856/1.6`
   (packageId `sarg.alphaanimals` confirmed from its own `About.xml`, content
   id `1541721856`). For each of the 67 defNames, parsed every
   `Defs/**/*.xml` file to find its `ThingDef`, walked its `ParentName` chain
   to collect every `compClass`/`workerClass`/`*Class` attribute (comps,
   death-action workers, hediff extensions), and separately resolved any
   `PawnRenderTreeDef` the ThingDef's render tree references, walking ITS
   render nodes for `Class` attributes too — the render-tree pass matters:
   the comp-only sweep alone would have missed two HIGH-grade defs
   (`AA_Mantrap`, `AA_OcularJelly`) whose only private-assembly dependency is
   a custom render node, not a comp.
   The mod ships exactly one assembly, `1.6/Assemblies/AlphaBehavioursAndEvents.dll`
   — any class in that namespace disappears the instant the donor mod folder
   is removed, with no replacement.

### Grade key

- **HIGH** — carries a class from the donor's own private `AlphaBehavioursAndEvents.dll`
  (a `DeathActionWorker_*` or `CompProperties_GraphicsRefresher` comp, or a
  `PawnRenderNodeProperties_SpasticScaled`/`_WithIndex` render node). Porting
  means either reimplementing that class in our own C# or dropping the
  behaviour/visual it provides — a call for the owner sitting, not this pass.
- **MEDIUM** — every graded entry (65 of 66) carries at minimum
  `VEF.AnimalBehaviours.AnimalStatExtension`, from Vanilla Expanded
  Framework's Animal Behaviours module (`vanillaexpanded.vfecore`). That
  framework is already a permanent load-bearing dependency of our own content
  (`src/RimStarWars/SWBestiary`, `Armoury`, `StarWarsRaces/SW_Genes.xml`
  reference `VEF.*` directly), so referencing it on a ported ThingDef is not
  new C# risk — it's a copy+rename+re-verify job, not a reimplementation.
- **LOW** — n/a for this donor. **Unlike `mlie.starwarsanimalcollection`
  (160/160 measured LOW, pure XML, zero required C#), Alpha Animals has NO
  zero-dependency entries** — every single graded def rides the VEF
  framework at minimum. The cheapest AA_ port is still a MEDIUM.

### Result: 66 graded (100% of resolvable), 15 HIGH / 51 MEDIUM / 0 LOW

| defName | kind | our biome(s) + commonality | cost grade | notes |
|---|---|---|---|---|
| `AA_AcanthamoebaGiganteaLarge` | ThingDef+PawnKindDef | RUT_Slime 0.15 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_AcidExplosion |
| `AA_AcanthamoebaGiganteaSmall` | ThingDef+PawnKindDef | RUT_Wasteland 0.1 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_AcidExplosion |
| `AA_Aerofleet` | ThingDef+PawnKindDef | RUT_GreySea 0.05, RUT_TheForge 0.4, RUT_TwilightSea 0.05 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_AsexualReproduction; CompProperties_Floating |
| `AA_Agaripawn` | ThingDef+PawnKindDef | RM_TheRot 0.2 | HIGH | private-assembly class: AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher |
| `AA_Agaripod` | ThingDef+PawnKindDef | RM_TheRot 0.25 | HIGH | private-assembly class: AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher |
| `AA_AngelMoth` | ThingDef+PawnKindDef | RM_TheRot 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_EatWeirdFood; CompProperties_Floating |
| `AA_AnimaColossus` | ThingDef+PawnKindDef | RM_TheRot 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_AttachEffecter |
| `AA_AuroraSylph` | ThingDef+PawnKindDef | RUT_PropaneLake 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AutoNutrition; CompProperties_CauseIncident; CompProperties_Floating |
| `AA_BedBug` | ThingDef+PawnKindDef | RUT_PoisonForest 0.3 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_BloodShrimp` | ThingDef+PawnKindDef | RUT_Contagion 0.2, RUT_Greentide 0.2, RUT_Miasma 0.1 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_BoulderMit` | ThingDef+PawnKindDef | RUT_NightsideIce 0.004 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct |
| `AA_Bumbledrone` | ThingDef+PawnKindDef | RUT_Sump 0.35 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Floating |
| `AA_BumbledroneHierophant` | ThingDef+PawnKindDef | RUT_Sump 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Floating |
| `AA_Cactipine` | ThingDef+PawnKindDef | RUT_AridShrubland 0.25 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct |
| `AA_CrepuscularBeetle` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.35 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_InitialHediff |
| `AA_CrescendoAnole` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_TheForge 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_CrystalMit` | ThingDef+PawnKindDef | RUT_PoisonForest 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_EatWeirdFood |
| `AA_DarkVandal` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_DigWhenHungry |
| `AA_Darkbeast` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.005 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_SummonEclipse |
| `AA_DecayDrake` | ThingDef+PawnKindDef | RUT_Miasma 0.1, RUT_PoisonForest 0.1, RUT_Slime 0.02 | HIGH | private-assembly class: AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher |
| `AA_Drainer` | ThingDef+PawnKindDef | RUT_Contagion 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_EatWeirdFood; CompProperties_Floating |
| `AA_DrainerLarva` | ThingDef+PawnKindDef | RUT_Contagion 0.05 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Metamorphosis |
| `AA_DuskProwler` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_DuskRat` | ThingDef+PawnKindDef | RUT_ForsakenCrags 1.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Eyeling` | ThingDef+PawnKindDef | RUT_Wasteland 0.6, RUT_WeepingStones 0.1 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_FrostboundBehemoth` | ThingDef+PawnKindDef | RUT_FuelSnows 0.126, RUT_Umbra 0.126 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Frostling` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.05 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Frostmite` | ThingDef+PawnKindDef | RUT_FuelSnows 0.35, RUT_Umbra 0.35 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_DigWhenHungry |
| `AA_GiantCrownedSilkie` | ThingDef+PawnKindDef | RUT_PoisonForest 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_GreenGoo` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Slime 2.0 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_AcidExplosion; AlphaBehavioursAndEvents.PawnRenderNodeProperties_SpasticScaled |
| `AA_Helixien` | ThingDef+PawnKindDef | RUT_Contagion 0.1, RUT_Miasma 0.1, RUT_PoisonForest 0.1, RUT_Scarlands 0.08, RUT_Slime 0.075 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_CorpseDecayer; CompProperties_ThoughtEffecter |
| `AA_InfectedAerofleet` | ThingDef+PawnKindDef | RUT_Contagion 0.5, RUT_PoisonForest 0.5 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_SmallRedAcidExplosion |
| `AA_Lockjaw` | ThingDef+PawnKindDef | RUT_Miasma 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Mantrap` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Miasma 0.2 | HIGH | private-assembly class: AlphaBehavioursAndEvents.PawnRenderNodeProperties_SpasticScaled |
| `AA_Metallovore` | ThingDef+PawnKindDef | RUT_TheForge 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_EatWeirdFood |
| `AA_Mime` | ThingDef+PawnKindDef | RUT_Slime 0.01 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Untameable |
| `AA_Murkling` | ThingDef+PawnKindDef | RUT_CrackedLands 0.2, RUT_ForsakenCrags 1.0 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_CorpseDecayer |
| `AA_MycoidColossus` | ThingDef+PawnKindDef | RM_TheRot 0.25 | HIGH | private-assembly class: AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher |
| `AA_Needlepost` | ThingDef+PawnKindDef | RUT_AridShrubland 0.1, RUT_Greentide 0.3 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_InitialAbility; CompProperties_LightSustenance |
| `AA_NightAve` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_InitialAbility |
| `AA_NightMule` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_NightRam` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.09 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Nightling` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_InitialAbility |
| `AA_OcularJelly` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Contagion 2.0, RUT_PoisonForest 0.5 | HIGH | private-assembly class: AlphaBehavioursAndEvents.PawnRenderNodeProperties_SpasticScaled |
| `AA_Plasmorph` | ThingDef+PawnKindDef | RUT_Miasma 0.05, RUT_Slime 0.1 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_InitialAbility |
| `AA_RaptorShrimp` | ThingDef+PawnKindDef | RUT_Miasma 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Regeneration |
| `AA_RedGoo` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Contagion 0.75, RUT_NightsideIce 0.003 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_RedAcidExplosion; AlphaBehavioursAndEvents.PawnRenderNodeProperties_SpasticScaled |
| `AA_RedSpore` | ThingDef+PawnKindDef | RUT_Contagion 0.85 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_RedAcidExplosion |
| `AA_RoughPlatedMonitor` | ThingDef+PawnKindDef | RUT_Contagion 0.1 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AcidImmunity; CompProperties_ExplodingEggLayer |
| `AA_SandProwler` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.075 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_GraphicByTerrain |
| `AA_SandSquid` | ThingDef+PawnKindDef | RUT_CrackedLands 0.1 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_TerrainChanger |
| `AA_ShadowCharger` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.09 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_ShockGoat` | ThingDef+PawnKindDef | RUT_NightsideIce 0.03 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_Skyeel` | ThingDef+PawnKindDef | RUT_PropaneLake 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Floating; CompProperties_Regeneration |
| `AA_Slurrypede` | ThingDef+PawnKindDef | RUT_FuelSnows 0.02, RUT_Miasma 0.1, RUT_NightsideIce 0.002, RUT_Umbra 0.02 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct |
| `AA_SpinedGow` | ThingDef+PawnKindDef | RUT_Scarlands 0.15 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_SummitCrab` | ThingDef+PawnKindDef | RUT_NightsideIce 0.004 | MEDIUM | VEF.AnimalBehaviours only: CompProperties_Untameable |
| `AA_Swarmling` | ThingDef+PawnKindDef | RUT_Contagion 0.1, RM_TheRot 0.3 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension |
| `AA_TarGuzzler` | ThingDef+PawnKindDef | RUT_Sump 0.5 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_EatWeirdFood |
| `AA_Terramorph` | ThingDef+PawnKindDef | RUT_FuelSnows 0.1, RUT_NightsideIce 0.003, RUT_Umbra 0.1, RUT_Wasteland 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_EatWeirdFood; CompProperties_NearbyEffecter |
| `AA_TetraSlug` | ThingDef+PawnKindDef | RUT_NightsideIce 0.002 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Electrified; CompProperties_InitialAbility |
| `AA_Thermadon` | ThingDef+PawnKindDef | RUT_Miasma 0.1 | HIGH | private-assembly class: AlphaBehavioursAndEvents.CompProperties_GraphicsRefresher |
| `AA_Thunderbeast` | ThingDef+PawnKindDef | RUT_Slime 0.005 | HIGH | private-assembly class: AlphaBehavioursAndEvents.DeathActionWorker_SummonFlashstorm |
| `AA_Thunderox` | ThingDef+PawnKindDef | RUT_ForsakenCrags 0.09 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_Regeneration |
| `AA_Wildpawn` | ThingDef+PawnKindDef | RUT_AridShrubland 0.1, RM_TheRot 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_AsexualReproduction; CompProperties_HighlyFlammable |
| `AA_Wildpod` | ThingDef+PawnKindDef | RUT_AridShrubland 0.025, RUT_PoisonForest 0.05, RM_TheRot 0.2 | MEDIUM | VEF.AnimalBehaviours only: AnimalStatExtension; CompProperties_AnimalProduct; CompProperties_AsexualReproduction; CompProperties_HighlyFlammable |

### One anomaly found, not part of the table — `VFEI2_BlackSwarmling`

Live in `RUT_Miasma` (0.5) and `RUT_Wasteland` (0.6) with
`MayRequire="sarg.alphaanimals"` in our own BiomeDef XML, but **the def does
not exist anywhere in the Alpha Animals mod's own `Defs/` folder.** The
defName prefix (`VFEI2_`) and the packageId it actually belongs to
(`oskarpotocki.vfe.insectoid2`, already counted separately as 7 entries in
this item's own donor table) say this is a VFE Insectoid2 def, misguarded on
Alpha Animals' packageId in our XML. Practical effect: if Alpha Animals is
ever retired while VFE Insectoid2 stays active, this row would silently
vanish from both biomes even though its actual donor is still installed —
worth a fix when someone next touches `RUT_Miasma.xml`/`RUT_Wasteland.xml`,
but out of scope for this read-only census (no XML touched this pass).


### What's left

- **The `AA_` census itself is complete** — 66 of 66 resolvable live entries
  graded by real C# dependency inspection, not by name or sampling.
- **Not done here** (out of this pass's scope, per the task): the keep/cut
  pass (spec step 2, already partly covered for other donors in the section
  above — Sump and Webwork have dated rulings touching a handful of these
  defNames; the rest of the 51 MEDIUM/15 HIGH entries have no keep/cut ruling
  yet), and any decompilation of `AlphaBehavioursAndEvents.dll` itself (this
  pass read only the XML-declared class NAMES the donor's own defs attach —
  confirming those classes' exact runtime behaviour, or hunting for a
  defName-keyed Harmony patch inside the DLL, would need a decompiler and
  was not attempted).
- **`VFEI2_BlackSwarmling` mis-tagging** (above) is unfiled.

## census: Star Wars Animal Collection (Mlie) donor — FOUNDRY, 2026-09-24

Read-only research, step 1 of this item's own spec, for the
`mlie.starwarsanimalcollection` donor specifically — the larger of the two
big donors and the one the AA_ census above did not cover. Nothing ported,
renamed, cut or edited; no Cherry Picker, roster or live/deployed file
touched.

**Coverage: 76 of 76 currently-live donor-referencing biome-roster entries
(97 defName/biome pairs) — 100%.** Not "160" (this item's own 2026-09-20
donor table counts entries, i.e. duplicate defName/biome pairs, and that
snapshot is four days stale — see drift note below); 76 is the number of
**unique defNames** our rosters actually reference today, which is what a
porting plan ports once each.

### Method — MEASURED, not scanned

1. **Live roster membership**: fresh `xml.etree.ElementTree` parse of all 27
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`, walking each
   `BiomeDef`'s `<wildAnimals>`/`<wildPlants>`/`<fishTypes>` children and
   keeping every entry whose `MayRequire="mlie.starwarsanimalcollection"` —
   same element-keyed method as `facts/biome_rosters.md` and the AA_ census
   above, re-run fresh. Also grepped every `UtinniPatches/Patches/*.xml` file
   naming the packageId (`WildAnimals_CrackedLands.xml`,
   `WildAnimals_Greentide.xml`, `WildAnimals_Pyrelands.xml`,
   `AnimalBiomeDuplicates_Fix.xml`, `AnoobaDrawSize_Fix.xml`,
   `RUT_TibannaTap_BeldonWiring.xml`): `WildAnimals_CrackedLands.xml` adds 5
   live `MayRequire="mlie.starwarsanimalcollection"` rows (Gornt, Eopie,
   CanCell, Convor, Woolamander) that **exactly duplicate** what
   `RUT_CrackedLands.xml` already carries directly (same defNames/values) —
   no new members. The rest only *mention* the packageId in comments/prose,
   with zero live `MayRequire="mlie.starwarsanimalcollection"` XML elements.
   **Result: 76 unique defNames, 97 (defName, biome) pairs.**
   🔑 **Drift confirms the doctrine, doesn't just illustrate it**:
   `WildAnimals_Greentide.xml`'s own comment block (dated 2026-09-23) still
   claims `RUT_Greentide` carries `Gizka`/`Convor`/`Nuna`... as donor bare
   names; live XML shows `Gizka`, `Worrt` and `Nuna` were already repointed
   to `RSW_Gizka`/`RSW_Worrt`/`RSW_Nuna` on 2026-09-23
   (`DUPLICATE_CANON_DEFNAME_PAIRS_1`) — the comment is one day stale. The
   fresh parse is what this table is built from, not any cited count.
2. **Per-def cost grading**: donor source resolved from the repo's own
   vendored copy, `vendor/mod_sources/StarWarsAnimalCollection_src/1.6/`
   (not present as a Steam Workshop folder on this machine — confirmed
   absent under `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/`,
   matching this item's earlier note). packageId confirmed from the
   vendored `About/About.xml` (`Mlie.StarWarsAnimalCollection`). **The mod
   ships NO `Assemblies/` or `Source/` folder at all** — confirmed by a
   filesystem search of the whole vendored tree, not inferred from the
   About.xml description. Every `Class=`/`compClass`/`workerClass`/
   `verbClass`/`hediffClass`/`giverClass` attribute or tag across the
   mod's **entire** `Defs/` tree (not just the races file) was enumerated
   and checked: all resolve to vanilla RimWorld Core or DLC (Anomaly)
   classes (`CompProperties_EggLayer`, `_Milkable`, `_Shearable`,
   `_CanBeDormant`/`_WakeUpDormant`, `_Glower`, `PawnRenderNodeProperties_Parent`/
   `_Carried`/`_Spastic`/`_BulbfreakTentacle`, `Verb_CastAbility`,
   `DeathActionWorker_BigExplosion`, `ThoughtWorker_Hediff`,
   `TileMutatorWorker_WildPlants`, etc.) — with exactly two exceptions, both
   **`MayRequire`-guarded soft extensions from OTHER mods**
   (`Mlie.XNDNocturnalAnimals`'s `NocturnalAnimals.ExtendedRaceProperties`
   and `pathfinding.framework`'s `PathfindingFramework.MovementExtension`),
   confirmed optional/degrade-to-nothing from the donor's own `<li
   MayRequire="..." Class="...">` guard syntax. For each of the 76 live
   defNames: resolved its `ThingDef` (+ `PawnKindDef` for animals, + parent
   chain for the 8 wild-plant variants, which inherit from a farmed base def
   in the same file), and separately resolved a `PawnRenderTreeDef` for any
   def that has one (`Beldon`, `Lylek` — both live in our rosters), walking
   its render nodes for `Class`/`workerClass` too, same method as the AA_
   census's render-tree pass.

### Grade key

- **LOW** — straight ThingDef+PawnKindDef(+art) copy-with-rename, comps are
  vanilla stock or an optional cross-mod extension that degrades to nothing
  absent its own donor.
- MEDIUM/HIGH — n/a for this donor; unlike `sarg.alphaanimals` (NO
  zero-dependency entries, every graded def rides a private assembly or the
  VEF framework at minimum), Star Wars Animal Collection ships **zero**
  required C# anywhere in the mod, so there is no mechanism by which a def
  here could grade above LOW.

### Result: 76 of 76 graded (100%), 76 LOW / 0 MEDIUM / 0 HIGH

12 of the 76 carry an optional soft-dependency class
(`NocturnalAnimals.ExtendedRaceProperties`: `Anooba`, `Borcatu`, `Shyrack`,
`Sketto`, `Voorpak`, `Vornskyr`; `PathfindingFramework.MovementExtension`:
`Dragonsnake`, `Falumpaset`, `Fambaa`, `Igitz`, `Mott`, `Ollopom`,
`Pikobis`) — still graded LOW because both extensions are `MayRequire`-guarded
by mods that are not this donor and disappear cleanly if absent; a port just
carries the same optional `<li MayRequire="...">` block forward unchanged.
2 entries (`Beldon`, `Lylek`) also carry a `PawnRenderTreeDef`, using only
vanilla/Anomaly-DLC render node classes (`PawnRenderNodeProperties_Parent`/
`_Carried`/`_Spastic`/`_BulbfreakTentacle`) — porting them means copying the
`PawnRenderTreeDef` alongside the ThingDef, not reimplementing anything.

| defName | kind | our biome(s) + commonality | cost grade | notes |
|---|---|---|---|---|
| `Anooba` | ThingDef+PawnKindDef | RUT_AridShrubland 0.4; RUT_Miasma 0.3 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `Bantha` | ThingDef+PawnKindDef | RUT_AridShrubland 0.5; RUT_WeepingStones 0.1 | LOW | stock comps only: CompProperties_Milkable, CompProperties_Shearable |
| `Beldon` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Greentide 0.008; RUT_TheForge 0.08 | LOW | stock comps only: CompProperties_EggLayer, CompProperties_Milkable, PawnRenderNodeProperties_BulbfreakTentacle, PawnRenderNodeProperties_Carried, PawnRenderNodeProperties_Parent |
| `Boma` | ThingDef+PawnKindDef | RUT_WeepingStones 0.15 | LOW | stock comps only: CompProperties_EggLayer |
| `Borcatu` | ThingDef+PawnKindDef | RUT_Wasteland 0.7 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `CanCell` | ThingDef+PawnKindDef | RUT_CrackedLands 0.2 | LOW | stock comps only: CompProperties_EggLayer |
| `Cannok` | ThingDef+PawnKindDef | RUT_AridShrubland 0.16 | LOW | no comps, plain ThingDef |
| `Clodhopper` | ThingDef+PawnKindDef | RUT_Greentide 0.7 | LOW | stock comps only: CompProperties_EggLayer |
| `Convor` | ThingDef+PawnKindDef | RUT_AridShrubland 0.08; RUT_CrackedLands 0.2; RUT_FeverWood 0.3; RUT_Greentide 0.3 | LOW | stock comps only: CompProperties_EggLayer |
| `Corinathoth` | ThingDef+PawnKindDef | RUT_AridShrubland 0.4 | LOW | no comps, plain ThingDef |
| `Dactillion` | ThingDef+PawnKindDef | RUT_WeepingStones 0.15 | LOW | stock comps only: CompProperties_EggLayer |
| `Dalgo` | ThingDef+PawnKindDef | RUT_Greentide 0.18 | LOW | no comps, plain ThingDef |
| `Dewback` | ThingDef+PawnKindDef | RUT_WeepingStones 0.4 | LOW | stock comps only: CompProperties_EggLayer |
| `Dragonsnake` | ThingDef+PawnKindDef | RUT_Greentide 0.12 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Eopie` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8; RUT_CrackedLands 0.25; RUT_WeepingStones 0.1 | LOW | stock comps only: CompProperties_Milkable |
| `Falumpaset` | ThingDef+PawnKindDef | RUT_Greentide 0.3 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Fambaa` | ThingDef+PawnKindDef | RUT_FeverWood 0.02; RUT_Greentide 0.25 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Fanback` | ThingDef+PawnKindDef | RUT_WeepingStones 0.5 | LOW | stock comps only: CompProperties_EggLayer |
| `FeralNerf` | ThingDef+PawnKindDef | RUT_AridShrubland 0.04 | LOW | stock comps only: CompProperties_Milkable, CompProperties_Shearable |
| `FrilledGorg` | ThingDef+PawnKindDef | RUT_AridShrubland 1.0 | LOW | stock comps only: CompProperties_EggLayer |
| `Gelagrub` | ThingDef+PawnKindDef | RUT_FeverWood 0.4; RUT_Greentide 0.3 | LOW | stock comps only: CompProperties_EggLayer, CompProperties_Milkable |
| `Gorg` | ThingDef+PawnKindDef | RUT_AridShrubland 1.0 | LOW | stock comps only: CompProperties_EggLayer |
| `Gornt` | ThingDef+PawnKindDef | RUT_CrackedLands 0.3 | LOW | no comps, plain ThingDef |
| `GraniteSlug` | ThingDef+PawnKindDef | RUT_PoisonForest 0.15 | LOW | no comps, plain ThingDef |
| `Grank` | ThingDef+PawnKindDef | RUT_AridShrubland 0.2; RUT_Miasma 0.3 | LOW | no comps, plain ThingDef |
| `Hawkbat` | ThingDef+PawnKindDef | RUT_Greentide 0.18 | LOW | stock comps only: CompProperties_EggLayer |
| `Hssiss` | ThingDef+PawnKindDef | RUT_Greentide 0.18 | LOW | stock comps only: CompProperties_EggLayer |
| `Igitz` | ThingDef+PawnKindDef | RUT_AridShrubland 0.7 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Iriaz` | ThingDef+PawnKindDef | RUT_AridShrubland 1.0 | LOW | no comps, plain ThingDef |
| `Jamel` | ThingDef+PawnKindDef | RUT_WeepingStones 0.1 | LOW | no comps, plain ThingDef |
| `Kinrath` | ThingDef+PawnKindDef | RUT_Greentide 0.3 | LOW | stock comps only: CompProperties_CanBeDormant, CompProperties_EggLayer, CompProperties_WakeUpDormant |
| `Klorslug` | ThingDef+PawnKindDef | RUT_Greentide 0.4 | LOW | stock comps only: CompProperties_CanBeDormant, CompProperties_EggLayer, CompProperties_WakeUpDormant |
| `KowakianMonkeyLizard` | ThingDef+PawnKindDef | RUT_AridShrubland 0.01 | LOW | no comps, plain ThingDef |
| `Kybuck` | ThingDef+PawnKindDef | RUT_AridShrubland 0.6 | LOW | no comps, plain ThingDef |
| `LavaFlea` | ThingDef+PawnKindDef | RUT_TheForge 0.25 | LOW | stock comps only: CompProperties_EggLayer, CompProperties_Shearable |
| `LongtailGorg` | ThingDef+PawnKindDef | RUT_AridShrubland 1.0; RUT_FeverWood 0.3 | LOW | stock comps only: CompProperties_EggLayer |
| `Lothcat` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8 | LOW | no comps, plain ThingDef |
| `Lylek` | ThingDef+PawnKindDef+PawnRenderTreeDef | RUT_Greentide 0.05 | LOW | stock comps only: CompProperties_EggLayer, PawnRenderNodeProperties_Carried, PawnRenderNodeProperties_Parent, PawnRenderNodeProperties_Spastic |
| `Massiff` | ThingDef+PawnKindDef | RUT_AridShrubland 0.6 | LOW | no comps, plain ThingDef |
| `Mott` | ThingDef+PawnKindDef | RUT_Greentide 0.4 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Mudhorn` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8 | LOW | stock comps only: CompProperties_EggLayer, CompProperties_Shearable |
| `Mynock` | ThingDef+PawnKindDef | RUT_PoisonForest 0.2; RUT_Scarlands 0.5 | LOW | no comps, plain ThingDef |
| `Neebray` | ThingDef+PawnKindDef | RUT_PoisonForest 0.8 | LOW | no comps, plain ThingDef |
| `Ollopom` | ThingDef+PawnKindDef | RUT_WeepingStones 1.3 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `PekoPeko` | ThingDef+PawnKindDef | RUT_Greentide 0.2 | LOW | stock comps only: CompProperties_EggLayer |
| `Pikobis` | ThingDef+PawnKindDef | RUT_AridShrubland 0.1 | LOW | stock comps + optional MayRequire-guarded ext: PathfindingFramework.MovementExtension |
| `Plant_Bubblespore_Wild` | ThingDef (plant) | RUT_Greentide 0.5 | LOW | no comps, plain ThingDef |
| `Plant_Chakroot_Wild` | ThingDef (plant) | RUT_FeverWood 0.4; RUT_Greentide 0.5 | LOW | no comps, plain ThingDef |
| `Plant_FelucianGlowspore_Wild` | ThingDef (plant) | RUT_Greentide 0.6 | LOW | stock comps only: CompProperties_Glower |
| `Plant_HubbaGourd_Wild` | ThingDef (plant) | RUT_Greentide 0.8 | LOW | no comps, plain ThingDef |
| `Plant_HydenockTree_Wild` | ThingDef (plant) | RUT_FeverWood 1.5; RUT_Greentide 1.5 | LOW | no comps, plain ThingDef |
| `Plant_JoganTree_Wild` | ThingDef (plant) | RUT_FeverWood 0.6; RUT_Greentide 1.2 | LOW | no comps, plain ThingDef |
| `Plant_MujaFruit_Wild` | ThingDef (plant) | RUT_Greentide 1.0 | LOW | no comps, plain ThingDef |
| `Plant_TookeTrap_Wild` | ThingDef (plant) | RUT_Greentide 0.5 | LOW | no comps, plain ThingDef |
| `Porg` | ThingDef+PawnKindDef | RUT_AridShrubland 0.04 | LOW | stock comps only: CompProperties_EggLayer |
| `Pufferpig` | ThingDef+PawnKindDef | RUT_AridShrubland 0.5 | LOW | no comps, plain ThingDef |
| `Qormot` | ThingDef+PawnKindDef | RUT_AridShrubland 0.2 | LOW | no comps, plain ThingDef |
| `Ronto` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8 | LOW | no comps, plain ThingDef |
| `Runyip` | ThingDef+PawnKindDef | RUT_Miasma 0.5 | LOW | no comps, plain ThingDef |
| `Scurrier` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8 | LOW | no comps, plain ThingDef |
| `Shiro` | ThingDef+PawnKindDef | RUT_Greentide 0.5; RUT_Miasma 0.4 | LOW | stock comps only: CompProperties_EggLayer |
| `ShiroTrap` | ThingDef+PawnKindDef | RUT_Greentide 0.5 | LOW | stock comps only: CompProperties_EggLayer |
| `Shyrack` | ThingDef+PawnKindDef | RUT_Webwork 0.2 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `Skalder` | ThingDef+PawnKindDef | RUT_AridShrubland 0.08 | LOW | no comps, plain ThingDef |
| `Sketto` | ThingDef+PawnKindDef | RUT_AridShrubland 0.8 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `Snoruuk` | ThingDef+PawnKindDef | RM_TheRot 0.5 | LOW | stock comps only: CompProperties_EggLayer |
| `Strill` | ThingDef+PawnKindDef | RUT_AridShrubland 0.2 | LOW | no comps, plain ThingDef |
| `Urusai` | ThingDef+PawnKindDef | RUT_AridShrubland 0.7; RUT_FeverWood 0.5 | LOW | stock comps only: CompProperties_EggLayer |
| `Voorpak` | ThingDef+PawnKindDef | RUT_AridShrubland 0.02 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `Vornskyr` | ThingDef+PawnKindDef | RUT_Miasma 0.15 | LOW | stock comps + optional MayRequire-guarded ext: NocturnalAnimals.ExtendedRaceProperties |
| `Vulptex` | ThingDef+PawnKindDef | RUT_AridShrubland 0.08 | LOW | no comps, plain ThingDef |
| `Whisperbird` | ThingDef+PawnKindDef | RUT_AridShrubland 0.15; RUT_FeverWood 0.3; RUT_Greentide 0.7; RUT_Miasma 0.3 | LOW | stock comps only: CompProperties_EggLayer |
| `Woolamander` | ThingDef+PawnKindDef | RUT_CrackedLands 0.15 | LOW | no comps, plain ThingDef |
| `Wyyyschokk` | ThingDef+PawnKindDef | RUT_Webwork 0.4 | LOW | stock comps only: CompProperties_CanBeDormant, CompProperties_EggLayer, CompProperties_Shearable, CompProperties_WakeUpDormant |
| `Yobshrimp` | ThingDef+PawnKindDef | RUT_Miasma 0.8 | LOW | stock comps only: CompProperties_EggLayer |
| `Zakkeg` | ThingDef+PawnKindDef | RUT_Miasma 0.05 | LOW | no comps, plain ThingDef |

### What's left

- **The census itself is complete** — 76 of 76 live entries graded by real
  compClass/render-tree inspection of the vendored source, not by name or
  sampling, and cross-checked against every patch file naming the donor.
- **Not done here** (out of scope for a read-only cost census): the keep/cut
  pass (spec step 2 — the section above already surveyed keep/cut ruling
  state across all donor-touched biomes, including Webwork, which has a
  dated CUT ruling on 3 of this donor's defNames: `Wyyyschokk`, `Kreetle`,
  `Shyrack` — `Kreetle` is not live in any roster today per this pass's
  fresh scan, so it is absent from the table above); art-copy verification
  (this pass read XML dependency classes only, not whether the donor's
  AssetBundle-packaged textures — note the mod's own About.xml says it
  ships via AssetBundles, not loose PNGs, which the porting work itself
  will need to account for, `loose-png-beats-assetbundle-donor-art`); and
  the `VFEI2_BlackSwarmling` mis-tagged row from the AA_ census above (still
  unfiled, not this donor's problem to fix).
- **Given the uniform LOW grade and zero-C# mod, the ordering table in the
  "spec steps 1 and 2" section above stands as written** — nothing here
  changes `mlie.starwarsanimalcollection`'s cost rating, only sharpens it
  from a 160-catalog/66-sampled estimate to a 76-live/76-graded measurement.

## census: the ten smaller donors — FOUNDRY, 2026-09-25

Read-only research, step 1 of this item's own spec, for every donor in this
item's own table below the two dominants (already fully censused above).
Nothing ported, renamed, cut or edited. Time permitted covering all ten, not
just "time permitting" a subset.

🔴 **A packageId lookup trap cost most of this pass's time and is worth
recording**: `grep "<packageId>$donor</packageId>" */About/About.xml`
false-positives on any mod that lists the donor as a **dependency** — a
`<modDependencies><li><packageId>...` entry is byte-identical to the tag
being searched for. It handed back `3309022698` ("Reel's Insector Faction",
`packageId Reel.InsectorFaction`) as if it *were*
`oskarpotocki.vfe.insectoid2`, and separately missed real matches for
`sarg.alphamemes`, `mlie.horrors`, `biomesteam.biomescaverns`,
`lingluo.cockroach`, `regrowth.botr.core` and `vanillaexpanded.vgeneticse`
entirely because their real `About.xml` casing (`Mlie.Horrors`,
`ReGrowth.BOTR.Core`, ...) didn't string-match the lowercase table spelling.
Fixed by parsing each `About.xml` with `ElementTree` and reading only
`root.findtext('packageId')` (never a body-wide grep), case-folded. Every
grade below is from the packageId re-resolved this way, confirmed by content
id.

### `neronix17.outerrim.droiddepot` (21 in the 2026-09-20 table) — ALREADY DONE, drop from any ordering

Zero live `MayRequire="neronix17.outerrim.droiddepot"` references anywhere in
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/{RUT_Desert,RUT_AridShrubland,RUT_ExtremeDesert}.xml`
today (MEASURED, fresh grep). `DESERT_FAMILY_PORT_EXECUTION_1` (§"B. The 7
Droid Depot droids") already resolved this: the 7 droids were never really a
`wildAnimals` roster in the porting sense — they're crash-wreckage spawns,
now handled by `FALL_LINE_ARRIVAL_MECHANISM_1`'s own
`RSW_DW_OuterRim_{MSE,SalvageAssist,DUM,GNK,FX7,Muckraker,Destroyer}Droid`
defs, removed from the desert biomes same-day 2026-09-20. **This donor needs
no porting plan at all** — it is off the table, not merely cheap.

### `sarg.alphabiomes` (6) — mostly LOW, one dead-reference flag

Live roster (fauna+flora only, excluding this donor's separate weather-condition
and disease-HediffDef entries in the same biome files — a different asset
class, out of this census's "creature/plant" scope): `AB_KeeningCordax`,
`AB_Iashiphus`, `AB_Gomphoeria` (RUT_FeverWood), `AB_JungleTree`,
`AB_SugarFamewort` (RUT_Greentide), `LavaSnail` (RUT_TheForge) — 6 unique
defNames, matching the item's own count exactly.

- **5 of 6 (all but LavaSnail): GRADE LOW.** Resolved from the donor's real
  source (content id `1841354677`, confirmed by packageId): plain
  `ThingDef` plants inheriting `TreeBase`/`BushBase`/`AB_FertileTreeBase`,
  zero `Class=` attributes anywhere in either source file
  (`Plants_TarPits.xml`, `Plants_FeraliskJungle.xml`). No comps, no C#.
- 🔴 **`LavaSnail` does not exist anywhere in `sarg.alphabiomes`'s own
  `Defs/` tree** (confirmed against content id `1841354677` directly), **and
  a defName-exact search of every mod's `1.6`/`1.5`/no-version `Defs/` tree
  on this machine's whole Steam Workshop cache (1,271 mods) found it
  nowhere.** Same shape as this item's own `VFEI2_BlackSwarmling` finding in
  the AA_ census above — a `MayRequire` guard naming a donor the def doesn't
  actually belong to, or a def whose real donor mod isn't in this machine's
  cache at all. **Unresolved, not gradeable**; flag for
  `RUT_TheForge.xml` next time it's touched, same disposition as the
  `VFEI2_BlackSwarmling` row (not this pass's to fix — no XML touched here).
  Practical effect if `sarg.alphabiomes` is ever retired while its real donor
  (whatever it is) stays active: this row would wrongly vanish, or if its
  real donor is also gone, it's already a dead reference today.
- **Retiring this donor is not JUST these 6 rows** — the same biome files
  carry `sarg.alphabiomes`-guarded `WeatherDef`s (`AB_RedFog`,
  `AB_ForsakenNight`, `AB_ForsakenThunderstorm`, `AB_ForsakenRainyNight`,
  `AB_VolcanicAsh`, `AB_VolcanicAshRain`) and `HediffDef`-guarded
  `<diseases>` entries (`AB_Disease_SporesAllergy`,
  `AB_Disease_AnimalSporesAllergy`, `AB_Disease_BacterialGangrene`,
  `AB_Disease_ViralAbasia`, `AB_Disease_RavagingIntestinalParasites`) across
  `RUT_Contagion`, `RUT_ForsakenCrags`, `RUT_TheRot` and `RUT_Miasma`. Those
  aren't "roster entries" this item's table counts, but they are real donor
  dependencies a full retirement test (this item's own `verify` section)
  would still trip over.

### `oskarpotocki.vfe.insectoid2` (7 in the table; 2 unique defNames measured live: `VFEI2_Megathrips` in RUT_FeverWood, `VFEI2_Swarmling` in RUT_Greentide/RUT_Miasma/RUT_Wasteland)

Real donor is content id `3309003431` (`OskarPotocki.VFE.Insectoid2`) — NOT
`3309022698`, which is "Reel's Insector Faction" and only *depends on* this
packageId (the trap above).

- **`VFEI2_Swarmling` — GRADE HIGH.** Carries its own `BodyDef`
  (`Bodies_Swarmling.xml`) and its own `PawnRenderTreeDef`
  (`PawnRenderTreeDefs.xml`), plus two private-assembly comps from
  `VFEInsectoids.dll`: `DeathActionProperties_VanishInsect` and
  `CompProperties_SwarmlingToCocoon`. Porting means carrying a whole
  BodyDef+BodyPartDefs+render-tree set, not just a ThingDef, and either
  reimplementing the death/cocoon behaviour or dropping it.
- **`VFEI2_Megathrips` — GRADE MEDIUM.** Uses the stock `BeetleLike` body
  (no custom BodyDef needed) and only
  `VEF.AnimalBehaviours.CompProperties_InitialHediff` — the same
  already-load-bearing VEF framework as the `sarg.alphaanimals` census above.
  Copy+rename+re-verify, not reimplementation.
- Corroborates rather than duplicates the AA_ census's `VFEI2_BlackSwarmling`
  finding: this donor's own Swarmling family really does exist and really
  does need the BodyDef treatment, which is exactly why a misattributed
  `VFEI2_BlackSwarmling` under `sarg.alphaanimals` was plausible-looking in
  the first place — it's the same species family from the same modder.

### `who.vfee.isopodageneline` (4; 3 unique defNames: `SW_Electrictick`, `SW_Electricgryllotalpa` (RUT_Scarlands), `SW_Juggernautbeetles` (RUT_Scarlands), `SW_Electrictick` also in RUT_Wasteland)

Content id `3357632382` (`Who.VFEE.IsopodaGeneline`). All three inherit
`VFEI2_BaseInsect` — **this donor's whole cast is itself parented on
`oskarpotocki.vfe.insectoid2`'s base insect def**, a compounding
cross-donor dependency: porting these three cleanly needs
`VFEI2_BaseInsect` (or an owned equivalent) to already exist, i.e. this
donor's port is not independent of the one above.

- `SW_Electrictick` — GRADE MEDIUM: stock `CompProperties_Explosive` +
  `CompProperties_MechPowerCell`, no private assembly (the donor ships
  `Isopoda_Geneline.dll` but neither this def nor `SW_Electricgryllotalpa`
  uses a class from it).
- `SW_Electricgryllotalpa` — GRADE MEDIUM: no comps of its own beyond the
  parent chain.
- `SW_Juggernautbeetles` — GRADE MEDIUM: `VEF.AnimalBehaviours.CompProperties_InitialAbility`
  only — the same already-load-bearing VEF framework.
- None reach HIGH on their own defs, but the `VFEI2_BaseInsect` parent
  dependency on the previous donor means "cheap" here is conditional.

### `sarg.alphamemes` (3: `AM_Dryad_Corruptor`, `AM_Dryad_Ocular`, `AM_Dryad_Tumorous`, all RUT_PoisonForest)

Content id `2661356814` (`Sarg.AlphaMemes`, not `3556875187` — the trap
above). **GRADE HIGH for all three.** These are Gauranlen-tree "dryad"
spirits, deeply wired into vanilla Ideology's connected-tree mechanic:
`AM_Dryad_Corruptor` carries its own `ThinkTreeDef`
(`Dryad_Corruptor.xml`) whose think tree runs vanilla
`JobGiver_ReturnToGauranlenTree`/`JobGiver_FightFiresNearConnectedTree`
alongside a **private-assembly** node,
`AlphaMemes.JobGiver_MergeIntoGaumakerPodCorruptor`
(`AlphaMemes.dll`). Porting means either reimplementing that JobGiver and
the whole custom think tree, or accepting the loss of the signature
merge-into-pod behaviour — a call for the sitting, not this pass. The
`CompProperties_Spawner` comps on these defs are stock, so the entire cost
here is the AI tree, not the ThingDef.

### `mlie.horrors` (2: `Terrorworm` RUT_AridShrubland, `Visceral` RUT_PoisonForest)

Content id `3535224844` (`Mlie.Horrors`). **GRADE LOW for both** — plain
`ThingDef`s off `BaseHorror`/`AnimalKindBase`, zero `Class=` attributes
anywhere in `Races_Animal_Horrors.xml` despite the mod shipping a private
`Horrors.dll` (used by other creatures/mechanics in the mod, not these two).
⚠️ Not to be confused with a *different*, unguarded `Terrorworm` name that
the 2026-09-20 SWAC twin-census section above lists as one of desert's "7
genuinely unported" rows — that one has no `MayRequire` at all and needs its
own resolution (which donor, if any, it's actually meant to come from); this
census only speaks to the `mlie.horrors`-guarded `Terrorworm` live in
`RUT_AridShrubland.xml` today.

### `biomesteam.biomescaverns` (2: `BMT_Rocktooth`, `BMT_Boneblade`, both RUT_CrackedLands)

Content id `2969748433` (`BiomesTeam.BiomesCaverns`). **GRADE LOW for both**
— both are catchable **fish items** (`VCEF_RawFishBase`/`FishBase` parent
chain in the donor's own `VFE_Items_Resource_Fish.xml`), not living
creatures: no comps, no BodyDef, no PawnKindDef. Cheapest class of port in
this whole census — an item ThingDef copy-with-rename.

### `lingluo.cockroach` (1: `Ling_Cockroach`, RUT_RustCathedral)

Content id `3196253802` (`LingLuo.Cockroach`). **GRADE LOW** — stock
`CompProperties_Milkable` only.

### `regrowth.botr.core` (1: `RG_Rimclaw`, RUT_Scarlands)

Content id `2260097569` (`ReGrowth.BOTR.Core`). **GRADE LOW** — stock
`CompProperties_EggLayer` only at this def's own tag (parent
`BigBirdKindBase` not walked further); the donor ships `ReGrowthCore.dll`
but it isn't referenced by this specific def.

### `vanillaexpanded.vgeneticse` (8 pairs, 7 unique defNames — the item's own table undercounts this one by one, since `GR_Beetlefleet` is wired into both RUT_PoisonForest and RUT_Wasteland)

Content id `2801160906` (`VanillaExpanded.VGeneticsE`; not present as a
Workshop folder was wrong to assume — it IS cached, the trap above just
missed it on casing). Vendored source also present at
`vendor/mod_sources/VanillaGeneticsExpanded_src`, no `Assemblies/` folder in
the vendored copy but the live cache confirms the real mod ships
`GeneticRim.dll`.

- `GR_Manbear` (RUT_Slime) — **GRADE HIGH**: private-assembly
  `GeneticRim.CompProperties_HumanoidHybrid`.
- `GR_Mecharat` (RUT_RustCathedral) — **GRADE HIGH**: private-assembly
  `GeneticRim.CompProperties_RegisterMechHybridWithAntenna` and
  `GeneticRim.CompProperties_DieUnlessReset`, plus VEF comps on top.
- `GR_Chickenrabbit`, `GR_ParagonRat`, `GR_Molebear`, `GR_Spidercat` — **GRADE
  MEDIUM**, all VEF.AnimalBehaviours-only (`AnimalStatExtension` plus, per
  def, `CompProperties_InitialHediff`/`InitialAbility`/`DigPeriodically`) —
  the same already-load-bearing framework.
- `GR_Beetlefleet` (RUT_PoisonForest, RUT_Wasteland) — **GRADE MEDIUM**
  (VEF.AnimalBehaviours only: `AnimalProduct`, `AsexualReproduction`,
  `Floating`), but 🔑 **it is defined in the donor's own
  `Mods/AlphaAnimals/` compat sub-folder**, meaning it only exists when
  *both* `vanillaexpanded.vgeneticse` and `sarg.alphaanimals` are active —
  a second compounding two-donor dependency found this pass (the first
  being `who.vfee.isopodageneline`'s `VFEI2_BaseInsect` parent above).
  Retiring either donor alone orphans this def; both need a joint plan.

### Rollup across all ten smaller donors

| donor | table count | unique defNames measured | LOW | MEDIUM | HIGH | unresolved |
|---|---:|---:|---:|---:|---:|---:|
| neronix17.outerrim.droiddepot | 21 | 0 (already fully retired) | – | – | – | – |
| sarg.alphabiomes | 6 | 6 | 5 | 0 | 0 | 1 (`LavaSnail`, dead/misattributed) |
| oskarpotocki.vfe.insectoid2 | 7 | 2 | 0 | 1 | 1 | 0 |
| who.vfee.isopodageneline | 4 | 3 | 0 | 3 | 0 | 0 |
| sarg.alphamemes | 3 | 3 | 0 | 0 | 3 | 0 |
| vanillaexpanded.vgeneticse | 8 | 7 | 0 | 5 | 2 | 0 |
| mlie.horrors | 2 | 2 | 2 | 0 | 0 | 0 |
| biomesteam.biomescaverns | 2 | 2 | 2 | 0 | 0 | 0 |
| lingluo.cockroach | 1 | 1 | 1 | 0 | 0 | 0 |
| regrowth.botr.core | 1 | 1 | 1 | 0 | 0 | 0 |

🔑 **Pattern across the whole census, both waves**: every HIGH-grade def in
every donor traces to one of two things — a **private assembly class**
(`AlphaBehavioursAndEvents.dll`, `VFEInsectoids.dll`, `AlphaMemes.dll`,
`GeneticRim.dll`) or a **custom `BodyDef`/`PawnRenderTreeDef`**. Every
MEDIUM traces to `VEF.AnimalBehaviours`, a framework this campaign already
depends on permanently — so MEDIUM is close to LOW in real cost, and the
true dividing line for the owner sitting is HIGH vs. everything else, not
the three-tier label. Two cross-donor structural dependencies (`who.vfee.isopodageneline`
→ `oskarpotocki.vfe.insectoid2`'s `VFEI2_BaseInsect`; `vanillaexpanded.vgeneticse`'s
`GR_Beetlefleet` → `sarg.alphaanimals`) mean at least two donor pairs can't be
retired independently of each other, which the ordering-by-entry-count table
in the "spec steps 1 and 2" section doesn't capture and the sitting should
know about.

Not done here (out of scope for a read-only cost census): the keep/cut pass
for any of these ten donors' rows (spec step 2 — none of them appear in the
Sump/Webwork/Miasma/Fever Wood sitting docs surveyed above), and resolving
the `LavaSnail`/`VFEI2_BlackSwarmling` dead-reference pair (both still
unfiled).

