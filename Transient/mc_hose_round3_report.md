# MessyConduit hose reel, round 3 (2026-10-04)

Owner: "Station 12: Wrapping cloth connectors look good! still bad graphics for the hose reel: shows a hose 'end' hanging off the reel even though it's also shown connected to the hose. And the reel should be 2x2, not 1x1, as the shown hose is quite large."

## 1. Dangling hose end
- Cause: not code. `Reel_Deployed.png` (round-2 art, a Codex edit of the stored reel) itself paints a loose hose dropping off
  the drum to a brass nozzle; the game also draws the real laid hose (mesh) leaving the reel, so two ends show.
  The mesh code draws only one free end (`DrawEnds`, at the far cell); the reel-end coupling sits under the reel sprite.
- Fix: new deployed art with no loose end (hose leaves the drum straight down into the base at the centre, where the
  mesh hose now starts); the stored art keeps its tucked nozzle (correct: that is the undeployed free end).
- artpipe search first: only the two round-1 stored-reel jobs (128 px), nothing at 2x2 scale. Both PNGs redrawn at 256 px
  (Codex imagegen edits, validate_sprite PASS, faint-alpha WARN ~0.7%); deployed covers 0.95 of the stored silhouette
  (0.989 of deployed inside stored, so the swap does not jump). Installed via the art ledger (`install_file`, reason
  script:conform_sprite.py), commit bb887728e. Known look risk: the deployed hose ends in a short flat stub below the
  base rail; it reads as going under the machine, but whether it lines up with the drawn hose is a live question.

## 2. Reel 2x2
- Def `Defs\Hose\RM_Hoses.xml`: `<size>(2,2)</size>`, drawSize 1.4 -> 2.3, shadow volume scaled. Not rotatable, so the
  footprint is Position..Position+(1,1). No placeworker or interaction cell exists or is needed (the hose is laid by gizmo).
- `HoseReelRect` (Verse-free, `Source\Hose\HoseMath.cs`): centre, edge cells per side, perimeter, start cell nearest target.
- Hose attach point = the reel CENTRE (`RM_MapComponent_Hoses.Start`), under the sprite, so the hose emerges from beneath it.
- Install check measures from the centre; target on any reel cell = "same cell"; route = centre hop + A* from nearest reel cell.
- Port coupling (round-2 rule) generalised to the footprint: neighbour across any shared edge of the 2x2; tie-break kind,
  side E/N/W/S, lowest cell along the side. Feed drawn from the touching reel edge cell across the shared edge.
  1x1 overloads kept and still answer as round 2.
- Probe: reel found by any of its 4 cells; census adds `footprint`, `start`, `portContact`, `retractReason/Tick`, `retracts`.
- Range ring now drawn from the reel centre.

## 3. Placers updated (7f3a09ec7)
- `validation_hose.py`: maze tank moved (43,96)->(44,96) to share the 2x2 reel's east edge; maze hose maxLength 40 (spiral
  measures 29.9 from the 2x2 centre); M3b now expects a retract "route too long" (a filler wall inside the corridor box
  triggers the 250-tick check), M4 `M4_unreachable_retracts` expects laid false + "no route", M5 re-lays first.
- `human_review.py`: station 15 far end (26,2)->(24,2) (route 29.6 of 30 was too close); a footprint-overlap check added.
- `northstar_matrix/scenes.py` / `design_spec.py` / `placer.py`: hose strip footprint accounted for; overlap check.
- `northstar_matrix/fakegame.py`: reel stand-in models the 2x2 (any-cell lookup, same-cell over 4 cells, distance from
  centre, retract rule, refuses an overlapping reel build). Matrix selftest 53/54 (C2 = pre-existing Transient shots).
- Detail per placement: `D:\Luke\dev\RimMandrake\Transient\mc_reel2x2_placers_notes.md`.

## 4. HOSE_BLOCKED_REROUTE_RETRACT_1
- `HoseMath.CheckReplan` = the install test (so a re-plan can never keep what install would refuse: length enforced) plus
  "a failed lay retracts". Every 250 ticks, when the corridor hash changes or the lay failed: route within length ->
  re-lay (re-route); else `CompHoseReel.Retract(why)`: reel in, NegativeEvent message on the reel, reason saved
  (`rmHoseRetractWhy/Tick`), inspect line "Retracted automatically: ...", and `Alert_HoseRetracted` (right-side alert,
  reels retracted in the last day, clears when re-laid). Never a laid-but-invisible ("ghost") hose.

## 5. Build / selftests / commits
- `winbuild.py MessyConduit`: Build succeeded, 0 warnings/errors (also compiles the peer's dirty Aerial/Core files).
- Hose selftest: 102/102 (81 round 2 + 14 Reel2x2 + 7 Replan).
- DLL: built from a clean local clone at the committed source (the working tree carries the aerial agent's dirty
  Core/ConduitVisuals edits), so the committed .srchash is true. Commits: 5a003c0a4 code, c40ee658a DLL, bb887728e art.
- Not deployed (game holds the DLL): owed `deploy_custom_mods.py --mod MessyConduit --apply` at the next shutdown.

## Unproven live
- Everything: no game/bridge this round, DLL not deployed. Owed: deploy at next shutdown, then `python.exe validation_hose.py
  --maze` + station 12/15/16/22/23 walk.
- Whether the deployed art's hose stub lines up with the mesh hose emerging from under the reel centre.
- The retract alert/message actually showing; the 250-tick re-plan firing on a wall built across a laid hose.
- Thin route margins (helper's own route estimate, not the game's A*): station 23 blocked route 29.1/30, station 15 ~27.6/30.
- run_selftests.py: 174/175, the one failure is `northstar_matrix/selftest.py` C2 (live shots in Transient, pre-existing).
