# SEA_FLOOR_AND_CATCH_PASS_1 — a sea is a floor you visit and a catch you pull

## the ruling

**Owner, 2026-09-21**, verbatim:

> *"The biomes should be describing the sea floors (what you encounter as an animal there) as
> well as what you can FISH out of the oceans on the shore. There should be defs made for each
> fish as something swimming around the floor area as well as something you can pull out as a
> fish."*

Scope confirmed 2026-09-22: **all four seas, the Scald included** (*"(2) plus the scald too"*).
That is `RUT_TheScald`, `RUT_GreySea`, `RUT_TwilightSea`, `RUT_PropaneLake` — the four biomes
that become the one `mandrake.rm.terminalbiomes` mod (§7 Q1 ruling), so this pass and
`TERMINALBIOMES_RM_MOD_BUILD_1` land together.

## ⛔ This is an EXTENSION of `FISH_BESTIARY_BUILD_1`, not a new programme

🔑 **Read that item and `design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`
first.** The catch half is a ratified, part-built programme — 32 `RUT_` species across 8
registers on 7 waters, 4 prize items, 6 rare-catch tables, six waves done, every §6 question
already ruled 2026-09-18. Do **not** re-derive a catch design; the gap his ruling names is the
**floor** half.

## what exists — MEASURED 2026-09-22 (parsed, not grepped)

| sea | terrain | floor animals | catch table |
|---|---|---:|---|
| `RUT_TheScald` | `RUT_ScaldWaterOceanDeep` | **4** — `RSW_SandoAquaMonster` .03, `RSW_ElderSando` .005, `RSW_Faa` .5, `RSW_Mee` .5 | ✅ 5 catches, `freshwater_*` + `RUT_RareScaldCatches`, on the def |
| `RUT_TwilightSea` | `WaterOceanDeep` | **2** — `AA_Aerofleet` .05, `RSW_Lanternwhale` .005 | ✅ 9 catches, `saltwater_*`, via `Patches/BiomeFishTypes_TwilightDeep.xml` |
| `RUT_GreySea` | `WaterOceanDeep` | **2** — `AA_Aerofleet` .05, `RSW_Reefback` .005 | 🔴 **none anywhere** |
| `RUT_PropaneLake` | `AB_PropaneLake` | **2** — `AA_AuroraSylph` .5, `AA_Skyeel` .5 | 🔴 **none anywhere** |

⇒ **The floor half is effectively unbuilt.** Every sea has 2–4 animals, and **not one of them
is one of its fish species**. The Scald has 5 catches and 4 floor animals with **zero
overlap** — its eesh, muddal, karrash, saal and bladderboil exist only as items you pull out,
never as something swimming. That is exactly the gap he is naming.

## 🛑 STOPPED ON THE MAC — owner's call 2026-09-22, needs `game-up`

**He stopped this item mid-sitting.** It moves to the Windows Desktop, and the thing to do
there FIRST is *look up how a SHORE map depicts ocean water* — i.e. which terrains a coastal
LAND map actually generates at its sea edge. His reason: until that is known we should not
continue trying to rule these biomes, because every remaining decision depends on it.

🔑 **Why that one lookup gates everything.** Step 1 below assumes a sea is fished from a map
generated ON the sea tile. If instead the catch is consumed from an adjacent coastal land map —
where shallow ocean water already generates — then the "no shore" blocker is measuring a map no
player ever sees, and the shore work in step 1/2 is partly or wholly unnecessary. ⛔ Do not
author shallow terrain, dive tagging or catch tables for the three unbuilt seas until that is
settled either way.

### ✅ Shore audit — step 1's deliverable, MEASURED on the Mac 2026-09-22 (parsed, not grepped)

**All four seas are structurally identical and generate 100% deep water.** Each carries exactly
ONE `terrainsByFertility` band spanning `min -999 max 999`, and **none has any
`terrainPatchMakers`** — so `MapGenUtility.TerrainFrom()` has one possible answer everywhere:

