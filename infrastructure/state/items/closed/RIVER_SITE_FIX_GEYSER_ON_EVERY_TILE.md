# RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE

Found live by BENCH 2026-10-11 (flowworks tier, 11 mods). Class: HARNESS (site finder).

`src/RimMandrake/FlowWorks/northstar/river_site.py` rejects any tile with a `BW.NATURAL_SCENERY` thing (SteamGeyser) anywhere
in the 130x130 central rect (61,61,130,130). On a vanilla quicktest world that is nearly every river tile: two attempts
(10 tries, then 30 after BENCH raised the cap to 40) rejected every river tile that had a current, so the river half of
extension_proof never got its site (`--site river` ran on the wrong map: 8 PASS / 1 FAIL / 11 UNMEASURED, not recorded).
Logs: Transient/bench_live_20261011/fw_river_site.log.

Trivial fixes already applied by BENCH (this commit): a rejected tile's map is dropped (`jawa/settlement_remove mode=map`)
-- the first attempt left 10 live maps behind -- and the try cap is 40.

NEXT: test geysers against the extension PLOT cells (site_spec layout + buffer), not the whole 130x130 rect, then rerun river_site.py + extension_proof --site river + --merge.

Fixed e70bbf9582bc: geysers now reject only on the DRY site, and only inside site_spec plot buffers (river chains use no plot).

## criteria

- A1 L0: selftest_extensions geyser probe passes (river site never rejected by a geyser; dry site rejected inside a plot buffer only)
- A2 L1: live, `python.exe src/RimMandrake/FlowWorks/northstar/river_site.py` exits 0 on a river tile and `extension_proof.py --live --site river` runs the river chains
