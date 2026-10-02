# WEEPINGSTONES_REFUSED_TOLL_RITE_1 — The Refused Toll, for Mob'Unloo: draw water in the open at a station metered by someone who does not live there, and walk away without paying

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Campaign tier**, `mandrake.rut.rites` (`src/RimUtinni/Rites/`,
found rite) plus a new campaign quest site (the Imperial metering station, `src/RimUtinni/UtinniPatches`). Design:
`design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §6 R2, §8. Register:
`design/Jawa/salvation_rites_2026-10-01.md` B15 (row added) and §(d) for the found-rite machinery; B6's "pool
rites" row now points here.

Ruling: owner, typed 2026-10-02: *"This is pretty cool (2). Gotta do it."* Option (2) is the card's **refused toll,
for the god of debt and trade**. **God: Mob'Unloo** (debt and the sacred exchange; the register's own reading at
B12, *"trading god = Mob'Unloo"*). Mob'Unloo's found rites: the Blind Offering (B2), the Storm's Receipt (B7,
pitched), the Cold Ledger (B7, ruled-kept), Mob'Unloo's Price (B14, ruled), and this: **five, at the cap of five**
(counted by hand from the register 2026-10-02). The Open Water (Oomo) was **NOT CHOSEN**; Oomo keeps his slot.

## spec

**God: Mob'Unloo.** Kind: feeding. Calls `GameComponent_Ninefold.ApplyDelta(MobUnloo, <amount>, "The Refused Toll")`,
the call shape of `SUMP_SINKING_RITE_BUILD_1`.

1. **Found / learned.** Inscription `RUT_RefusedTollMeter` (name collision-checked): at an oasis outside an Imperial
   garrison, a water meter torn off its post and laid face-down in the pool's ring, its dial jammed at zero,
   scratched *nothing owed*. Placed on Weeping Stones maps near Imperial presence by a map GenStep with a chance
   (never worldgen; the `RUT_FelledNoonStump` shape). Studying it → the Rites tab's found-rites row →
   `RUT_ResearchMod_GrantRite`, per §(d). Performable after at any qualifying site.
2. **The site.** A new campaign quest site: an **Imperial water-metering station** at an oasis the Empire does not
   live on (sheet: the Empire's metering stations break the claim law *as policy*). Offered as a quest/site the
   clan can travel to; also any faction post the claim law convicts (a toll on water the toll-keeper does not live on).
3. **The rite.** Participants draw water at the metered source in the open, in sight of the meter, and walk away
   without paying.
4. **Risk (the point).** A letter warns that the toll-keeper answers (an Imperial patrol). The water carries the
   truce: if a participant **strikes first** there, the wild herds turn on the clan (the built retribution,
   `RM_MapComponent_WaterTruce`, reused off its biome for the site). The clan must refuse the debt and not start
   the fight.
5. **Outcomes (cohesion only).** Shared memories by quality; Mob'Unloo's favour told by the Narrator, shown only in
   his subtle odds; the Deep Desert Tribes hear of it (world state, not a reward). No power, no item reward.
6. **Readable signs.** The warning letter, the truce radius drawn at the station's water, the retribution letter if
   it breaks.

Depends on: `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` (truce semantics at the site), §(d) machinery.

## criteria

- `jawa/get_defs` for the precept/ritual, `RUT_RefusedTollMeter` and the station site def: `foundCount` 1 each.
- Live: studying the inscription grants the rite; performing it at a debug-spawned station completes with
  memories and a `MobUnloo` delta; a debug guilty strike by a participant triggers retribution on the colony; the
  patrol letter fires.
- No free-tier file references any def here.
