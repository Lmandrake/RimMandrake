## spec
Measured 2026-08-21 on the painted world. 238 river edges over 248 tiles form **ten
disconnected systems, and exactly ONE reaches water** — on a planet with three seas.

**Six `HugeRiver`/`LargeRiver` chains simply begin on dry land** with no tributary above
them. The largest starts at tile 2020 carrying a flow of **28,936**.

Worked example, system 2 in The Dune Sea:

    tile 11347   550 m   HugeRiver   flow 26193   ← starts HERE, nothing upstream
    tile 14568   419 m   HugeRiver   flow 23103
    … 30 tiles downhill, still HugeRiver …
    tile 16727   200 m   HugeRiver   flow  6968
                  71 m               ← stops in mangrove, never reaches the sea

**Two defects, and they compound.**

1. 🔴 **It appears from nowhere.** The channel head is wherever `acc` first crosses the
   threshold in `ashkarr_paint.py` (`chan = (acc > need) & …`). The catchment feeding those
   26,193 units exists in the field and is never drawn, so the river springs from a hillside
   at full size.
2. ✅ **FIXED — it never narrowed.** Grade was fixed for a whole river, so a stream losing
   water to evaporation drew at maximum width all the way down. `ashkarr_regrade_rivers.py`
   (`7d7ebca`) now grades each segment from the **min** flow of its two endpoints — taking
   the max is how a dying river stays wide by borrowing the water above it. Planet-wide:
   Creek 103→**112**, River 10→46, LargeRiver 12→51, **HugeRiver 113→29**. Pushed live.

⚠️ **Ending inland is DEFENSIBLE and is not part of this item.** Endorheic basins are real,
this is a desert world, and `evap` terminates rivers on purpose. A *HugeRiver* evaporating
in open desert was the defect, and the re-grade fixes exactly that.

🔑 This is the owner's 2026-08-17 complaint — *"they started in flat sand and ended in open
desert"* — still present after the authored-rivers rewrite. The flow accumulation got
authored; the channel extraction did not follow.

## verify
Defect 2 is verified: the re-grade asserts every other column and all 837 road rows are
byte-identical before writing, and the live `world_links_import` returned
`rivers 238, roads 837, unknownDefs []`.

Defect 1 is NOT fixed and needs the painter: lower the channel threshold upstream of each
head so the tributaries that carry the accumulation are actually drawn. Re-running the
painter moves biomes, so this waits behind a fresh look at the globes — same gate as
`SCALD_PLUME_SATURATES_RAIN_1`.

## criteria
- no river segment is graded above the flow crossing it ✅
- Creek is the commonest grade ✅ (112 of 238)
- 🔴 **no `HugeRiver` or `LargeRiver` chain begins on a tile with no upstream river tile** —
  currently **6 do**, and that is what remains
- and more than one of the ten systems reaches a sea

## notes
Filed by CHECK 2026-08-21. Half fixed the same night on the owner's call ("YES to the
re-grade"). ⚠️ Do not close this on the re-grade alone — the visible half is fixed and the
structural half is not, and the criteria above are written so that cannot be missed.
