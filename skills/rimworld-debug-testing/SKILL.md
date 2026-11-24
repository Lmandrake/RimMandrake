---
name: rimworld-debug-testing
description: Testing anything in RimWorld without spending a cold load — starting and destroying throwaway dev quicktest colonies through the bridge, deciding what a quicktest can and cannot prove, and knowing when disk evidence (def dumps, XML on disk) is not evidence about the running game at all. Use whenever a test needs "a map", whenever someone says they are blocked waiting for a world or a colony, before adding anything to the cold-load run-sheet item (COLD_LOAD_RUN_SHEET_*), when choosing between a bridge test and a game restart, when a def-derived claim needs checking against runtime, or when a result must be attributed to the campaign versus scratch. For writing, running or reading a live proof or validation script (a long full-list proof failing on its own harness, two proof runs that disagree, log budgets, perf rows), use live-debugging-proof-harness.
---

# Debug testing: never wait for a map you can make

A **quicktest** is a throwaway dev colony that the bridge starts. Old evidence and struck lines:
[references/history.md](references/history.md).

> 🟢 **UPDATED 2026-08-19 — the economics changed.**
>
> - On the 13-mod minimal list (`modlist_swap.py`, see the `rimworld-load-round` skill), a **cold load is 22 seconds**.
>   `ModsConfig.MINIMAL.xml` holds more mods now, and its load time is UNMEASURED (`rimworld-load-round` §0).
> - On that list, `rimworld/start_debug_game_ready` makes a full quicktest world and map in **5 seconds**.
> - The whole edit → build → deploy → launch → test cycle is about **one minute**.
> - Each rule below that protects a load still holds for the owner's real full list (`ModsConfig.FULL.LATEST.xml`).
> - For tool work and mechanism work, relaunch at once.
>
> ⚠️ **What a minimal-list quicktest still cannot prove:**
>
> - anything that depends on real tile IDs. Such a quicktest makes 119,904 tiles, not 21,872;
> - anything that needs the content mods;
> - anything about the owner's actual mod interactions.
>
> A minimal-list quicktest proves MECHANISM, not CONTENT.
>
> **`rimworld/search_debug_actions` timed out at 30 s even on 13 mods.** So a heavy mod list is not the only cause
> when the search for debug actions hangs.

**This skill is METHOD, not mechanics.**

- `skills/rimbridge/SKILL.md` says how to drive the bridge: the call palette, debug actions, map authoring, speed and
  the companion DLL.
- `skills/rimbridge/references/traps.md` is the index of the bridge failures. **Read the traps file before any live
  session.** That file stops you from paying for a lesson a second time.
- This skill answers only *what to test on, and what a result is worth.*

The cost of each:

- A cold load of the owner's FULL list costs **~15 minutes** (MEASURED 2026-09-07 on 599 mods). The other measured times
  are in `rimworld-load-round` §0.
- The 13-mod minimal list cost ~22 seconds.
- A quicktest costs from seconds to ~90 s (§1), and belongs to nobody.
- There are four games, each with its own bridge lock (root `CLAUDE.md` §There are several live games). A quicktest on a
  small mod list does not need ArchBig, the game on Archmagi with the full list.

> 🔴 **"Blocked on a map" is almost never real.** Owner's ruling, `infrastructure/agents/CHARTER.md` (maps, saves and
> colonies are "not precious"): **whoever holds the bridge may create and destroy dev colonies at will.** You need no
> permission, no queue entry and no wait for worldgen.

Before you call a test blocked on a map, ask one question. Does the test need *a* map, or *the* map (the campaign
map)? Do not save up a test that needs only *a* map.

---

## 1. Start one

```
rimworld/start_debug_game_ready
```

**The time, as measured:**

| list or sample | time |
|---|---|
| the 13-mod minimal list (2026-08-19) | 5 s |
| 68 calls of one night (2026-11-11 to 2026-11-12) | 10 s each |
| the 580-mod stack | **78.5 s** |
| plan, when you do not know (root `CLAUDE.md`) | about 90 s |

⚠️ **The call exceeds the 30-second client timeout and succeeds anyway.** The response is only late.

- **Give the client a longer timeout first.** 30 s is the default of `rimbridge_client.RimBridge`.
  `prove_quicktest_world.py` uses `timeout=600.0` on the client and `timeoutMs=280000` on the call.
