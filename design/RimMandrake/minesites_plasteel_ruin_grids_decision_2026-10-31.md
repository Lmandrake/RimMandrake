# Ancient mining ruin grids: plasteel and components cells (MINESITES_DECIDE_PLASTEEL_IN_RUIN_GRIDS)

Decided 2026-10-31 by FOUNDRY lane A3 under delegation (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM).
Build item: `MINESITES_GRIDS_BUILD_STEEL_FOR_BANNED_ORE`.

## What is there

Measured from the def dump capture 2026-10-28T23-26-38Z, `StructureLayoutDef.json` (126 KCSG layouts; sanity
probe: 3396 `MineableSteel` cells counted by the same walk). Mod "Ancient mining industry"
(packageId `xmb.ancientminingindustry.mo...`). Ten layouts (`AncientOpenPitMiningSite_A` was missing from the
finding's list). Correction 2026-10-31 (lane A4 build): this record first said "eleven"; its own table and an exact re-scan of
the same capture both give ten.

| layout | MineableComponentsIndustrial | MineablePlasteel |
|---|---:|---:|
| AbandonedPlasteelMineSite | 0 | 312 |
| AbandonedMine_Plasteel | 0 | 24 |
| AncientOpenPitMiningSite_A | 42 | 27 |
| AncientOpenPitMiningSite_B | 54 | 0 |
| AncientShieldMiningSite_A | 79 | 9 |
| AncientShieldMiningSite_B | 51 | 10 |
| AncientTunnelRuins_A | 67 | 3 |
| AncientTunnelRuins_B | 76 | 13 |
| AbandonedSteelMineSite | 18 | 0 |
| AbandonedUraniumMiningSite | 5 | 0 |
| total | 392 | 398 |

## Rulings it rests on

- Owner 2026-09-25: components and plasteel are never mined from rock ("fix that absurd thing in Vanilla where
  components and plasteel can be mined from rock"). Only iron/steel and plain stone form planet-wide veins
  (`minerals_where_they_belong_design_2026-10-02.md` section 2, form F1).
- Owner 2026-10-09: a planet of old broken salvage from mining companies and ancient war fleets
  (`canon_materials_design_2026-10-09.md` section 0). Salvage is the source of advanced material.

## Decision

Swap the symbol, keep the geometry: every `MineablePlasteel` and `MineableComponentsIndustrial` cell in these
ten layouts becomes `MineableSteel`.

- Not "keep as salvage flavour": a plasteel or components wall is mined from rock, which the 2026-09-25 ruling
  forbids outright. A ruin is not an exception to it.
- Not "strip": removing the cells opens holes in authored tunnel and pit walls, changing what the layout author
  built (rooms open to the outside, tunnels lose their sides). Swapping keeps every wall a wall.
- Steel, because it is the only ore allowed as a common vein, and an abandoned mine with its last steel seams
  left in the walls reads true. The ruins keep their own loot and salvage, so they still pay out as salvage
  sites; this only removes the forbidden ore.
- `AbandonedPlasteelMineSite` keeps its name: the plasteel was worked out long ago (that is why it is abandoned).
  No label change is in scope.
- Gated on the Minerals policy being on, like the rest of `RM_MineralExplicitLists`: with the policy off the grids
  are left as the mod ships them.

## For the build

Layout cells are comma-joined strings, so a PatchOperation cannot rewrite one symbol inside a row. The build goes
in Minerals C# beside `RM_MineralExplicitLists` (reflection, KCSG not referenced). Read the KCSG source first for
when layouts are parsed: if `StructureLayoutDef` resolves its rows into a symbol grid in `ResolveReferences`, the
rewrite must also (or instead) fix that resolved grid, or run before it. Verify offline against the dump counts above
(398 + 392 cells to 0) and live (L1) by `ProofState`-style read of the ten layouts after load.

## Built (MINESITES_GRIDS_BUILD_STEEL_FOR_BANNED_ORE, 2026-10-31)

- KCSG 1.6 (decompiled): `StructureLayoutDef.layouts` strings are parsed into `_layouts` (`List<SymbolDef[,]>`) once, in
  `KCSG.StartupActions`' static constructor; generation reads only `_layouts`. `src/RimMandrake/Minerals/Source/RM_MineralLayoutGrids.cs`
  therefore rewrites both, from the rows as first seen, on every `RM_MineralPolicy.Apply` (startup, settings change, FinalizeInit).
  Pure part: `Source/Kernel/RM_MineralLayoutKernel.cs`.
- Offline exact scan through the production kernel over the 2026-10-28 capture: 126 layouts, 10 touched, 790 cells; before
  plasteel 398 / components 392 / steel 3396, after 0 / 0 / 4186.
- Owed L1: `validation.py` chain `ruin_grids` (rows and resolved grid hold 0 banned cells; master off brings back 790).
