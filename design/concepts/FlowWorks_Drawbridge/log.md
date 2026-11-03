# FlowWorks drawbridge: Designer log

## Sitting 1, 2026-11-03

Trigger: run-now by the Conductor. "Owner asks: what are the human-perspective expectations we would want to test to ensure this passes a relentless build and validate." Option B already picked.

Scope call: this folder is one feature of FlowWorks, not a mod-level definition, so it is `FlowWorks_Drawbridge`, not `FlowWorks`. `kind: mod` and the gate read `<Mod>`; how a feature-scoped tree enters Relentless is not settled. Stopped at Stage 2: core lines are open, so no tree.

### Stage 0: already built (not up for argument)

- Defs: `RM_DrawbridgeWinch_Timber`, `_Steel`, `RM_DrawbridgeGate`, `RM_WorkDrawbridge`, `RM_WorkDrawbridgeGiver`, raid planks (`src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml`).
- Mechanics in `Source/Pits/Drawbridge/`: leaf record, one drag with winch and gate, sided orders, tip with overflow fall, peace auto-lower and hostile lock, unpowered freeze, winch-lost crash, raid hand-off and planks, gravship, hoses and cords cut by a raised leaf, settings.
- Proof: `northstar/drawbridge_proof.py`, 14 rows. Zero screenshot or capture calls (grep count 0). It proves mechanism only.
- Art: 78 files in `Textures/Things/Building/FlowWorks/Drawbridge/`, all for the upright-leaf contract (design R12), which option B replaces.
- Rulings: `design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md`.

### Stage 0: what the code does today against his 2026-11-03 words (read, not run)

- Stretch: `RM_DrawbridgeArt.DrawLeafUp` (`Source/Pits/Drawbridge/RM_DrawbridgeArt.cs:236-244`) scales the picture's height by `length * rise`. That is the animation, and it stretches. Design R12 line 197 also stretches a steel leaf over 4 cells. Both now break his ruling.
- Pop: a leaf is rigid, so any progress above 0 is raised (`RM_DrawbridgeMath.IsRaised`, `RaisedSquares`). `Building_SuspensionDeck.Print` returns nothing when raised. So the deck vanishes on the first step, and the leaf grows from zero height.
- Friendly bank: `RM_Drawbridges.ColonyEndIsFirst` guesses from the home area, then mean building position, then end A. `Designator_SuspensionBridge.cs:95` calls it. Rotation only picks the winch's lateral side (`:504`, `:517`). No player control found over which bank.
- Urgency: `WorkGiver_Drawbridge`, BasicWorker, priorityInType 110. No float menu or drafted order in `Source/Pits/Drawbridge/` (grep empty).
- Click: Test Pilot 2026-11-03, on `DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD`: order taken, colonist about 50 cells away, game paused, no message, gizmo unchanged, steel unpowered never moves.
- Staged look: `D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE\ask.md` discloses debug-call build, instant raise, dev power, 528 plants removed.
- Geometry (v3 helper, in progress, `...\mockups\v3\_work\sweep.md`, k = 0.5, 4 cells): south-directed candidates 38 to 45 deg, with a 60 to 70 deg edge-on zone refused. North-directed candidates 75 to 85 deg, leaving 26 to 41% of the pit open.
- Not measured: selection when raised. A raised deck square prints nothing yet is still spawned, so clicking the open gap may select an unseen deck, and clicking the drawn leaf may select whatever is under it. Check 6 covers it through "the click"; not run.

### Three ways this could fail him

1. Every row is green and the look is still wrong, again, because no check sees a picture or uses a mouse.
2. It looks right on a 4-cell timber leaf and is ridiculous at other sizes or moving.
3. North-directed raised never reads as up, and art rounds spin with no fallback.

### Contradiction found

Card 2026-10-25 "Two-leaf drawbridge, far-bank winch acceptable? → Yes, far-bank winch is fine", and follow-up "each leaf has its own winch house on its own bank", against 2026-11-03 "You would never have a winch on the "enemy" side". The v3 brief states the second as binding and does not mention two-leaf bridges. Ask 1.

### Asks (askcheck: clear for all three, no tree exists to repeat)

Pre-review (GPT, job consult-20261103-151313-1729414): kept ask 1; struck asks 2 and 3, now delegated on the sheet.

1. Two-leaf far-bank winch: keep as an exception, no two-leaf, or only where both banks are yours. My pick: no two-leaf.
2. STRUCK. Raise during a raid: he asked for a click that responds, not emergency dispatch.
3. STRUCK. Does foreshortening count as stretching: show rigid motion, he judges it.

Answers: none yet.

Leaf limits read from code: defaults timber 4, steel 8; sliders 2 to 8 and 2 to 14 (`RM_DrawbridgeSettings.cs:59-62`). Width to 4 by card 2026-10-25. "Finishing what they were doing first" was cut from the brief: not read from the job scheduling code.

### Trial formats

Short stories at key moments: not used here. The table's situations stood in for them. Note whether he finds the table readable.