- If the call timed out, **do NOT retry** on that connection. The connection is desynced, not idle.
- **Do NOT issue the call again.** You get a *second* map.
- **Open a fresh connection.** Then wait for the map with `live_site.wait_ready(rb, budget_s=…)`
  (`src/RimMandrake/Utils/live_site.py`).
- Do not write a new poll by hand, and do not guess a sleep. Budget well over a minute. `wait_ready` uses the one shared
  lifecycle wait, `await_lifecycle` (READYWAITS_UNIFY_ONE_HELPER).

**If a game is already loaded, call `rimworld/go_to_main_menu` first.**

- From inside a running colony, the call starts no fresh colony. The call can wait 280 s, and the old map stays
  ("A game is already loaded.").
- If the call answered, accept the start only when four things are true. The call said `success: true`. `programState` is
  `Playing`. `hasCurrentGame` is true. One map is loaded.
- If the call timed out, you have no answer to read. Then `wait_ready` decides.
- `src/RimMandrake/bridgetools/prove_quicktest_world.py` does the whole route and refuses to leave a real colony.

🔴 **Do not quicktest on the owner's FULL mod list when a tier can answer.** On the full list, a quicktest failed on two
nights, in two ways:

- On a full ~599-mod run, the process crashed outright. `Player.log` stopped in the middle of worldgen for 5+ minutes,
  and the process was gone with no crash dialog (2026-09-08).
- On a full ~590-mod run, no game came and nothing crashed. `WorldGenStep` and pawn-generation exceptions looped
  forever at `Entry`, with `hasCurrentGame:false` (a MonoMod IL collision between two content mods). The bridge caller
  saw nothing. Only `Player.log` shows it (2026-09-12).

Either failure costs the load.

- **Build a `modset_builder.py` tier first**, and quicktest on the tier. A tier is a named small mod list.
- A normal boot to the menu on the full list is fine, and so is a load of a real save. Quicktest worldgen there is the
  dangerous act.
- The quicktest worked on the full 629-mod list on 2026-09-27, after three faults in our own content were fixed. No record
  was found that ties those faults to the two failures above. The next fault of either kind costs a load again.
- So use the full list only for the final verification pass (`rimworld-load-round` §0, "Which list to test on"). If the
  start fails there, read the FIRST exception in `Player.log`
  (`skills/live-debugging-proof-harness/references/traps.md`).

🔴 **The route DISCARDS the current map without further warning.** `rimworld/go_to_main_menu` drops the game, and
anything that another seat left on the old map is gone. **Before you
call `go_to_main_menu` or `start_debug_game_ready`, read the driver lock:**
`python3 src/RimMandrake/rimflow/game_lock.py query` (ArchBig and ArchSmall; the test lane drives Steve1 and Steve2). Do
not call them while another process drives that game.

The result is an ordinary map: spawn, build, paint terrain, set the time, take a screenshot.

**To destroy a quicktest, start another one, or leave it.**

- A quicktest is scratch. Nothing in it is precious, and nothing in it needs a cleanup.
- A stale quicktest has one cost: you can confuse which map a result came from (§3).

### 🔴 Reversible, cheap and unobtrusive are three different properties

A quicktest is **reversible**. A quicktest is not free, and it is not invisible.

- Each `start_debug_game_ready` is a full RimWorld **world** generation.
- A loop of seven took `/proc/loadavg` to **22.58**. RAM was fine. The load was CPU and 9p-mount contention on the disk
  that RimWorld streams assets from. The owner reported *"stuck on Generating Map…"*, then *"running badly"*. Nothing
  was stuck.
- **From the keyboard, an agent-driven worldgen and a hang are the same event.** There is no *"an agent is doing this"*
  indicator on RimWorld's loading screen.

🔴 **If a quicktest map generation crashes, the crash takes down the WHOLE process of that game.**

- A stable campaign that is loaded in the same process goes down too. Two agents crashed the same stable, freshly
  recovered campaign load this way (2026-09-09/10).
- So "Just testing a quicktest" is not isolated from a live campaign in the same game. Use another game.

**When work occupies the UI of a game on his machine, tell the OWNER before the work starts. Report when it ends.**

