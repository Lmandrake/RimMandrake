# GSS Ralph: where the last pass got to

Pass 1 was offline only (Graffiti held the game). Nothing below has been seen in the game yet. The new DLL is built and committed but NOT deployed.

## Built, proven offline only
- **Modern junction strip** (the owed change). `CordBuilder.PoseStrip`: sockets face the T's stem, the lead takes the arm to their right, a cord from behind swings round the free end. One plug per bundle. Selftest `JunctionStripChecks`; `CordAudit` reads the strip from the decal alone and now covers blobs in every look.
- **Blob junctions in box looks changed too**: cords now end on the box's arms, not its centre. Not asked for by name, but the plan's "arm alignment must cover blobs" needs it. Look at this one: it touches approved Industrial/Scrapper/Futuristic.
- **Plug altitude**: plugs print 0.001 above other decals so they lie over the strip. This touches every plug.
- **Cord shape instrument**: `Core/CordShape.cs`, probe `shapetable`. Offline: 8 parallel equal runs, 5 seeds, closest pair 0.99 cells apart, bar 0.3, planted twin reads red. Bar not yet checked by eye.
- New rows, never run: `M15f_restring_joined_run_one_look`, `S12e_batched_links_merge`, `M22a/b` kinetic sway (`explode:x,z,r,dmg,kinetic` carries its own marker, so no KineticArms needed), and B6/B6b now read tangle-only strip counts, because Modern junction strips sit on other nets and would have false-failed them.

## Offline state
validation.py 9/9, selftest 1056/1056, proof_all --offline-gate green with no allow-red.
`review/render_laid.py` draws a selftest `--dump` with the real art. It is geometry only: flat cords, no floor. It is how I judged the strip; it is not the game.

## Items
Fixed in code, runtime half unproven: BATCHED_LINK, STYLED_WINNER, COLOUR_SEED, STRIP_LED (selftest for the signature; live repaint unseen), MULTILINK, FRESH_BUILD.
Fixed, offline is the whole fix: FUZZ_ONLY, CORD_AUDIT, RECOLOR (the --check now accepts the necked T/X: no orange, same shape as the base; the writer skips them. I tried regenerating them first: the art guard refused the push, rightly, they are judged art, and installing would write to infrastructure/state.)
Already fixed before this pass (notes were stale): POWER_THEFT (TapWindowChecks), RESTRING_FIX (Patch_Restring_Bridge), CORD_SWAY alloc half (SwayInto), WATER_STUB (FlowWorks swim made deep water read walkable; WaterStubChecks). Each still owes its live row.
Ruled out: CORD_ADAPTER no-lamp-geometry. Lamps read as Consumer and slide to the centroid, the look he walked; enabling Lamp would change approved art with no north-star line false. Comment on `KindOf`.
Rows exist, need a live run: SWITCHES (M21a-f, M12a/b). keepWiresOnGravship is setting-state only; its behaviour is not shown anywhere live.
Not mine to edit (`infrastructure/state/`), for the Conductor: `--allow-red O6_review_round1` can drop from the SWITCHES and WATER_STUB live_proofs; RESTRING_PROVE's A2 wants `live-proof A1:` naming M15f.

## Not done
The 23 scenes in `scenes.json` are not built, deliberately: authored blind they would be harness I can't run. Build them with the game up, starting with those that show a north-star line and aren't already a proof row. Showcases `workshop_floor` / `yard_of_masts` too.

## Next, with the game
1. Deploy (dry run, then --apply), modset `gimmesomeslack`, launch, `proof_all.py --live`. Read the first exception first. Likely suspects: S10/S9 rows if the styled-winner force write stores too much; M1c if a Modern default loses boxes.
2. Look at play zoom, Modern: T, +, blob, strip beside a wall, adjacent junctions. Does the plug really lie over the strip? Is the spare black plug acceptable? Does the skew read loose or broken? LEDs flip when power is cut?
3. Look at Industrial/Scrapper/Futuristic blobs (they changed) against the old look.
4. `shapetable` over a real room next to a shot: does 0.3 match what the eye calls a repeat?
5. Screenshots for all eleven north-star lines, in a real colony, for DONE.md.
