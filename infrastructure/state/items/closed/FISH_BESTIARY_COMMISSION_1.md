## spec
Owner-said (2026-09-10): "Commission lots of fishes! I would like there to be a
plethora of different kinds for each biome actually. Fish are easy. Lets get
creative! Squid like. Octopus like. Eel like. Crustaceans. Floaters. Jellyfish.
Cucumbers. Bring in that Star Wars creature richness." `kind: design` — a roster
proposal for the owner to rule on, never built defs. Folds in the four owed defs
(Scald thermophile shoal, Cathedral coolant eel, Wasteland brine-battery, Twilight
shoal); the `swfish_` Weeping Stones donors are the v1 placeholder by ruling.

## verify
Every fished water has a proposed table (buckets, weights, rare catches); every
register the owner named appears; the four owed defs carry a full spec; every
invented rule is flagged; the §6 questions are ruled and a build item is filed.

## status — proposal complete, reconciled; awaits rulings
`design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md` (Fable,
`50af6a2b`): 32 new `RUT_` species in 8 registers on 7 waters, 4 prize items,
6 rare-catch tables, the 4 owed defs specified in §4.

Evening pass (Fable, same day) reconciled it against the sea-beast family built
tonight and the hydrocarbon commission — no duplicate species; the bladderboil
catch folded into the Scald table (§2E). One finding, engine-read via RimSage
(`FishingUtility.GetCatchesFor` → `ThingMaker.MakeThing`, no category guard):
the live `BiomeFishTypes_Greentide.xml` (closed `FISH_TYPES_PATCH_BUILD_1`)
wires the scalefish RACE defs `RSW_Mee/Faa/Laa` into `fishTypes`; a net there
makes a bare `Pawn` with a stack count. Three scalefish catch items are owed
(§2C, §5.0, §6.7) — not live-tested, a quicktest fishing pass decides it.

Next action: owner/BENCH rules on §6's 8 cardable questions (7 and 8 added
tonight), then a build item is filed; §5.0's Greentide repair can go first.
