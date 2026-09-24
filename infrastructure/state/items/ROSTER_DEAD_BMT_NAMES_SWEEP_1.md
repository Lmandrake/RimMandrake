# ROSTER_DEAD_BMT_NAMES_SWEEP_1 — the dead BMT_ rows nobody can rename safely

## ✅ DONE 2026-09-23 — zero `BMT_` rows remain in any roster's `fauna` array

**MEASURED after the pass: 0 of 31 rosters carry a `BMT_` name in `fauna`** (parsed, not grepped).
The verify criterion below is met for the rename/eviction half. Two verifications remain open and
both need the Desktop — they are named in *what is still owed*.

🔴 **The table further down was STALE when this pass started, and its count was wrong.** It lists
14 rows; **only 10 existed.** The four it was wrong about were resolved on 2026-09-22, *after* this
item was filed on 2026-09-21 — so the item was asking for work already done, exactly the failure
`CLAUDE.md` warns of:

| the table's claim | what was actually true |
|---|---|
| `BMT_Stoneback` × 3 in `arid_shrubland`, `the_scarlands`, `wasteland` **fauna** | ⛔ **Never existed as fauna rows.** Settled by `576abc14c` (2026-09-22, *"One arid home each"*) — the owner's one-arid-home ruling. The only live Stoneback rows are **evictions** in `desert.json` and `weeping_stones.json` |
| `BMT_CaveLemming` in `nightside_ice` **fauna**, blocked on an owed refashion | ✅ **Wired already** — `28ef99344` (2026-09-22, *"breaking the pyramid on purpose"*). MEASURED: `RSW_CaveLemming` = 0.03 in `RUT_NightsideIce.xml`. Its only live row is an eviction in `poison_forest.json` |

⇒ 🔑 **So step 3 and step 5 of the spec were already complete before this pass began.** Do not
re-derive them.

### what this pass did, row by row

| row | roster | outcome |
|---|---|---|
| `BMT_Megakrill` | `the_twilight_sea` | → **evictions**, `fishTypes-only`. Its own law: *"still a FISHING RESULT, never a wildAnimals spawn"*. ⚠️ **Not a cut from the biome** — it belongs in `<fishTypes>`, which MEASURED **does not exist** on either sea def. Owed inside `TERMINALBIOMES_RM_MOD_BUILD_1` |
| `BMT_CrystalCrab` | `the_lantern_deeps` | → **evictions**, cited to the Deeps' **hard ban 3**. The row was the stale thing, not the wiring |
| `BMT_Polluwog` | `the_grey_sea` | renamed `RSW_Polluwog`. **Not wired** — see the sea ruling below |
| `BMT_MutatingTumorfish{Adult,Fry,Spawn}` | `the_twilight_sea` | renamed to `RSW_`. **Not wired** — same reason |
| `BMT_SandPillar` | `the_cracked_lands` | ✅ renamed + **wired 0.5** onto **`RM_FloodedCanyon`** via `WildAnimals_CrackedLands.xml` op 2 — ⛔ never the frozen `RUT_CrackedLands` |
| `BMT_MegaphoridLarva` | `the_scarlands` | ✅ renamed + **wired 0.5** into `RUT_Scarlands.xml` |
| `BMT_CrystalFairyMole` | `the_scarlands` | ✅ renamed + **wired 0.5** into `RUT_Scarlands.xml` |
| `BMT_Sacapillar` | `wasteland` | ✅ renamed + **wired 0.5** into `RUT_Wasteland.xml` |

### 🔴 the sea question is SETTLED — and it is a fact, not a judgement

**There is no separate floor BiomeDef.** MEASURED: `the_twilight_deep.md` and `the_grey_deep.md`
exist as design **sheets**, but no `RUT_TwilightDeep`/`RUT_GreyDeep` def and no deep roster exist
anywhere in `src/`. ⇒ A sea's **floor and its catch both live on the one sea def** — floor residents
in `<wildAnimals>`, the catch in `<fishTypes>`. So *"retarget to the deep"* means **that same def's
`wildAnimals`**. One answer, four rows.

⛔ **But the four were deliberately NOT wired.** Both seas are `impassable=true` (MEASURED), and
whether `<wildAnimals>` spawn at all on an impassable biome is an **engine** question, UNMEASURABLE
on the Mac. The two entries already sitting there (`AA_Aerofleet`, `RSW_Lanternwhale`/`RSW_Reefback`)
are somebody's bet, not proof. Renaming asserts only the admission that was *already* ruled; wiring
would assert an engine behaviour nobody has tested.

### 🔑 the commonality principle this pass established

