# BROADEN: PIT_TEMPERATURE_SOFTENING_1

2026-11-12, CLAUDE_ARCHMAGI_FWLIVE. Second model: GPT (`gpt_consult.py`, gpt-6.1-sol), given the statement, the two source
files (`RM_PitExposure.cs`, `RM_PitExposureMath.cs`) and what had been tested. Question and full answer are kept at
`D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_FWLIVE\broaden\question.md` and `answer.md`; the essentials
are below.

## The question (short form)
What would real players try that I have not tested (someone new, someone experienced, someone trying to break it, a
messy real game)? Rank 6-10 scenarios by how likely they are to expose a real defect, each with the one observation
that shows it working or broken. Tested so far: an open 4 m pit vs a roofed twin vs a walled prison cell, one prisoner
each, Charity / Psychopath / no-Charity colonists, a hot day sampled hourly.

## The answer (GPT's ten scenarios, ranked by GPT)
1. **Several prisoners in one pit for days**: does each prisoner add a memory (stackLimit 5), and does it expire one day
   after the last refresh? The owner should judge A6 on the stacked penalty.
2. Mod settings changed mid-game (narrowing 8 -> 0 -> 15, resistance x0/x2, exposure off/on).
3. A new player's whole route: capture a downed raider, wardens feed and chat, recruit to zero resistance.
4. **A mostly roofed pit (1 hole of 25)**: the coupling postfix branch, which a fully open pit never reaches.
5. Cold nights; clothed vs naked vs gene-tolerant prisoners: is each deduction that pawn's own hurt?
6. Caravan, hospital, save/load: the marker's lifecycle.
7. Every interaction mode, and an unwaveringly loyal prisoner.
8. Workers, slaves and guests on the pit floor.
9. Ideoligion changes mid-game (Charity Worthwhile/Important/Essential, conversion).
10. No Ideology installed: `FeelsForExposedPrisoners` returns true when Ideology is inactive.

## What I tried and what I found
**Scenario 1 (most revealing) found a real defect, now fixed.** Six prisoners in one open pit; the Charity colonist read
after one hour.
- Before the fix: ONE `RM_ExposedPrisoner` memory, -3 total
  (`evidence/broaden_stacking_before_fix_one_memory.json`). Cause, read in vanilla 1.6 source:
  `Thought_Memory.GroupsWith` puts memories about different pawns in one group when their labels match, and
  `MemoryThoughtHandler.TryGainMemory` then trims each group to `stackLimitForSameOtherPawn` (1). The fixed label
  "prisoner left exposed in a pit" therefore collapsed every prisoner into one memory, against the def's intent (one
  per prisoner, `stackLimit` 5).
- Fix (`dc5b4685e4c9`): the label names the prisoner, `{0} left exposed in a pit`, as vanilla's per-pawn memories do
  ("{0} died").
