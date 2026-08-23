# CREATURE_RESIZE_PATCH_1 — 25 approved resizes applied. BUILD, 2026-08-23

Owner approved 2026-08-23: *"nice job on the animals. I approve for v1. We'll have to meet
them and see how it feels during live play."*

`src/Jawa/Jawa_Patches/Patches/CreatureResize_Ashkarr.xml` — **75 operations, 25 creatures.**
Deployed, VERIFIED in sync.

## the criterion the item set, and it is MET
> *"A patch that matches nothing logs nothing. Count the operations that applied; do not read
> the absence of a red error as a pass."*

    validate_patch.py --defs (Data + Mods + Workshop) --defnames <578-mod capture>
    operations matching NOTHING: 0 of 75
    0 errors, 2 warnings

- [x] All 25 creatures patched with the field and magnitude the list names
- [x] Zero `bodySize` edits among the 23 shrinks
- [x] `Zakkeg` and `BMT_Thrumbungus` carry BOTH fields

## 🔴 drawSize is not where you would look, twice over

**1. Not on the ThingDef.** It lives on `PawnKindDef.lifeStages[].bodyGraphicData.drawSize`.

**2. The def dump does not carry it at all.** All 25 read `null` in capture
`2026-08-23T07-12-04Z` — the dumper does not serialise the Vector2, exactly as it does not
serialise `Color`. ⇒ **Every current value had to be read from each mod's own source XML on
disk**, across the eight mods involved, and the new value is current × the approved
multiplier PER LIFE STAGE. A resize job cannot be done from the capture.

## ⚠️ THE TRAP THAT NEARLY SHIPPED, and it produced a confident wrong patch

A `PawnKindDef` block also contains **`dessicatedBodyGraphicData`**, which has its own
`<drawSize>`. A regex for `<drawSize>` over the whole block returns **twice** as many values
as there are life stages — Zakkeg came back with 6 for its 3 stages — and the generator
duly emitted operations indexed `li[1]` through `li[6]` against a def that has three.

**The first patch had 170 operations. The correct one has 75.** It validated as "OK - 0
errors" both times; what caught it was printing the per-creature table and seeing `1.5->2.46,
1.5->2.46` repeated. ⇒ Extract only from inside `<bodyGraphicData>`, and always print what a
generator produced before trusting it.

## what to watch in play, in the owner's own framing
⭐ **The two enlarges are the risky half.** `Zakkeg` 5 → 8.2 and `BMT_Thrumbungus` 4 → 8.2
roughly double meat, melee scaling and food need. Both went in because `AB_MiasmicMangrove`
and `IceSheet` had no super-huge creature at all. These are exactly what *"see how it feels
during live play"* is for — watch them before anything else.
