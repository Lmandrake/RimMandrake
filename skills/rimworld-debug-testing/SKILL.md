---
name: rimworld-debug-testing
description: Testing anything in RimWorld without spending a cold load — starting and destroying throwaway dev quicktest colonies through the bridge, deciding what a quicktest can and cannot prove, and knowing when disk evidence (def dumps, XML on disk) is not evidence about the running game at all. Use whenever a test needs "a map", whenever someone says they are blocked waiting for a world or a colony, before queueing anything into NEXT_RELOAD.md, when choosing between a bridge test and a game restart, when a def-derived claim needs checking against runtime, or when a result must be attributed to the campaign versus scratch.
---

# Debug testing: never wait for a map you can make

⚠️ **This skill is METHOD, not mechanics.** How to drive the bridge — the call
palette, debug actions, map authoring, speed, the companion DLL — is
`skills/rimbridge/SKILL.md`, and its hard-won failure catalogue is
`skills/rimbridge/references/traps.md`. **Read the traps file before any live
session; it is the one that stops you re-paying for a lesson.** This file only
answers *what to test on, and what a result is worth.*

A cold load costs **~23–30 minutes** and one game is shared by five seats. A dev
quicktest colony costs **~30 seconds** and belongs to nobody.

> 🔴 **"Blocked on a map" is almost never real.** Owner's ruling,
> `agents_def.md` rule 1c: **whoever holds the bridge may create and destroy dev
> colonies at will.** No permission, no queue entry, no waiting for worldgen.

**This skill is why that ruling exists.** On 2026-08-13 four seats sat idle
waiting for the owner to generate a world, holding tests that needed *a* map and
not *the* map. One of them — the only possible proof that `JawaIonWeapons` works
— had been hoarded for weeks as a scarce-session item. It never needed the
campaign at all.

---

## 1. Start one

```
rimworld/start_debug_game_ready
```

⚠️ **It exceeds the 30-second client timeout and succeeds anyway.** The response
is merely late. This has already cost real time, so it is the first thing here:

- **Do NOT retry** — the connection is desynced, not idle.
- **Do NOT re-issue** — you get a *second* map.
- **Open a fresh connection**, then poll `jawa/list_pawns` until it stops
  returning *"No current map"*.

Then it is an ordinary map: spawn, build, paint terrain, set time, screenshot.

**Destroy it by starting another, or by leaving it.** It is scratch. Nothing about
a quicktest is precious and nothing about it needs cleaning up — the only cost of
a stale one is confusing yourself about which map a result came from (§3).

## 2. What a quicktest proves, and what it cannot

| ✅ a quicktest settles it | ⛔ it cannot |
|---|---|
| does this def load, spawn, and behave | anything about **worldgen choices** — the Configure Factions page is spent once, on the campaign |
| does this tool/API call work at all | anything about **the campaign's own state** — its pawns, its factions, its map |
| does this art read correctly at game scale | **faction relations that took game-time to form** |
| does this terrain/map-gen override appear — **a quicktest map IS a newly generated map** | **anything requiring the real 580-mod load order to differ from what is loaded now** |
| does a silent failure actually fire (§4) | a claim about **save-file** contents |

**The rule of thumb:** a quicktest answers *"does this work?"* It never answers
*"is this true of our campaign?"*

## 3. Always say which map a result came from

**A quicktest finding and a campaign finding are different claims.** Report which
one you were on, every time, or the next reader cannot tell what you established.

🔴 **RETRACTED 2026-08-13 — nothing is untouchable.** This section said the
campaign save must not be tested on. **Owner's standing ruling overrides it:**

> *"NO AGENT SHOULD TRY TO PRESERVE MAP CONTENTS OR CAMPAIGN INTEGRITY AT THIS
> TIME OR ANY TIME IN THE FUTURE. YOU WILL BE INFORMED WHEN WE GET TO THAT
> PHASE. STOP ASKING FOR NOW."*

**Test destructively. Wipe, overwrite, regenerate.** Do not defer a test, hoard
one as a scarce-session item, or ask permission, to protect a map.

⚙️ **Saying which map a result came from still stands** — that is evidence
hygiene, not preservation. A quicktest finding and a campaign finding are
different claims regardless of how disposable both maps are.

## 4. A clean log is not evidence

Two independent traps, both measured here, both of which make "no errors" mean
nothing:

**Some failures cannot log even in principle.** `JawaIonWeapons`' user-string
heap is four bytes, all zero — there is no string for it to print. A clean
`Player.log` is *compatible with total failure*. The only proof is the positive
observation: put a KotOR droid in front of it and look.

**A negative needs a positive observation.** If the claim is *"X no longer
appears"*, absence of an error is not evidence. Go and see that X is gone.

## 4a. 🔴 LOOK AT IT. `take_screenshot` and then READ the image.

**Owner's instruction, 2026-08-13, and it is the most under-used capability we
have.** `take_screenshot` returns an absolute path, and **you can open that path
and actually look at the picture.** Not parse it — *look* at it.

**This matters because most of our evidence is inference and a screenshot is
observation.** `list_pawns` returning a xenotype name tells you what a field
says. A screenshot tells you what the player sees — which is the only thing the
v1 gate ever asked for:

> **"Every v1 item must be seen working in-game once. Not 'the log is clean' —
> SEEN."** — `V1_SCOPE.md`

**A def query cannot close that gate. A screenshot can.**

### What only a screenshot will tell you