| sea | its single terrain band | patch makers |
|---|---|---|
| `RUT_TheScald` | `RUT_ScaldWaterOceanDeep` −999..999 | none |
| `RUT_GreySea` | `WaterOceanDeep` −999..999 | none |
| `RUT_TwilightSea` | `WaterOceanDeep` −999..999 | none |
| `RUT_PropaneLake` | `AB_PropaneLake` −999..999 | none |

⚠️ **The Scald's 100%-deep result is LIVE-PROVEN** (the 100/100 fishing-zone refusal already
recorded above). The other three are a **structural inference from identical construction, NOT
a live measurement** — do not upgrade that wording without a run.

For scale: of **32** own BiomeDefs parsed, only `RM_GelatinousSlime` and `RM_Pyrelands` use
`terrainPatchMakers` at all, so two working in-repo templates exist if scattering ever is the
answer.

### ✅ Also measured: the Scald is far ahead of the other three, and they lack the mechanism

- The Scald already ships **three** Standable water terrains — `RUT_ScaldWaterShallow`,
  `RUT_ScaldWaterMovingShallow`, `RUT_ScaldWaterMovingChestDeep` — **all three already tagged
  `RM_DiveEligible`** by `src/RimMandrake/DivingInteraction/Patches/RM_ScaldDiveEligibleTerrain.xml`.
  Plus `RUT_ScaldMargin` (a real `WaterShallowBase` TerrainDef, `burn 0`, the biome's sole
  `dbh_water` source).
- 🔴 **`RUT_GreySea`, `RUT_TwilightSea` and `RUT_PropaneLake` have NO shallow terrain def of any
  kind and NO `RM_DiveEligible` tagging anywhere.** `RM_DiveEligible` appears in exactly four
  files, all inside `DivingInteraction`, and its only wiring patch names Scald terrains only.
  ⇒ Their floor is unreachable by the shipped diving mechanism even if animals do spawn. That
  gap is **larger than step 2 describes** — it is new terrain defs, not just a tag.

### ⛔ And one thing step 1 must not do: scatter the margin procedurally

`RUT_ScaldMargin.xml`'s own header rules it out, and the reason generalises to any lethal water:
`PawnUtility.KnownDangerAt` is **edifice-only** and reads neither `burnDamage` nor `avoidWander`,
so nothing in vanilla stops a swim path crossing open boil cells to reach a cool strip. The
margin must be a cove geometrically sealed off by land — **hand-placed via the bridge**, which is
why the def deliberately does not place itself. A `terrainPatchMakers` block on the Scald would
actively create the hazard that file was written to avoid. (The Grey and Twilight Seas are not
lethal, so this constraint is not obviously theirs.)

**NEXT (Desktop):** open a coastal land map beside an ocean and record which terrain defs
generate at the water's edge, then answer on this item whether a sea's catch is consumed from
the land map or from the sea tile. Only then resume step 1.

⚠️ All four are `impassable=true`. The floor is reached by **diving**, which already exists
generically: `mandrake.rm.divinginteraction` makes any `RM_DiveEligible`+Standable terrain a
place a colonist can be sent ("Dive to hunt" / "Dive to commune"), built for the Scald under
`SCALD_DIVING_MOD_1`. So the mechanism his ruling needs is shipped — it needs wiring per sea,
not inventing.

## 🔴 Two measured blockers this pass must NOT pretend to solve

Both were found by `FISH_BESTIARY_BUILD_1`'s own live bridge testing. Believe them; they cost
that item five waves of deferral to establish.

1. **The Scald has no shore, so fishing there is impossible today.** Its map generates 100%
   DEEP water — `terrainsByFertility` has one entry spanning the whole fertility range, and
   `MapGenUtility.TerrainFrom()` always resolves to it. A Fishing zone was refused on
   **100/100** test cells with the engine's own reason: *"Must be placed over shallow water
   containing fish."* The intended fishing spot is `RUT_ScaldMargin` (a hand-painted shallow
   cove), and **no such terrain exists anywhere on the live planet** — `SCALD_MECHANICS_1`
   owes that map-authoring step. ⇒ 🔑 His words *"what you can FISH out of the oceans **on the
   shore**"* are the same requirement: **a sea needs shore cells or its catch table is
   decoration.** Check the other three for the same defect before authoring any new catch.
   ⛔ The Scald's `fishTypes` wiring itself needs no change; don't "fix" it.
