# TODO.md — the authoring backlog

_Started 2026-08-12. **Work we have decided to build but have not started.**_

Distinct from its two neighbours, and the distinction matters:

| File | Holds |
|---|---|
| `TODO.md` (this) | Accepted work, not yet started. A **queue** — things leave it by being built. |
| `design/Jawa/parked_mod_concepts.md` | Ideas we liked but have **not** committed to. A shelf, not a queue. |
| `NEXT_RELOAD.md` | Questions that need the **game running** to answer. |

Any thread may append. Each entry states the goal, what is already verified, and
what must be decided before code is written — so the next thread does not
re-derive the ground truth.

---


> ⚠️ **V1 SCOPE IS SET** — `file:///D:/Luke/dev/Rimworld/infrastructure/state/V1_SCOPE.md`.
> Everything ships **thin** except the gravship. Gate: **every v1 item seen
> in-game once.** Tag new items `[v1]` or `[v2]`; v2 bodies live in
> `file:///D:/Luke/dev/Rimworld/infrastructure/state/TODO_v2.md`.

## 0. [v1] ⭐ THE FACTIONS — one reskin ships; the roster is v2

**v1 bar (thin):** ONE authored faction — the **Imperial Desert Directorate**, on
`OuterRim_GalacticEmpire` as vessel, **label-level only**: name, leader title,
colour. Plus **Faction Control** suppression of factions that break the fiction.

**Gate:** the faction is **seen on the world map**. Needs `jawa/list_factions`,
which is companion work and lands only in a **shutdown** window — see
`V1_SCOPE.md` §Sequencing.

**Stage 1 ✅ done.** `Faction Control` is the authoring lever and unblocked U1
(`factionGrouping: Tight` + `CenterPoint` + `OverrideFactionMaxCount`, modded
factions covered). Configured in `Config/Mod_2882785581_Controller.xml`.

**Stage 2 ✅ done** — `file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/faction_engine_gap_audit.md`.
Headline: **the roster is not underspecified, it is specified in a vocabulary
that does not reach the engine.** `grep -c defName` on its 2,433 lines = **0**, so
**no faction has a vessel**. Only 4 of 12 roster parameters map to real fields.

⚠️ **`125 distinct fields` is the SCHEMA, not a checklist** — all 125 sit on all 88
defs because the dump serialises defaults, and **24 never vary**. The real surface
is dominated by `pawnGroupMakers` (50 distinct shapes).

**[v2] Stages 3 and 4** — the other 11 dossiers, `pawnGroupMakers`, memes,
ideoligions, the relations matrix, the deployable-config mapping. Licensing gate
stands: Outer Rim is **CC BY-NC-ND** — loading and our own `PatchOperation`s are
fine, **copying their defs into a mod of ours is a derivative.**

## 2. [PROJECT] ⚠️ PARTLY OPEN — `agents_def.md` contradicts itself on its own status

**a. ✅ DONE.** `CLAUDE.md` line 7 no longer states a mod count at all — it says
to read `ModsConfig.xml`. Filed as "561 is stale, write 568"; by the time it was
fixed the stack was 573, which is why the answer was to **remove** the number
rather than update it. Generalised into `DOC_BUDGET.md` §"A written instruction
rots" rule 1 (filed as `agents_def.md` **Rule 0.6**; moved 2026-08-13).

**b. ⬜ STILL OPEN.** `agents_def.md` line 8 reads *"Status: **DRAFT,
2026-08-12.** Open questions are marked ❓ and are for the owner to settle"*,
while its own §"Open questions" reads *"All settled 2026-08-12. Nothing
outstanding."* Both cannot be true. Given the file now carries Rules 0, 0.5 and
0.6 plus four ratified role definitions, **DRAFT is the stale half** — but the
header is the owner's to clear, not mine.

**Checked and clean:** `src/RimMandrake/WreckedMachines/Source/__pycache__/` is
covered by that folder's own `.gitignore` — verified with `git check-ignore -v`.

## 3d. [WORLD] `faction_roster_v2.md:42` claims `FactionDef` expresses "goodwill". It does not.

**Filed by [PROJECT] 2026-08-12** from the Stage 2 audit. `design/Jawa/worldbuilding/` is
WORLD's, so this is filed, not fixed (rule 9).

**The line**, at `file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/faction_roster_v2.md`
line 42:

> `FactionDef` technology level, **goodwill**, permanence of hostility, traders,
> pawn groups, settlement generation

**Everything on that line is correct except `goodwill`.** Probed across all 88
live `FactionDef`s and all 125 fields: **zero hits** for `goodwill` in any form.
The engine offers booleans about *hostility* — `permanentEnemy`, `naturalEnemy`,
`mustStartOneEnemy`, `permanentEnemyToEveryoneExceptPlayer` — not a signed
integer of goodwill.

**Why it matters more than a one-word slip:** this is the sentence that
authorised **all twelve dossiers** to specify a "Starting goodwill" number. The
error is upstream of twelve downstream decisions, so correcting it here stops the
next author adding a thirteenth.

### ⚠️ AMENDED within the hour — a mechanism DOES exist, and my first evidence was the wrong layer

**First filed as "no mechanism at either layer", on the strength of Faction
Control's config XML. That was the wrong source** — a RimWorld `Mod_*.xml` records
only what has been *changed*, never what the mod *supports*. Same wrong-layer
mistake as the Rebel Alliance one, three hours apart. **Re-checked against the
assemblies, which is the right layer:**

| mod | assembly evidence | verdict |
|---|---|---|
| **Faction Customizer** (`azravos.factioncustomizer`, 1.6 present) | `Dialog_ModifyFactionRelation`, `baseGoodwill`, `naturalGoodwillOffset`, `get_BaseGoodWill` | ✅ **CAN set base goodwill** |
| Faction Control | only `IsRandomGoodwillLoaded` — a **compat check for a different mod**, not a feature | ❌ confirmed, on better evidence |
| Sensible Factions | `biome` only | ❌ ruled out |
| *Random Goodwill* (the mod Faction Control probes for) | — | **NOT INSTALLED** |

**So `goodwill` still does not belong on line 42 — the claim there is that
`FactionDef` expresses it, and no `FactionDef` field does.** The fix stands
unchanged. What changes is the *recommendation*: goodwill is a **third-party
runtime mechanism**, not a def field and not a settings file.

