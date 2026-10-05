# MessyConduit art round 7 — Scrapper laid reel connector

Owner: "The junk-built reel (when deployed) shows an open connector pointed at the camera rather than it pointing down and plugged in like the others."

## Status
- [x] inspect current + comparisons
- [x] redraw
- [x] validate
- [x] art install
- [x] commit

## Notes
- inspected: scrapper laid reel had an open brass socket at drum face (x~145-172,y~110-142); others have a vertical inlet post from drum bottom to base bar.
- approach: deterministic hand edit, src/RimMandrake/Utils/mockups/messy_conduit/round7_reel_fix.py (paint socket out with cloned drum pixels; draw rusty inlet stub down from drum centre bottom x=159).
- validator (`skills/generating-rimworld-sprites/scripts/validate_sprite.py`, ref = round-6 picture): PASS; 256x256 RGBA, subject bbox (11,29) 240x180 unchanged, centroid (132,131) vs (131,131). `--strict` only warns on 0.74% faint fringe inherited from the round-6 art (ref 0.78%).
- installed via `art install` (reason `script:src/RimMandrake/Utils/mockups/messy_conduit/round7_reel_fix.py`): cb47aac97 -> 0c5979549a39; ledger shard `infrastructure/state/art/events/BENCH.jsonl`.
- review sheet updated: `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round6_scrapper_reel.png` (laid AFTER panel = round 7).

## Result
Open brass socket on the drum face painted out (drum rust cloned from either side); a rusty junk inlet stub now drops from the drum's centre bottom (x=159) into the base bar — welded collar, brass wire lashings, bodged grey clamp band — matching the Industrial/Modern/Futuristic laid reels. Junk look, canvas and anchor unchanged. No Source/Defs touched.
