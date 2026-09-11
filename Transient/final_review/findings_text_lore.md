# WORLDMAP_FINAL_REVIEW_1 — Phase 3: player-visible text & plot-leak audit

Scope: every string the world screen serves — live biome labels/descriptions (deployed
game copy + def dump labels), landmark defs and 3,414 live landmark names, 71 features,
96 settlements, the deployed `Scenario_Utinni`. Rule source: §P/§GM partitions in
`design/Jawa/worldbuilding/biomes/the_scarlands.md` and `the_rust_cathedral.md` (both
read in full before judging).

## The structural fact everything below hangs on (MEASURED)

`BiomeNames_Ashkarr.xml` is **label-only by design** (its own header: "LABEL ONLY").
The live planet runs **donor defNames** on ~23 of 29 painted biomes (AB_*, ZBiome_*,
GRiNDTerra, COMIGO, vanilla) — so the player reads OUR label over the DONOR's
description. The 27 fully-authored `RUT_*` BiomeDefs in
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/UtinniPatches/Defs/BiomeDefs/`
carry superb campaign descriptions — but only six of them own live tiles
(NightsideIce, BlueDesert, TwilightSea, GreySea, TheScald, PropaneLake, ~3,500 tiles).
The other ~18,000 land tiles serve donor prose. No patch in any deployed mandrake mod
touches a biome `description` (verified across all seven deployed mods).

## A. PLOT-LEAK — 4 findings, all donor-inherited; 0 in authored text

Every string WE wrote is clean: biome defs, landmark defs, features, settlements, and
the scenario contain no Rakata, no Assailants, no Cathedral-nature, no scaria
authorship, no terramanufacture. The leaks are donor descriptions asserting past-why
on gated ground:

1. WORST — `AB_MechanoidIntrusion`, labeled "the Rust Cathedral" (236 tiles):
   "A mechanoid hive was dismantling this biome, turning its mass into computronium,
   and hastily left it abandoned for unknown reasons. Almost no trace of its
   biological origins has been left untouched, with even the trees turned into
   mechanical contraptions destined for some nefarious purposes." — first-tier text
   asserting a machine-industrial history of THE gated biome; "turning its mass into
   computronium" lands a near-miss on §GM's smart-metal/mind-factory truth, and the
   whole line violates ban 6.1 ("the mind's nature… plot only, gate-kept") and §P's
   register. Plus a `<color>` difficulty footer.
2. Vanilla `Scarlands` (90 tiles, not even relabeled — shows "scarlands"):
   "Ruins of an ancient city which was destroyed by weapons of mass destruction.
   Water here is toxic and scaria runs rampant among the animals. Mechanoids lurk
   among the shattered buildings, waiting to awaken and kill again." (+ settleWarning:
   "…dangerous insects and rogue mechanoids…") — wrong past-why: §P says defense-works
   with no trace of the enemy, not a bombed city; "waiting to awaken and kill again"
   contradicts ban 6.6 (Sentinels defend only) and "every ancient danger here has
   already been opened and destroyed". The authored `RUT_Scarlands` text is perfect —
   and owns zero tiles.
3. `AB_PropaneLakes`, "the Propane Lakes" (2,531 tiles): "As propane is a compound
   that doesn't occur naturally, this is probably the remnant of some weird ecological
   or industrial experiment gone awry." — asserts industrial origin; the Lakes are
   terramanufacture's far end (§GM, `TERRAMANUFACTURE_CANON_1`). Leak-adjacent
   past-why in first-tier text.
4. `AB_RockyCrags`, "the Forsaken Crags" (1,135 tiles): "In the ancient past it
   was partly terraformed by a mysterious humanoid alien race simply known as
   Forsakens." — invents a rival ancient race in player text, corrupting the one
   reveal ladder the campaign has (players taught wrong ancients before the Rakata
   gates open).

Not leaks, noted: 97 vanilla "terraforming scar" landmark labels (ambient ancient
engineering, explains nothing — tolerable); `RUT_Slime` "It was a weapon once…" is the
slime sheet's own sanctioned register (`the_slime.md:54`, verbatim source), and the
def owns no tiles anyway; the four authored LandmarkDefs: clean.

## B. QUALITY

**Authored voice: one campaign, unmistakably.** The 27 RUT_ biome descriptions, all 71
feature names (Nightspill, Cinderdark, Salt Gate, Grinding Floor, Lantern Deeps), all
96 settlement names (faction-differentiated: Outlander water-hunger — Whistledew,
Cloudtrap, Reservoir 7; Hutt vanity — Mokka the Unpaid's Palace; droid theology —
Unbound Exception, Second Speaker; Geonosian — The Godmouth, The Unfinished Work), and
the scenario all speak the same voice. Zero Earth slips in any of them.

**Three mods arguing — literal, and planet-wide.** Under our labels the player reads:
"the Greentide" → "Overgrown jungle." (GRiNDTerra, 235 tiles); "the Cracked Lands" →
"Rocky, dry and desolate, these temperate regions…"; "the Weeping Stones" → "Desert
with a few small islands of life"; "the Rot" → a mushroom gameplay-tips essay; five AB
texts ship `<color>` "Biome difficulty:" footers; "the Miasma" opens with an Earth
encyclopedia entry ("Mangrove swamps, also known as mangals, are coastal wetlands
found in tropical and subtropical regions"); "the Poison Forest" mentions Earth trees
(poplars). Flat-generic-on-marquee at its purest: "the Greentide"/"Overgrown jungle."
(Blue Desert mostly escaped: 1,029/1,030 of its tiles are RUT_BlueDesert, our text.)

**Landmark names (procedural vanilla/VEE namers):** no leaks, but 358 possessive Earth
forenames (Howard's, Betty's, Matthew's, Mindy's Caves) and ~80 Earth-animal names
(Iguana Neck Valley, Elephant Seal Foot Ice Mounds, Polar Bear Water-Filled Cenotes,
Prime Dove Village) on a world whose doctrine evicts vanilla-Earth fauna. Wide,
low-stakes, ambient; Dead Sarlacc ×7 dupes are already punch row 4.

**Scenario nit:** the file's own header vows no invented duration ("A first draft
had… 'twenty thousand years'; neither is in any founding doc") — yet the shipped text
says "in a language nobody on this world has heard in **ten thousand years**." One
phrase to cut or ratify. **RULED 2026-09-11 (card sitting): CUT the number** —
reword to a non-numeric span; filed as `SCENARIO_DURATION_CUT_1` (FOUNDRY,
needs deploy). Blast radius: the scenario narration only — design docs'
"ten thousand years" prose is not bound by the scenario header's vow.

**Best 5 strings, worth celebrating:**
1. Scenario close: "The hull is yours because you woke it, and a thing that could
   still be made to work was never scrap; it was a sleeping hand, owed its waking.
   Get it off the ground."
2. `RUT_BlueDesert`: "what lives is a fuel charge stable only in the cold, and warmth
   is detonation."
3. `RUT_Sump`: "the tar takes slowly, keeps perfectly, and everything that ever
   blundered in is still in there."
4. `RUT_ExtremeDesert`: "Nothing here tracks the sun because the sun does not go
   anywhere; everything owns a shadow instead."
5. `RUT_Webwork`: "The map shows a jungle with no water because the water is inside."

## Lore-vs-map (sheets' landform prose vs Phase 1/2 MEASURED/SEEN — not re-derived)

- Scald "perched ocean… vast crater ringed by mountains" ↔ SEEN stare_closeup_Scald:
  blue disc, green shore ring, mesa rim, canyon terraces. MATCH (the centerpiece).
- Greentide "gallery jungle hugging every mile of the rivers" ↔ SEEN §7: jungle
  ribbons tracing rivers. MATCH.
- Scarlands "crater fields… shattered megastructure floors" ↔ def gensteps
  (CratersLarge/Med/Small, AncientMegastructure terrain) + SEEN red mass east of
  substellar. MATCH in mechanism and paint.
- Cracked Lands "canyon country below the only dayside mountains that rain" ↔ SEEN
  canyon bands SW of substellar. MATCH.
- Rust Cathedral "at the foot of the eternal noon" ↔ placed by Scorch; the
  Scald/Scorch label-collision row already covers the presentation nit. MATCH.
- Umbra "frozen ammonia flats" ↔ feature "Ammonia Flats" on the far side. MATCH.
- Forge "only vertical skyline in the Dune Sea" ↔ 31-tile massif; the 3 rivers hidden
  beneath it (report row 11) remain the only landform friction. Already punched.
- No sheet's canyon/rim/disc/arc claim contradicts anything Phase 1/2 measured or saw.

## Correctives (one new punch row, S–M)

**BIOME_TEXT_PORT pass:** the fix is already written — port the RUT_* descriptions
onto the live donor defs via description patches in the same conditional style as
`BiomeNames_Ashkarr.xml` (or migrate tiles to the RUT_ defs under
NAMING_SCHEME_EXECUTION_1), and relabel/replace the three never-relabeled biomes
(`Scarlands`, `Wasteland`, `AridShrubland` — 2,571 tiles showing lowercase donor
labels), including the vanilla Scarlands settleWarning. That single pass clears all 4
leaks and the whole three-mods-arguing class. Optional S: landmark rename sweep for
the worst Earth names, folded into punch row 4's dupe-rename sitting; scenario
"ten thousand years" ruling.