⚠️ **Open, and it decides whether the 12 numbers survive:** Faction Customizer's
editor is a **`Dialog_`**, i.e. an in-game UI acting on live world state. It
carries `ModSettings` + `Scribe_Values` + `ExposeData`, so it *may* persist across
worlds — **unproven**. No `Config/Mod_3336572602*.xml` exists yet, which proves
only that nobody has touched its settings.

- **If it persists as mod settings** → the 12 roster numbers are authorable. Keep them.
- **If it only writes world/save state** → each number is a manual click per world
  roll, and 12 precise values are a liability in an *authored, reproducible*
  campaign. Reduce them to the engine's coarse hostility booleans and delete the
  rest.

**Do not design further on goodwill numbers until that is answered** — the U1
treatment still applies, just against a named candidate instead of nothing.

**Suggested fix:** strike `goodwill` from line 42 and point at
`design/Jawa/worldbuilding/faction_engine_gap_audit.md` §3, which carries the evidence and
the U1-shaped recommendation (do not design further on goodwill numbers until a
mechanism exists).

## 7. ⏳ Items that belong in `NEXT_RELOAD.md` but could not be filed there

**[PROJECT] 2026-08-12.** `NEXT_RELOAD.md` was held `M` all session — WORLD was
working in it — so per `agents_def.md` rule 6 these were not written there.

⚠️ **UPDATE 2026-08-12 21:4x: the file is now FREE** (`git status` clean), so the
stated precondition is met. **Held anyway, deliberately:** the game is live and
WORLD is mid-harvest, and appending ~120 lines to the queue someone is reading
is the collision rule 6 exists to prevent. **Migrate once the harvest settles**
— that is the next action on this item, and it is PROJECT's. They are all
load-round work and will be missed if they sit here.

✅ **ALL FOUR MIGRATED 2026-08-12 by WORLD — commit `8a6659e`.** They are in
`NEXT_RELOAD.md` with their caveats intact, including the load-bearing one: the
Rebel Alliance suppression proves itself by a **negative** observation, so a
clean log is not evidence. The table below is kept as the record of what was
parked and why, not as a live queue. **Do not re-file these.**

**WORLD added a constraint I could not have seen from outside their role:**
enabling the Empire and Rebel Alliance are **mod-list changes**, so they
re-stale the def dump through the fingerprint and must ride the *same* restart
as the pending assemblies. Split across two trips they quietly cost an extra
~25-minute load.

| item | tag | why it needs the load |
|---|---|---|
| Enable Outer Rim – Galactic Empire and verify the trooper ladder spawns | `[WORLD]` | §3. Solo-load waived, so it can share the trip |
| Rebel Alliance: enable + **suppress the faction** (W6) | `[WORLD]` | §4.1. ⚠️ success is a NEGATIVE observation — *no* Rebel settlement on the world map, **and** `OuterRim_A280Blaster` resolvable. A clean log proves nothing here |
| Re-cast rebel gear onto Junkers / Homestead (W7) | `[WORLD]` | §4.1. Without it the gear loads but nobody wears it |
| LK Mineable Resources: confirm the four ores scatter, check durasteel at 0.5 | `[WORLD]` | `desert_world_design.md` §3B(6) |
| Ion downs a droid — the capacity-based downing has **never been watched** | `[WORLD]` | §1 W8. Already queued by WORLD at `NEXT_RELOAD.md:784` ✅ |

### ⚠️ And the one nobody has filed at all

**`NEXT_RELOAD.md` still contains ZERO `[BRIDGE]` items.** Checked again
2026-08-12: 9 `[WORLD]`, 1 `[CREATE]`, 1 `[ANY]`, 1 `[?]`, **0 `[BRIDGE]`** —
while `agents_def.md` documents the tag convention using `set_terrain_batch` as
its worked example.

⚠️ **CORRECTION 2026-08-12, same day — my example was already stale when I wrote
it.** I claimed the `set_terrain_batch` timing test was "built, deployed and
inert until a restart". **It was run live this session and the result is in.**
`AGENT_BRIDGE_state.md:77` §"✅ MEASURED LIVE": paint 421 cells / 124 rects went
**1,611 ms → 14.0 ms, 115×**; capture went **6,086 ms → 17.5 ms, 348×**. Caught
by BRIDGE. I was reading a stale copy of their state file — which is precisely
the failure mode I spent the day correcting in other people's documents, so it
is recorded rather than quietly edited.

**The underlying point survives the correction, and BRIDGE confirms it.** There
is still real bridge work that needs the next load and is still not in the shared
queue:

* `jawa/spawn_batch` and `jawa/destroy_batch` — built, and **cannot be written to
  disk while the game runs**, so they need the shutdown→launch window.
* ✅ **The reload-survival test is now OWNED — BRIDGE took it 2026-08-12.** It was
  blind spot #1 in the completion survey: `build_plan.md:107` calls it ten minutes
  that de-risks the whole architecture, and it had sat ❓ in two docs with no
  owner. BRIDGE's own framing is the sharpest statement of why it mattered:
  **painted terrain is itself bridge-injected content, and nobody has ever
  checked that it survives a save/load** — after a session spent proving the
  paint is exact to the cell. It goes ahead of the new tools.

✅ **CLOSED 2026-08-12 18:30.** `NEXT_RELOAD.md` now carries a `[BRIDGE]` item
(B3) — the first ever. Counts are now `[WORLD] 15 · [BRIDGE] 1 · [CREATE] 2 ·
[ANY] 1 · [?] 1`. The file freed at 18:01 and BRIDGE filed within the half hour,
which is rule 6a working as intended. **All four agents have also published
cross-session addresses**, so the routing table resolves 4/4.

### ⚠️ THREE assemblies now want the same shutdown window — the waiver's premise has changed

**[PROJECT] 2026-08-12, for the owner.** BRIDGE established that a companion DLL
**cannot be written at all** while RimWorld runs — Windows refuses with
`WinError 1224` because the game holds it memory-mapped. So an assembly change
is gated on a **shutdown**, not a startup: it lands in the window between the
game closing and the next launch. The same mechanism applies to any deployed mod
assembly the game has loaded, which includes ours.

Three assemblies are now converging on that one window:

| assembly | whose | status |
|---|---|---|
| `JawaBench.BridgeTools` (companion) | BRIDGE | built; `spawn_batch`/`destroy_batch` waiting |
| `JawaIonWeapons` rebuild | WORLD | **only if the owner approves W8** |
| `OuterRimGalacticEmpire.dll` — 10,752 bytes | the Empire module | adopted; **solo-load waived by the owner** |

