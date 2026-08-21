## spec
🔴 **THE OWNER'S RULE THAT PRODUCED THIS ITEM, 2026-08-21:** *"I'm not convinced there were
graphical problems to fix with BarkHead and Bandolier. I think we didn't understand how
graphical assets are stored and frequently don't carry the full SNWE full orientation... so
I'd like to leave them out until I can be shown it's a problem."*

He was RIGHT about the bandolier, and that half is closed: west is absent on all four
bandoliers (the convention), and the two that ship north are the two whose front and back
genuinely differ — the knife bandolier's authored north carries no knives, because a
rotated south would put the sheaths on the pawn's spine. Evidence:
`infrastructure/output/TRANSIENT_missing_facing_evidence.md` and
`infrastructure/output/bandolier_north_evidence.png`. `KotORBandolierNorthFix` stays
UNACTIVATED.

**This one survived the same test and is the only one that did.** In Vanilla Races Expanded
- Phytokin's `Textures/Things/Pawn/Humanlike/Heads`:
  - **10 head sets. All 10 ship south and north. 9 of 10 ship east.**
  - The single exception is `BarkSkinFemale_Wide_Normal` — exactly the file
    `src/RimMandrake/PhytokinBarkHeadFix` supplies.
  - 🪤 And the slip that made it is still in the folder: **`BarkSkin_Wide_Normal_east copy.png`**,
    a mis-saved duplicate, sitting beside the set that is one file short.
One sibling differing, with the accident still visible, is the opposite of a convention.

⚠️ **What is NOT established, and is the whole reason this is a look and not a fix:** what a
missing head east actually LOOKS like. Heads render through `PawnRenderNode`, not plain
`Verse.Graphic_Multi`, so the `_north`→`_south`@180 / `_east`↔`_west`-flip fallbacks measured
for apparel and buildings may not apply here at all. Nobody has looked.

## verify
Spawn a Phytokin with **bark skin**, **female**, **wide head type**, and face it **EAST**.
🔑 The gene and head type must be SET, not hoped for — a random Phytokin rolls this
combination rarely, and photographing a default proves nothing. Compare against the same
pawn facing south, and against a male or narrow-headed bark Phytokin facing east (which has
its own art and should look right).

## criteria
One of these two, either is a result:
- The east view is visibly wrong (a face where a profile belongs, a mirrored or substituted
  head) ⇒ the fix is real. Say so and BUILD adds `mandrake.phytokinbarkheadfix` to
  `ModsConfig.xml`; it already declares the correct `loadAfter`.
- The east view looks correct ⇒ the engine covers it, the fix is unnecessary, and the mod
  is retired unbuilt — and we learn that the owner's rule generalises further than the
  sibling census suggested, which is worth more than the fix.

## notes
BUILD measured this offline and stopped at the look deliberately. The mod is DEPLOYED but
NOT in `ModsConfig.xml`, so it currently loads nothing and changes nothing — there is no
need to remove it before testing, and no risk in leaving it while this is decided.