- A message to peer seats does not count. The owner sees the screen and cannot identify the work.
- The message does not gate the work. Do not wait for an answer. Do not wait for the owner to leave the keyboard
  (root `CLAUDE.md` §The bridge is passed through one file).
- Run a loop on another game when a tier list can prove the work (root `CLAUDE.md` §There are several live games).
- Read `/proc/loadavg` before and during the work. Over ~10 on this box, the load takes frames from a game.
- The rule applies to each loop of `start_debug_game_ready`, `load_game`, `go_to_main_menu` or long `save_game` calls.

More traps for this section: [references/traps.md](references/traps.md) § 1. Start one.

## 2. What a quicktest proves, and what it cannot

| ✅ a quicktest settles it | ⛔ it cannot |
|---|---|
| does this def load, spawn, and behave | anything about **worldgen choices** — the Configure Factions page is spent once, on the campaign |
| does this tool/API call work at all | anything about **the campaign's own state** — its pawns, its factions, its map |
| does this art read correctly at game scale | **faction relations that took game-time to form** |
| does this terrain/map-gen override appear — **a quicktest map IS a newly generated map** | **anything that needs the real 580-mod load order to differ from what is loaded now** |
| does a silent failure actually fire (§4) | a claim about **save-file** contents |

**On a trimmed tier list, GenStep NREs and `StatRequest for null def` spam are NORMAL behaviour.** Such lines are
not a defect.

- An unresolved `BiomePlantRecord` or `BiomeAnimalRecord` cross-reference leaves a record IN the list, with a null
  `plant` or `animal` field. Only `MayRequire` removes the entry outright.
- Code like `WildPlantSpawner.EnoughLowerOrderPlantsNearby` then reads that null field with no guard.
- A BiomeDef can name 480 species of mods that the tier does not load. Then hundreds of these nulls are the expected
  state of the tier.
- Do not read that count as a defect. Do not let that count stand for anything about the full mod list (2026-09-20).

**The rule of thumb:** a quicktest answers *"does this work?"* A quicktest never answers *"is this true of our
campaign?"*

More traps for this section: [references/traps.md](references/traps.md) § 2. What a quicktest proves, and what it cannot.

## 3. Always say which map a result came from

**A quicktest finding and a campaign finding are different claims.** Report which one you were on, every time. Without
that, the next reader cannot tell what you established.

Nobody plays a game during development. Only the canonical world saves are protected (root `CLAUDE.md` §Facts you cannot
guess; `design/RimMandrake/standing_rulings.md` §Nobody plays during development). **Owner's standing ruling:**

> *"NO AGENT SHOULD TRY TO PRESERVE MAP CONTENTS OR CAMPAIGN INTEGRITY AT THIS
> TIME OR ANY TIME IN THE FUTURE. YOU WILL BE INFORMED WHEN WE GET TO THAT
> PHASE. STOP ASKING FOR NOW."*

**Test destructively. Wipe, overwrite, regenerate.** To protect a map, do not defer a test, save a test up
or ask permission.

- Two limits stay. The first is the canonical world saves (`infrastructure/state/CANONICAL_SAVE.md`). Test on a loaded
  game. Write over a frozen one only as that page allows.
- The second: his OWNER hold and `./pipe off game:ArchBig` guard his look at staged work on ArchBig. Both bind.

⚙️ **You must still say which map a result came from.** The report is evidence hygiene, not
preservation, however disposable both maps are.

🔴 **Say which MOD LIST too — and read it from the game, not the label.**

- A proof with the label "gimmesomeslack tier" ran on 550 mods. Its preflight checked only that the mod was PRESENT.
  Three of its 15 FAILs PASS on the 11-mod list.
- Before you compare two runs, read `len(env.running)` (`jawa/running_mods`) on each run. You cannot compare a run that
  does not record the running list (2026-10-11).

## 3a. 🔴 One crash signature that looks like several: a missing `thingClass` blocks EVERY route to a `Game`

A null `thingClass` on ANY ThingDef crashes `ReadingPolicyDatabase.GenerateStartingPolicies()` inside `Game..ctor()`.
The engine has no null guard there. The ThingDef can be as unrelated as a colored water-bottle item.

