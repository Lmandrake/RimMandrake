# LEANINGSCRUB_ART_WIRING_1 report

## Subjects and texture status (before)
All 13 animals, 8 plants (4 fuzz + 4 venomvine forms), RM_VisslerArm and RM_RawVenom were missing their textures. RM_Fuzz, Grellbush, Grellspine, WildHealroot were already wired in 66dffc905. Thunderstep (`RSW_ShrublandGiant`), yanker (`RSW_TunnelSnake`) and scrap-nest bird (`RSW_ScrapNestBird`) are `RSW_` defs in SWBestiary, still on donor Fambaa/Klorslug/Whisperbird art with a colour tint.

## Found art wired (57 PNGs)
Source: `infrastructure/artpipe/_artsrc/<job>/<job>.png` (jobs in `done/`, all manifests status ok, facts PASS; located by python sweep of _artsrc/done/registry/art_status/Transient decisions, sanity probes korrum=15 / imperialtoad=11 hits; no `.decisions.json` rules on any of these subjects).
- 13 animals x east/north/south, 256x256, at `src/RimMandrake/LeaningScrub/Textures/Things/Pawn/Animal/RM_<Name>/RM_<Name>_<facing>.png`: Fuzzrunner, Thornhold, Shokka, Zellik, Fuzzviper, Surrik, Ribbonwhip, Vissler, Dustflutter, Shirrel, Crustweevil, Rollbug, Tikkit.
- 8 plants as `Textures/Things/Plant/RM_<Name>/RM_<Name>_a.png`: Whipfuzz, Pillowmoss, Tanglefuzz, Cruststar, Dripping/Twitcher/Hollow venomvine (256), CrownVenomvine (512, as its def states).
- Item `Textures/Things/Item/Resource/RM_VisslerArm.png`.
- Thunderstep (512), yanker (256), scrap-nest bird (256), east/north/south, at `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_<ShrublandGiant|TunnelSnake|ScrapNestBird>/`. The three PawnKindDefs now point their bodyGraphicData at these and drop the `<color>` tint (art is baked-colour). drawSizes unchanged (JUDGEMENT: tuned for donor art, needs a look in game). Dessicated graphics and the scrap-nest bird flight flip-book still use donor paths.
- Stale "queued in artpipe / placeholder" header comments in the four LeaningScrub def files and "zero new PNGs / retint" claims in the three RSW def headers corrected.

## BLOCKED
- `RM_RawVenom` (Graphic_StackCount): no art anywhere, not in any artpipe list (0 hits in _artsrc, done, pending, registry). Drop-in: `D:\Luke\dev\Rimworld\src\RimMandrake\LeaningScrub\Textures\Things\Item\Resource\RM_RawVenom.png`.
- Optional, not blocking: Zellik and Dustflutter flight frames (none exist; they fly with the grounded sprite).

## Verification
- All 130 LeaningScrub + SWBestiary race XMLs parse.
- Every LeaningScrub texPath resolves except RM_RawVenom; the three RSW body texPaths resolve.
- Selftests: see commit message / final reply.