⚠️ **The waiver was granted on a premise that no longer holds.** Recorded at §3.1
as: *"the assembly is tiny, the pre-load baseline is clean and measured, and a
faction mod that misbehaves usually fails loudly and names itself. The cost of a
wrong guess is attribution effort, not a lost colony."* That reasoning assumed
the Empire would batch with **cosmetic XML work**. Batching it with **two other
assemblies**, one of which (`B3`) is itself gated on a second, is a materially
different attribution problem — three independent C# surfaces changing across one
23–30 minute load.

**This is not a recommendation to reinstate the solo rule.** It is a flag that
the owner's decision was made against different facts, and the owner may want to
re-decide. If the load goes wrong with all three in, the debugging cost lands on
whoever harvests the log (rule 8) — and the pre-load baseline that makes
attribution possible at all (0 dead mods, 0 Scribe, 25 cross-refs) is the thing
being spent.

### ✅ RE-PUT TO THE OWNER 2026-08-12 ~23:20 — **the waiver STANDS. Batch it.**

Asked explicitly against the changed facts above, with "split the assemblies out"
offered as an option. **The owner's answer: the waiver still stands.** The
question is closed; do not re-litigate it, and do not quietly split the load out
of caution.

⚠️ **The mitigation is now mandatory, not optional, and it is the owner's own
recorded condition:** *write the three expected-failure signatures down **before**
launching.* Batching is only affordable because the three fail in distinguishable
places — that property is worthless unless the distinctions are on paper before
the log exists. A signature invented after reading the log is not evidence, it is
a story that fits.

**Whoever calls the next load owes those three signatures in `NEXT_RELOAD.md`
before the game starts.** One per assembly: BridgeTools companion, JawaIonWeapons
(if W8 is approved), `OuterRimGalacticEmpire.dll`.

**And it is not only assemblies.** WORLD's fingerprint point means the two
mod-list additions must ride the *same* restart. So the next load would carry,
in one 23–30 minute trip:

* **3 C# assemblies** — BridgeTools companion, JawaIonWeapons rebuild (if W8 is
  approved), OuterRimGalacticEmpire
* **2 mod-list additions** — Galactic Empire, Rebel Alliance
* the existing `[WORLD]` verification queue — 15 items
* BRIDGE's B1–B3, of which **B1 is the reload-survival test** whose whole purpose
  is to answer an unknown before more is built on it

That is a lot of independent change riding one baseline. **B1 in particular
argues for care:** it exists to establish whether bridge-injected content
survives a save/load *at all*, and it is cleanest to answer on a stack that has
not simultaneously gained three assemblies and two factions.

**Cheapest mitigation if all three do ride:** they fail in different places.
BRIDGE's companion fails as an unregistered tool (`time_formation.py` reports it
directly); the ion rebuild fails as a droid that stuns but does not down (B3 has
both branches written); the Empire fails as a missing faction or missing
stormtrooper pawnkinds. **Write those three expected-failure signatures down
before launching**, and attribution stops being guesswork even with three DLLs
in flight.

---

## 9. ⚠️ [PROJECT] CORRECTED — this is a mode confusion, not a validator bug

**Filed by WORLD 2026-08-12 as "triple-counts defs in any mod whose LoadFolders
lists `/`". PROJECT tried to fix it 2026-08-12 and could not reproduce it.**
Leaving the item open only to carry the correction; **no code change is wanted.**

**The reported symptom is real** — a patch targeting one def reported
`xpath matches 3 nodes IN ONE MOD`, naming the same file three times. **The
diagnosis is not.** It blamed `_iter_def_xml()` being handed the mod root, but:

* `load_defs_scoped()` walks `os.path.join(folder, "Defs")`, **not** the folder.
* Outer Rim - Rebel Alliance's root has **no `Defs/` at all** (`1.4`, `1.5`,
  `1.6`, `About`, `Common`, `Common_Old`, `LoadFolders.xml`) — so the root is
  skipped outright.
* The version folders are **siblings** of `Defs`, never underneath it, so
  `os.walk("<root>/Defs")` can never reach `1.6/Defs`.

**Scoped mode is structurally incapable of the reported inflation**, and a
reproduction confirms it — probe patch on `OuterRim_RebelAlliance`, live
`ModsConfig.xml`, 573 active mods → 8,917 def files:

```
info  Operation[1] (PatchOperationReplace): 1 match(es)
      in Outer Rim - Rebel Alliance: FactionDefs.xml(1)
```

**Where the 3 comes from: `--all-versions`** — reproduced exactly, same probe
patch, 1,231 installed mods -> 34,073 def files:

```
info  --all-versions: UNSCOPED scan of 1,231 installed mod(s), every version
      folder. Match counts do not describe the running game.
...
WARN  Operation[1]: xpath matches 3 nodes IN ONE MOD and this operation applies
      to ALL of them  in Outer Rim - Rebel Alliance: FactionDefs.xml(1),
      Outer Rim - Rebel Alliance: FactionDefs.xml(1),
      Outer Rim - Rebel Alliance: FactionDefs.xml(1).
```

That is WORLD's reported symptom character for character. **Both modes confirmed:
scoped -> 1, unscoped -> 3.** Inflation in the unscoped mode is the advertised
behaviour, not a defect.

**So the real finding is a reporting one, and it is worth keeping:** the warning
text says *"IN ONE MOD"*, which reads as a scoping claim and is what made the
count look authoritative. In unscoped mode there is no load set, so "one mod" is
a statement about the folder a file sits in, not about what the game will load.
**A fix, if anyone wants one, belongs in the warning's wording — not in the
walk.**

⚠️ **Do not "fix" the walk.** Pruning version folders from `load_defs_scoped`
would change nothing (it never sees them), and pruning them from
`load_defs_all_versions` would break the one thing that mode exists to do.

**Lesson, logged in `traps-tooling.md`:** the report was verified, the *argument*
was not. A reproduction in the mode you actually use is cheaper than reading the
call graph, and it is the step that separates "this is broken" from "I ran it
differently".


---

## 11. [ANY] The git hook guards `add`, not `commit` — a bare commit still sweeps another agent's staged files

**Filed by CREATE, 2026-08-12, under Rule 0.5. I caused this, twice in one
minute, and the second time only stopped because I had just been burned.**

`CLAUDE.md` says *"Commit explicit paths only. Never `git add -A`, `git add .`,
or `git commit -a`"*, and `.claude/hooks/block_blanket_git_stage.py` enforces it.
**The hook guards the wrong verb.**