- Campaign load, new colony AND quicktest all construct a `Game`. So all three die in the same way.
- The result looks like "a crash loop across several different doors". The cause is one bug. The bug hit twice,
  independently (2026-09-09/10, and 2026-09-12 on four newly-authored defs that silently blocked a full night of
  loads).
- A `has null thingClass` config-error line is a game-breaking finding, not def-quality noise.
- Check that every new ThingDef has an explicit `thingClass` before the first live load. Do not wait until several
  failed loads get blamed on something else.

## 4. A clean log is not evidence

Two independent traps make "no errors" mean nothing. Both were measured here.

**Some failures cannot log even in principle.**

- When an assembly has no string for the failure, the failure cannot print one. An earlier `JawaIonWeapons` build was
  like that: its user-string heap (the table of string literals in a .NET assembly) was four bytes, all zero.
- A clean `Player.log` is *compatible with total failure*. The only proof is the positive observation: put a KotOR droid
  in front of the weapon and look.

**A negative needs a positive observation.** If the claim is *"X no longer appears"*, the absence of an error is not
evidence. Go and see that X is gone.

**A single spawned pawn is not a sample.** Owner's instruction, 2026-08-30:
*"Please always spawn MANY examples to test, because sometimes random humans
pop up at the beginning of a new colony."*

- A fresh `start_debug_game_ready` map seeds wildlife, and can seed wandering or joining humans near the player
  start. So an unrelated pawn nearby can confound the outcome of one test pawn.
- RimWorld also rolls dice for each pawn: damage, hit location, and the storyteller-seeded traits and xenotype. So one
  result cannot tell "this is what the mechanism does" from "this is what happened to happen once."
- Measured the same day: 5 identical droids took identical damage. 4 gave a clean corpse and detonation. One only lost
  both arms to bad hit-location rolls, and a follow-up hit finished it. A test with that one pawn reports a mechanism
  failure.
- **Spawn a batch (3-5+) of the same kind, run the same test on each, and confirm that the result is consistent across
  the batch.** Only then report a mechanism as proven or broken. First check `jawa/list_pawns` for an unrelated pawn
  near the test site.
- A batch is the sample of one run. How many runs decide a scene is in root `CLAUDE.md` §A live test declares its kind.

🔴 **A flying creature needs a BIGGER batch than most mechanisms — the RNG gate is per job-start, not per pawn.**

- `flightStartChanceOnJobStart` is typically ~0.1–0.15. A flier rolls that chance only when it starts a new job.
- So one pawn that you watch for a few minutes can easily never take off. One solo watch of FireHawk's flight gave
  nothing in ~35 minutes (`FIREHAWK_FLIGHT_BEHAVIOR_1`, 2026-09-24).
- Owner's fix, verbatim, 2026-09-25: *"the way to test flyers is to spawn like 20 of them to see if any start
  flying, not just one."*
- When the test is "does this thing fly", **spawn ~20** (`jawa/spawn_pawn` `count: 20`, faction `none`). The odds then
  do the work of a long watch.
- The batch size applies whether the owner watches live or not. The batch does not license an *unattended* flight hunt.
- Root `CLAUDE.md` says "Never live-test a flyer's flight without the owner present", at any batch size. Verify flight
  with the state read `jawa/pawn_flight` (`skills/rimworld-modding/references/flight.md`).

🔴 **A state assertion and the screen can both be right, and still disagree.**

- A pit mod's `expect_pawn_despawned` PASSED, and the pawn really left the map. But a custom render hook drew the first
  occupant over a vanilla placeholder texture. So the player saw a person who stands in a box with the label Pit.
- A suite that asserts only state will certify a wrong mod: one with correct state and an absent or wrong in-game
  EXPERIENCE.
- A mechanism pass (this skill) does not replace a look (`rimworld-live-review`). Run both before you call a feature
  done.

More traps for this section: [references/traps.md](references/traps.md) § 4. A clean log is not evidence.

## 4b. Live proofs and validation scripts → `live-debugging-proof-harness`

`skills/live-debugging-proof-harness/` holds these topics:

- how to write, run or read a proof (`proof_all.py`, `proof_hose.py`, a `northstar/` runner, a `validation.py`);
- log budgets, perf rows, timing windows and pre-port save fixtures;
- how to class a row as MOD, SITE or HARNESS.

