# KOTOR_HEADBAND_DANGLING_REFS_1

## spec

Filed off the 2026-09-03 big-dump-load harvest: 23 dangling crossrefs + 1
failed PatchOperationAdd, all touching `guy762_Headband_*` defNames (interface,
verpine, nerualband, lightscan, bothan, demovisor, exchange, medical,
regalvisor, breathmask, rebreathermask). Filer's guess was "likely
Cherry-Picker-cut". Wrong guess — root cause found by history, not more
scanning: commit `8c946ec9` ("Graffiti: deploy today's undeployed changes,
fix 4 more real bugs", 2026-09-02 17:32, entirely about Graffiti job-driver
bugs) also deleted, with zero mention in its own message,
`src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Gadgets/Absorbed_KotorWeapons_GadgetApparel_KotORHeadgear.xml`
whole (749 lines) — an accidental sweep-up, not a design decision. That file
held exactly these 11 real, art-complete apparel ThingDefs (absorbed from the
live guy762.KotORWeapons donor, confirmed still present in its currently-
subscribed Steam Workshop copy — this was never upstream drift). Losing it
orphaned: guy762.kotordroids' `Patch_MHCStatsInterfaceVisor.xml`
(PatchOperationAdd onto `guy762_Headband_interface`, third-party, outside
our repo, harmless matches-nothing failure) and our own hand-authored
`CastRoster_{HOMESTEAD,BLACKSTAR,WILDSTEAM}.xml`, each with one pawn's
`<apparel>` deliberately set to `guy762_Headband_rebreathermask` — for
CastRoster_HOMESTEAD's watch-pawn specifically, the def IS the character's
whole narrative hook ("A scavenged rebreather that clicks twice on every
exhale..."), so this was never a candidate for "extend the cut instead" —
restoring the file is the only fix that doesn't destroy owner-approved pawn
flavor content (Pawn flavor phase 2, `7cfeb3e5`).

Also noted in the same crossref bucket, unrelated root cause: vanilla
count-class pseudo-defs (`MealSimple10`/`Chemfuel60`/`Steel75`/`Silver120`/
`ComponentIndustrial12`) — split off to `[[VANILLA_COUNT_PSEUDO_DEF_1]]`.

## verify

`git show 66207f15:<path>` (the last commit that legitimately touched the
file — SWAPPAREL_NEURALBAND_TEXTURE_MISSING_1's worn-graphic comment-out fix,
right before the accidental deletion) holds all 11 `guy762_Headband_*`
defNames the dangling-ref report named. Restored via
`git checkout 66207f15 -- <path>`; XML parses clean
(`xml.etree.ElementTree`). A live re-harvest would be the full proof but
isn't needed to close this — the restore is a straight revert of a
verified-accidental deletion, not new content needing a fresh live check.

## criteria

The file exists again with its 11 defNames and the SWAPPAREL fix's
comment-outs intact (not reverting that fix). guy762.kotordroids' patch and
the 3 CastRoster pawns resolve again. No further action on the CP-cut
question — there was never a cut.
