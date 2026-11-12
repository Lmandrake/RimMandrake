# Broaden: what a real player would try (2026-11-11, GPT via gpt_consult --codex wsl, gpt-6.1-sol)

## Question

Statement criteria plus what was tested (49 offline kernel cases; glue compiled, never run live), sent as `D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_OFFLINE4\broaden_q.md`. Asked: list the 8 things a real player would try that these tests have not covered, most revealing first.

## Answer (verbatim)

1. **Perform the ritual through the normal UI**, offering pitch, a dig find, ordinary goods, then attempting a pawn, corpse, and below-floor offering—selection, eligibility messages, outcome execution, and actual destruction remain untested; stack handling could consume the wrong amount or leave the offering held.

2. **Save, quit, and reload mid-effect**, with a beast asleep, two trap fizzles remaining, and an Imperial raid postponed—serialization could lose counters, reset durations, duplicate effects, or restore the original incident schedule.

3. **Sink an offering just before an already-scheduled Imperial raid and its warning**, then let time advance—faction eligibility filtering may block a fresh raid without actually postponing the queued incident or keeping its warning aligned.

4. **Try repeated offerings, interrupted rituals, and two rituals finishing close together**—effects could fire before completion, apply twice, consume the offering without granting effects, or refresh/stack durations and trap counters incorrectly.

5. **Wake an actual lulled beast using construction, digging, pumping, and nearby explosions**, including explosions just inside/outside range—real wake paths may bypass the patched methods, while the explosion relay could miss the beast or wake unrelated ones.

6. **Trigger four real trap opportunities across several worked objects and maps**, including existing armed traps—a shared counter could be spent on the wrong map, decrement more than once, or suppress arming while still allowing explosion damage.

7. **Play through raids from several sources during the lull, then past its expiry**, including storyteller raids, quests, and forced incidents—the `TryFire` hook may miss paths, suppress unintended factions, or leave the reduced chance active after expiration.

8. **Use a messy save with existing claims, colonist records, Ninefold/Heat state, and active effects; toggle each setting during play**—live integration could erase colony claims, alter pawn records or Heat, duplicate Ishko rewards, misname the letter item, or leave disabled effects active.

## What I tried and found

- **#2 save/reload mid-effect** (checked offline by reading code): the trap counter is saved by `MapComponent_SinkingTraps.ExposeData` (`sinkingTrapsRemaining`); the three conditions are ordinary GameConditions saved by vanilla's GameConditionManager; the moved Imperial timers live in EmpirePursuit's own saved dictionaries, which the Sinking edits in place. No Sinking state lives only in memory except the probe's last-letter/last-delta strings, which are debug reads. A real save/reload has NOT been run: offline lane, no game.
- **#1 perform it through the normal ritual UI**: cannot be done offline. The live proof cases in `src/RimUtinni/Rites/validation.py` (`sinking`) call the same `SinkingGlue.Apply` the outcome worker calls, through the probe, so they do not exercise the ritual dialog, target selection or the outcome worker itself. This is the first thing the live lane must do by hand (start the rite from the ideo's ritual gizmo on pitch, a dig find, steel; try a prisoner and a corpse) before the scripted cases.
- Found and fixed while reading: the pitch rider's letter did not say an explosion still wakes the bulge (spec §4); it does now.