Four agents share **one working tree and one git index**. So:

```bash
git add MyFile.md          # allowed, correct, my file only
git commit -F - <<'MSG'    # ← commits the ENTIRE INDEX, including
...                        #   whatever another agent staged and
MSG                        #   has not committed yet
```

No blanket add. No `-a`. Nothing the hook can see. And the result was commit
`7c15278`, whose message describes a decision about a sled animal and whose
**content is entirely BRIDGE's** `AGENT_BRIDGE_state.md` and `NEXT_RELOAD.md`
edits. My own edit had failed silently earlier in the same command block, so the
commit contained *only* work that was not mine.

⚠️ **It recurred 30 seconds later.** The next `git add TODO.md` produced a
`--stat` showing `AGENT_BRIDGE_state.md` staged again — BRIDGE was actively
staging while I worked. That one was caught by the `git diff --cached --stat`
gate and unstaged with `git restore --staged`.

**History was NOT rewritten.** BRIDGE had already committed on top, so a reset
would have rewritten shared history under another agent's commit — worse than a
wrong message. Nothing was lost; the record is corrected in prose instead.

**What actually protects you, in order:**

1. **`git commit <paths> -F -`** — a pathspec on the *commit* bypasses the index
   entirely and cannot pick up anyone else's staged work. This is the real fix
   and it costs nothing.
2. `git diff --cached --stat` between add and commit, and **read it**. Already in
   `CLAUDE.md`; it works, and it is the only thing that saved the second one.
3. Never leave files staged. The window between `add` and `commit` is a window in
   which any other agent's commit takes your files.

**Suggested hook change:** extend `block_blanket_git_stage.py` to also intercept
`git commit` **without a pathspec** when the index contains paths the calling
session has not touched. Hard to scope perfectly — but even a warning naming the
foreign staged files would have stopped both instances.

### 🔬 CORROBORATED — three agents, three directions, verified in the log

BRIDGE reported the same thing from the other side before rebooting, and I
checked it against history rather than taking it on report:

| commit | its message says | what it actually also contains |
|---|---|---|
| `7c15278` | *"Sled beast: choose Eopie over Massiff"* | **all** of BRIDGE's `AGENT_BRIDGE_state.md` + `NEXT_RELOAD.md` — and none of the sled |
| `5f67910` | *"Rebuild rimbridge.skill"* | **38 lines** of `AGENT_BRIDGE_state.md` |

**Two commits, two different agents, one evening**, plus my own near-miss thirty
seconds after the first. BRIDGE supplied the staged files in every case and
described the window as one they created.

⚠️ **The decisive detail, and it kills "just be careful" as the answer:** in the
second case the `git diff --cached --stat` guard **ran and printed the foreign
file**, inside the same `&&` chain — and it was still missed. A check that fires
inside a chain nobody stops to read is not a guard, it is output. BRIDGE's own
words on rewriting their handoff: *discipline does NOT fix this.*

**None of the three of us could have seen this alone.** One swept, one swept
differently, one supplied the files. It took the collision of all three for the
shape — *the hook guards the wrong verb* — to become visible at all.

⚠️ **A hook is the only real fix and it is CONFIG, so it needs the owner.** A
peer asking for it is not authorisation. The shape BRIDGE and I both landed on:
fire on `git commit` **with no pathspec** while the index holds paths the
committing session did not add. Even a warning naming the foreign staged files
would have stopped all three.

**Checked and clean, so nobody re-checks:** nothing was lost in either event.
BRIDGE's content is intact in `7c15278` and they committed again afterwards in
`5f67910`; the working tree and index are consistent; and BRIDGE has been told
directly rather than left to find it.

---

## 15. ✅ DONE [CREATE] `graphics_overhaul_protocol.md:217` — premise now false

**FIXED `c585929`.** Premise replaced, table and warning kept verbatim — PROJECT's
call was right: a false premise under a correct conclusion *argues against* it,
and a reader who tests it makes exactly the swap the section prevents.

Re-measured after the install rather than assumed: `pip install UnityPy` **still
fails** (the install supplied `pip`, but PEP 668 externally-managed is unchanged),
so the venv is still required. `ensurepip` now exists, so the recipe dropped from
five lines to two; venv moved to `~/.venvs/rimworld` so it survives a reboot.
Verified end to end — UnityPy 1.25.3 installed, Bantha textures listed.

---

## 16. [WORLD] `refresh.py --patches` validates against NOTHING under WSL and reports ok

**Filed by [CREATE] 2026-08-13.** `src/RimMandrake/Utils/refresh.py` is WORLD's — `29c89f0` made
it run under both interpreters. That fix is real and it is **incomplete**, which
is why this is filed rather than fixed.

**What I saw.** `python3 src/RimMandrake/Utils/refresh.py --patches` prints:

```
--- validate (with --live)
    ok (exit 0)
...
=== VERDICT ===
  Everything is current.
```

**Why that is wrong.** Lines 290–292 still pass three hardcoded Windows literals
as `--defs`:

```
"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
```

**None of those paths exists from WSL** — `_first_existing` was applied to
`D_CONFIG` and `D_DUMP` but not to these. Run with exactly those arguments,
`validate_patch.py` says:

```
WARN  no def files found under the given --defs paths; live xpath checks skipped
OK TOTAL - 9 file(s), 0 error(s), 329 warning(s)      EXIT=0
```

So **every live xpath check is skipped and the exit code is still 0.** `refresh.py`
renders that as `ok`, and the run ends "Everything is current."

⚠️ **This is TODO §12's own pattern — a tool that fails toward success — inside
the file that reports whether everything is current.** The warning exists but is
one line among 329 and is discarded by the exit-code check above it.

**Already checked, so nobody repeats it:**
- Under `python.exe` (real, 3.13.14) **all three literals resolve** — measured,
  `os.path.isdir` true for each. So this is **WSL-only**: both interpreters now
  "work" and only one actually validates, which is worse than a clean break.

  ⚠️ _Filed first as an inference and listed under "checked" before it had been.
  Measured immediately after and it held — but it was the same shape as the
  defect it describes, so it is flagged rather than quietly upgraded._
- `D_CONFIG`/`D_DUMP` are correctly dual-form; only the `--defs` trio was missed.
- Not caused by the owner's Python install; it predates it and is now reachable
  more often because `python3` runs the script at all.