2. **Quicktest maps currently generate zero water terrain at all** — 6 tiles, 5 biomes,
   including non-`RUT_` controls (`RM_FE_Pyrelands` riverCount 4, `RUT_RustCathedral`
   riverCount 2), both yielding no water despite the tiles declaring rivers/lakes. Filed as
   `QUICKTEST_RIVER_WATER_MISSING_1`. ⇒ **Live verification of any fishing or floor work is
   blocked until that is understood.** Author against the defs; do not claim a live proof.

## ✅ The pairing rule — RULED 2026-09-22, and it needs no new mechanism

A literal "def for each fish" breaks at both ends: the Scald's `RUT_Eesh` is a *finger-long,
finless sliver* that moves in clouds, absurd as a single spawnable animal, while
`RSW_SandoAquaMonster` is a leviathan nobody nets. Owner ruled the middle:

- **Every catch species gets a floor animal.**
- **A shoal species gets ONE swarm creature** standing in for the whole cloud, so a diver sees
  something rather than empty water — not skipped.
- **Existing megafauna stay floor-only**, with no catch item.

🔑 **This is already our established pattern — do not invent a swarm mechanism.** MEASURED
2026-09-22:

- `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Swarm.xml` already
  exists and holds three of them (`RSW_Yobshrimp`, `RSW_SiltLamprey`, `RSW_RustNipper`).
- `RSW_Mee` (bs 0.15, *"a silver-blue **schooling** scalefish"*) and `RSW_Faa` are **already
  wired as individual floor animals in the Scald at 0.5 each** — a shoal represented by one
  spawnable creature, exactly the shape he just ruled, shipped and live.

### ✅ The scalefish are NOT a gap — the three catch items are built and wired