- After the fix: FIVE memories, one per prisoner up to the cap, -3 each, named ("Oyster left exposed in a pit", "Duck
  left exposed in a pit", ...), -15 in all; each is its own group, so vanilla's stacked-effect discount does not apply.
  After the pit was roofed (prisoners still in it), all five were still present 6 h later, as a 1-day memory should be
  (`evidence/broaden_stacking_after_fix_five_memories.json`).
- What this means for A6: one exposed prisoner costs a compassionate colonist -3; five or more cost -15. That is the
  number the owner judges.
- Side observation: an earlier attempt removed the prisoners with `vanish` (destroy), and the memories disappeared within
  5 h. Vanilla drops memories about destroyed pawns, so that test measured the harness, not the mod.

**Scenario 4: the coupling postfix works in a partly roofed pit.** A 5x5 pit with one roof hole (4 % open, under
vanilla's 25 % outdoor rule) at a hot noon. Its per-250-tick approach rate to outdoors is k = 0.018 at
`pitTemperatureCoupling` 1 and k = 0.031 at 3, alternated 1, 3, 1, 3 with the same result each time
(`evidence/broaden_partial_roof_coupling.json`, script `evidence/broaden_exp.py`). Only the open-roof share of the
exchange is multiplied, so the whole rate rises about 1.7x, not 3x. (The stacking half of that file ran on a planet
with no Charity ideoligion and read 0 memories, as it should; it is not the stacking evidence.)

**Also found during the main runs (before BROADEN), now handled:**
- Overnight rain filled the open pit to the brim (4 m) and the prisoner swam out: filed as
  `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT` (about 0.5 m an hour; real heavy rain is 10-50 mm an hour).
  The proof now locks a clear sky (a desert noon) and calls a wet or shallow pit a SITE fault, never a pass.
- A spring day too mild to hurt left resistance untouched (run 1). That is the design: mild weather costs nothing.

## Not tried, and why
- 2 (settings mid-game): each number is read every 250 ticks (`ApplyNarrowing`). Not run live this round.
- 3 (full capture-to-recruit route): capture-down belongs to other items (`SUPERDEEP_PRISON_ROOM_1`, capture-down); the
  prisoners were placed. Wardening them was tried in the second round, below.
- 5-9: not run. 7's unwaveringly-loyal prisoners did appear in runs 2 and 4 (the inspect pane said so); resistance
  still fell in the pit, as coded.
- 10: moot by standing ruling (every DLC is assumed). A colonist with no ideoligion (a child) does count as caring in
  the code; the proof excludes children.

# Second round (2026-11-12, after the judge's "would show: yes")

## What the first round's proof never tried, found by reading it
Every earlier run left each prisoner on vanilla's default mode, so **no warden ever worked a prisoner**: A3 compared an
unwardened pit against an unwardened cell, which no player does. A player sets "Reduce resistance". If wardens could not
reach a pit prisoner, or their chats did much less to a miserable one (vanilla scales each chat by the prisoner's mood,
0.2x at mood 0), a wardened cell could out-pace the pit and A3 would be false in ordinary use.

Built: `ProofSetInteraction` (the Prisoner tab's choice, vanilla `SetExclusiveInteraction`); `pit_exposure_live.py
--interaction ReduceResistance`, now the suite's run; A3 counted from placement (run 16 showed both cell chats landing
before the first 06:00 sample, which made the cell look untouched); A3 is UNMEASURED unless all three prisoners were
chatted and the pit prisoner no more often than the others (code review found an extra chat alone could beat the margin).

Result, three fresh desert maps: run 18 (HEAD's DLL) pit 13.0 -> 3.4, roofed twin 12.0 -> 10.5, walled cell 17.0 ->
14.9 by 15:00, two chats each; run 17 pit 11.0 -> 3.4, cell 11.0 -> 10.4; run 15 to 22:00 pit 9.7 -> 1.2, cell and twin
about -0.5 each (run 15 re-judges UNMEASURED under the stricter gate: it has no placement read). The pit prisoner's
Prisoner tab reads "Reduce resistance only" and a colonist's inspect line reads "Reducing resistance of Peza"
(`evidence/run17_a6_panels.jpg`). So with wardens on, the pit is several times faster; A3 holds in ordinary use.

**Found on the way, filed (not this item):** in run 18 a colonist, Thib, ended up inside the roofed twin pit. Ordered out,
he moved 0 cells, yet the pocket grid reads him `trapped=False`, so no rescue queues
(`RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE`, evidence `evidence/run18_colonist_stranded_in_roofed_pit.json`).

## The question to the second model
GPT (`gpt_consult.py`, gpt-6.1-sol), given the statement, the two source files and everything above. The question and
full answer: `D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_FWLIVE\broaden2\question.md` and `answer.md`.
In short: "what would a real player try that I still have not, that could show A2-A4 false in ordinary use, or misbehave
in a way the owner would hate? Rank the 5 most revealing, each with one observation and its cost."

## The answer (GPT's five, ranked)
1. A warden feeding a downed pit prisoner from the lip (food delivery, not chat).
2. Roof the pit over a prisoner who already has heatstroke: the pit's resistance loss must stop at once, though the hole
   stays hot.
3. A prisoner protected well enough (clothes, mild weather) that nothing hurts: resistance must stay flat.
4. The thought's expiry after exposure ends: about one day after the last refresh, not sooner, not never.
5. A mostly-roofed pit room over 400 cells: the coupling multiplier is skipped above 400 cells (a scope limit).

## What I tried and found
**2 and 4 together** (the commonest player reaction to a roasting prisoner is to roof the hole): the run 18 noon save,
the open pit roofed 1 h after noon, sampled for 25 game hours (`evidence/broaden2_roof_the_pit_at_noon.json`, script
`evidence/broaden2_roof_exp.py`).
- Open: resistance 4.94 -> 4.44 in the hour before the roof.
- Roof on (12:46): `exposed` False at once, the exposure marker gone within 250 ticks, and **resistance flat at 4.44
  for 17 hours** while the roofed hole stayed 40-47 C and heatstroke rose to 0.363. The only later loss (4.44 -> 4.22,
  next morning) is a warden's chat, the marker off throughout. So the pit's own loss is the exposure, not the heat.
- Manuel's "Cambarseacha left exposed in a pit -3" stays all night and **expires between 12:16 and 12:46 the next day**:
  one day after the roof, as the def says.
- Side observation, vanilla: heatstroke held at 0.363 overnight in the 40 C roofed hole; vanilla heals it only below the
  pawn's comfortable maximum, not merely the safe one. Not a mod defect.

**3** was shown in the first round (run 1: a mild spring desert, nobody hurt, no resistance lost).

## Not tried, and why
- 1 (feeding from the lip): `RM_PitPrisonCare` belongs to `SUPERDEEP_PRISON_ROOM_1`, not this item's statement.
- 5 (rooms over 400 cells): the bound is the coupling's own (`RM_PitExposure`), a scope limit of the provisional
  multiplier; A2's open pit is a fully unroofed room, which vanilla already treats as outdoors.