**Suggested fix:** give the three `--defs` roots the same `_first_existing`
treatment. Consider making `validate_patch.py` **exit non-zero** when `--live` was
requested and zero def files were found — a skipped check reported as a pass is
the failure mode, not the missing path.

**The line:** *"A bare `python` is not on PATH in WSL at all, so every `python …`
line fails with `command not found`."* **No longer true** — `/usr/bin/python`
exists, 3.14.4.

⚠️ **Why this is worse than ordinary staleness: the doc's conclusion is still
correct, and the false premise now argues against it.** The section's real point
— *the interpreter is PER-SCRIPT, and the obvious repair (swap in `python3`) is
wrong for this script* — still holds. But a reader who tests the premise, finds
`python` works, and concludes the section is stale will make **exactly the
interpreter swap the section exists to prevent.**

**Suggested fix:** keep the per-script table and the warning verbatim; replace
only the premise with something like *"`python` and `python3` both exist in WSL
(installed 2026-08-13) — but WSL's interpreter is the wrong one for this script;
it needs `python.exe`."* The hazard was never that `python` was missing.

**Already checked, so nobody repeats it:** `python src/RimMandrake/Utils/refresh.py` and
`python src/RimMandrake/Utils/package_skill.py --all` both run clean under the WSL interpreter
(exit 0). This item is about the *documented rationale*, not those scripts.

## 12. [v2] Tools that compare a proxy and fail toward success

**5 confirmed, all fixed by their owners 2026-08-12.** The lessons are in the
traps logs, which is where they belong and where they are searchable:
`skills/rimworld-modding/references/traps-tooling.md` (`f8eea20`, `cfaaf0d`) and
`skills/rimbridge/references/traps.md:1132` (`2b266d3`).

**The generalisation, kept here because it is short and it is the point:**

> **An artifact that records an OUTCOME cannot answer a question about a**
> **CAPABILITY.** The def dump records what the game *loaded*, not what a mod
> *ships*. A `Mod_*.xml` records what was *changed*, not what a mod *supports*.
> To know what something CAN do, read the thing that **defines** it.

> **Naming a failure shape does not inoculate the document that names it.**
> Three agents hit this in one evening, each while holding the lesson.

**The procedure, which is the deliverable:**

> 1. What artifact does this compare?
> 2. What can that comparison NOT distinguish?

Question 2 is operational: **construct the case where the thing changes and your
field does not.** Cannot build one → gate. Can → proxy in the artifact's clothes.

### 🔁 The counterpart lesson — take the RULE from a precedent, not the NUMBER

**PROJECT made this mistake and BRIDGE refused it, 2026-08-13.** The mirror image
of everything else in this item.

Reviewing the ship build I found the only shipped example ships **90
`HiddenConduit` / 50 `PowerConduit`** and recommended matching that **64% hidden**
split. BRIDGE declined, correctly:

> **The rule is the precedent; the ratio is an artifact of density.** That example
> is a small dense ship where conduit runs under rooms. Ours is a long open keel
> with almost nothing on it — **1 hidden / 184 exposed**. Copying 64% would hide
> conduit for no structural reason.

They implemented the *rule* instead — hidden wherever a keel tile carries a
building or node, exposed otherwise, selftest asserting no node sits on exposed
conduit.

> **A number from a valid source is only valid under that source's conditions.**
> The rest of §12 is *"you read a field that cannot answer the question"*. This is
> *"you read a field that answers a **different instance's** question"* — real
> field, authoritative source, wrong transfer.

**Before copying a figure from a precedent: what produced this number, and is that
thing true here?** If it is a density, scale or workload artifact, take the rule
and recompute the number.

### Open, and the only part still owed

- [ ] **`deploy_custom_mods.py` needs a per-FILE hold list.** The plan reports
      2 Jawa_Armoury files (owner ruled SHIP NEITHER) + 14 WreckedMachines files
      as drift and invites `--apply`. **Acting on it overrides an owner ruling.**
      CREATE is taking this. Interim: scope with `--mod`.
- [ ] 🔴 **`refresh.py` reports `current` for artefacts that do not exist.**
      **CONFIRMED by WORLD** from the code path, `src/RimMandrake/Utils/refresh.py:160-195`.
      Delete all 7 `observed/2026-08-13_pre-restructure/inventory/*.csv`, keep `GENERATED_FROM.json`, and it
      prints **current** — the row is built entirely from the stamp with **no
      existence check**. `contact_sheets/` and `Jawa_Armoury/Patches` are weaker
      still: **≥1** file passes for N. **`DefDump/` is sound** — the dump carries
      the mod list it was built from, so comparing it *is* comparing the
      artefact. **New member of the family: a stamp is not the artefact, and it
      can outlive what it describes.** Not v1-blocking. Fix: hash the artefact
      set, or at minimum assert an expected file count.
- [ ] 🔴 **`loadset_fingerprint()` answers "which mods are LISTED", never "which
      mods EXIST".** WORLD's, confirmed structurally by PROJECT in the code:
      `src/RimMandrake/Utils/refresh.py:107-116` reads `activeMods` out of `ModsConfig.xml` and
      hashes the names — **there is no existence check on any mod folder.** A
      listed-but-missing mod is invisible to the fingerprint and to the count.
      Distinct from §16, which is about `--patches` validating against nothing.
      ⚠️ **The demonstration has expired; the defect has not.** On 2026-08-13
      `refresh.py` printed *"Everything is current"* while
      `wiggler310.mythologicalcreatures` was listed and its folder was gone. The
      entry was cleared at **01:02:48**, so that exact case no longer reproduces
      — **do not conclude it was fixed.** Nothing in the code changed; only the
      data did. Fix: cross-check listed IDs against the workshop and Mods dirs.
- [ ] `validate_patch.py` reads `Patches/` only, never `Defs/` — does it SAY so,
      or just print clean?

## 13. [WORLD] ✅ CLOSED 2026-08-13 01:05 — removed, 573, new fingerprint

**Verified, and the prediction in this item was WRONG in an instructive way.**

```
workshop/294100/3520377015        GONE
ModsConfig.xml                    573 active, entry absent
fingerprint                       87050b782f95012f   (was e2d8e325bab06b68)
DefDump                           correctly STALE — "- wiggler310.mythologicalcreatures"
```

⚠️ **It did NOT happen on the clean exit, which is what this item and
`CLAUDE.md` both predicted.** Immediately after a confirmed clean exit
(Unity memory block present, game ran 23:04→01:01), `ModsConfig.xml` was
**untouched at mtime 22:38** and still listed the mod while its folder was
already gone. RimWorld rewrites that file only when the list changes
**in-game**; an unsubscribe performed in Steam is invisible to it. The file was
reconciled at **01:02:48** by a separate RimSort write, ~90 seconds later.

