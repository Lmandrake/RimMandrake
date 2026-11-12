# Broaden: what a real player would try (2026-11-12 02:41 -0800)

Asked a different model (GPT `gpt-6.1-sol` through `src/RimMandrake/Utils/gpt_consult.py`, job
`consult-20261112-020303-3628305-3ae8ee`), after A1-A5 had passed live and the reel's inspect text had been fixed once.

## The question (verbatim)

RimWorld mod feature: passive gravity levelling. Two bodies of liquid (dug pits holding water, natural ponds, a limitless sea) joined by a pipe network with two open hose ends (one hose reel set Intake, one set Outflow, both on one pipe run) slowly level out, higher surface to lower, no pump. Rules: no overshoot, volume conserved, different liquids never mix (water vs chemfuel: nothing moves), a dry receiver takes the source's liquid, siphon always works, flow stops when the intake end is out of the water, off while a pump on that network runs. The hose reel's inspect pane reads "Levelling: flowing (no pump; the higher water runs to the lower)." / "Levelling: level." / "Levelling: stopped, different liquids never mix." etc.

The done statement (what must be true):
- A1: offline kernel selftests green (volume exact incl. limitless net, energy never rises, gap never grows or flips, no link reverses, no mixing; 300-scene fuzz converges; 1-square vs 100-square basin, ten parallel links, same-body loop, siphon, exposed intake, water/oil, dry receiver, sea to brim).
- A2: budget case 200 bodies, 400 links, 64 links per cycle: ~89 us per 250-tick cycle.
- A3: live, 325x325 map, two ~40,000-cell basins, 200 links: tick time and allocations of the levelling tick.
- A4: live, two ponds of unequal height joined by a hose with two open ends level out (surfaces within 1 cm), the hose reads "Levelling: flowing" then "level".
- A5: live, a water pond and an oil (chemfuel) pit joined the same way exchange nothing; the hose reads "different liquids never mix".

What I tested and how:
- A1/A2: the C# selftests, 11/11 green, budget case 88.9 us/cycle.
- A3: live on a fresh 325x325 map, 200 rigs (each: two reels on one pipe run, hoses laid to the two basin lips): 200 links, avg 14.0 ms per 250-tick cycle, max 53.8 ms (one cycle with a GC), 460 KB allocated per cycle.
- A4: live, two 3x3 pits 4 notches deep, 360,000 dL vs 90,000 dL, reels set Intake/Outflow: reel inspect read flowing from tick 250, the pools reached 225,234 / 224,766 dL (total conserved) and the reel read "Levelling: level." at tick 4750. Then I topped one pool back up (as rain or a pump would) and it flowed again and re-levelled, total conserved.
- A5: same rig, water vs chemfuel: 0 moves over 1500 ticks, volumes unchanged, both reels read "different liquids never mix".
- I looked at desktop screenshots of the inspect pane. I found and fixed two things: the pane said "Intake needs a working pump on this network" right above "Levelling: flowing (no pump...)" (contradiction), and the extra text pushed the Levelling line below the pane's fold. Now a levelling end drops the pump-need line, and an end already set to Intake drops the "(set this end to Intake)" hint.

Question: what would a real player try that I have not, given that statement? Think of someone new to the mod, someone experienced, someone trying to break it, and a messy real base. Name the 5-8 most revealing experiments, most revealing first, each with what result would show a defect. Be concrete about RimWorld mechanics (saving/loading mid-flow, deconstructing a reel mid-flow, a pump switched on mid-flow, roles swapped, one end in a natural pond or river, a limitless sea end, freezing, rain filling a pit, different elevations/floor depths, a third open end on the same network, etc.).

## The answer (verbatim)

1. **Save, quit to desktop, reload mid-flow.**  
   Save your unequal-pond rig just before a 250-tick update, then repeat near the 1 cm stopping threshold. Reload each save several times and continue to equilibrium. Also reload the blocked water/chemfuel rig.  
   **Defect evidence** — changed volumes on loading, duplicated transfers, a permanently stalled connection, mixing after reload, or inspect text disagreeing with actual movement.

2. **Deconstruct a working connection, then rebuild it.**  
   While flowing, have a pawn finish deconstructing one reel. Repeat with a middle pipe segment and with a reel destroyed by damage. Let several cycles pass before rebuilding. Then reconnect both ends to the same pond.  
   **Defect evidence** — continued transfer across the broken connection, disappearing liquid, errors referencing destroyed buildings, duplicate flow after rebuilding, or measurable transfer around the same-body loop. Check the surviving reel’s explanation throughout.

3. **Switch a real pump on halfway through levelling.**  
   Attach a powered pump to a branch of the same network. Start it during passive flow, switch it off, then cause a power loss and restore power. Repeat with a running pump on a separate network nearby. Account separately for the pump’s own transfers.  
   **Defect evidence** — passive transfer continues while the same-network pump runs, passive flow fails to resume after pumping stops, a disconnected pump suppresses levelling, or the pane still says “flowing (no pump)” during pumping.

4. **Add a third open end, especially into a dry pit.**  
   Connect a water intake and two outflows to separate receivers. First use two water receivers at different heights. Then make one receiver chemfuel. Finally, connect water and chemfuel intakes to one initially dry receiver. Rebuild in a different order.  
   **Defect evidence** — combined withdrawals exceed the available source volume, competing links overshoot a receiver, liquid identity changes after the dry receiver first acquires liquid, or adding an incompatible branch enables mixing. Your statement leaves three-end pairing open, but these conservation and compatibility checks still apply.

