<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **L1 (L4):** zersium's home biome is The Forge (ruled 2026-10-09) | evidence: `whittle/ship_alloy_forge_1/evidence/offline_proof.txt`
- true: **L2 (L0):** `RSW_Zersium` exists with a canon description and the confirmed source; steel + zersium makes `RSW_Durasteel` on the confirmed building | evidence: `whittle/ship_alloy_forge_1/evidence/offline_proof.txt`
- true: **L3 (L0):** the alloy forge's plasteel recipe is the only fabricated plasteel route and unlocks after the durasteel one | evidence: `whittle/ship_alloy_forge_1/evidence/offline_proof.txt`
- true: **L4 (L0):** settings toggles exist and default to the shipped behaviour | evidence: `whittle/ship_alloy_forge_1/evidence/settings_toggles.txt`
- unseen: **L5 (L1):** a minimal-list load shows the forge's recipes gated as specified, with no config errors | evidence: none. My lane (offline) can't load a game, and SteveDesktop has no VFE Factory installed. The rows that will show it are ready in `src/RimMandrake/WreckedMachines/validation.py` (`alloy_forge_gated`, the two forge setting drives) and `src/RimStarWars/Armoury/validation.py` (`alloy_forge_durasteel`). The live step is noted on the item, which now reads needs=bridge.

## What I fixed this round (published e08969370e)
- The "early" forge cost 4 advanced components, and those need plasteel plus AdvancedFabrication, the late gate
  itself. With the gate on it now costs 460 steel + 18 industrial components, set at startup.
- The forge's two research projects sat alone on the Main tab, away from the smelter restoration they follow (Workshop
  tab). Both moved to the Workshop tab.
- Turning plasteel off and on put it ahead of durasteel. It now goes back before its loaded neighbour, which holds in
  either startup order of the two mods.
- The live proof chain gained rows for the cost, for durasteel being the first recipe, and for the research tab. The
  code review's false-fail paths are closed (unreadable reads UNMEASURED; a session with the gate off says so).

## What I'm least sure about
- L1's level is L4, an owner-level look. The build matches his card ruling (The Forge is the only placement), but a
  verdict at his level is his, not mine.
- The census in L3 reads the DefDump capture from 2026-11-06 (317 mods, Archmagi). That load predates this round,
  but this round added no producer. The patched-forge view in the same proof is built from current source on VFE
  Factory's real defs, and its process order matches the capture's.
- The forge cost is PROVISIONAL (18 industrial components is a straight swap, not a calibration), like the research
  costs and the durasteel ratio already flagged on the item.
- The DLL was built on SteveDesktop against VFE Factory's assembly copied from Archmagi. It is the same workshop item,
  but the copy is not a Steam install.

## What I did not test
- Any running game: whether PipeSystem's bill menu enforces `ProcessDef.researchPrerequisites` (plasteel before its
  research), hopper-fed production, a save and reload mid-batch, toggles during play, and Player.log config errors.
  All of that is L5's live run.
- The deck-plan placement of the forge in the ship (spec point 4). It is not a statement bullet.
