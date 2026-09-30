# WARCASKET_CASK_BAY_AND_SARCOPHAGI_1 report

## Sources and rulings

🔴 **The item title misreads "Cask bay approved".** The owner's approval was "7) yrs" in his
typed turn-2 message (WASTELAND_BEDAZZLE_SITTING_1, session 4a17676e, 2026-09-28T14:43Z),
answering BENCH's opening slate item 7, verbatim:

> 7. **The lead-lined cask bay** *(gravship touch)* — a shielded hardpoint that lets the ship
> haul the Throat's casks, unlocking your own authored waste-run dilemma (the five
> destinations, each a moral verdict).

So the approved Cask Bay is a **gravship hazmat hold for waste casks**, not a warcasket
crafting workbench. The five destinations are wasteland.md §10 "The waste run — the gravship
disposal dilemma". Nothing in the sitting approved a warcasket workbench.

Sarcophagi, wasteland.md §7 verbatim:

> ⭐ **Warcasket sarcophagi** — a dead Junker in an adjusted warcasket is a sealed
> salvage-within-salvage: suit, tools, and the half-extracted core still in its grips.

Suit-side hook from WARCASKET_SUIT_CLASS_1 (`e6d9de93f`): `RM_JunkerSarcophagusExtension` on
`RM_WarcasketJunker`.

## Spec / verify / criteria

**A. The Cask Bay (settled: gravship hardpoint, shielded, hauls casks):**
- `RM_CaskBay`: a `Building_Storage` that can only go on gravship substructure
  (`terrainAffordanceNeeded Substructure`, Odyssey tab, `BasicGravtech`), so it rides the ship.
  Its storage filter is limited to hazard casks: Biotech `Wastepack`, the new
  `RM_HalfExtractedCore`, and anything in the new `RM_HazardCasks` ThingCategory. Vanilla
  shelves *refuse* wastepacks, so this is the first storage built for them.
- "Lead-lined / shielded", done as `RM_CompCaskShielding`: while a cask sits in the bay, its
  vanilla `CompDissolution` clock is held at zero, so it never dissolves or pollutes, and a
  core in the bay gives off no dose.
- Criteria: the XML parses, the csproj builds, and the filter and affordance resolve to real
  vanilla defNames. RimSage confirmed `Wastepack`, the `Substructure` affordance and
  `BasicGravtech`.

**B. Sarcophagi (settled by §7's sentence):**
- Sealed: when a wearer of a warcasket whose `RM_JunkerSarcophagusExtension` says
  `isSealedSarcophagus` dies, `RM_CompSarcophagusSeal.Notify_WearerDied` locks the suit onto
  the body. Vanilla `Pawn.Strip` calls `DropAll(dropLocked: Destroyed)`, which is false for a
  corpse's inner pawn, so ordinary stripping leaves the sealed suit on (checked in RimSage).
- Salvage-within-salvage: right-clicking the corpse gives **Crack open sarcophagus**
  (`FloatMenuOptionProvider`, which registers itself by reflection). It is timed work with a
  progress bar. When done, the **suit** drops and the extension's `salvage` list spawns:
  **tools** (components and steel from the welded extraction rig) and **the half-extracted
  core** (`RM_HalfExtractedCore`, new).
- A loose core (not in a cask bay) doses nearby pawns through vanilla
  `ToxicUtility.DoPawnToxicDamage`. This follows the dose-layer ruling ("mostly pollution
  mechanism"), and it is also the reason the bay exists.
- Settings (Mod Settings, Warcasket tab): sarcophagi on/off, cask-bay shielding on/off, loose
  core dose on/off. Each defaults to shipped behaviour and switches off cleanly.

## Existing code found

- `src/RimMandrake/Warcasket` (`mandrake.rm.warcasket`, `e6d9de93f`) holds the suit, the
  extension, and settings. It had no bay and no corpse code. Its header, recipe comment and
  About.xml all described the cask bay as a warcasket crafting bench. That was wrong and has
  been corrected in place.
- `src/RimStarWars/Armoury/Patches/Warcasket_BuildPathCut.xml` patches the VFE Pirates donor
  warcaskets. It has nothing to do with our RM_ suit.
- `src/RimMandrake/Wasteland` has no cask, core, bay or Junker code. There was no art for any
  of the new things: artpipe `done/`, `_artsrc/` and `registry.jsonl` were searched in Python,
  and the `korrum` sanity probe returned 6 hits, so the search does work.

## Built (all in `src/RimMandrake/Warcasket`)

- `Defs/ThingDefs_Buildings/RM_CaskBay.xml`: `RM_CaskBay`, a lead-lined cask bay. It is
  Building_Storage, 2x2, needs Substructure, sits on the Odyssey tab and needs BasicGravtech.
  It stores casks only.
- `Defs/ThingDefs_Items/RM_HalfExtractedCore.xml`: the `RM_HazardCasks` category and the
  `RM_HalfExtractedCore` item.
- `Defs/JobDefs/RM_CrackSarcophagus.xml`.
- `Source/RM_CaskBay.cs`: `RM_CompCaskShielding` holds dissolution at zero by reflection, with
  no Harmony. `RM_CompCoreDose` uses vanilla ToxicUtility, scaled to the vanilla rate.
- `Source/RM_Sarcophagus.cs`: the seal comp, the float-menu provider and the JobDriver.
- The extension gained `crackOpenTicks` and `salvage`. `RM_WarcasketJunker` carries the seal
  comp and a salvage list of ComponentIndustrial 2, Steel 25 and RM_HalfExtractedCore 1.
- Settings: three new toggles.
- Verify: XML parses. `dotnet build` passes with 0 errors and writes a fresh DLL and
  `.srchash`. Selftests are 77/79, and the only failure is the known
  `selftest_deployed_biome_refs`. Nothing was deployed or live-tested.

## Remaining / owner calls

1. **The item title is wrong.** It treats the Cask Bay as a warcasket workbench. The
   coordinator should correct that when closing, because the ledger is not mine to write.
2. **The five waste-run destinations** (wasteland.md §10) are campaign quest work, and no
   ruling covers the mechanics.
3. **The Stenchlands' own waste casks** (the "Throat's casks") have no item yet. Once one is
   authored, it joins `RM_HazardCasks` and the bay accepts it.
4. **Where dead Junkers come from.** No Junker PawnKindDef wears `RM_WarcasketJunker` yet, and
   nothing scatters sealed corpses on Wasteland maps. That belongs to the Wasteland/Junker
   cast items.
5. **What the core is for** (fuel, trade, or a reactor input). It is currently a sellable,
   dosing cargo item only.
6. Edge cases, unverified in game: butchering or burning a sealed corpse destroys the suit
   with it. A core in a pawn's inventory may not tick.

## BLOCKED art (owned texPaths, nothing generated)

- `D:\Luke\dev\Rimworld\src\RimMandrake\Warcasket\Textures\Things\Building\RM_CaskBay\RM_CaskBay.png` (2x2 building, Graphic_Single)
- `D:\Luke\dev\Rimworld\src\RimMandrake\Warcasket\Textures\Things\Item\Resource\RM_HalfExtractedCore\RM_HalfExtractedCore.png` (item, Graphic_Single)
