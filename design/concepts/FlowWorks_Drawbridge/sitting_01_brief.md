# Drawbridge: what a human must see before Relentless may call it done

For Mandrake, through the Conductor. Items: `DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED`, `DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS`, and the two your 2026-11-03 look exposed, `DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` and `DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE`. The list of what the bridge does and does not do is in `D:\Luke\dev\RimMandrake\design\concepts\FlowWorks_Drawbridge\sheet.md`.

## My position

**Claim.** The drawbridge can pass its 14 mechanical proof rows and still fail you. None of those rows could have caught what you saw, because none looks at a picture or clicks a button (`drawbridge_proof.py` holds no screenshot or capture at all). The bridges staged for your look were made by debug calls and raised instantly, with no colonist and no swing. So the test has to start where you started: a player, a mouse, a colonist, at normal zoom.

**Attack.** The hardest case may be impossible. When a leaf runs north from its hinge, it stands between the camera and the gap. The offline sweep for the v3 mockups (still in progress) finds only 26 to 41% of a 4-cell gap showing open at 75 to 85 degrees. Any lower and the leaf covers more of the gap, and at 90 it is the vertical bar you refused.

**Picture.** If the claim wins: you open a save, drag a bridge, and every picture and button behaves as you expect the first time. If the attack wins: a north-running raised bridge still reads as down after every art round, and the choice comes back to you with the real pictures. I hold that the test should run anyway: the gap is not the only cue, because the gantry, the hauling lines and the shut gate also say "up". The check below decides it, and no art round may loosen it.

## What gets tested

Three kinds of proof:
- **Math**: an offline check, no game.
- **Cold reader**: an agent that made nothing sees real game captures, shuffled and uncaptioned.
- **Your look**: you in the game on a numbered review save.

The numbers are my proposals. Bars run on a real drag-built bridge wherever the proof touches the game. Each visual check first runs on what you already rejected in today's build (the east-west pole, the north-running raised leaf, the silent click, the stretching swing). It must fail those, or the check is blind.

| # | The situation | What good looks like | The cheap fake it must catch | Proof |
|---|---|---|---|---|
| 1 | Up or down: one glance at normal zoom, all 4 directions, timber and steel | Cold readers point to the leaf and say whether it is up or down, correct on all 16 pictures, with the gate hidden from the question so a shut gate can't give the answer away. The readout matches the picture at every moment | Looks fine zoomed in or on a cleared test site. Or the readout says "raised" while the deck still draws | Cold reader (two readers, Claude and GPT), then your look |
| 2 | Finding a raised bridge: lived-in base, plants and clutter left in, position not given | The reader marks the right squares. You don't hunt for it | Passes only on a scrubbed map, as the staged look was (528 plants removed) | Cold reader, then your look |
| 3 | Which bank: bases with a clear home side, facing each of the 4 ways | Hinge, winch and gate land on the home side. The drag preview shows it before the commit, and it can be flipped | Right for the one test site only, or shown only after building | Math for the pick, your look for the preview |
| 4 | The gate: a colonist walks through, and the gate is seen raised, lowered and locked | It reads as a doorway. The colonist passes under the lintel, not over it. It stays shut while the leaf is up. The north-running panel isn't a jumble (v2's blind reader called it congested) | A pretty still with the colonist drawn on top of the frame | Cold reader on captures, then your look |
| 5 | The lines: raised, and at each stage of the swing, in each material | Lines stay attached from leaf to winch side and don't cross the gap (the Conductor's reading of your words; say if wrong). No stiff rope in the air (your 2026-10-23 picture). Rope on timber, cable or chain on steel | Lines correct raised, but they pop or detach mid-swing | Math for attachment points, cold reader for the look |
| 6 | The click: raise or lower while paused, with a colonist 50 cells away, with steel unpowered, and with nobody able to reach it | An immediate message saying what happens next. The button shows the order is waiting, and can cancel it. A steel leaf with no power says so at the click, not later | A message that appears but a button that looks the same; or a click that works only when a colonist stands beside the winch | Live state read, then your look |
| 7 | The whole order: a bridge built by colonists from one drag, not by debug call; raise and lower both, timber and steel | A real colonist walks over and works it, and the leaf moves. This is the job your look never saw finish | Done with `ProofMakeDrawbridge` and `ProofOrder`; or the job is taken but the picture does not move | Live, no debug calls after the map starts |
| 8 | The swing: all 4 directions, down to up and back, at normal speed; stopped midway and reversed; steel losing power midway | The hinge never moves. The same planks stay visible all the way. No pop at either end, and it joins the lowered deck exactly. A stopped leaf holds its pose and reverses from it. The gate never clips through the leaf | Today's code: the deck vanishes on the first step and a scaled picture grows from nothing. Or a smooth start and a jump at the end | Math for hinge and joins; cold reader on a filmstrip for shape only. Agents can't judge how it feels at speed, so frames captured at game speed are played back to catch breakage, and **your look decides** |
| 9 | Sizes: shortest and longest leaf in each material, widths 1 to 4, a two-leaf bridge | Same plank size at every length. A 4-wide leaf reads as one leaf, not four strips. The longest one still fits the gate and the screen | One 4-cell timber leaf looks great, and steel at 8 is that art stretched (the art contract says exactly that today) | Math for plank size, cold reader for the look |
| 10 | Timber or steel: side by side, lowered, raised, moving | Told apart at normal zoom in every state | Steel lowered still draws brown (`DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER`) | Cold reader |
| 11 | One real sitting, on a save you could really play: drag, build, raid approaches, raise, save mid-swing, reload, lower, then again on another direction | The reload shows the same pose. Anyone on the leaf is moved off it once, not again after the reload. Nothing above fails on the second pass | Each check passes alone, and the sequence breaks | Live, then your look |

