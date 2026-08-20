# Doc audit — `skills/` — 2026-08-20

**Scope:** 69 `.md` files, 14,366 lines, 26 skills (`skills/skills-workspace/` excluded — eval fixtures).
**Metric:** how many files must be edited to record ONE fact. **Analysis only; nothing was changed.**

---

## 0. The headline

The corpus is not bloated. **It is under-normalised.** Almost every file earns its
place; what costs money is that the *same fact* lives in six to twenty of them,
and there is no rule saying which copy is the original.

Worst measured case: **"a cold load costs ~23–30 minutes" is written into 20 places
across 14 skills, in two mutually-inconsistent forms.** Re-measuring that one number
is a 20-file edit today.

---

## 1. Why each high-churn file churns

### `skills/rimworld-modding/references/traps.md` — 31 lines, 38 commits
**Diagnosed, and already cured — do not act on this one.**
The churn is historical. Until 2026-08-15 the file was a **numbered index of every
trap plus a running count**, so adding a trap anywhere in the five topic files
forced a `+2/-1` edit here as well. The commit log shows exactly that shape:
twenty-odd commits of `2 insertions, 1 deletion` titled after a trap that landed in
a *different* file.

`f7de141` (2026-08-15, *"traps.md: delete the index, the counts and the protocol"*)
removed 230 lines and left a pure 31-line router. **Since that commit the file has
been edited once.** The bottleneck was real and it was removed. Its current text even
forbids the practice that caused the churn: *"Never number an entry, and never cite
one by number, line or heading."*

⭐ **This is the model for everything else in this report:** the fix was to stop the
file certifying facts that live elsewhere.

### `skills/rimbridge/references/traps.md` — 307 lines, 34 commits
**Churn is legitimate; the file is an append-only evidence log and 34 commits is
~34 lessons.** One edit per fact is the target cost, and this file hits it.

Two structural problems remain, neither of them the churn:
1. It has **no filing rule that survives contact.** §7 of `skills/rimbridge/SKILL.md`
   routes by *what failed* (engine API → `silent-failures.md`, bridge/client →
   `traps.md`), but ~19 of its ~58 entries are "reported success, changed nothing",
   and six are outright engine-API entries misfiled here (`:37`, `:134`, `:141`,
   `:147`, `:296`, `:302`). `silent-failures.md` §6 (`:99-111`) leaks the other way —
   that section is def-dump tooling, not an engine call.
2. It has **16 internal duplicates** (see §2).

### `skills/rimworld-modding/references/traps-tooling.md` — 205 lines, 20 commits
**Healthy for the same reason** — one lesson, one append. But it is the *default
destination*: `traps.md` tells the reader *"If you only read one, read
`traps-tooling.md`"*, and "a tool answered a different question" describes most
traps in the project regardless of subject. Several entries here are really art
(`:37-41`, vanilla textures not on disk) or def facts, filed under tooling because
the *fix* landed in a script.

### `skills/README.md` — 66 lines, 16 commits
**Every commit is a roster edit.** 11 of 16 subjects are literally *"New skill: X"*
or *"Three new skills: …"*. It is a hand-maintained index of a directory listing,
and it has already drifted: `rimworld-scenario-building` sits as a **stray bullet at
line 66, outside the table**, appended rather than filed. See §4.

---

## 2. The traps corpus — overlap

### Cost of adding ONE trap today
**Nominally 1 file. Empirically 2.**
Of 89 commits that touched `skills/rimworld-modding/references/` or
`skills/rimbridge/references/`, **36 touched one skills file and 53 touched two or
more** (7 touched three, 4 touched four, and one touched 23). The router edit is gone;
what remains is that a trap genuinely straddles two topic files and gets written into
both — 22 duplicate pairs found.