- **Art that is technically correct and reads wrong** — right canvas, right
  alpha, unreadable at game scale. Every offline validator passes.
- **A texture that loaded as the magenta/checker placeholder.** Nothing logs it.
- **Terrain that painted but looks like the wrong material.**
- **A faction name that is GENERATED** — the Fallen Dominion's label is not a
  fixed string, so no grep finds it. You look, and you screenshot it.
- **UI state**: a quest actually sitting in the Quests tab, a letter actually in
  the notification pane, a pawn actually holding the weapon.
- **Anything where "it exists in a def" and "the player experiences it" differ**,
  which after today is most things.

### 🔴 A SCREENSHOT IS A CACHE, NOT AN OBSERVATION — read this before trusting one

**Two traps already cost real debug cycles and both are in
`skills/rimbridge/references/traps.md`. That file is the home; this is the
pointer.** They matter here because §4a tells you to trust an image:

1. **Screenshots overwrite by FILENAME, so a stale image reads as a failed
   action.** Measured: eight Jawas spawned, `success: true` on all eight, and the
   screenshot showed **empty ground** — because the call reused a `fileName` from
   an earlier failed attempt and the old file was read. `list_colonists` showed
   all eight exactly where requested.
   ⇒ **Give every screenshot a UNIQUE name**, or cross-check with
   `list_colonists` / `get_camera_state` before believing it. **When the action
   reports success and the picture says nothing happened, suspect the picture.**
2. **You cannot photograph a stale mesh** — every framed-shot tool moves the
   camera, and camera movement repaints the map sections. Any visual A/B over the
   bridge must ask what the act of looking changed.

⚠️ **So §4a and this section are in tension on purpose.** Look at the image —
*and* know that an image file is the one piece of evidence that can be silently
out of date. It is the same silent-failure family as everything else in this
project: nothing errors.

### How to use it well

1. **Screenshot before AND after** a change. One image proves a state; two prove
   a *transition*, which is usually the actual claim.
2. **Attach it to the finding.** A path in the report beats a sentence of
   description, and it lets the next reader disagree with you.
3. **Screenshot the irreversible screens** — worldgen, Configure Factions. They
   cannot be revisited, so an image is the only record that survives them.
4. **When a result surprises you, look before you theorise.** Two rulings were
   wrong for an hour today because they reasoned from a file instead of looking.

🔴 **CLEAR THE DEBUG LOG WINDOW BEFORE YOU SHOOT.** Owner's instruction,
2026-08-13. Dev mode's log window sits over the game and eats most of the frame,
so the screenshot documents *our own error console* instead of the thing being
tested. **Close it, and clear it, then take the shot.**

Two reasons, and the second is the one that bites:

1. **It occludes the evidence.** A shot that is 70% debug output proves nothing
   about the map underneath it.
2. **Stale lines read as fresh failures.** An unfiltered log window carries
   errors from earlier in the session, so the next reader attributes them to the
   thing in the screenshot. **Clear it, then act, then shoot** — anything showing
   afterwards was caused by what you just did, which is a far stronger claim.

⚙️ Zoom and camera matter: an object correctly spawned off-screen is
indistinguishable from one that never spawned. Frame it before you shoot.

## 5. 🔴 A def dump is DISK. The running game is RUNTIME. They differ.

**This cost two wrong rulings in one hour on 2026-08-13**, and it is the subtlest
thing in this file.

Mods mutate defs **at load**. Dedup, remap, implied-def generation — none of it is
visible in any file on disk. Measured live, from `Player.log`:

```
[BTD Xenotype Remix] Current xenotype count: 250
[BTD Xenotype Remix] Remapped 552 xenotype chances across 9 factions and 99 pawnkinds
[BTD Xenotype Remix] Successfully removed 100 duplicate xenotypes (BTD preference active)
[BTD Xenotype Remix] Final xenotype count: 150
```

A def dump taken before that ran showed **three** Jawa xenotypes and named
`OuterRim_Jawa` as the one the pawnKinds pinned. At runtime `OuterRim_Jawa` **does
not exist** — BTD deduped it away and remapped the pins onto `BTD_Jawa`. Two
rulings were made on the dump and both were wrong.

> **When the question is "what does the game HAVE?", only the live game or the
> log can answer it.** The dump answers "what is on disk", which is a different
> question wearing the same words.

⚙️ **The tell:** any mod whose log lines say *remapped*, *removed*, *merged*,
*generated* or *patched at runtime* has invalidated your dump for those defs.

## 6. Choosing: bridge test, quicktest, or a real load

Ask in this order and stop at the first yes.

1. **Can a file on disk settle it?** — an `About.xml`, a def, `ModsConfig.xml`.
   Free. But re-read §5 before trusting it about *runtime*.
2. **Can the live bridge settle it on whatever map exists?** — seconds.
3. **Does it just need *a* map?** — quicktest, ~30 seconds. **Most "needs a load"
   items land here.**
4. **Does it need the real campaign, or a changed mod list?** — only now is it a
   cold load. **A mod-list change is the one thing a quicktest cannot fake**, and
   it only lands on a restart.

**Before you put anything in `NEXT_RELOAD.md`, run this list.** An item that a
quicktest could have closed does not deserve a 25-minute slot.

## Keeping this skill honest

Every numbered trap here cost a real debug cycle. If you find another, add it with
its evidence — and if you find one of these is wrong, say so loudly rather than
softening it. Two of the rulings that produced §5 were mine and were confidently
wrong for an hour.