`skills/northstar-validation/` holds these topics:

- how to run a north-star suite live: the bland world (generated or saved), and the situational envelope
  (`modcheck run --situational`);
- the live_queue jobs, and the detectors that read the companion;
- the interference playbook (naming dialogs, focus theft, late replies, extra maps);
- the time ledger of a live pass.

A proof that runs unattended (a `live-proof` line, a testq/Lightspeed job) follows
`skills/live-debugging-proof-harness/references/lightspeed-authoring.md`:

- exit 0/1/2, and deterministic rows;
- no `$`-built commands;
- `B.ticks`, never a poll loop;
- a named UNMEASURED reason for a bad site;
- a flyer is read as state only.

## 4a. 🔴 LOOK AT IT. `take_screenshot` and then READ the image.

**Owner's instruction, 2026-08-13, and it is the most under-used capability we have.** `take_screenshot` returns an
absolute path. **You can open that path and actually look at the picture.** Do not parse the picture. *Look* at it.

**Most of our evidence is inference, and a screenshot is observation.** A xenotype name from `list_pawns` tells you
what a field says. A screenshot tells you what the player sees. The v1 gate asked for only that:

> **"Every v1 item must be seen working in-game once. Not 'the log is clean' —
> SEEN."**

**A def query cannot close that gate. A screenshot can.** A passing bar is an experience of the player too (root
`CLAUDE.md` §A passing bar is an experience).

### What only a screenshot will tell you

- **Art that is technically correct and reads wrong**: the right canvas, the right alpha, and unreadable at game scale.
  Every offline validator passes.
- **A texture that loaded as the magenta/checker placeholder.** Nothing logs it.
- **Terrain that painted but looks like the wrong material.**
- **A faction name that is GENERATED.** The Fallen Dominion's label is not a fixed string, so no grep finds it. Look,
  and take a screenshot.
- **UI state.** A quest is actually in the Quests tab, a letter in the notification pane, or a weapon in a pawn's hands.
- **Anything where "it exists in a def" and "the player experiences it" differ.** Most things are like that.

### 🔴 A SCREENSHOT IS A CACHE, NOT AN OBSERVATION — read this before trusting one

**These traps cost real debug cycles.** Their home is `skills/rimbridge/references/traps/` (indexed in `traps.md`),
mostly in `camera.md`. This list is the pointer.

0. **`take_screenshot` names files by SECOND. Two shots in the same second silently return the same file.** Run md5sum
   on any batch that you take fast. Shoot again with ~1.5 s sleeps between calls. Without that, the second "result" is
   the first file, read twice (2026-09-08).
1. **Screenshots overwrite by FILENAME, so a stale image reads as a failed action.**
   - Measured: eight Jawas spawned, with `success: true` on all eight. The screenshot showed **empty ground**, because
     the call used the `fileName` of an earlier failed attempt again. `list_colonists` showed all eight exactly where
     requested.
   - **Give every screenshot a UNIQUE name**, or cross-check with `list_colonists` or `get_camera_state` before you
     believe it. `Session.look` in `rimbench` makes the name unique for you.
   - **When the action reports success and the picture says that nothing happened, suspect the picture.**
2. **You cannot photograph a stale mesh.** Every framed-shot tool moves the camera, and camera movement repaints the map
   sections. For any visual A/B over the bridge, ask what the act of looking changed.

⚠️ **The advice to look and these traps pull against each other on purpose.** Look at the image. Also know that an
image file is the one piece of evidence that can be silently out of date. Nothing errors.

### How to use it well

1. **Take a screenshot before AND after** a change. One image proves a state. Two images prove a *transition*, and a
   transition is usually the actual claim.
2. **Attach the image to the finding.** A path in the report beats a sentence of description. The next reader can then
   disagree with you.
3. **Screenshot the irreversible screens**: worldgen, Configure Factions. Nobody can open them again, so an image is the
   only record that survives them.
4. **When a result surprises you, look before you theorise.** Two rulings were wrong for an hour (2026-08-13) because
   they came from a file and not from a look.