5. **Put the intake on a shallow shelf above a deeper sump.**  
   Make the source deep enough to retain substantial water after its shoreline intake becomes exposed. Connect it to a lower, initially dry receiver with a different floor depth. Route the hose over higher ground to exercise the siphon. Repeat with equal absolute surface elevations but different water depths. Refill the source until the intake is submerged again.  
   **Defect evidence** — draining continues after exposure, re-submergence fails to restart flow, hose routing prevents the promised siphon, or unequal floor depths cause transfer between already equal surfaces. Measure surface elevation as well as dL.

6. **Use natural water and the limitless sea in live play.**  
   Run the same small receiver successively from a natural pond, a river, and a limitless sea. Put the sea-fed receiver close to its brim. Record the receiver gain and the corresponding finite-source loss or limitless-source exchange. Run through several cycles after filling stops.  
   **Defect evidence** — valid natural-water endpoints are unrecognized, the sea becomes depleted, the receiver exceeds capacity, exchange accounting fails, or repeated cycles keep adding liquid after the permitted stopping surface. Record any intended river replenishment separately.

7. **Swap the roles through the normal gizmos while flowing.**  
   Change Intake/Outflow to Outflow/Intake, passing through the temporary two-Intake or two-Outflow configuration a player will create. Restore the original roles. Repeat after the ponds have reached “level,” then add water to one side. Inspect both reels at normal UI scale.  
   **Defect evidence** — old roles keep operating, restoring a valid configuration requires rebuilding or reloading, an invalid intermediate configuration still transfers, or the pane gives contradictory or hidden instructions. The expected response to the fully swapped roles needs clarification in your stated rules.

8. **Let weather and excavation change an operating base.**  
   Start with flowing ponds, let actual rain fill them, then dig a connecting trench so they become one body and backfill it to split them again. Where supported, freeze and thaw the endpoint cells. Repeat these changes on your 200-link map while measuring levelling-only time and allocations. Odyssey supplies freeze/thaw and flooding transitions worth exercising. [Ludeon’s terrain description](https://store.steampowered.com/news/posts/?appids=294100&enddate=1761924617&feed=steam_community_announcements)  
   **Defect evidence** — stale body membership, duplicated volume after splitting, failure to resume after valid water returns, or persistent timing/allocation growth after restoring the original layout. Balance rain and any spills explicitly. Frozen-intake behavior is unspecified in your statement, so establish its intended result before judging continued flow itself.

## What I tried, and what I found

I picked the two a player does all the time and that most directly threaten "levels out, conserved": **(1) save and reload
mid-flow** and **(7) flip the reels' roles mid-flow**. Script: `whittle/pipe_levelling_build_water_finds_its_level/evidence/try_broaden.py`,
run on the A4 rig `walk_gaps_proof.py --fresh-map` leaves (SteveDesktop game A, FlowWorks tier, the final DLL). Result:
`whittle/pipe_levelling_build_water_finds_its_level/evidence/broaden_saveload_roles.json`.

- **Save/reload (1): holds.** One pool topped up, 500 ticks of flow, saved; 750 ticks on; reloaded and ran the same 750 ticks.
  The reload lands on exactly the saved volumes, the replay lands on exactly the volumes of the run with no reload, total dL
  constant throughout (`saveLoad`: reloadMatchesSave, replayMatchesNoReload, conserved all true). No duplicated, lost or
  stalled transfer.
- **Found and fixed on the way:** right after a load, before the first levelling cycle, the intake reel said "Intake needs a
  working pump on this network." on a rig that was about to level (the per-reel levelling state is not saved; a paused,
  just-loaded game shows that line until unpaused). Now, until a levelling cycle has seen the network since its
  pipes or hoses last changed (`RM_Levelling.SeenTopology`: after a load, and after laying or re-laying a hose), a no-pump
  network with two open ends makes no pump claim and the reel reads "Levelling: checked on the next cycle." (widened after the
  judges' first and fourth passes). Capture: `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_after_reload_pane.png`.
- **Roles (7): holds.** Swapped (Outflow/Intake) and both-Intake still level (roles do not set the direction: higher runs to
  lower); one end Capped stops it dead (volumes unchanged over 500 ticks, the Levelling line goes); back to Outflow resumes.
  Total dL constant across all of it.
- **Found and fixed (the same family, while looking at the panes):** an Outflow end lying beside deep water still carried the
  hose's "(taking water in needs a pump: set this end to Intake)" hint while levelling was moving water through it with no
  pump. The hint is now dropped on an end that is in a levelling link (as it already was on an Intake end).
- An earlier run of this script showed a "stall" after reload; it was the script setting roles while the game was still
  loading (map reads came back null). Harness, fixed by waiting for the load (and for visual readiness before the capture).

## Not tried, and why

- (3) a pump switched on mid-flow: the owner's ruling (ledger note 2026-10-21) is "off while pumping, resumes when it stops";
  it is in the kernel adapter's skip (`HasWorkingPump`) but I did not stage a powered pump live. The most valuable next try.
- (4) a third open end, (5) shelf intake over a sump, (6) river and sea ends live, (8) weather/trenching on the 200-link map:
  offline cases exist for parallel links, exposed intake, sea to brim and dry receiver (A1), not live.
