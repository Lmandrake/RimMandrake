## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod tier, `glow_tank_live.py --fresh-map`).
Class: SITE + HARNESS. Evidence `Transient/bridge_run_1_20261023/glow_tank.json` / `glow_tank.log`.
GLOWTANK_SALT_CROP_GROWS (GLOW_TANK_LIQUID_FEED_1 A2, crop half) UNMEASURED "crop growth unreadable": growth1/growth2 null
for both S and F although set_plants planted 4 at growth 0.10. Every glow-tank inspect read "Cannot grow (bad seasonal
temperature)" — the fresh quicktest map is out of growing season (SITE), and the growth() reader (glow_tank_live.py:108,
inspect line starting "growth") finds no such line (HARNESS: read the plant's Growth field via thing read instead).
Fix: pin season/temperature (or set the map to summer before planting, never warp the clock) and read growth from the
plant thing; the drawn-one-unit and setting-off rows already PASS (GLOWTANK_DRINK A1 verified this run).
