# MessyConduit code round 6

## status
Built offline. NOT deployed (no --apply), NOT run live (main window holds the bridge). Commits below.

## (1) standing lamps
- Why the owner saw nothing: (a) round 5 registered StandingLamp for the build-menu picker but kept it OUT of the run members, and the only gizmo ("Restyle this run") is gated on IsMember -> a lamp had no style button; (b) RestyleRun repainted run members only, so lamps never followed the cable; (c) human_review placed every lamp through jawa/build_batch (no style) -> legacy lamp = vanilla art in every look.
- Build menu: unchanged from round 5 (the 4-look float menu on the lamp's Architect button already exists via ConduitStylePicker; unproven live).
- New gizmo "Restyle this lamp" on any player floor lamp: the 4 looks + "Match its cable run" (`RM_MapComponent_ConduitRuns.RestyleLamp`; probe `clamp:x,z:<Look>|MatchRun`).
- RULE (`ConduitStyles.LampFollowsRun`, stateless, nothing new saved): a lamp is hooked to a run when its power connection (CompPower.connectParent) is a run member, or it stands on/beside a member. On "Restyle this run" every hooked lamp takes the new look if it wore the run's previous look (unstyled run = default look) or has no look (vanilla art). A lamp wearing a DIFFERENT look was styled on purpose and keeps it. A bridge repaints the losing run's lamps by the same rule but never writes an unstyled (older-save) lamp. A lamp is still not a run member (never bridges runs). Switches were already members.
- human_review.py: `lamp_looks` per station; stations 1-4 (their look), 5 (Modern), 7/8 (b-run's look; the after row shows the bridge repainting the loser's lamp), 9 (Industrial), 10 (Scrapper; notice/interact lines added) place lamps by `cplace:StandingLamp:<look>`; station 12 (older save) stays unstyled; station 6 has no floor lamps.
- Probe `cstyles` now lists `lamps` (look, hooked run, runLook, drawnPath, lit) and counters lampsFollowed/lampsKeptOwn/lampRestyles.

## (2) hose length 40
- `HoseMath.DefaultMaxLength = 40` is the one number (settings field init, Scribe default, Reset). Same key `maxLength`; new key `maxLengthDefaults` (0 = file from before round 6). `HoseMath.MigrateMaxLength`: an old file still holding the old shipped 30 becomes 40; any other saved length (the player's) is kept. 5% route margin unchanged.

## (3) relay chaining (design)
- A hose may end at ANOTHER reel (a relay placed in the field). Lay onto any cell of that reel: the hose end is moved to the reel's INTAKE = the outside cell across one of its side edges (not a corner), the walkable one nearest this reel's mouth, and it ends on the shared edge with a brass coupling pointing in (like the pipe/tank feed coupling). The relay lays its own hose onward with its OWN 40-cell cap; each hose is pathed, length-checked, re-routed and retracted exactly as before (nothing shared).
- Connection is derived, never saved: a reel whose laid `far` is an intake cell of another reel feeds it (lowest thing id if two). So saves are unchanged, packing up the relay just leaves a hose end lying there.
- Loops are refused at lay time ("would loop back"), and the flow provider ignores a loop anyway (no latched flow).
- Liquid: FlowWorks pipes/pumps are paper, so there is no real liquid. 'Working' = the connection is accepted, both hoses are laid, the relay's hose reads flow from its feeder (new `relay` flow provider, before the debug one) so the feeder plump => the relay's hose plumps, and the chain is shown connected (coupling on the relay's edge; inspect strings name feeder/relay; probe `relayTo`/`fedBy`).

## (4) draw order
- Cause (code): altitude was already right (hose: Conduits 1.83 + <=0.025; span: PawnState+5 = 9.33). The defect is the RENDER QUEUE: every hose material is Transparent at `StrandQueue + 3` (3003), the span cable and the pole/lamp-mast head overlays are Transparent at the default 3000. Unity draws queue before distance, so the hose was painted after (over) the overhead wires and pole heads whatever its altitude.
- Fix plan: Verse-free `Core/DrawOrder.cs` owns the queues + altitudes; span + top materials get `OverheadQueue` (above hose and tap clamp); production reads it; selftest asserts queue AND altitude order with a can-fail (round-5 queues).

## build/tests
- New selftests `Source/SelfTest/ReviewRound6Checks.cs` (draw order x3 strand queues + vanilla altitude constants + band below next layer + can-fail round-5 queues; length 40 + migration 6/6 + can-fail; 38-cell run fits, 39 refused by the 5% margin, 30 refuses 38; relay intake cells/side/edge point/walled side/RelayOf/loops/chain/ring stop/station geometry A->B->C each within 40, A->C impossible; lamp rule 6/6 + bridge rule + can-fails).
- selftest_messyconduit 606/606; selftest_human_review 24/24; validation_style --offline S0+S0b PASS; run_selftests 176/178 (northstar_matrix C2 live shots + UtinniPatches dump, both pre-existing, listed in every stage report).
- winbuild MessyConduit 0 errors.

## live check written, not run
- `python.exe src\RimMandrake\MessyConduit\validation_hose.py --relay` (RL1-RL9: reels, one hose cannot reach, A onto B and B onto C each relayTo + intake + edge end + own cap, ring refused, flow passes through (provider "relay"), no latch after flow off, chain > one hose, live render queues overhead > hose and span material = overhead).
- Lamps: `cstyles` + `crestyle` + `clamp` probe verbs (no new validation row written for lamps).

## unproven live
- Everything on screen: hose now under span cable and mast heads (queue fix is the theory from code; RL9 reads the queues, not pixels); lamp gizmo + menu; lamps following a restyle/bridge; relay coupling drawn at the edge and the relay hose plumping; settings migration of the owner's saved 30 -> 40; the human_review lamp/relay stations.
- Side effect: span cable/mast heads now render after ALL default-queue transparents (motes, etc.) at their spots; they were already the highest-altitude overhead layer.

## Reading notes
- Screenshot 20261004214227_1.jpg (station 12): the reel's hose crosses the scrap mast's span and is drawn on top of both the span wire and the pole.
- Lamp: ConduitStylePicker registers StandingLamp (menu + getter) but excludes it from `members` -> Restyle gizmo patch (IsMember) never yields on a lamp; RestyleRun's RunOf never reaches a lamp; human_review places lamps as plain StandingLamp (no style) -> legacy lamp = vanilla art. Those three facts are the whole defect.

- lamps, relay, draw order, length: code written; building
- human_review: lamps in style stations 1-5, 7-10 placed styled (lamp_looks -> cplace StandingLamp:<look>); station 12 kept unstyled; new station 42 RELAY REELS at (160,172) region 2. selftest_human_review 24/24 (scope of 'new' limited to 1-12).

## Commits
- 9de0f9200 source, selftests, human_review, validation_hose --relay, this report
- 96d984aca DLL + .srchash from committed source (both on origin/main). Owed: deploy_custom_mods.py --mod MessyConduit --apply at the next shutdown.