**MEASURED 2026-09-22.** `RSW_Mee`, `RSW_Faa` and `RSW_Laa` exist as animals
(`SeaBeasts_Scalefish.xml`) **and their three catch items exist as ours**, in
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_ScalefishCatch_Items.xml` —
`RSW_MeeCatch`, `RSW_FaaCatch`, `RSW_LaaCatch`, each `ParentName="FishBase"`
`MayRequire="Ludeon.RimWorld.Odyssey"`, with our own descriptions and `RSW_LaaCatch` carrying
the deliberate `MarketValue 9` override. Built by `GREENTIDE_FISH_ITEMS_FIX_1`, which also
recorded on disk that the donor ships `swfish_Faa`/`swfish_Laa` but **no** `swfish_Mee`, so
falling back to Mlie was never an option for all three.

They are **already wired**, at exactly the weights the commission proposed: `RUT_Greentide`'s
`fishTypes` carries `RSW_MeeCatch` 0.4 in `freshwater_Common` and `RSW_FaaCatch` 0.3 /
`RSW_LaaCatch` 0.3 in `freshwater_Uncommon`.

⇒ 🔑 **`FISH_BESTIARY_BUILD_1`'s verify clause is satisfied in substance.** It names the three
with a `RUT_` prefix; they shipped as `RSW_`, which is the CORRECT tier for Star Wars scalefish
under `design/NAMING_SCHEME_PLAN.md` (RimStarWars = any Star Wars scenario). The clause's real
requirement — *ours, our own art, not a MayRequire fallback to Mlie* — is met. ⛔ **Do not
"build" them again under a `RUT_` prefix: that would ship three duplicate defs in the wrong
tier.** Fix the prefix in that item's verify clause instead.

⚠️ **The one thing genuinely owed is item-scale ART.** Each catch currently reuses its species'
south-facing pawn body sprite as the stack icon (`Things/Pawn/Animal/SeaBeasts/<X>/<X>_south`),
which the def file itself flags as a placeholder — `Graphic_StackCount` renders it fine, so this
is a look problem, not a mechanism problem. ✅ Before commissioning any, apply the standing
check-for-existing-art rule in CLAUDE.md: search `infrastructure/artpipe/done/` and `_artsrc/`
for these three subjects first.

## spec

Work per sea, in this order — cheapest and most decisive first.

1. **Shore audit, all four seas.** For each, determine whether any *shallow* water terrain is
   generated or paintable. The Scald's answer is known (none, and a cove is owed). Record the
   other three. ⛔ A sea with no shore cannot be fished regardless of its table, so this gates
   every catch claim.
2. **Wire the diving hook per sea.** Tag each sea's floor-reachable terrain `RM_DiveEligible`
   so "the floor" is a place a colonist can actually be, per
   `mandrake.rm.divinginteraction`. ⚠️ The Scald's boiling SURFACE stays no-swim (ban 4 in
   `the_scald.md`, superseded only as far as the DEEP interaction) — copy that shape, do not
   widen it.
3. ✅ **DONE, do not redo** — the three scalefish catches are built as `RSW_MeeCatch`/
   `RSW_FaaCatch`/`RSW_LaaCatch` and wired into `RUT_Greentide`'s freshwater bands (see above).
   The residue is item-scale icon art, and correcting the `RUT_` prefix inside
   `FISH_BESTIARY_BUILD_1`'s verify clause so it names what shipped.
4. **Author the remaining floor residents** for the two seas that already have catch tables
   (Scald, Twilight Sea), one animal per catch species, one swarm creature per shoal species,
   per the ruling above. Reuse `RSW_`/`RUT_` defs where the species exists; new defs where it
   does not. `SeaBeasts_Swarm.xml` is the file to grow, not a new one.
5. **The Grey Sea and Propane Lake need both halves.** They have no catch table at all. The
   commission doc's register system is the template — do not invent a parallel one. ⚠️ The
   Propane Lake is *propane, not water*: whether "fishing" is even the right verb there is a
   design question, not a default. Ask rather than assume.
6. Only then: `TERMINALBIOMES_RM_MOD_BUILD_1` carries all four into one mod with a per-biome
   settings toggle, so land this before or with that build, not after.

## verify

Each of the four seas: a stated shore verdict; a `RM_DiveEligible` floor a pawn can reach; and
for every species in its catch table, either a floor animal or a recorded reason it is
catch-only. `validate_patch.py` clean on every touched file. ⛔ **No live-verified claim** while
`QUICKTEST_RIVER_WATER_MISSING_1` stands — say "authored, not live-proven" and mean it.

## criteria

Diving a sea shows you the animals its fish descriptions promised, and fishing its shore pulls
out the same creatures you swam past.

## Watch out

- ⛔ **Do not re-derive the catch design.** `FISH_BESTIARY_BUILD_1` is ratified and part-built;
  duplicating it would produce a second, conflicting fish economy.
- ⚠️ **Mod shape is per-biome** (that item's own ruling): a water's fish defs live alongside
  that water's own biome mod. For these four that means `mandrake.rm.terminalbiomes`.
- 🔴 **`GREENTIDE_FISH_ITEMS_FIX_1`'s bug class:** wiring *race* defs instead of *item* defs
  into `fishTypes` makes a net produce a bare `Pawn`. The floor half of this pass creates
  exactly the conditions for that mistake — one species, two defs, one an animal and one an
  item. Keep them straight, and name them so they cannot be confused.
- ⚠️ Whether `<wildAnimals>` actually spawn on an `impassable=true` water biome is **not
  measurable from the Mac** (no RimSage, no def dump). All four seas already wire 2–4 animals,
  so somebody bet yes, but that is a bet and not a measurement. Settle it on the Desktop before
  authoring a large floor roster.
