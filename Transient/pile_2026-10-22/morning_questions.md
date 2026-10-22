# FlowWorks — morning questions from the night fixer (2026-10-22)

Each question comes from the live helper's joints study (`D:\Luke\dev\RimMandrake\Transient\pile_2026-10-22\joints_study.md`,
pictures in `D:\Luke\dev\RimMandrake\Transient\pile_2026-10-22\joints\`; Transient is untracked, so the files are in the BENCH clone
`/home/mandrake/rm/bench/Transient/pile_2026-10-22/`). Each one needs your taste or a ruling. Everything that did not need you
was fixed tonight (list at the end).

## Q1. Which way should a hose leave its reel? (D2)

**What you see:** every hose leaves the reel on its WEST side. When the target is east, north or south, the hose runs
straight out west for about 1.6 squares and then makes a U-turn round the reel. This is the "it leaves the reel and loops
round" you saw on 10-21; tonight's port fix only fixed the far end. It also makes two scenario lays fail ("no room for the
straight lead-out") where something stands west of the reel.
Pictures: `joints\sheet_H1.jpg`, `joints\sheet_H3.jpg`, `joints\jg_fac_scrapper.png`.

- **A. The player turns the reel** (rotatable, 4 facings; the outlet, the nozzle and the picture turn with it; east is the
  west picture mirrored). The player decides, and the build preview shows which side the hose leaves from. Costs: the
  north/south facings need either new reel pictures or a rotated top-down view.
- **B. The reel picks the side at lay time:** the outlet moves to the side facing the target (mirrored picture for east).
  Nothing for the player to do, but the reel's picture flips when a hose is laid.
- **C. Keep one outlet, drop the straight lead-out rule** so the hose bends away at once (no U-turn, but it still starts
  out of the west side).

*Night fixer's lean:* **A** (it is the player's tool; a rotate key is the RimWorld way). Nothing built until you pick.

## Q2. Pipe and hose joints: fittings art and where a pipe meets a tank (D3, D4, D8)

**What you see:** no joint anywhere has a fitting. `joinFittings` is OFF "until the owner rules on the art", and its pictures
(`Joins/<Look>/{Flange, Coupler, Saddle}`, 3 pieces x 4 looks) were never made. Also, a pipe can only reach a 2x2 tank at
the middle of a square (z + 0.5 or z + 1.5), while the tank's flange, where a hose now ends, sits at mid-height (z + 1.0): the
pipe slides in under the tank's skid on the bottom row, so pipe and hose meet the same tank at different heights.
Pictures: `joints\sheet_B.jpg`, `joints\jg_B_modern.png`, `joints\sheet_C.jpg`, `joints\sheet_H2.jpg`.

- **A. Make the 12 fitting pictures (flange about 0.13 square, union 0.12, hose ferrule 0.24, one set per look), show them
  to you on a review sheet, then turn `joinFittings` on.** The pipe-into-tank arm also gets a short riser so it ends on the
  flange, not under the skid.
- **B. Move the tank's ports instead:** a low manifold on both rows of each 2x2 tank picture, so a pipe on either row
  meets a drawn inlet (a tank art change, 4 looks x 3 sizes).
- **C. Leave the joints bare for 1.0.**

*Night fixer's lean:* **A**. I did not start the art: cosmetic changes need your OK first.

## Q3. The "liquid tap" is not a tap (D6)

**What it is:** `RM_LiquidTap` is a hand-bled well hammered into the ground over a surveyed liquid. It is not on the pipe
network and has no spout. Scenario C7 stages "a fountain line: three taps off a pipe" and says colonists drink from taps,
which a player would read the same way. Picture: `joints\sheet_E.jpg`.

- **A. Rename it** ("bleed well" or "ground tap") and change C7's text to match. Small, honest, no new mechanics.
- **B. Build a real pipe-fed faucet** (a fitting on a pipe that colonists drink from or fill bottles at) and keep "tap" for that.
- **C. Both:** rename the well, and add the faucet as new work.

*Night fixer's lean:* **C**, with the rename now and the faucet filed as work.

## Q4. The default Scrapper hose is brown on brown ground (D7)

**What you see:** the empty (flat) Scrapper hose is about the same brightness as desert soil, so at play zoom it nearly
disappears whatever its width. Tonight's plump fix (Q-free, below) makes a FULL hose read clearly; the empty one is still
low-contrast. Picture: `joints\sheet_girth_pawn.jpg` (top).

- **A. Lighten the Scrapper flat strand's highlight and add a thin dark edge line** (a light edit of the existing picture).
- **B. Strengthen the contact shadow every hose already draws** (`Strand_Shadow`, today at 55 % opacity and the hose's
  width): darker and a little wider for an empty hose. One number in code, all four looks, no picture touched.
- **C. Leave it** (Scrapper is meant to look like scrap).

*Night fixer's lean:* **B**, then A only if it still disappears.

## Q5. Art polish: pipe crossings, couplings, end caps, pump looks (D9, D10, D11)

- D9: where pipes branch (T and cross), the centre is a small token, and Modern and Futuristic have many coupling bands
  close together, so a run can read as a ladder or a cable (`joints\sheet_A.jpg`).
- D10: the pump has one picture (the scrap pump) in every look, so it sits oddly on red Modern or pale Futuristic pipe
  (`joints\sheet_C.jpg`).
- D11: end caps differ between looks: dark knobs in Scrapper/Industrial, tiny ticks in Modern/Futuristic (`joints\sheet_A.jpg`).
- UI: an unpowered pump's no-power lightning bolt (vanilla) sits over the flange cross and hides where the pipe joins.

Question: **may I draft these as a review sheet** (real 3- and 4-way fittings, one coupling per joint, a matched end cap
per look, three more pump looks), for you to keep or cut? Nothing would be installed without your picks.

## Fixed tonight without needing you (for reference)

- Reach map ghost road (REACH_WINCH_SITE): a new wall reached the wall-aware reach map only when some pawn asked for a
  path, so on a quiet map "can reach" said yes through it. Now seen at once. `3810af4e5f`
- Hose strands tile without a seam (base and Modern plump). `27586425d9`
- A dig order deeper than colonists may dig no longer vanishes when "Machines dig deeper" is off: it waits, the alert says
  why, and the right-click and placement text name the switch. `9aef556eff`
- A full (plump) hose now draws wider than an empty one in every look; Modern's sat off the hose centre. `5ebfd259b2`
- A pipe pole's span draws that look's own pipe instead of a power wire, and a ground pipe beside a pole runs its arm to the
  pole instead of stopping short. The pole picture itself is still the stand-in mast. `d5481252ae`
- A hose aimed at a tank, pump or machine now ends on its nearest free side instead of "target blocked". `ba1c8d16ab`
- Scenario signs and the scenario design said pipes and hoses were "being redrawn" (false since tonight). `cda3b0f940`