⇒ **A clean exit makes `ModsConfig` authoritative about what the game LOADED,
never about what is on disk NOW.** Check the entry *and* the folder, and read
the mtime as the tell. `CLAUDE.md` corrected by PROJECT.

⚠️ For ~1 hour the stack was **listed-but-missing** and `refresh.py` reported
"Everything is current" throughout — it hashes `activeMods` names with no
existence check. Filed in §12; the demonstration expired, the defect did not.

⚠️ **I wrote to `ModsConfig.xml` during that window and must declare it: a
verified NO-OP.** My removal matched 0 lines because RimSort had already done
it; I wrote the file back anyway and `cmp` against
`deployed/config/ModsConfig.pre-mythological-removal.2026-08-13.xml` is
byte-identical. Re-read before writing to a file a live tool also owns.

<details><summary>Original item, kept for the method</summary>

## 13. [WORLD] ⏳ Mythological Creatures! unsubscribed — verify after a CLEAN EXIT

**Owner unsubscribed 2026-08-13:** *"primitive, off-genre, and poorly
implemented."* Reasoning and the def-level audit are in
`file:///D:/Luke/dev/Rimworld/design/Jawa/mods/forbidden_mods.md` — do not duplicate them
here.

⚠️ **This cannot be verified while the game is up, and the failure mode is
reporting it wrong.** Steam does not delete an unsubscribed mod's folder while
RimWorld holds it open, and the running game rewrites `ModsConfig.xml` from
memory on exit. So a folder still present under `294100/3520377015` proves
nothing, and a `<li>` still in `ModsConfig.xml` proves nothing. **Never tell the
owner the removal "didn't land" before a clean exit.**

**After the next clean exit, in this order:**

```bash
# 1. did Steam actually remove it?
ls -d "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3520377015"   # want: No such file

# 2. is it out of the load list? parse activeMods -- NEVER grep -c '<li>',
#    knownExpansions adds exactly 5 (trap 45)
python.exe src/RimMandrake/Utils/refresh.py        # expect the count to drop by 1 and a NEW fingerprint

# 3. the dump and every artefact keyed to the old fingerprint are now stale
```

**Expected end state:** active mods **573** (from 574), a fingerprint that is
no longer `e2d8e325bab06b68`, and the live def dump correctly reported STALE
until the next load refreshes it.

⬜ **Then re-run the harvest on the first load without it** and confirm the
standing checks stay at baseline — in particular `Could not load reference to`
(Scribe) stays at **0**. That check is the one that matters here: it is the
signature of a *saved file* holding a dead name, which is exactly what removing
a mod with spawned creatures produces. Owner has confirmed the current saves are
throwaway, so a non-zero count there is informative, not an emergency.

⚠️ **Do NOT "fix" a Scribe hit by re-subscribing.** The decision is settled.


---

</details>

## 14. [BRIDGE] The visual-audit queue is not runnable — the bridge cannot style or turn a pawn

**Found 2026-08-12 while running WORLD's on-screen checks**, which the owner
assigned to BRIDGE. Four of the five items could not be completed, and **not for
want of effort — the tools do not exist.**

**Missing capabilities, confirmed by enumerating all 141 registered tools:**

| needed | exists? | blocks |
|---|---|---|
| set a pawn's **hairstyle** (`OuterRim_CereanMane`) | ❌ none | `CereanMane_south` — cannot put the hair on a pawn at all |
| set a pawn's **facing** / rotation | ❌ none | every "face it south, then rotate through four facings" check |
| read the **faction list** | ❌ none | W6's Rebel-suppression half |
| spawn a specific **xenotype** (Hutt) | ❌ not via `kindDef` | V5 Hutt eyes on fresh spawns |

`rimworld/set_draft` and `rimworld/move_camera` exist; nothing sets pawn style or
rotation. Stepping ticks makes a pawn wander to a random facing and, in the run
that produced this note, under tree canopy — **that is not a test, it is a wait.**

**What DID work, so the gap is precisely bounded:** `OuterRim_MSEDroid` needed no
styling and no rotation, and its check passed cleanly at close zoom. Every item
that failed, failed on styling or facing.

⚠️ **The finding that matters is not the missing tools — it is that the queue was
SIZED as though it were runnable.** These items have sat as "dev-spawn it and
look" for days. That reads as cheap. It is not cheap; for four of five it is
currently impossible, and no amount of care at the bridge would have changed
that. **A queue item's cost was never checked against the tools that exist.**

**Proposed** — all are companion work, so all are gated on a game *shutdown*
window, not a startup.