`RSW_Korrum` was wired into the Scarlands at **0.05** against its roster's 0.5, on the reasoning
that *"the roster's 0.5 was a round2-mapping placeholder, not an ecology call."* That precedent was
**followed for the reasoning and not for the number**, because the reasoning is about *risk to the
pyramid*, and that risk has a direction:

- ⇒ **A SMALL animal can never break `ECOSYSTEM_PYRAMID_LAW_1`** — raising its commonality raises
  the small share. So `SandPillar` (0.80), `MegaphoridLarva` (0.32) and `CrystalFairyMole` (0.86)
  needed **no measurement at all**, only the observation that they are small. 🔑 A monotonic law
  makes a whole class of checks unnecessary; notice that before computing anything.
- ⚠️ **Only `Sacapillar` (bodySize 2.40) could move it the wrong way.** Wired at the ruled 0.5
  rather than trimmed, because the Korrum trim answered a *measured* thin roster (total 1.51) while
  the Wasteland is rich (17 rows, total 8.28), making 0.5 about 6% of spawns. ⛔ **Recorded as a
  BOUND, not a number:** at the 2026-09-20 sweep the Wasteland was 73.3% small and adding 0.5 large
  gives 66.1%, far above the 50% floor; the floor would only be at risk if current `largeC` had
  grown to ~3.9+. The roster HAS drifted since (sweep total 9.28 vs 8.28 now) and the current
  small/large **split is UNMEASURABLE here** — no `defs.sqlite`, so donor and vanilla bodySizes
  cannot be resolved.

## 🔴 what is still owed — both need the Desktop

1. **Test whether `<wildAnimals>` spawn on an `impassable=true` biome**, then wire `RSW_Polluwog`
   and the three `RSW_MutatingTumorfish*` into their sea def, inside `TERMINALBIOMES_RM_MOD_BUILD_1`.
   Those four rows are renamed and admitted but unwired until this is known.
2. **Re-run the ecosystem pyramid sweep** to confirm `RUT_Wasteland` still clears the 50% floor with
   `RSW_Sacapillar` at 0.5, and to refresh numbers that are now three days stale.
3. Confirm every newly wired name resolves against the **live** mod list (the caveat at the bottom of
   this file, unchanged): existence was verified by parsing `src/` — all four resolve as **both** a
   `PawnKindDef` and a `ThingDef`, which is what a `wildAnimals` key needs, but that is not the same
   as resolving in a loaded game.

⚠️ `validate_patch.py` is clean on `WildAnimals_CrackedLands.xml` (static checks only — no `--defs`
available here, and it warns that this is exactly how an xpath matching nothing stays silent).

## where this came from

`MIASMA_FEVERWOOD_GREENTIDE_BMT_1` fixed three rosters. Generalising its measurement
across all **31** rosters (2026-09-21, BENCH, Mac session) found **32 more** live `BMT_`
rows in 12 rosters. All 32 name a `biomesteam.biomescaverns` def (donor **NOT** in the
active mod list) that we have **already ported** under an `RSW_` name; **0** were
unportable.

**18 of the 32 were already wired** in their biome under the ported name — pure stale
rows, renamed at `b173e699d`, no judgment needed.

**These 14 are the remainder: ported, and wired NOWHERE.** They are deliberately left
under their dead `BMT_` names, because renaming a row is an assertion that the species is
admitted — and for several of these that assertion is false or contested. Renaming first
and asking later would launder a guess into the roster.

## 🔴 Do NOT bulk-wire these to close the count

That is the exact trap the parent item's spec names. At least four of the 14 are unwired
**correctly**, by an existing ruling — evidence below, gathered per species. A sweep that
wires all 14 would re-admit creatures the owner already excluded and put fishing results
on the land.

## the 14, with what is already known about each

`bs` = `race.baseBodySize`, MEASURED off our own port def, not the donor.

