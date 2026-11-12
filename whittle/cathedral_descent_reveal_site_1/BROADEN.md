# Broaden: what a real player would try that we had not

Asked 2026-11-11 21:30 -08:00 to GPT (gpt-6.1-sol via `src/RimMandrake/Utils/gpt_consult.py --codex wsl`, job consult-20261111-213009-73390-dbaf56), with `src/RimUtinni/CathedralPass/Source/CathedralDescent.cs` attached. A fresh Opus reviewer (rm-consult) read the same code in parallel; its findings are listed after GPT's because they overlap.

## The question (verbatim)

> We are building, for a RimWorld 1.6 campaign mod, a one-time late-game "reveal": a hidden machine-mind under a desert plateau finally addresses the player. Spec (owner's words, abridged): a real structure-injected site the player walks (canyon-scale halls, a mile-long production line, a coolant channel, mechanoid Sentinels that walk past the party); one-time escorted descent; at the bottom the first direct address through the party's droid/comms gear, text/menu only, prescribed fallback text (the game is whole with no LLM). Discloses only that it is alive, that it is vast, and that the salvage was cover and the player's conduct an audition; never why droids are spared, never the drill response, never purpose. Scoped to the player: no faction text, trader chatter or codex changes. Trigger: VOUCHED standing + the post-restore-choice flag, never standing score alone; fires once; sets the reveal flag later systems read. Verify: dev-flag matrix (VOUCHED without flag = no fire; flag without VOUCHED = no fire); re-trigger refused; diff the faction-visible string surface; all reveal text passes our bans linter; completes with the LLM absent; site present per slot; lore docs updated.
> 
> What we built and tested OFFLINE (no game run is possible in this lane):
> - Python GM blackboard gate (pure function + full fixture runs of a simulated colony climbing WARY->TOLERATED->VOUCHED doing missions): matrix of 72 gate inputs; VOUCHED w/o flag, flag w/o VOUCHED, Regard forced to 1000 with no missions, setting off: no opening; both: exactly one opening on the first VOUCHED poll, reveal once when the descent quest ends Success, stage 3 from then on and never before; demote-and-reclimb: no second opening; a descent quest already on the list (dev-opened): never doubled; descent never walked: stage 3 stays shut.
> - C#: incident (refuses if save flag says opened/revealed), auto-accepted non-expiring quest that places the site, map component firing a 5-page dialog + archived letter when a colonist is within 6 cells of a bottom marker, escort = mechanoid hostility exception on that map only, lost by a pawn that deliberately strikes a sentinel. Compiles.
> - Text linted at the right stage; linter shown to refuse the address at pre-reveal stage and planted ban lines; string-surface diff of all faction-visible strings (3864) between the pre-item commit and HEAD.
> - The site map (KCSG layout) is built by another agent with a per-slot audit (BFS walkability, marker exactly once).
> 
> Question: what would a real player try that we have not — someone new, someone experienced, someone trying to break it, a messy real save? List the 6-10 most revealing scenarios, each with what could go wrong and how we could check it OFFLINE (code reading, a fixture, a static audit), and mark the two you think most likely to find a real bug.

## The answer (verbatim, minus the transport header)

**The first two are my strongest bug candidates:** both expose gaps visible in the supplied C#, without depending on unusual engine behavior. These are proposed offline checks, not additional test results.

1. **★ A pack animal reaches the bottom before its handler.**  
   **Could go wrong:** `SpawnedPawnsInFaction(Faction.OfPlayer)` includes candidates beyond colonists. The filter only excludes dead/downed pawns, so an animal can receive the address, acquire an imaginary belt-mounted comms set, and complete the reveal. An unsuitable mech or other modded pawn may do the same.  
   **Offline check:** Extract the listener-selection logic into a fixture with a colonist, droid, animal, player mech, downed pawn, and temporarily controlled pawn. Vary distance and enumeration order. Assert an explicit intended listener policy.

2. **★ An experienced player approaches the terminus through an adjacent corridor—or tunnels toward it.**  
   **Could go wrong:** The six-cell trigger uses straight-line distance, with no reachability, room, or approach check. A pawn behind a wall can complete the reveal without walking the intended descent. BFS proving that the marker is reachable does not exclude this shortcut.  
   **Offline check:** For every layout slot, overlay the trigger disk on the intended route. Enumerate walkable cells within six cells of the marker, including across walls, and identify the earliest route position that can trigger it. Include plausible mined shortcuts.

3. **The opening waits in a dispatch queue while the colony loses VOUCHED standing.**  
   **Could go wrong:** The Python decision was valid when made, but stale when executed. `OpeningRefusal()` checks settings, saved flags, definitions, and a home map; it does not recheck either story prerequisite. That makes the dispatch boundary part of the gate’s correctness.  
   **Offline check:** Run the actual decision-to-dispatch adapter with “eligible → queued → demoted → delivered,” duplicated deliveries, and retries after reconnect. Establish exactly when eligibility must hold. Verify the normal dispatch path, beyond the pure gate fixture.

4. **A messy save reloads after only part of the reveal committed.**  
   **Could go wrong:** `SpeakAddress()` sets `revealed` before building the dialog, delivering the letter, or ending the quest. A subsequent exception can leave the C# reveal permanently consumed while the blackboard still sees no successful quest. Conversely, a legacy successful quest with default component flags could permit another opening.  
   **Offline check:** Fault-inject each step and round-trip serialized state. Test contradictory combinations of `opened`, `revealed`, site presence, and quest outcome, including an older save lacking the component fields. Require a defined recovery or reconciliation path.

5. **The player leaves halfway down, returns later, then revisits after the address.**  
   **Could go wrong:** Non-expiring quest status alone does not establish map retention or site lifetime. Quest success might invoke cleanup; map regeneration might reset escort state. Also, “Go back up.” only closes the dialog—it performs no return travel.  
   **Offline check:** Audit the quest XML, site worker, spawn part, and removal signals. Model departure before/after the reveal, map unloading/regeneration, and caravan re-entry. Verify a usable return route and define whether later visits remain allowed.

6. **The player brings animals, automatic weapons, explosives, or a pawn having a mental break past a Sentinel.**  
   **Could go wrong:** “Deliberately strikes” needs a precise implementation. Splash damage, autonomous fire, friendly fire, and mental-break attacks could revoke escort incorrectly—or avoid revocation entirely. The shown component records revocation but does not show what calls it.  
   **Offline check:** Audit the hostility and damage patches with an attacker/victim/cause matrix. Include Sentinel retaliation, player turrets, faction changes, and identical encounters on another map. Assert that protection and revocation remain correctly scoped.

7. **The player disables the feature while the party is underground.**  
   **Could go wrong:** The setting immediately disables both the address watcher and `EscortApplies()`. Depending on the hostility patch, machines that just escorted the party could become hostile, leaving an opened, unfinished descent. Re-enabling may resume in a surprising state.  
   **Offline check:** Fixture setting changes before opening, during approach, beside Sentinels, and after reveal. Trace hostility and progression at each transition, including save/reload. Decide whether the setting controls new openings or also revokes an existing expedition.

8. **A crowded or unusual world makes site placement fail.**  
   **Could go wrong:** `TestRunInt()` and `RunInt()` independently find a tile. If the latter fails, it silently returns; whether that still produces a successful incident must be checked before trusting the permanent `opened` latch. Multiple colonies can also make `AnyPlayerHomeMap` choose an inconvenient origin.  
   **Offline check:** Stub tile searches as “success during test, failure during run,” plus no free tiles, no Cathedral biome, multiple homes, and unsuitable world layers. Trace the real quest-generation contract. Assert that opening success entails an actual spawned, reachable site.

9. **Two descent quests exist in an imported or dev-touched save.**  
   **Could go wrong:** The address ends **every** ongoing quest whose root matches `QuestDef`, without tying completion to the current site. One visit can mark unrelated or duplicate expeditions successful and trigger their cleanup.  
   **Offline check:** Construct two matching quests with different sites, plus failed/ended copies. Invoke the address once and inspect outcomes and signals. Audit whether a durable quest-to-site identity exists elsewhere; none appears here.

10. **The player uses a strange pawn name, another language, and no LLM.**  
    **Could go wrong:** The XML text audit does not necessarily cover hardcoded choices/messages or runtime substitutions. This file contains `"Listen."`, `"Go back up."`, the escort-break message, and generated speaker phrases. Names can introduce markup, newlines, banned words, or misleading channel descriptions.  
    **Offline check:** Inventory every player-facing string source, then render complete dialog/message/letter outputs with representative pawn types and adversarial names. Lint authored text separately from player-supplied substitutions. With the LLM adapter unavailable, assert all pages, archive content, completion flags, and quest outcomes.

These checks would substantially strengthen the offline evidence. Actual Sentinel movement, dialog interaction, and map cleanup would still need an eventual in-game acceptance pass.

## What I tried, and what I found (2026-11-11, -08:00)

GPT ranked 1 and 2 as most likely to hold a real bug, and on reading the code both did. An independent Opus reviewer found the same two, plus the others below, without seeing GPT's answer. I fixed every one I could fix offline and published the fixes in `2b51bf3116`.

1. **A pack animal reaches the bottom first:** a real bug. Any spawned player-faction pawn could hear the address and spend the beat, a dog included ("the comms set on Husky's belt"). Fixed: `CathedralDescent.CanHear` now admits only an awake, upright clan colonist or droid/mech, never an animal or a pawn in a mental break.
2. **Reaching the terminus through a wall or a side tunnel:** a real bug. The trigger was distance alone. Fixed: `AtTheBottom` now also requires a line of sight to the terminus and a walkable path to it.
4. **A save that stops halfway through the reveal:** a real bug. `revealed` was set before the dialog, the letter and the quest's end, so a throw part way left the game revealed and the blackboard not. Fixed: the site's own quest is ended first and the flag is set last; if the quest is missing the address refuses and logs, and nothing is spent.
7. **The setting switched off underground:** a real bug, worse than GPT guessed. The escort hung off the pass setting, so with the mechanoid pass off the descent's machines attacked the party outright. Fixed: the setting now decides only whether the way down opens; the escort is independent of both settings, and a broken escort is kept in the save.
8. **Site placement fails:** a real bug. The opening could be marked spent with no site. Fixed: the incident marks "opened" only when the quest exists and carries its site, and the quest node throws instead of returning silently. On the blackboard side, an opening that never reaches the quest list re-arms after a game day. This is tested: the game refuses the first opening, the second is delivered, one quest, one reveal.
9. **Two descent quests:** possible through the dev "generate quest" menu. Fixed: the quest node's test run uses the same once-gate as the incident (which now also refuses if any descent quest exists), and the address ends only the quest whose site this map is.
10. **Hardcoded strings:** the dialog options, the escort-broken message and the speaker phrases are now constants, and the selftest lints them at stage 3.
3. **A stale dispatch** (the opening queued while the colony is demoted): not fixed. The in-game worker cannot read VOUCHED, which only the blackboard holds, so eligibility is decided on the poll that fires. Recorded as known.
5 and 6. **Leaving and coming back, and splash or turret damage on a Sentinel:** these need the live game. The rule that only a deliberate strike counts is the pass's existing `IsDeliberateStrike` logic. Left for the live proof.
