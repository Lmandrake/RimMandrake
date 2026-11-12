# Broaden: SHIP_ALLOY_FORGE_1 (2026-11-11 21:40 -0800)

## The question (to GPT, `gpt_consult.py --codex wsl`, model gpt-6.1-sol)
I gave it the five statement bullets, then what I had tested offline (our patches applied to VFE Factory's real
defs, every ProcessDef field checked against PipeSystem.dll, a census of plasteel/durasteel/zersium producers over a
317-mod DefDump capture, how zersium gets placed) and the three fixes I had made (forge cost, research tab, plasteel
re-enable order). I asked: what would a real player try that I haven't (someone new, someone experienced, someone
trying to break it, a messy save)? Six concrete tests, most revealing first. The full question text is in the
prompt above; the full answer is `whittle/ship_alloy_forge_1/evidence/broaden_gpt_answer.txt`.

## The answer, in short
1. A fresh colony on a minimal list, played through smelter, then forge restoration, then building the forge, then
   hopper-fed durasteel, with no cheats. Look for hidden plasteel dependencies and early resources you can't reach.
2. Attack the plasteel unlock: load the inputs before the late research and try to start a run; finish the research
   with the forge already built and check the menu updates.
3. A newcomer looking for zersium: several Forge maps, then non-Forge maps, then the mine-shaft bills.
4. Interrupt real production: power cuts, an empty hopper, blocked output, save and reload mid-batch.
5. Every setting across restarts, with a batch queued while plasteel is toggled.
6. An established messy save with existing forges and queued processes.

## What I tried and found
- **(1) Hidden dependencies on the early path. Tried offline, found a real one, fixed it.** Before the broaden
  question, the same line of thought had already turned up the main defect. The forge's stock cost includes 4
  advanced components. Every recipe that makes them in the 317-mod capture (`Make_ComponentSpacer`, the Rimefeller
  and GravForge variants, VFE's assembler process) needs 10 plasteel plus `AdvancedFabrication`, which is the same
  late gate plasteel sits behind. So the "durasteel early" forge was really late. Fixed: with the gate on it costs 18
  industrial components.
  I then followed GPT's test 1 the rest of the way. The durasteel process only pulls from factory hoppers and outputs
  to them (`onlyGrabAndOutputToFactoryHoppers`), so I read the hopper, conveyor and factory-floor defs in VFE
  Factory's real XML. All of them need only `VFE_BasicFactories` (after Machining) and steel; the floor is 5 steel.
  The smelter restoration the forge follows already needs that floor. **No hidden late dependency.**
  Also found on this path: the forge's research sat alone on the Main tab while the smelter restoration before it was
  on the Workshop tab. Fixed.
- **(3) Zersium for a newcomer. Checked offline, holds.** It is placed only by `RUT_ZersiumForgeLumps`, gated on
  `RM_TheForge`: scatter 0, `mineablePreventMeteorite` true, no deep deposit. The minerals mod's meteorite whitelist
  names it, but that filter only keeps entries from vanilla's list, which already leaves out meteorite-prevented
  rock. The mine shaft has a zersium bill (`RM_MineShaft_RSW_MineableZersium`), but with `onlyMapVeins` on (the
  default) it is only offered on a map that holds the vein. Scarcity is a provisional ~660 per Forge map. Traders can
  carry it (tradeTags ExoticMisc); that is trade, not a biome.
- **(5) Settings toggled during play. The code review found two defects, both fixed.** Re-enabling plasteel was
  keyed on a stored index, which goes wrong if the Armoury removes durasteel first. It now goes back before the
  process that followed it at load. Changing the cost live would have let a player build the forge cheap, flip the
  gate and deconstruct it for spacer components; the cost is now set once at startup, and the tooltip says so.
- **Not tried (need a running game, which my lane can't use):** (2) plasteel started before the late research
  (whether PipeSystem enforces `ProcessDef.researchPrerequisites` in the bill menu), (4) production interruptions,
  (6) a messy save. The live rows I added to `alloy_forge_gated` cover the load-time half of (2). The rest is for
  the live loop's L5 run.
