# STILLSAND_RETURN_REMAINDER_1 — the Return: live proof and the parts not built offline

From `STILLSAND_RETURN_RITUAL_1` (built c1aa656de). What shipped there: the RM bloom-on-pour
(`src/RimMandrake/Stillsand/Source/RM_StillsandWater.cs`, right-click a water item on Stillsand
sand → "Pour … into the sand"), the inert water-ledger engine (`RM_WaterLedger.cs`), and the
Utinni faith as XML (`src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_TheReturn.xml`:
`RUT_SunDebt`, `RUT_SunDebtOwed`, `RUT_Ritual_TheReturn`, `RUT_DebtStone`), plus the krayt-kill
opening (`Patches/RUT_TheReturn_KraytOpens.xml`). Settings rows: Stillsand panel, "Water on the sand".

## spec

1. **Live proof (Desktop, quicktest on RM_Stillsand, all DLC).** The parent's two criteria:
   a Sun-Debt colony (an ideo holding the `RUT_Ritual_TheReturn` precept) accrues debt from
   drinking water, the Return opens after a sandstorm ends (dev-fire it), and a good outcome
   lowers the debt and blooms the ring at the stone. Without the Utinni layer, pouring a guzzka
   egg on sand still blooms hourbloom and no debt rows appear in settings. Read the first
   exception in `Player.log`, not the loudest.
2. **The Return line is not drawn.** Poured cells are tracked as wet (`RM_MapComponent_WetSand`,
   wiped by a gale) but nothing renders the darker stain. Needs a visual (a terrain overlay or a
   filth def) bound to those cells; check artpipe `done/` and `_artsrc/` before queuing art.
3. **Old tribal debt stones in the debt cave** (`STILLSAND_PRECIOUS_CAVES_1` row) with lines
   worn in: not built.
4. **More water sources for the debt.** Only the guzzka egg (6 L, `RM_CompProperties_WaterVolume`)
   carries it. The still flask (`STILLSAND_GLASS_LENS_CHAIN_1`), a duumma sac and a wringing
   should carry the same comp, or call `RM_WaterLedger.Notify_Drawn(map, litres, what)` directly.
   Drinking an egg through Dubs Bad Hygiene's thirst job may not run `PostIngested`; check live.
5. **The dune gale.** `galeWeathers` lists only Odyssey's `Sandstorm`; `STILLSAND_DUNE_GALE_1`
   appends its WeatherDef in `src/RimMandrake/Stillsand/Patches/RM_SandRemembersWater_Stillsand.xml`.
6. **Stale folded-id guards.** `RUT_KraytAttack` was gated on `mandrake.rm.stillsand` (folded into
   `mandrake.rm.biomes`, so the def never loaded); fixed in the parent. Other Utinni XML still
   names `mandrake.rm.stillsand` in `MayRequire` (e.g. `Defs/BiomeDefs/RUT_CrackedLands.xml`'s
   `RM_DuneCrawler` row) and is silently skipped. Sweep them to `mandrake.rm.biomes`.

## criteria

- Spec 1's two criteria pass live, with the log quoted.
- A pour leaves a visible line that a gale removes.