| roster | biome | dead name | bs | what the evidence says |
|---|---|---|---|---|
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_Megakrill` | 0.2 | 🔴 **Leave unwired.** Its own roster law says it: *"still a FISHING RESULT, never a wildAnimals s[pawn]"*. The row belongs in a fishing/`fish` context, not `<wildAnimals>`. |
| `the_lantern_deeps` | `RUT_LanternDeeps` | `BMT_CrystalCrab` | 2.4, predator | 🔴 **Leave unwired — evicted by its own sheet.** `RUT_LanternDeeps.xml`'s header records the Deeps sheet's **hard ban 3** evicting the six crystal-studded residents *by name*, crystal crab among them. The roster row is the stale thing here, not the wiring; it should become an **eviction record**, not an admission. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishAdult` | 1.8, predator | ⚠️ **Probably the wrong roster.** Law says *"RETARGET: the_twilight_deep (schooling/multiples)"* — the twilight **deep** is the sea-FLOOR sheet (`the_twilight_deep.md`), a different thing from the surface. Resolve where it lives before wiring anything. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishFry` | 0.8, predator | ⚠️ Same as above. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishSpawn` | 0.8 | ⚠️ Same as above. |
| `the_grey_sea` | `RUT_GreySea` | `BMT_Polluwog` | 0.1 | ✅ **Wiring looks genuinely owed** — law: *"STAYS Grey Deep — not flagged schooling; cap released so it is a resident (owner ruling 2026-09-…)"*. But note it says Grey **Deep**, and the roster is the Grey **Sea**; settle surface-vs-floor first, same question as the tumorfish. |
| `wasteland` | `RUT_Wasteland` | `BMT_Sacapillar` | 2.4 | ✅ Wiring looks owed — law: *"PLACED: wasteland (homeless disposition sitting, frozen 2026-09-10)"*. A placement ruling exists and nothing acted on it. |
| `the_cracked_lands` | `RUT_CrackedLands` | `BMT_SandPillar` | 0.8 | ✅ Placed by the round2 move mapping (*"cracked land"*), never wired. ⚠️ Wire onto **`RM_FloodedCanyon`**, not `RUT_CrackedLands` — that twin is FROZEN as of `FLOODEDCANYON_RM_MOD_BUILD_1`, and campaign fauna rides a Utinni patch onto the `RM_` def. |
| `nightside_ice` | `RUT_NightsideIce` | `BMT_CaveLemming` | 1.0 | ⚠️ Placed (*"ice sheet, rename"*) but the law also says a **rename/refashion is owed** with a thermal-only sensing line (owner ruling 2026-09-1x). Do the refashion question first; wiring a def that is about to be renamed buys nothing. |
| `the_scarlands` | `RUT_Scarlands` | `BMT_CrystalFairyMole` | 0.86 | ⚠️ Placed here by the round2 mapping (*"Scarlands, oddly"*), and it is ALSO one of the six names in the Deeps' ban 3 — which under the owner's 2026-09-21 cut-scope ruling does **not** reach the Scarlands. So it may legitimately live here. Also note the biome is being renamed to `RM_Warscar` (`SCARLANDS_STANDALONE_MOD_1`). |
| `the_scarlands` | `RUT_Scarlands` | `BMT_MegaphoridLarva` | 0.32 | ✅ Placed (*"scarlands"*), never wired. Same `RM_Warscar` note. |
| `arid_shrubland` | `RUT_AridShrubland` | `BMT_Stoneback` | 0.4 | ⚠️ **One species, three rosters.** Law is *"Anywhere on the dayside where it might be needed"* — a generic dayside filler. It IS already wired in `RUT_Desert`. Decide once whether "anywhere on the dayside" means wire it into all of them or leave it as the Desert's. |
| `the_scarlands` | `RUT_Scarlands` | `BMT_Stoneback` | 0.4 | ⚠️ Same species, same one-time decision. |
| `wasteland` | `RUT_Wasteland` | `BMT_Stoneback` | 0.4 | ⚠️ Same species, same one-time decision. |

## spec

Work species-by-species, in this order, because the first two shrink the list without any
judgment call:

1. **`BMT_Megakrill` and `BMT_CrystalCrab`** — do NOT wire. Move each row out of `fauna`
   into that roster's `evictions` array with a `reason` citing the ruling that excludes it
   (its own "fishing result" law; the Deeps' ban 3). This is bookkeeping, not a decision.
2. **Settle surface-vs-floor once** for the sea species (`Polluwog`, the three
   `MutatingTumorfish`): does a sea-FLOOR sheet (`the_twilight_deep.md`,
   `the_grey_deep.md`) have a def of its own to wire onto, or do floor residents ride the
   surface biome? One answer resolves four rows. ⚠️ Those four biomes are also merging into
   ONE mod, `mandrake.rm.terminalbiomes` (§7 Q1 ruling), so the answer interacts with
   `TERMINALBIOMES_RM_MOD_BUILD_1`.
3. **`BMT_Stoneback` × 3** — one ruling, not three: does "anywhere on the dayside" wire it
   into the Arid Shrubland, Scarlands and Wasteland, or does it stay the Desert's alone?
4. **The four straightforward placements** (`Sacapillar`, `SandPillar`, `MegaphoridLarva`,
   `CrystalFairyMole`) — rename the row and wire at the roster's own commonality, checking
   `ECOSYSTEM_PYRAMID_LAW_1` before each (compute the biome's small-weighted share the way
   `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` did; `Sacapillar` at bs 2.4 into the Wasteland is the
   one most likely to matter). ⛔ `SandPillar` goes onto `RM_FloodedCanyon` via a Utinni
   patch, never the frozen `RUT_CrackedLands`.
5. **`BMT_CaveLemming`** — resolve the owed rename/refashion first, then wire under the
   new name.

## verify

Zero `BMT_` names remain in any of the 31 roster JSONs' `fauna` arrays. Every row either
resolves to an `RSW_` name that is wired in the biome it names, or sits in that roster's
`evictions` with a reason citing a real ruling. `validate_patch.py` clean on every edited
XML. No biome newly fails `ECOSYSTEM_PYRAMID_LAW_1`'s proposed 60% small-weighted floor as
a result of the wiring.

## criteria

Every species each roster admits can actually appear in the shipped game, and every species
it excludes says why and on whose ruling — with no row silently renamed into an admission
nobody made.

## 🔴 NOT measurable on the Mac laptop

Whether each `RSW_` port resolves against the **live** active mod list was not checked here:
`measure` is not executable on this machine (`permission denied`) and there is no local def
dump. Existence in `src/` was verified by parsing the XML. A Desktop pass should confirm
resolution before wiring.

## Noted, not a defect

94 distinct `BMT_` defNames are still targeted by xpath across 12 of our patch files (42 in
`Doctrine/Patches/MegafaunaYield.xml`) while that donor is inactive — but those ops are
wrapped in `PatchOperationConditional` (931 of them in that file), so they are inert by
design, not silently broken. Cleanup at most, and only alongside other work in those files.

## FOUNDRY, 2026-09-24: engine question resolved (Desktop session, RimSage confirmed available)

**"What is still owed" item 1's engine question is now answered, CONFIRMED, not
UNMEASURABLE.** `RimSage` connected successfully this session — RC-verified, not
assumed — and a source read settled it decisively: `BiomeDef.impassable` is never
read anywhere in the wild-animal population path. `GenStep_Animals.Generate` loops
`RCellFinder.RandomAnimalSpawnCell_MapGen` → `WildAnimalSpawner.SpawnRandomWildAnimalAt`,
and none of the three checks `impassable` — that field is read only by
world-traversal/UI/landmark code (`Find.World.Impassable`, `CellInspectorDrawer`,
`LandmarkDef.cs`). So `<wildAnimals>` WILL populate normally on `RUT_GreySea`/
`RUT_TwilightSea` once a real Map generates for the tile, impassable or not.

Updated both roster JSONs' `law` fields for `RSW_Polluwog` and the three
`RSW_MutatingTumorfish*` rows to record this (`the_grey_sea.json`,
`the_twilight_sea.json`) — replacing the stale "UNMEASURABLE on the Mac... NEXT:
test on the Desktop" line. **Not wiring the four rows into the live `RUT_GreySea.xml`/
`RUT_TwilightSea.xml` this pass** — both rosters' own `law` text says this wiring is
scoped to `TERMINALBIOMES_RM_MOD_BUILD_1` (the mod-split build that owns those
biomes' successor defs), not this sweep item; wiring here first would just have to be
redone there. This item's own step 2 (surface-vs-floor + the engine question) is now
fully settled either way — nothing left blocking that step's *reasoning*, only its
*execution*, which belongs to the other item.

**Not re-checked this pass**: item 2 (ecosystem pyramid sweep re-run, now several
days stale) and item 3 (live-mod-list resolution check for the four newly-wired
`RUT_Scarlands`/`RUT_Wasteland` names) — both still genuinely need a live game
check, out of scope for this pass's narrow engine-question fold-in.

## FOUNDRY, 2026-09-24 (same session, later): item 3's live-resolution check done

The item's own "🔴 NOT measurable on the Mac laptop" caveat no longer applies —
this session runs on the Desktop, with live bridge access. Checked all four
2026-09-23-wired names directly against the running process via `jawa/get_defs`:
**`RSW_SandPillar`, `RSW_MegaphoridLarva`, `RSW_CrystalFairyMole`, `RSW_Sacapillar`
all resolve live as BOTH ThingDef and PawnKindDef** — CONFIRMED, not inferred from
`src/`. Item 3 of "what is still owed" is now closed out.

⚠️ **Flagged, not chased**: the same check on `RSW_Korrum` (unrelated to this
item's 14 names, but checked opportunistically since it shares a file with
`RSW_SandPillar`) came back MISSING on both ThingDef and PawnKindDef, despite
`mandrake.rsw.swbestiary` being active and the def genuinely present in
`RSW_DesertPortMisc_Races.xml`. Likely just pending the next restart (defs
parse once at startup) rather than a real defect — noted on `KORRUM_ART_REGEN_1`
instead of chased further here, since Korrum is out of this item's scope.

**Remaining before this item can close**: item 2 (ecosystem pyramid re-sweep,
now stale) and step 3/step 5's owner-judgment calls (Stoneback's one-species-
three-rosters question; CaveLemming's owed rename/refashion). None of those are
offline-doable by this seat.