⚠️ **Re-ordered 2026-08-12 against `V1_SCOPE.md` (PROJECT, owner's call). My
original ordering was by cost-to-build; the right axis is the v1 gate.**

1. 🔴 **`jawa/list_factions` — V1-CRITICAL, build first.** defName, hostility,
   settlement count. The v1 gate is "every item SEEN in-game once", and that
   needs a faction actually read off the map; it also answers W6's "did the
   suppression apply" without a UI read. **This is the highest-priority BRIDGE
   item on the board**, and my own list had it third because I ranked by ease.
2. `[v2]` `jawa/set_pawn_rotation` — trivial (`Pawn.Rotation`), unblocks every
   four-facings art check at once. Still the best value per line of code — but
   the checks it unblocks are cosmetic polish, which is v2.
3. `[v2]` `jawa/set_pawn_style` — hair, beard, tattoo by defName. Cerean mane.
4. `[v2]` `jawa/spawn_pawn` gaining a `xenotype` parameter — V5 Hutt eyes.

⚠️ **BRIDGE tooling is now ON the v1 critical path**, because the gate cannot
afford ~25 min per game load and verification therefore rides the bridge. That
changes what this item is: not a convenience backlog, a dependency.

**Until these exist, do not queue an art check that needs a specific hairstyle or
a specific facing** — file it as blocked and say which of the four it needs.

## 17. [PROJECT] [v2] Evaluate **Space Tower** — orbital dungeon, and does it reach the gravship?

**Owner's ask, 2026-08-13**, routed to PROJECT. Is this interesting content —
semi-orbital structures the gravship could interact with — and is it *usefully*
on-brand? Needs research, not a verdict from the store page.

**Tagged `[v2]`** per `V1_SCOPE.md`: adding a content mod is new scope, and v1 is
set. Filed here rather than acted on because the mod list and "is this on-brand"
are not CREATE's call.

### What it is, measured from the files rather than the description

| | |
|---|---|
| mod | **Space Tower** (singular), author HaiLuan |
| packageId | `HaiLuan.SpaceTower` |
| folder | `file:///C:/Program%20Files%20(x86)/Steam/steamapps/workshop/content/294100/3527936083/` |
| versions | **1.6 only** |
| hard dependency | `HaiLuan.CustomQuestFramework` (ws `2978572782`) — **folder is present on disk** at `.../294100/2978572782/` |

Its own description: *"This quest generates a space tower site in orbit, which
players can explore — essentially, a space-themed version of a dungeon."* It
ships one `QuestScriptDef` (`ST_Quest_SpaceTower`), a multi-level map set
(`ST_MapPart_TowerLevelI` … `IIII` plus `TowerLeveRest`), buildings, items, and a
gold chest. Hostiles are `AncientsHostile`.

### ⭐ The two lines that decide the owner's actual question

From `.../1.6/Defs/QuestScriptDefs/ST_Quest_SpaceTower.xml`:

```xml
<planetLayer>Orbit</planetLayer>                            <!-- line 21 -->
<canOccurOnAllPlanetLayers>False</canOccurOnAllPlanetLayers> <!-- line 95 -->
<everAcceptableInSpace>False</everAcceptableInSpace>         <!-- line 93 -->
```

**The site is generated on the `Orbit` planet layer — the same Odyssey layer a
gravship flies to. That is the encouraging half.**

⚠️ **But `everAcceptableInSpace: False` is the whole risk, and it points the other
way.** If that gates whether the quest can *fire* while the colony is in space or
aboard a gravship, then a Jawa clan living on a gravship might never be offered
it — the exact interaction the owner is asking about would be the one case it
excludes. **Do not read those three fields and conclude either way; find out what
`everAcceptableInSpace` actually gates.** Reading a def field and inventing its
runtime consequence has cost this project twice today (see `AGENT_CREATE_state.md`).

### What CREATE already checked, so nobody repeats it

- ✅ The mod is on disk and is 1.6.
- ✅ Its dependency CQF is on disk too.
- ✅ It genuinely targets the orbital layer — not a re-skinned ground site.
- ✅ It contains a real `QuestScriptDef`.
- ⬜ **Not checked:** whether either mod is *active* in the running game. The game
  was live when this was filed and mod-list state on disk is not authoritative
  then (`CLAUDE.md`). A folder proves nothing about subscription.
- ⬜ **Not checked:** licence, or whether CQF conflicts with anything in the stack.

### 🔗 One connection worth making before deciding

**`V1_SCOPE.md` row 3 is "One `QuestScriptDef`", owned by CREATE, currently at 0
and unworked.** Space Tower ships a working, non-trivial `QuestScriptDef` that
targets the orbital layer. Even if the mod is rejected as content, **it is a
ready-made worked example for the thing v1 needs us to author** — so the read is
worth doing either way, and that is an argument for doing it sooner than "v2"
would normally imply.

## ✅ Closed — one line each, so nobody re-files them

| item | outcome | commit |
|---|---|---|
| 3a. Do symlinked skills get discovered? | **Yes.** Layout stays; the directories fallback is dead. | `0ee33f6` |
| 3c. `src/Jawa/README.md` said four mods | Six. Corrected. | — |
| 5. Docs instructed the call that livelocks the game | All five instances **replaced**, not just warned. | `0b44a1c` |
| 8. Companion build output untracked | Tracked; false rationale removed. | — |
| 3b2. rimbridge traps described its own size | Fixed, then the **fix decayed too** — "short" → "It is 800 lines" at 1,127. Number removed, not corrected. | `b267fab` `297f19d` |
| 3b3. `savemap.py` save-write gotchas | `paint()` no longer orphans `underGrid` (measured 829 buried cells; tested 4/4 incl. write+reload). **`fogGrid` deliberately NOT fixed** — see below. | `cccfeb5` `914eecd` |
| 10. `refresh.py` interpreter/path failures | **Both halves fixed.** `D_CONFIG`/`D_DUMP` are candidate lists via `_first_existing`; `run()` now prints `FAILED (exit N)` and `do_offline` refuses to stamp on failure. **Verified under WSL `python` — clean run, exit 0.** | `29c89f0` |

### ⚠️ Emerging pattern — sometimes the correct output is a DO-NOT-DO-THIS

**Two instances in two days, both BRIDGE's, both where the obvious repair is the
destructive one:**

- **`fogGrid`** — `fogGridDeflate` is **7,813 bytes for 62,500 cells = one BIT
  per cell** (verified: `ceil(62500/8)` = 7,813 exactly), while every `GRIDS` row
  unpacks as unsigned **shorts**. Adding fog to `GRIDS` would decode a bitfield at
  the wrong width and **silently corrupt the fog of a healthy save.** Leaving it
  stale is safe by construction: never decoded, never re-encoded.
- **§3b2's line count** — the maintenance instinct ("helpfully put the number
  back") is what caused the defect both times.

**So a closed item may ship a prohibition rather than a fix**, and the
prohibition has to say *why* or the next person will "helpfully" undo it.

⚠️ **Also flagged by BRIDGE, untested:** `foundationGrid` is **uniform across all
62,500 cells**. A rule inferred from a uniform sample is how a wrong rule gets
baked in — do not generalise from it.

**A third instance, and it was PROJECT's — the *quiet* one.** My collapse above
said *"the detail lives in their traps entry"*. **There was no traps entry**; the
detail was in a commit message only, so the collapse would have destroyed the
only searchable copy. BRIDGE caught it and wrote the entry (`cbae29c`, now 25/25
in the index). The same sweep also left an **orphaned `3b3-orig` body** reading as
open ~500 lines above its own closure.

**Both are now `DOC_BUDGET.md` §"A written instruction rots"** (was `agents_def.md`
Rule 0.6)**:** *check the target exists before you
collapse, summarise or defer* — and *assert block boundaries before deleting*.
**Audited the rest of this file after the catch: all 12 cited commit hashes and
all 5 cited paths resolve.**

**A fourth instance, also mine, and it is the one a sweep is most prone to:**
§10 (`refresh.py`) was **already fixed** in `29c89f0` when my sweep reformatted it
and carried it forward as open. **A sweep that reformats without re-checking
launders stale items into fresh-looking ones** — they gain a recent commit date
and read as current. **Re-verify an item is still open before you keep it**, not
just before you close it.

---

## 20. [?] `src/RimMandrake/Utils/ilscan.py` reads only `ldc.r4` — it cannot see stored defaults `[v2]`

Filed by CREATE 2026-08-13 while closing queue C4. **Tagged `[?]` because I could
not tell whose tool this is** — it is a repo Util, not art and not a bridge tool.
Not v1: nothing in `V1_SCOPE.md` depends on it, and C4 closed without the fix.

**Symptom:** run it against `GravshipSize.dll` and it prints `Field rows: 96` and
essentially nothing useful.

**Cause, verified by reading it:** the opcode switch handles exactly one case —
`Utils\ilscan.py` L152, `if op == 0x22:  # ldc.r4`. A .NET settings class loads its
defaults with `ldc.r4` **followed by `stfld` (0x7D)**, and without decoding
`stfld` the constants cannot be attributed to a field name. So the tool sees the
values and cannot say what they are.

**Fix:** decode `0x7D` and pair each preceding `ldc.r4`/`ldc.i4` with the field it
stores into. **Verified this works before filing** — widening the filter that way
dumps both compiled default blocks, and the parse validates itself: the Ludeon
block comes out `18.9 / 16.9 / 6 / 18.9`, support `500 / 250`, **reproducing
`Data\Odyssey\Defs\ThingDefs_Buildings\Buildings_Gravship.xml` exactly.** The mod
block comes out `25.9 / 25.9 / 8 / 25.9`, support `500 / 500`.

**Why it is worth the small fix:** that second block is the only place
`gravExtenderSupport = 500` is recorded anywhere — it is absent from the config
file, and `src/RimMandrake/mapsynth/ship_designs.py` had claimed it came from there. **This tool
is how a compiled-in default gets proven rather than assumed**, and mod settings
increasingly live in C# rather than XML.

⚠️ **The working version was never saved** — I widened the filter in a throwaway
copy to check the claim, and the scratchpad is `tmpfs`. Whoever takes this
re-applies a two-line change; nothing is lost but nothing is banked either.

---

## 21. [?] Two donor mask filenames carry an underscore RimWorld will never look for `[v2]`

**Found by CREATE while building C5's `BlastDoorFrameAsyncFix`, 2026-08-13. Not
mine to fix — it is a different texture slot from the one I was authoring, and
fixing it is a second override mod.**

In *Doors Expanded Star Wars edition* (`Lumi.doorsexpanded`, ws `3550435517`),
under `Textures/Things/Building/Door/Blast/`:

```
SWDoorBlastBDoor_Frame_east_m.png     <- underscore before the m
SWDoorBlastDDoor_Frame_east_m.png     <- same
```

RimWorld builds a `CutoutComplex` mask path as `texPath + "_eastm"`, with **no
underscore**, so neither file is ever loaded. Both doors' **ordinary** east
frames therefore tint through the **north** mask today — a different canvas and a
different layout.

**Verified before filing:** all three affected defs (`PH_DoorThickBlastBDoor`
L288, `PH_DoorBlastCDoor` L372, `PH_DoorBlastDDoor` L456 in
`.../3550435517/Defs/ThingDef_Building/Heron_Doors.xml`) declare
`shaderType CutoutComplex`, so a mask is genuinely wanted; and base Doors
Expanded ships `DoorBlastDoor_FrameAsync_eastm.png` for the sibling slot,
confirming the correct spelling has no underscore.

**Checked and CLEAN, so nobody repeats it:** the `_eastm` files we ship in
`src/RimMandrake/BlastDoorFrameAsyncFix/` are spelled correctly and are a
different slot (`doorFrameSplit`, not `doorFrame`) — this defect is untouched by
that mod either way. There is **no log signal** for it: a missing mask is not an
error, it silently falls back.

**Fix if taken:** ship both files at the correct name in a `Lumi.doorsexpanded`
override mod — same bytes, no art to draw, exactly the C6 shape. `[v2]`, because
it is a tint artefact on one facing of two doors, not a missing texture.

---

## 22. [?] "RimWorld rewrites `ModsConfig.xml` on exit" is FALSE and is written in five more places

**Owner's ruling 2026-08-13:** *"RimWorld does NOT rewrite that file on exit, nor
does RimSort. It is only modified by these agents, or by the user using
RimSort."* And the process: **OPS determines which mods go in; the OWNER does the
RimSort ordering by hand and then tells OPS it is done and the game is started.**

CREATE has corrected its own two rows (`NEXT_RELOAD.md` §CREATE'S ROWS (a),
`queue/CREATE.md` C5/C6/C11). **The claim is still asserted, verbatim or nearly,
in five files CREATE does not own** — each needs its owner's hand, and two are
skills, which a peer's ask cannot authorise editing:

| file:line | what it says |
|---|---|
| `skills/rimworld-load-round/SKILL.md:47` | "…rewrites `ModsConfig.xml` on exit" — and the SKILL's own front-matter description sells "what ModsConfig.xml is and is not authoritative about" |
| `skills/rimworld-modding/references/traps-mods-and-managers.md:69` | whole trap entry *"Mod-list state on disk is not authoritative while the game is running"* rests on it (indexed at `traps.md:107`) |
| `skills/rimworld-modding/SKILL.md:326` | "the manager holds rules in memory and rewrites the file on exit" |
| `infrastructure/state/TODO.md:644` | §13, the Mythological Creatures removal — "the running game rewrites `ModsConfig.xml` from memory on exit", used to say a `<li>` still present "proves nothing" |
| `design/Jawa/mods/forbidden_mods.md:171` | same, gating a follow-up on a clean exit |

⚠️ **The Steam half of those entries is a SEPARATE claim and may well still be
true** — Steam does not delete an unsubscribed mod's folder while RimWorld holds
files open in it. Do not delete those sentences wholesale; only the
`ModsConfig`-rewrite half is refuted.

**Where it was already acted on, not just written:** the seven fix mods
(`mandrake.gravshipastronautfix`, `sauridfrillfix`, `toolbeltfix`,
`researchkiteastfix`, `blastdoorframeasyncfix`, `cereanmanefix`, `msedroidfix`)
were held back from the mod list as a "shutdown-window change" and are **still
absent from `ModsConfig.xml`** (checked 2026-08-13 16:5x — only the seven older
`mandrake.*` entries are there). They could have been handed to OPS and the owner
at any point today.
