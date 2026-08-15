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
> `infrastructure/agents/POLICY.md` §"Nothing outside the repo is precious":
> **whoever holds the bridge may create and destroy dev colonies at will.** No
> permission, no queue entry, no waiting for worldgen.

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
  returning *"No current map"* — two polls, ~30–45 s. ⏱️ Measured **78.5 s** on
  the 580-mod stack, so plan for well over a minute and poll rather than guessing
  a sleep.

⚠️ **It needs `rimworld/go_to_main_menu` first** if a game is already loaded —
from inside a running colony it will not start a fresh one.

🔴 **And it DISCARDS the current map without further warning** — that is how it
gets you a clean one. Anything another seat left on the old map is gone.
**Announce before calling it, and check nobody is mid-audit.**

Then it is an ordinary map: spawn, build, paint terrain, set time, screenshot.

**Destroy it by starting another, or by leaving it.** It is scratch. Nothing about
a quicktest is precious and nothing about it needs cleaning up — the only cost of
a stale one is confusing yourself about which map a result came from (§3).

### 🔴 Reversible, cheap and unobtrusive are three different properties

A quicktest is **reversible**. It is not free, and it is not invisible. Each
`start_debug_game_ready` is a full RimWorld **world** generation: a
`sea_seed_sweep.py` loop of seven took `/proc/loadavg` to **22.58** (RAM fine —
CPU and 9p-mount contention on the disk RimWorld streams assets from), and the
owner reported the game *"stuck on Generating Map…"*, then *"running badly"*.
Nothing was stuck. **From the keyboard, an agent-driven worldgen and a hang are
the same event** — there is no *"an agent is doing this"* indicator anywhere on
RimWorld's loading screen.

**Announce anything that occupies the game's own UI to the OWNER before it
starts, and report when it ends.** Announcing to peer seats does not count — they
cannot see it and do not care, while the owner can see it and has no way to
identify it. Prefer to run world or map generation when nobody is at the
keyboard, and check `/proc/loadavg` before and during: over ~10 on this box means
somebody's frames are being eaten. Applies to any loop over
`start_debug_game_ready`, `load_game`, `go_to_main_menu` or long `save_game`
calls.

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

⏸️ **SUSPENDED 2026-08-13 — not repealed. It comes back when play starts.**
This section said the campaign save must not be tested on. That protection is
correct *for a campaign being played* and premature now — nothing is being
played yet, so it costs tests and buys nothing. **Owner's standing ruling:**

> *"NO AGENT SHOULD TRY TO PRESERVE MAP CONTENTS OR CAMPAIGN INTEGRITY AT THIS
> TIME OR ANY TIME IN THE FUTURE. YOU WILL BE INFORMED WHEN WE GET TO THAT
> PHASE. STOP ASKING FOR NOW."*

**Test destructively. Wipe, overwrite, regenerate.** Do not defer a test, hoard
one as a scarce-session item, or ask permission, to protect a map.

🔔 **THE TRIGGER THAT BRINGS IT BACK:** the owner says the play phase has begun.
**Nobody else may reinstate it, and nobody should ask.** When that word comes,
this section reverts to *"the campaign save is untouchable — do not test on it"*
and every seat is told. **Until then, test destructively.**

⚠️ **This is written as a suspension rather than a deletion on purpose.** A rule
that is simply erased does not come back when the situation that justified it
returns — it is forgotten, and rediscovered by losing a colony.

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
> SEEN."**

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

## 7. 🔴 The validation plan — what this skill produces

Everything above answers *what a result is worth*. **The validation plan is how you
hand that judgement to somebody else** — it is this skill's deliverable, and this
skill is its home.

📄 **The canonical format, with worked false-pass examples:**
`/mnt/d/Luke/dev/Rimworld/skills/rimworld-debug-testing/references/validation_plan_format.md`
**Copy it verbatim into any skill that produces something the game must render,
run or resolve** — skills package as independent zips, so a cross-skill pointer
does not ship.

The six fields, one line each, so you know whether you need to open it:

