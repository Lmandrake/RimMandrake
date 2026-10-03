# TWILIGHT_REVIEW_FIXES_1 — fix the 14 code-review findings in the Twilight build wave

Full-file reviews of all 29 new TerminalBiomes .cs files ran 2026-09-27 (opus
review agent, BENCH-graded; status commit `eecf7d496`). 19 files marked CLEAN,
10 stay DIRTY with the findings below. Every file has its `<Compile Include>`
line; the Harmony launch gate reviewed clean (downgrade-only confirmed, refusal
cleared by a normal deconstruct job). Fix, re-review the touched files whole,
mark-clean.

## Ship-blockers — features that do not work at all

1. **`RM_Comp_VaeuliskLure.cs:64`** — reveal check runs from `CompTick`, but the
   lure is a plant (`ParentName="PlantBase"`) and plants never call `CompTick`.
   The disguise never drops; the vaulisk never appears. Use `CompTickLong`
   (CLAUDE.md's plant-ticker law), and remove any manual `IsHashIntervalTick`
   gate on top of it.
2. **`RM_Thing_CargoFloat.cs:44`** — `RM_CargoFloat.xml` sets no `tickerType`
   and parent `ResourceBase` doesn't either, so it defaults Never and `Tick()`
   never runs. A loaded float never unloads at a weir or the sink, and with no
   unload gizmo while loaded its cargo is stuck forever.
3. **`RM_MapComponent_ChannelCurrent.cs:724-748`** — the component is added to
   every map and the undersurge roll checks only Mod Settings, not the biome.
   Default settings give EVERY colony map an undersurge roughly every 12 days.
   Gate on the Twilight biome (or on the map actually carrying channels).
4. **`RM_MapComponent_ChannelCurrent.cs:497-511, 344-351`** — downstream drift
   and the two-cell surge grab never check the target cell is standable; the
   channel line crosses arbitrary terrain (bed/ford terrain defs don't exist
   yet). Pawns/items can be pushed into rock or a wall.

## Real defects, smaller blast radius

5. `RM_MapComponent_ChannelCurrent.cs:750-762` + `warnedPawns` (137/772) —
   first-entry warning fires for every pawn incl. wild animals though the
   setting says "each colonist"; `warnedPawns` grows forever and holds refs to
   destroyed pawns.
6. `RM_GenStep_TwilightChannels.cs:193` — bank-band cells get the channel's
   downstream direction instead of pointing INTO the channel (the component's
   contract); surged bank pawns travel along the bank, never into the bed.
7. `RM_Building_BankWeir.cs:114` — stake cascade only snaps already-damaged
   stakes; stakes never tick/wear, so a breach snaps none.
8. `RM_Building_BankWeir.cs:123-129` — breach end re-enables catch regardless
   of health; a weir below 50% re-breaches 600 ticks later, spamming the same
   message ~every 2,500 ticks all surge.
9. Weir catch on/off flag (via `CompChannelArrester`,
   `RM_MapComponent_ChannelCurrent.cs:122-125`) is not Scribed — a save
   mid-breach loads with the weir catching again.
10. `RM_Comp_WellChart.cs:35-50` — forecast captured at item creation, before
    it's on a map, so the lookup is empty; every chart reads "No open well to
    forecast".
11. `RM_MapComponent_WellLedger.cs:178-180` + `273-276` — well visuals only
    update while waning; a well starting in its opening stage (~7-14%) sits at
    radius 0.5 for days, and newly opened wells never ramp up.
12. `RM_CompCageCropSnapshot.cs:69-73` — crops captured-and-deleted on EVERY
    despawn, not just pack-up; deconstructing/destroying a cage deletes the
    crops under it.
13. `RM_Comp_ClaimBuoy.cs:45` — a destroyed buoy never clears the well's buoy
    link; a rebuilt buoy can't claim that well until reload.
14. Stale comments: `RM_TerminalBiomesMod.cs:459` and
    `RM_Comp_VaeuliskLure.cs:11` say "No Harmony in this assembly" — false
    since the launch gate. (Only finding in RM_TerminalBiomesMod.cs.)

## Open question carried, not a finding

The sunk hediff counts any roofed cell as "rescued". If the Twilight sea-floor
map is roofed everywhere, a sunk pawn is never at risk — check the floor map's
roof state when the dive map genstep exists, and tighten if needed.

## verify

- All 10 DIRTY files re-reviewed whole after fixes and marked CLEAN.
- A quicktest (minimal list) shows: lure reveals, a loaded float unloads at a
  weir, no undersurge on a non-Twilight map, drift never lands a pawn on an
  unstandable cell.
