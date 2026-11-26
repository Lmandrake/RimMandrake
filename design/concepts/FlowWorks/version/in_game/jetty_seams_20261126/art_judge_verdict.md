# Blind art judge verdict: FlowWorks jetty seams (16 jetties)

- Date: 2026-11-26
- Judge model: claude-opus-5-5 (blind; did not make the work)
- Brief: design/RimMandrake/art_judge_brief.md@9ad7d729e5; standing_rulings.md §The judge refuses flaws, not polish
- Clone HEAD at judging: 73416d51c1
- Pictures used:
  - design/concepts/FlowWorks/version/in_game/jetty_seams_20261126/sheet_16_after.jpg (build under judgment)
  - design/concepts/FlowWorks/version/in_game/jetty_seams_20261126/sheet_16_before.jpg (comparison only)
  - Transient/jetty_seams_v3/jetty_{steel,heavy}_{E2,N2}_{Scrapper,Industrial,Modern,Futuristic}.png (native, after)
  - Transient/jetty_seams_v2/ same names (native, before)
  - Crops by this judge: Transient/judge_crops/ (nat_E_steel.png, nat_E_heavy.png, nat_N_steel.png,
    nat_N_heavy.png, joint_E.png, joint_N.png, before_E.png, modernN_ba.png)

## The promise judged

Owner, 2026-11-25: "Station 78/79 jetty's still look like two blocks stuck together rather than a seamless whole, FIX."
Owner, 2026-11-22: "Both of them need cables shown to connect their support on the ledge to the end of the jetty."

## Method

1. Located each jetty in its native capture by RGB normalised cross-correlation against the sheet tile (match
   0.96-0.995 for all 16; the same screen position in every file).
2. Looked at each deck at 3x and at the joint at 5x (nearest-neighbour).
3. Measured a line detector along each deck: the second difference of the mean brightness across the deck, at the
   joint (deck middle) and everywhere else.
   - Sanity check that the detector can see the old seam: on the BEFORE build it fires at the joint on
     heavy N Modern (42.6), heavy N Futuristic (56.2), heavy N Scrapper (22.0) and steel E Industrial (14.1).
   - On the AFTER build, these values at the joint are 0.7, 0.3, 3.8 and 2.1. The median of the deck is 0.2-0.7.
   - On AFTER, a value near the middle stays only where the look draws a repeating pattern: the Futuristic bars or
     panels (about every 28-30 px), the Industrial grid (about every 4-5 px), and the Modern panel joints. Each of
     these values was the same on BEFORE, so they are part of the art, not the joint.
4. Compared the mean brightness of the root half and the tip half. The step is 4 or less on 15 of 16. On steel N
   Industrial it is +7.7, which comes from the bolted plate drawn at the root end, not from a break at the joint.
5. Checked that the top and bottom rails and side frames run through the joint without a gap.

## Verdicts

| Jetty | Verdict | Middle of the deck | Cables, ledge post to end |
|---|---|---|---|
| steel E Scrapper (stn 78/79 look) | KEEP | planks and rails run through; the plank ends are staggered, with no line across the full width | yes, chain from post top to tip corner |
| steel E Industrial | KEEP | one plate from the bolted root to the hazard tip; old faint joint line gone | yes |
| steel E Modern | KEEP | evenly spaced panel joints, dashed centre line runs through, nothing at the joint | yes |
| steel E Futuristic | KEEP | evenly spaced dark bars (pattern), rails run through | yes |
| heavy E Scrapper (stn 78/79 look) | KEEP | planks and plates run through | yes, multiple chains to tip |
| heavy E Industrial | KEEP | grid runs through unbroken | yes |
| heavy E Modern | KEEP | evenly spaced panel joints (about every 37 px); the one near the middle matches the others | yes |
| heavy E Futuristic | KEEP | evenly spaced panel joints (about every 29 px) | yes |
| steel N Scrapper | KEEP | planks run through; old seam gone | yes, chains on both sides to tip corners |
| steel N Industrial | KEEP | one plate; bolted plate only at the root end | yes |
| steel N Modern | KEEP | evenly spaced panel joints, dashed line runs through | yes |
| steel N Futuristic | KEEP | evenly spaced bars (pattern) | yes |
| heavy N Scrapper | KEEP | old cross-deck seam (22.0) gone (3.8) | yes |
| heavy N Industrial | KEEP | grid runs through unbroken | yes |
| heavy N Modern | KEEP | old seam line gone (42.6 to 0.7); the panel lines left are thin and of equal weight | yes |
| heavy N Futuristic | KEEP | old seam line gone (56.2 to 0.3); the panel joints are even | yes |

16 KEEP, 0 REDO. No flaw was refused, so no fix was made in this run.

## Polish (blocks nothing, files no ticket)

- polish: heavy N Modern. The panel lines are spaced unevenly (about 23 px, then 37 px at native size). One line
  sits about 7 px past the old joint. It has the same weight as the other panel lines and reads as plating, not as
  a block edge. Even spacing would remove the last hint.
- polish: steel N Industrial. The bolted root plate makes the root half about 8 levels darker than the tip half. This
  is the look's design, not a seam.