| field | what it holds |
|---|---|
| **observable** | what a player SEES when it works — a positive sighting, never "no error" (§4) |
| **route** | the exact call, defName or click path that produces it — blocked on a missing tool is a finding, not a queue item |
| **prediction** | a number or string written BEFORE the look; without it you rationalise whatever you see |
| **threshold** | what CLOSES it, and the minutia deliberately skipped (§9) |
| **batch or solo** | most checks ride together; **a new assembly goes solo** or attribution dies |
| **false pass** | how *this* check lies — the field everyone skips |

```
ITEM     <what is being validated>
SEE      <the positive observation>
ROUTE    <exact call / defName / click path>
PREDICT  <number or string, before the look>
CLOSE    <the bar> — NOT chasing: <the minutia deliberately skipped>
RIDE     batch | solo (<why, if solo>)
LIES     <how this check produces a false pass>
```

Seven lines. If it does not fit, the item is really two items.

⚙️ **Write it before you run §6's list, not after.** Half the items that look like
they need a cold load turn out, once the observable and route are written down, to
be closable on a quicktest — and the plan is what makes that visible.

## 8. Advising: turning "can you check X" into a plan

Most requests arrive half-formed. *"Can you check the bandolier looks right?"*
*"Does the ion weapon work?"* **These are not checks. They are gestures at an
area**, and accepting one as written is how a load gets spent producing an opinion
instead of a finding.

🔴 **Ask two questions before you agree to look at anything:**

1. **"What would you SEE?"** — forces the observable. If the answer is "the log
   would be clean" or "it would work", there is no check yet; keep asking until a
   thing on screen is named. *Bandolier looks right* → **a pawn selected, facing
   north, with the strap drawn over the torso and not behind it.*
2. **"What number do you expect?"** — forces the prediction. A range is fine, a
   guess is fine, *"I don't know"* is the useful answer because it means the look
   cannot fail and therefore cannot succeed either. *Does the ion weapon work* →
   **a KotOR droid at 8 tiles drops in ≤3 shots.**

Then close it out loud: **"so the bar is one screenshot of X, and I am not chasing
Y."** State the threshold back to the asker (§9) — that is the half they did not
think about, and it is the half that costs them a second load.

⚠️ **You are entitled to refuse the shape, not the request.** "I can look, but as
written nothing I see will settle it — here is the version that would" is a
complete and helpful answer. **Never accept a check whose failure mode is
identical to its success mode** (`DOC_BUDGET.md`: *ask what your check would print
if the thing were broken*).

⭐ **Advising is where the false-pass field earns its keep.** The asker knows what
they built; they almost never know how the instrument lies. That is what you add.

## 9. 🔴 Threshold discipline — an item with no closing bar is inspected forever

**The scarce resources here are game loads and the owner's attention, not
thoroughness.** A check with no stated bar does not fail; it recurs — looked at
again next load, and the load after, because nobody can point at the sentence that
closed it.

Every item states **both halves**:

- **the bar** — the single thing that, once seen, ends the item. *"One screenshot
  of the pawn facing north with the strap drawn."*
- **the minutia NOT being chased** — named on purpose, so the next reader knows it
  was a decision rather than an oversight. *"NOT chasing: the two-pixel seam at the
  belt buckle, or the other three rotations."*

⭐ **A good threshold is usually ONE observation, not a battery.** Four rotations,
three light levels and a stress test is not rigour — it is an item that will not
fit in a load and will be half-done twice. Pick the one view most likely to be
wrong (usually north, usually the rotation nobody drew) and close on it.

**If you cannot say what would close it, you do not yet understand what you
built** — and that, not the load, is the thing to go and fix.

⚠️ **A threshold met is announced.** Say "closed by `<screenshot path>`" and stop
looking. Re-inspecting something already closed costs exactly what inspecting it
the first time cost, and buys nothing anybody asked for.

## Keeping this skill honest

Every numbered trap here cost a real debug cycle. If you find another, add it with
its evidence — and if you find one of these is wrong, say so loudly rather than
softening it. Two of the rulings that produced §5 were mine and were confidently
wrong for an hour.