🔴 **CLEAR THE DEBUG LOG WINDOW BEFORE YOU SHOOT.** Owner's instruction, 2026-08-13. The log window of dev mode covers
most of the frame. So the screenshot documents *our own error console*, not the thing under test. **Close it, and clear
it, then take the shot.** `jawa/clear_ui` closes the window. `rimworld/clear_log` empties the log and does not close the
window (`rimworld-live-review` §5).

There are two reasons, and the second one costs more:

1. **The window hides the evidence.** A shot that is 70% debug output proves nothing about the map under it.
2. **Stale lines read as fresh failures.** An unfiltered log window carries errors from earlier in the session. The next
   reader blames them on the thing in the screenshot. **Clear it, then act, then shoot.** Then what you just did caused
   anything that shows. A claim about such a line is far
   stronger.

⚙️ Zoom and camera matter. An object that spawned correctly off-screen looks the same as an object that never spawned.
Frame the object before you shoot.

## 5. 🔴 A def dump is DISK. The running game is RUNTIME. They differ.

**Read `references/disk-vs-runtime.md` before you quote any number off a dump.** The difference is the single most
expensive confusion in this project. The difference has four distinct shapes:

| shape | the tell |
|---|---|
| the dump is STALE: captured under a different mod set | dump `modCount` != `<activeMods>` children. Compare the SET, never a timestamp |
| the def loaded and was then DELETED at runtime by a dedup mod | present in the dump, absent in game, no log line |
| the field is present and current but a **C# comp computes the real value** | the mod's assembly declares a member named after the field (`AdjustedArmorPenetration`, `get_ArmorPenetrationInt`). Read it out of the metadata with `ilprobe`. ⛔ Not `strings`: the blind-scan hook refuses it, and it sees a minority of names anyway. `references/disk-vs-runtime.md` has the command |
| a **runtime enforcer silently rewrites a value your XML never claimed** | a raw `jawa/get_defs` read-back differs from the authored XML. The difference shows the rewrite. To find the mod that did it, add one mod at a time |

The third shape is the nastiest, because nothing about the dump looks wrong. The in-game info card is the arbiter. A
read of the card costs no map, no spawn and no bridge privileges.

The measured case of the fourth shape (2026-09-17):

- A startup mod capped `BiomeDef.plantDensity` at 1.0 and rescaled `wildPlantRegrowDays` for every biome, ours included.
  Map Designer (`zylle.mapdesigner`) does this with no log line.
- The Pyrelands went from 1.55 to 1.0, and its regrow from 9 to 9/1.55. So each density nudge still read 'still too
  bare'.
- Wild plant cover per cell is `min(plantDensity x fertility^2, 1)`. Fertility multiplies twice.
- The fix was not an XML edit. The fix is an enforcer (`LongEventHandler`+`GameComponent`) that asserts our values again
  after the other mod runs. `RM_PyrelandsDensityEnforcer` ships it, and it runs after all mods load.

More traps for this section: [references/traps.md](references/traps.md) § 5. 🔴 A def dump is DISK. The running game is RUNTIME. They differ..

## 6. Choosing: bridge test, quicktest, or a real load

Ask in this order. Stop at the first yes.

1. **Can a file on disk settle it?** An `About.xml`, a def, `ModsConfig.xml`: all free. Read §5 again before you trust
   a file about *runtime*.
2. **Can the live bridge settle it on whatever map exists?** That costs seconds.
3. **Does it just need *a* map?** Use a quicktest (§1). **Most "needs a load" items land here.**
4. **Does it need the real campaign, or a changed mod list?** Only now is it a cold load. **A quicktest cannot fake a
   mod-list change**, and a mod-list change takes effect only on a restart.

**Before you put anything on a cold-load run sheet (an item `COLD_LOAD_RUN_SHEET_*`), run this list.** An item that a
quicktest can close does not deserve a slot of the full load.

**A biome-purity census on a quicktest map can read as contamination when Odyssey only blends NEIGHBOUR biomes into the
map's edge zones.**

- A biome-purity census counts how much of the map's content belongs to the biome. On a lone re-tiled scratch tile,
  one census read 78% foreign plants. The map only bled its (correct) neighbours at the edges.
- Take a census only on a tile whose neighbours share the biome. Or use the spatial split: compare the shares of each
  def family per quadrant. The split tells edge bleed from a genuine global injection defect, at low cost.

