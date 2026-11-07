# Graffiti: where the last pass got to

Pass 3 was offline: Pyrelands held the game. **Nothing below has run in the game.** Build compiles, kernel fuzz passes (136k cases, including new `social` and climb checks). Those prove the tables and polygons, not the game.

## Built, unproven
- **Option D geometry.** `RM_GraffitiKernel.MarkPieces` cuts a mark at the crease in the wall's plane, maps the face foreshortened and the top 1:1 (`TopRate`), clips to `TopPoly` per cell. `ClimbHeight` 1.2 world cells. Side faces climb to mid-cap only. Offline twin `art_source/wallgeom.py` agreed by eye on granite: straight runs, T junctions, a free end, a door gap. Side marks are bigger scraps, still sideways.
- **Bolder paint.** `bake.py`: alpha, streak floor, wear, `bolder()`. All textures re-baked. Posters lose their paper in `paste_to_paint`, but flyer/wanted/gig still read as square prints: weakest art.
- **Social layer.** `GraffitiSocial.cs`, `JobDrivers_AnswerMark.cs`, tables in the kernel. Pawns read marks in sight in their room; memories and opinions (`ThoughtDefs_Graffiti.xml`), line over the head, social log entry, message. Answers: scrub, cross out, paint back, confront (game's own fight check at base 0.75). Painters choose mockery/tribute/memorial from real opinions and grief. Territory thought, faction insult goodwill, per-painter tag hand and crew colour, click-a-wall inspect. Designator asks who or which faction.
- **Portraits.** `WallPlane.PaintedPortrait` puts the subject's real head in the art's gap. Riskiest code: it renders during mesh building. Materials moved from SpawnSetup to Print because of the loading thread.

## Do first, in order
1. `live_session.py` per CLAUDE.md, bridge held. Read the FIRST exception. Check DefOf binding, especially `GraffitiSocial.T` (private nested) and the Graphic_Random folders.
2. Look at D at 64 ppc in a real colony: crease read, top-of-wall paint "the same paint"? `WallPlane.TopThrough` 0.45 is a guess. No crease hairline was built; add one if the bend doesn't read. Check sigil emblems sit inside frames.
3. Check marks don't draw over pawns/things differently now they reach further up the cell, and a mark on a wall's top vs anything standing north of it.
4. Portraits: does a head appear, right way up, recognisable, in each gap? `gapV`/`gapSize` are unverified guesses. Try after save/load and on a dead subject.
5. Social proof with real pawns: `RM_GraffitiSocialProof.Feud "A|B"`, `.Order "A|RM_Graffiti_Mockery|B"`, `.Ledger ""` (static_call, one `args` string), then let time run. Watch: subject humiliated, friend turns, scrub/cross-out/reply/confront, fight. Natural paths too: a hater's joy job, a death to a memorial, a spree.
6. Re-prove on this build what never ran on it: spree, raid-exit tag, sigil, going over a rival's mark, unease, clean protection, plus territory thought and visitor goodwill.
7. Tune rates: `WantsToPaint` and `AnswerOf` odds, `ReadAgainTicks`, mood sizes, and message spam are all unmeasured. Watch the mood bill in an ordinary colony over days.
8. `first_look_*.png` and `ralph/LOOK.md`, then DONE.md per PROMPT.

## Known left out so far
Accusation answered by a deed, forged Feud Mark, shaming spree as its own break (a spree just favours mockery), raid anger from insults, slave/prisoner defiance marks, god satiation. `patch_defs.py` doesn't know the new marks' DESC; sizes are correct.

## Traps
- The gate matches words in any Bash command, even `cat` of the stage script or a heredoc mentioning it. Use Read and Write for those files.
- New .cs files must be listed in `Source/Graffiti.csproj`; default compile items are off.
- Decomp is at `decomp/rw16/all/RimWorld/` and `/Verse/`.
- Traps from earlier passes: paused shots draw pawns at stale spots (`Settle`); naming dialogs over long advances (`shot` closes them); `load_game_ready` returns early; the service shell needs PATH and `RIMFLOW_SEAT=BENCH`.
- Owner's mod list was left on `graffiti_solo` by pass 2.
