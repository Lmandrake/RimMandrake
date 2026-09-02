<!-- status: SW_SEA_MONSTERS_ART_1 art state. 16 of 18 shipping facing sets exist.
     Roster (RULED): design/Jawa/worldbuilding/sea_beasts_roster.md ·
     def spec (drawSize): design/Jawa/worldbuilding/sea_beasts_def_spec.md §5 -->
# Sea beast facings — what exists

One folder per creature: `<Slug>/<Slug>_{south,east,north,west}.png`, a contact
sheet, and a `PLAN.md` carrying that set's PROVE/EXPECT/LIES. `<Slug>` is the
defName suffix, so `RSW_ShaleGorger` ⇒ `ShaleGorger/`.

**Every set here is 4/4 and clears `../tools/seacheck.py` with 0 REJECT.**
⚠️ `Graphic_Multi` needs all four or it fails silently — no magenta — so a
folder with three PNGs is not a partial delivery, it is a bug. There are none.

| role | creature | canvas |
|---|---|---|
| silt ambushers | OpeeSeaKiller · CrimsonOpee · ShaleGorger | 256 · 512 · 512 |
| harpooners | ColoClawFish · AbyssalColo · ThornbackColo | 512 |
| leviathans | SandoAquaMonster · ElderSando · StormSando | 1024 |
| shoal grazers | Mee · Faa · Laa | 256 |
| scavenger swarm | Yobshrimp · SiltLamprey · RustNipper | 256 |
| colossal neutrals | Reefback | 1024 |

## Still owed

**`Starmaw` and `Lanternwhale` have no facing set.** Generation stopped on a
hard ChatGPT usage limit (`ERROR: You've hit your usage limit`), not on a
quality or validator failure. `Transient/sea_raw/Starmaw_south_raw.png` was
produced before the limit; nothing else. To finish, once the limit resets:

```
python3 ../tools/gen_sea_facings.py Starmaw Lanternwhale
python3 ../tools/build_sea_facings.py Starmaw Lanternwhale
python3 ../tools/write_sea_plan.py Starmaw Lanternwhale
```

Then LOOK at each contact sheet — `seacheck.py` proves the files are shippable
and cannot tell you the four facings are the same animal.

## The one deliberate deviation, stated

`OpeeSeaKiller` is the pilot set and is **256x256**, while its def spec drawSize
of 2.25 wants 288 px ⇒ a 512 canvas. Its own PLAN.md predicted this ("if the def
later ships a different drawSize than 1.4, this canvas is the WRONG budget"),
and the def spec then shipped 2.25. It is not a blocker — RimWorld scales the
texture to `drawSize` regardless, so the sprite is correct and merely blockier
than its two siblings. Rebuilding it needs two generations and the same usage
limit blocks that.

The three colossi are capped at a 1024 canvas rather than the 2048 that 128
px/cell would want. The image model returns ~1.5 Mpx natively, so 2048 would be
an upscale of detail that does not exist; each PLAN.md states the cap and the
px/cell it actually ships at.