**Never, anywhere:** a leaf straight up or a thin bar · anything stretched · a line across the open gap (same reading).

**Must stay green, and proves none of the above:** the 14 existing rows in `drawbridge_proof.py` (tipping, locking, freezing, crashing, raids, reload).

**Tools that don't exist yet (Relentless builds them first):**
- A way to hold a leaf at a chosen stage of the swing, paused, and capture it at true normal zoom.
- A measure of what normal zoom is on your screen. The mockups' 22.5 px per cell is an estimate.

**Stopping rule.** Agents run checks 1 to 11 without you, and no drawbridge look reaches you until they pass. You then get one numbered save, and your word closes checks 1, 2, 4, 8 and 11. If you reject something an agent passed, that rejection becomes a new line in the agents' checklist.

## One question

**Two-leaf bridges: the winch on the far bank.** A bridge longer than one leaf allows has two leaves, hinged on opposite banks. Today that puts one winch on the far side. On 2026-10-25 you said by card "Yes, far-bank winch is fine". Today you said "You would never have a winch on the "enemy" side".

- *(a)* Keep two-leaf bridges, and the far winch is the one exception. You'd see a second winch out on the enemy side, exposed.
- *(b)* No two-leaf bridges. The drag refuses anything longer than one leaf (timber 4, steel 8 by default; the Mod Settings sliders reach 8 and 14).
- *(c)* Two-leaf only where both banks are yours, such as an inner moat.

My pick is **(b)**. It keeps your rule without an exception and removes the sizes that cost the most art. It does shrink what a bridge can span.

## Picked for you, say so to undo

- **A raid is coming and you click Raise.** It stays an ordinary colonist job, like a vanilla switch, and the wait is shown clearly (check 6). I found no way today to send a drafted colonist to it. If waiting feels wrong in play, that is the next change.
- **Stretching.** A leaf is one rigid thing turning on its hinge, and the planks stay the same planks. On screen it will look shorter as it tips toward you, as any board does. If that reads as stretching on the v3 motion page, it goes to the 4 to 10 steps you offered. Your look decides (check 8).

## Pre-review

A reader who did not write this (GPT, `consult-20261103-151313-1729414`) struck two of three questions as ones your words already cover or a demonstration should settle; they are now picks above. It also caught a check a shut gate could fool (fixed in row 1), a motion check agents could not actually judge (fixed in row 8), and overstated causes (removed). Not yet run against a tree: core line `two_leaf_bank` is still open.