### Cross-file duplicates (13 pairs, file:line for each copy)
| the lesson | copies |
|---|---|
| `isJunk`/`junkDensityFactor`≈0 zeroed the scatterer | `traps-xml-and-defs.md:121-125` ∥ `traps-diagnosis.md:43` |
| Deployed ≠ live; a GenStep map is frozen at deploy time | `traps-mods-and-managers.md:119` ∥ `traps-diagnosis.md:41-45` |
| `jawa/get_def` `extra: null` reads as "field absent" | `traps-tooling.md:124-128` ∥ `traps-mods-and-managers.md:118` |
| `Armadillo` duplicate-key `ArgumentException` | `traps-xml-and-defs.md:11-15` ∥ `traps-diagnosis.md:29` |
| `About.xml`'s FIRST `<packageId>` is a dependency | `traps-tooling.md:87` ∥ `traps-mods-and-managers.md:79` |
| `search_debug_actions` enumeration livelock | `traps-diagnosis.md:19-23` ∥ `rimbridge/traps.md:159-163` ∥ `rimbridge/traps.md:291-294` |
| Absence from the def dump is instrument blindness | `traps-tooling.md:71` ∥ `rimbridge/traps.md:49-53` ∥ `silent-failures.md:101-105` |
| `Zone.AddCell` silently refuses (11 of 36 cells) | `silent-failures.md:52` ∥ `rimbridge/traps.md:302-307` |
| `success: true` ≠ the game moved | `rimbridge/traps.md:17-18` ∥ `silent-failures.md:130` |
| `ThingMaker.MakeThing` leaves the object half-built | `rimbridge/traps.md:37-41` ∥ `silent-failures.md:76-77` |
| `python.exe` vs `python3` picks the wrong interpreter | `rimbridge/traps.md:128-132` ∥ `:188` ∥ `:260-263` ∥ `traps-tooling.md:92-96` ∥ `traps-art.md:14` |
| A sample inflated into a proof | `traps-diagnosis.md:35-39` ∥ `rimbridge/traps.md:176-180` |
| The scrapfields `ChunkSlagSteel` count | `rimbridge/traps.md:165-174` ∥ `traps-diagnosis.md:41-45` |

### Within-file duplicates (9 more)
`rimbridge/traps.md` alone: `set_camera_zoom` rootSize (`:189` ∥ `:202-211`), armed
designator eats clicks (`:99-103` ∥ `:122-126`), stale screenshot frame (`:31-35` ∥
`:105-114` ∥ `:213-224`).
`traps-art.md`: last-loose-wins (`:15` ∥ `:73-79` ∥ `traps-mods-and-managers.md:96-101`),
`Graphic_Multi` facing substitution (`:37` ∥ `:45` ∥ `:81-87`), clean log proves nothing
about art (`:46` ∥ `:86-87`).
`traps-mods-and-managers.md`: RimSort Community Rules vanish → `userRules.json`
(`:11-15` ∥ `:78` ∥ `:85`).
`traps-tooling.md`: abstract/no-`defName` defs dropped from every index (`:13-17` ∥ `:173-174`).