**"Just needs a quicktest" is true only if the thing under test is already deployed AND in `ModsConfig`.**

- If the mod under test is not loaded yet, a "pre-build quicktest gate" in a design can hide three acts: a
  deploy, a mod-list write and a restart.
- In one case, the right move was to implement both branches behind one def field. A restart of the owner's live 599-mod
  session to settle a one-field decision was the wrong move.
- Check that the subject is actually live before you call a check "just a quicktest" (2026-09-09).

## 7. The validation plan → `live-debugging-proof-harness`

PROVE / EXPECT / LIES, the six fields and "a live run must be proven needed":
`skills/live-debugging-proof-harness/references/validation-plan-and-thresholds.md`.

## 8. Advising: turning "can you check X" into a plan

Most requests arrive half-formed. *"Can you check the bandolier looks right?"* *"Does the ion weapon work?"* **These are
not checks. Each one only points at an area.** If you accept one as written, you spend a load on an opinion, not a
finding.

🔴 **Ask two questions before you agree to look at anything:**

1. **"What would you SEE?"** This question forces the observable. If the answer is "the log would be clean" or "it would
   work", there is no check yet. Keep asking until someone names a thing on screen. *Bandolier looks right* → **a pawn
   selected, facing north, with the strap drawn over the torso and not behind it.*
2. **"What number do you expect?"** This question forces the prediction. A range is fine, and a guess is fine. *"I don't
   know"* is the useful answer: the look cannot fail, and so it cannot succeed either. *Does the ion weapon work* → **a
   KotOR droid at 8 tiles drops in ≤3 shots.**

Then close it out loud: **"so the bar is one screenshot of X, and I am not chasing Y."** State the threshold back to the
asker (§9, the threshold discipline). The asker did not think about the threshold, and a missing threshold costs a
second load.

**You are entitled to refuse the shape, not the request.**

- "I can look, but as written nothing I see will settle it — here is the version that would" is a complete and helpful
  answer.
- **Never accept a check whose failure mode is identical to its success mode**: *ask what your check would print
  if the thing were broken*.

**The false-pass field of the plan (§7) matters most when you advise.** The asker knows what they built. The asker
almost never knows how the instrument lies. Add that.

## 9. Threshold discipline → `live-debugging-proof-harness`

Every item states the bar that closes it and the minutia not chased:
`skills/live-debugging-proof-harness/references/validation-plan-and-thresholds.md`.

## Keeping this skill honest

Every numbered trap here cost a real debug cycle.

- If you find another trap, file it with its evidence: `python3 src/RimMandrake/Utils/lessons.py add "…"`. A curation
  session adds it here.
- If you find that one of these is wrong, say so loudly. Do not soften it.

### 🔴 Never CHOOSE between mods by reading a def dump

A dump shows the world after the load and after the dedup. One of the mods that you choose between can delete the
others at load. Then the others are **already gone from the dump**, and your preference list silently collapses to one
option.

Measured 2026-08-15, in `gen_races_mod.py` (fixed since):

- The tool declared "source preference BTD, then SWX, then Outer Rim". The tool picked with
  `next((c for c in cand if c in x))`, where `x` was the live dump. BTD, SWX and Outer Rim were three mods with the same
  species.
- BTD deletes the SWX and Outer Rim duplicates at load. So those candidates were never in `x`, and the fallback could
  not fire. The tool built all 70 species from BTD's gene lists.
- BTD's lists carry the head*bone* genes, but not the head*type* genes that the other donors had. So
  `guy762_Head_rodian` was dropped, and Rodians shipped with a generic scale head.
- The build was correct about everything that it could see, and blind to two thirds of its own input.

⇒ **To compare mods, read their XML on disk. Use the dump only for what the game finally built.** The same failure hides
behind any "best available source" rule.

A headless COUNT (a count of species with no head type) does not find the worst version of this fault.

- A species whose only head-forcing gene is a GENERIC one (`Outland_ScaleSkin`) has a head type and resolves clean. The
  species still renders as the wrong creature.
- Ask the running game for `forcedHeadTypes` per gene. Check WHICH head the gene forces, not whether one exists.

More traps for this section: [references/traps.md](references/traps.md) § **A quicktest finding and a campaign finding are different claims.** Report which.
