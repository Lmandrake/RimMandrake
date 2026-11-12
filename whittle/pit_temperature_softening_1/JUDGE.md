# PIT_TEMPERATURE_SOFTENING_1: judge's verdict (2026-11-12, fresh eyes, from the evidence files only)

Method: I read STATEMENT.md, NOTES.md and the owner's spec lines in the item file. I re-ran HEAD's pure `verdicts()` from
`src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py` offline on the recorded results for runs 10, 13, 14, 15, 17 and 18.
The output is in `D:\ClaudeWork\rimmandrake\judge_pit\rejudge.txt`. I viewed `run18_a6_panels.jpg` and `run18_site_*.jpg`.
I did not drive the game. The pit code was last changed in `aa599da2d0` (03:03), before runs 17 and 18, so those two runs
tested the pit code that is at HEAD now.

## Lines

- **A1: true.** Run 18's `PEX_A1_defs_resolve` row reads PASS, with found `[RM_ExposedPrisoner, RM_PitExposure]` and
  notFound `[]`. The load was a 12-mod list (Harmony, the core game and DLCs, the bridge, a camera mod, GimmeSomeSlack,
  FlowWorks, Patches), which is the minimal FlowWorks tier.
- **A2: true.** In run 18 (Desert, outdoors at 45.5 C at 12:00) the open pit stayed within 0.06 C of outdoors at every
  hourly sample. It rose 6.95 C from 06:00 to noon. The roofed twin rose 0.16 C and trailed outdoors by up to 4.95 C. Both
  pits were dry and dug the full 8 notches. The same holds in runs 10, 13, 14 (AridShrubland, 36 C), 15 and 17: the open
  pit's largest lag was 0.06 to 0.10 C and the roofed pit's was 4.57 to 5.5 C. HEAD's verdicts() gives PASS on every one.
- **A3: true.** In run 18, wardens worked all three prisoners with ReduceResistance, two chats each, and the drop is counted
  from placement at 00:00. Over 00:00 to 15:00 resistance fell 9.56 in the pit (13.0 to 3.44), 1.53 in the roofed twin and
  2.10 in the normal cell. The pit prisoner was hurting from 06:00 onward. Run 17 agrees: the pit fell 7.64, against 0.57 and
  0.59 for the others, even though the pit prisoner got fewer chats (1 against 2). The unwardened runs show the pit's own
  loss with no chats at all: 2.7 against 0 (run 13), 0.85 against 0 (run 14) and 4.5 against 0 (run 10). Runs 15 and 16
  correctly read UNMEASURED under the fixed verdicts, because they had no reading at placement. The pit prisoner's safe
  maximum is 46 C at placement and 38 C later. That drop is the mod's exposure effect, not an unequal setup.
- **A4: true.** At 12:00 in run 18, the Charity_Essential colonist (Manuel) has `RM_ExposedPrisoner -3 "Cambarseacha left
  exposed in a pit"`. The psychopath of the same ideoligion (Montoya) does not have it, and neither does the colonist whose
  ideoligion has no Charity precept (Thib). The A6 panel shows the same thing on the Needs tabs. The result repeats across
  seven runs. This matches the spec's "copy the beggar-rejection structure".
- **A5: true** for the build that was tested. On the 12-mod list, `run18_toggle_pit_exposure_flowworks_tier.json` reads GREEN
  (pit_exposure_on and pit_exposure_off both PASS, run_validity CLEAN, assembly_matches 1). The chain's read of the driver
  rows (`run18_pit_exposure_chain_reads_driver_rows.json`) has A1 to A4 all PASS at mod hash ccef5b84 / DLL 8286201b.
  The FlowWorks DLL has changed since then (HEAD's DLL hashes to 65277837). The only change is `CompHoseReel.cs` in
  `0bedc0e76e`, which belongs to another item, and no pit code changed. Until the driver runs again at the current hash, the
  `pit_exposure` chain at HEAD will read "UNMEASURED: live check owed". That is a re-read the pipeline owes, not a pit defect.
- **A6: cannot tell.** This is the owner's judgment, and NOTES.md has no words of his on it. `run18_a6_panels.jpg` is a
  readable panel to put in front of him. It shows -3 next to Uncomfortable -3, Hot -8 and Depressive -12. It also shows the
  pit prisoner's Prisoner tab (resistance 4.9) and the inspect line "Held in a pit: it cannot climb out without a ladder."
  His ruling on the number settles this line. He should be told two things alongside the panel. First, the thought stacks one
  per prisoner (`broaden_stacking_after_fix_five_memories.json`: five prisoners give -15). Second, the spec says the numbers
  go to him as a proposal.

## Where the evidence is staged or flattering

- The site is set up on purpose, and the docstring declares it. The tile's mean temperature is forced to 28 C, the clock jumps
  to midsummer, and each run is one hot desert day (outdoors 36 to 50 C). Nothing here shows a mild season or a cold night.
  Run 1 (mild spring, no heat) is the only counterweight in the evidence folder.
- The psychopath trait is added by the harness in every run. A Charity precept was added in run 17. Run 18's Charity_Essential
  ideoligion was already there. Each run has only one compassionate colonist.
- The run 18 site picture shows a real defect. A colonist (Thib) is stuck inside the roofed pit B next to its prisoner, and
  the pocket reads trapped=False. It is filed as RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE and is outside
  this item's scope. He could have affected PB's numbers in run 18. Run 17 gives the same A3 result, so the verdict does not
  depend on run 18 alone. The owner will see him in the picture, so he should be told what it is.
- The images are stills. A2 and A3 rest on the hourly samples in the result JSONs, not on the pictures.

would show: yes