### `traps-diagnosis.md` is an orphan bucket, not a topic
45 lines, five entries, **none of which is uniquely about diagnosis**:
`:11-15` → `traps-xml-and-defs` · `:19-23` → already in `rimbridge/traps.md:159` ·
`:27-31` → duplicate of `traps-xml-and-defs.md:11` · `:35-39` → `traps-tooling` ·
`:41-45` → duplicate of `traps-mods-and-managers.md:119`.
Its remit as advertised in the router (`traps.md:12`, *"believe a diagnosis, or call
into a running game"*) is the `rimbridge` skill's entire subject.

### The 5-way split is not predictable
The router sorts by **artifact** (xml · tool · art · mod · log). Real traps sort by
**failure mode** (silent no-op · stale consumer · wrong corpus · wrong instrument),
which cuts across all five. Three worked examples where two homes are equally defensible:
- `traps-tooling.md:37-41` "vanilla textures are NOT on disk" — an *art* fact, filed
  under tooling because the fix landed in `validate_patch.py`; its bundle half restates
  `traps-art.md:11-15`.
- `traps-mods-and-managers.md:96-101` reskin loses to load order — identical mechanism
  to `traps-art.md:73-79`; nothing distinguishes them.
- `traps-xml-and-defs.md:121-125` `isJunk` — a def field (xml), a count prediction
  (tooling), *and* present in `traps-diagnosis.md:43`. Three homes, two used.

### `rimbridge/traps.md` vs `silent-failures.md`
~58 lessons vs 36. The declared axis (`traps.md:3-5` vs `silent-failures.md:7-9`) is
bridge-versus-engine, and **neither file applies it consistently** — 4 hard duplicates
and 6+ misfilings in each direction. These are one file split on an axis nobody can hold.

---

## 3. ⚠️ CROSS-SKILL CONTRADICTIONS

### C1 🔴 `loadBottom` vs `loadAfter` — a live THREE-WAY conflict
The correction exists and was never propagated. Two stale texts are still shipping.

- `skills/rimworld-modding/references/load-order.md:42-44`
  > **"`loadBottom` is a *hint*. It asks for 'near the end' and creates no edge, so nothing prevents another mod landing after you."**
- `skills/rimworld-modding/references/traps-mods-and-managers.md:99`
  > **"`loadBottom` outranks `loadAfter`: the rule is then satisfied trivially by sinking to the end and carries no placement force relative to the donor"**
  — *the exact opposite of its own skill's `load-order.md`, two files apart.*
- `skills/rimworld-start-prep/SKILL.md:111-131` (the correct one, read out of RimSort's source 2026-08-19)
  > **"the previous text here ('loadBottom is a *stronger* constraint that defeats loadAfter') and `rimworld-modding`'s ('loadBottom is only a hint and creates no edge') were both wrong, in opposite directions… `loadBottom` + `loadAfter Y`: the edge is dropped, but the mod still lands after Y… The rule was redundant, not defeated. The genuinely broken pairing is `loadBottom` + `loadBefore` a non-bottom mod."**

`skills/rimworld-modding/SKILL.md:309-310` already cedes load-order ownership to
`rimworld-start-prep` — **the two reference files simply were not repointed.**

### C2 ⚠️ What a quicktest costs — 5 s vs ~30 s vs 118 s
- `skills/rimworld-debug-testing/SKILL.md:10` — "produces a full quicktest world+map in **5 seconds**"
- `skills/rimworld-debug-testing/SKILL.md:30` and `:307` — "A dev quicktest colony costs **~30 seconds**"
- `skills/rimbridge-companion/SKILL.md:61` — "a quicktest world **5 s** — both measured"
- `skills/rimbridge/references/traps.md:257` — `start_debug_game_ready {"readiness":"playable"}` "from the main menu to paused-and-drivable in **118 s**"

`rimworld-debug-testing` contradicts **itself in one file**. The spread is probably a
`readiness` level difference — **and not one of the four files says so.**

### C3 ⚠️ Cold load — `~25 min` vs `23–30 min`, in 20 places
`~25 min`: `rimworld-load-round/SKILL.md:14` · `rimworld-quests/SKILL.md:311` ·
`rimworld-xenotypes/references/verifying.md:77` ·
`rimworld-world-editing/references/tidally-locked.md:68` ·
`generating-rimworld-sprites/SKILL.md:11` · `README.md:39` ·
`rimworld-modding/references/traps-xml-and-defs.md:5`
`23–30 min`: `rimworld-debug-testing/SKILL.md:29` · `rimworld-deploy/SKILL.md:175` ·
`rimworld-load-round/SKILL.md:8` · `rimworld-start-prep/SKILL.md:8` and `:183` ·
`rimworld-modding/SKILL.md:85` and `:383` · `rimworld-modding/references/validation-plan.md:11` ·
`rimbridge/references/traps.md:71` · `rimworld-ideoligion/references/validation.md:8` ·
`rimworld-quests/references/mod_patterns.md:245` · `rimworld-savegame/SKILL.md:131` ·
`generating-rimworld-sprites/SKILL.md:266` · `gravship-layout/SKILL.md:345` ·
`rimworld-debug-testing/references/validation_plan_format.md:8`
**One re-measurement = 20 edits.** `CLAUDE.md` says `~25 minutes`; the memory file says `~23`.

### C4 ⚠️ Bridge tool counts, contradicting *inside one skill*
- `skills/rimbridge/SKILL.md:151` — "`JawaBenchTerrainTools.cs` | **32**"
  vs `skills/rimbridge/references/extending.md:26` — "`JawaBenchTerrainTools.cs` **all 14 [Tool] methods**"
- `skills/rimbridge/SKILL.md:86` — "**125 tools**: `rimworld/` (107), `rimbridge/` (18)" + `:145` "**91 `jawa/` tools**" ⇒ **216**
  vs `skills/rimbridge/references/capability-matrix.md:68` — "**141 tools** on the bridge overall"

`SKILL.md:145` even records the history ("91 on 2026-08-19, 32 that morning"), so
`extending.md` and `capability-matrix.md` are fossils of two different mornings.

### C5 ⚠️ Cherry Picker — the cutting tool, or ruled out
- `skills/rimworld-content-moderation/SKILL.md:69` — "**Cut with Cherry Picker, not by uninstalling**"
- `skills/rimworld-world-editing/references/curation-and-looks.md:14` — "⛔ **We are NOT using Cherry Picker for this.** Owner's ruling: *'we won't use Cherrypicker here, but simply clean the map.'*"

Genuinely scoped (the carve-out is map mutators/landmarks, which live in the save),
**but neither file points at the other**, so whichever one you load is the whole truth.

### C6 ⚠️ Active mod count — NINE different numbers, all stated as fact
570 (`rimworld-savegame/SKILL.md:92`) · 573 (`rimbridge/references/performance.md:59`,
`capability-matrix.md:41`) · 574 (`capability-matrix.md:66`) · 575 (`rimbridge/references/traps.md:161`) ·
578 (`rimworld-load-round/SKILL.md:47`, `traps-tooling.md:77`) · 579 (`rimworld-modding/SKILL.md:59`) ·
580 (`rimworld-debug-testing/SKILL.md:58,102`, `rimworld-deploy/SKILL.md:141`, `rimworld-start-prep/SKILL.md:286`) ·
585 (`rimworld-ideoligion/**` ×6, `rimworld-quests/references/design_and_community.md:20`) ·
587 (`rimworld-xenotypes/SKILL.md:14`, `references/appearance.md:4`).
Only `rimworld-ideoligion/references/authoring.md:8-12` and `design_and_community.md:20`
mark theirs as a **dated stamp** rather than a current fact. `CLAUDE.md` already rules
that the live number comes from `ModsConfig.xml`, never from a doc — **these 15 numbers
are all violations of that rule.**

### C7 ⚠️ Stale: "one game shared by FIVE seats"
`skills/rimworld-debug-testing/SKILL.md:29` · `skills/rimworld-deploy/SKILL.md:176` ·
`skills/rimworld-load-round/SKILL.md:8` · `skills/rimworld-start-prep/SKILL.md:8`.
`infrastructure/agents/` holds **four** seat files (BUILD, CHECK, DECIDE, REP) after the
2026-08-19 *"purge the retired seats"* commit. One retirement = four edits, none made.

### Redundant-but-agreeing (16 groups — cost, not risk, yet)
Steam Mods path restated in **7** files · `knownExpansions` over-counts by 5 in **6** ·
`ModsConfig.xml` path in **4** · `Player.log` path in **3** (two notations) ·
`PatchOperationFindMod` returns true on no match in **4** · `validate_patch.py`
`--live` vs `--defs` in **5** · def dump is disk-not-runtime in **5** · shortHash needs
the same mod set in **3** · RimWorld does not rewrite `ModsConfig.xml` on exit in **2**
(same measurement quoted twice) · `userRules.json` path in **3** · `search_debug_actions`
30 s timeout in **3** · 13-mod/22 s minimal list in **4** · quicktest 119,904 tiles in **2** ·
DLL cannot be written while the game runs in **3**.
Every one of these is a future C1: **a fact in N places drifts in N directions.**

---

## 4. Skill body vs `references/` — the split is GOOD, one exception

**Verified: every one of the 42 reference files is routed to from its own `SKILL.md`.**
There is no dead weight and no orphan; `package_skill.py` already fails a build on a
link to a file that does not exist. The 500-line rule is producing real files, not spill.

Three defects, none of them "unused":

**(a) Section-number coupling.** 17 `§N` citations inside `rimworld-modding/references/`
point into `SKILL.md`'s numbered headings (`§2`, `§4`, `§5b`, `§6b`, `§7`). The headings
still exist — but **renumbering `SKILL.md` silently breaks 17 pointers**, and nothing
validates them. This is exactly the failure the same skill's `traps.md:30` bans for
trap entries: *"never cite one by number, line or heading."* The ban was not applied here.

**(b) Four reference files under `rimworld-modding` duplicate whole SKILLS.**
- `references/minimal-load.md` (55 lines) and `references/spending-a-load.md` (36) are
  the subject of the `rimworld-load-round` skill.
- `references/deploying-and-liveness.md` (53) is the subject of `rimworld-deploy` — it
  even opens by saying so (`:3`, *"The deploy PROCEDURE is `skills/rimworld-deploy/SKILL.md`"*).
- `references/load-order.md` (60) is the subject of `rimworld-start-prep` — and is
  where contradiction **C1** lives.

**(c) The validation plan is maintained in THREE places, deliberately.**
`skills/rimworld-debug-testing/references/validation_plan_format.md:3-5` states the policy:
> *"**Copy this section into any skill that produces something a game has to render, run or resolve.** It is reproduced verbatim rather than linked because skills package as independent zips: a cross-skill pointer does not ship."*

That constraint is **real** — and the copies are already **not verbatim**: the canonical
file has *six* numbered fields with four worked false-pass examples;
`skills/rimworld-modding/references/validation-plan.md` has four *different* false-pass
examples and adds `§`-couplings; `skills/rimworld-modding/SKILL.md:379` carries a third
abbreviation. The seven-line `ITEM/SEE/ROUTE/PREDICT/CLOSE/RIDE/LIES` block also appears
in `editing-images`, `generating-images`, `generating-rimworld-sprites`, `gravship-layout`,
`rimworld-debug-testing/SKILL.md` and `rimworld-deploy/SKILL.md` — **8 files.**

🔑 **This is the one duplication that cannot be fixed by a pointer, and it is therefore
the one that must be MECHANISED.** See §6.

---

## 5. `skills/README.md` — can it be generated? Yes, mostly

All 26 skills have valid YAML frontmatter with `name` and `description`
(`package_skill.py` already parses and validates both, and enforces `DESC_MAX`).

| README section | generable? |
|---|---|
| the 26-row "skill \| when" table (lines 35–60 + the stray line 66) | **YES** — name + first sentence of `description:`, straight out of frontmatter |
| the 4-row owner table (lines 18–23) | **NO** — human assignment. Keep, but as `owner:` in each skill's own frontmatter, then render |
| the doctrine (lines 3–33, 62–65) | **NO** — hand-written, and rightly so. It changes ~twice a year |

**Evidence it should be generated:** 11 of 16 commits are *"New skill: X"*, and the
roster has **already drifted** — `rimworld-scenario-building` is a bullet at line 66,
outside the table it belongs in, because someone appended instead of filing.
A `--roster` flag on `package_skill.py` writing between two marker comments makes the
drift structurally impossible. **~30 lines of Python; the parser exists.**

⚠️ **A second roster exists at `infrastructure/STRUCTURE.md`, listing 12 of 26.**
Out of scope for this audit, but it is the same roster and it is already 14 short.

---

## 6. Target shape — cost and saving per change

**Ranked by saving ÷ effort.**

### T1 🔴 Fix C1 now (it is a wrong instruction, not a cost)
Delete the `loadBottom` claim from `rimworld-modding/references/load-order.md:42-44` and
from `traps-mods-and-managers.md:99`; replace both with a one-line pointer to
`skills/rimworld-start-prep/SKILL.md` §loadBottom.
**Cost:** 2 edits. **Saving:** stops shipping two opposite wrong answers.

### T2 One fact, one home + pointer — for the 16 agreeing groups and C3/C6/C7
Rule: **the skill named in the `description:` owns the fact; everyone else writes one
sentence and a path.** Cold-load duration → `rimworld-load-round`. Steam Mods path,
`knownExpansions`, `validate_patch.py` flags → `rimworld-deploy`. Load order,
`userRules.json`, `ModsConfig.xml` → `rimworld-start-prep`. Def-dump semantics →
`rimworld-modding/references/traps-tooling.md`.
**Cost:** ~45 edits, once. **Saving:** re-measuring the cold load goes **20 → 1**;
the mod count goes **15 → 0** (it is deleted, because `CLAUDE.md` already says read
`ModsConfig.xml`); a seat retirement goes **4 → 1**.

### T3 Refile the modding traps by FAILURE MODE, 5 files → 4
Retire `traps-diagnosis.md` (all five entries re-home; two are already duplicates).
Keep `traps-xml-and-defs` · `traps-tooling` · `traps-art` · `traps-mods-and-managers`,
and rewrite the router at `traps.md:6-13` to ask *what lied to you* rather than *what
were you holding*. Merge the 13 cross-file and 9 within-file duplicates.
**Cost:** one refactor pass, ~8 files. **Saving:** adding a trap goes **2 → 1** (the
measured average), and the "which file?" decision stops being a coin flip.

### T4 Merge `rimbridge/references/silent-failures.md` INTO `rimbridge/references/traps.md`
Same skill, same zip, an axis neither file holds, 4 hard duplicates and 12 misfilings.
Keep the loud `silent-failures` framing as the **first section** of `traps.md` — it is
described as *"the most expensive knowledge in the project"* and must stay first.
Update the two routing tables (`rimbridge/SKILL.md:30` and `:392`).
**Cost:** 1 merge + 2 table edits. **Saving:** a bridge trap goes **1 file, 0 decisions**.

### T5 Move the four straddling reference files out of `rimworld-modding`
`minimal-load.md` + `spending-a-load.md` → `rimworld-load-round`;
`deploying-and-liveness.md` → `rimworld-deploy`; `load-order.md` → `rimworld-start-prep`.
Leave a routing row in `rimworld-modding/SKILL.md`'s reference table.
**Cost:** 4 moves + 1 table. **Saving:** ~200 lines stop being maintained in the wrong
skill, and C1 becomes structurally impossible.

### T6 Mechanise the two things a pointer cannot fix
- **`package_skill.py --roster`** regenerates `skills/README.md`'s table from frontmatter
  between `<!-- ROSTER:BEGIN/END -->`. **Cost:** ~30 lines. **Saving:** README churn
  goes **16 commits → 0**; a new skill costs **1 file, not 2**.
- **`package_skill.py` injects the validation-plan block** from the single canonical
  `validation_plan_format.md` into every skill declaring `validation_plan: true`, at
  package time. This is the *only* honest answer to "a cross-skill pointer does not
  ship". **Cost:** ~40 lines. **Saving:** the plan format goes **8 hand-maintained
  copies → 1**, and the copies stop diverging (they already have).
- **A `§`-citation check** in `package_skill.py`: every `§N` in `references/` must match
  a heading in that skill's `SKILL.md`. **Cost:** ~10 lines. **Saving:** 17 silent
  pointers stop being able to rot.

### Bottom line
| change | files today | files after |
|---|---|---|
| add one trap | 2 (measured avg) | 1 |
| add one bridge trap | 1 + a filing decision | 1, no decision |
| re-measure the cold load | 20 | 1 |
| retire a seat | 4 | 1 |
| add a skill | 2 (skill + README) | 1 |
| change the validation-plan format | 8 | 1 |

⛔ **No skills are merged.** Every proposal moves a fact to the one skill whose
`description:` already claims it, or mechanises a copy that must physically exist.
