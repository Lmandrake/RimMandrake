# Determinism assessment — what an LLM is doing here that Python should do

Written 2026-09-17 on the **Mac laptop**, offline, against the working tree at
`f873119d9` (plus 28 uncommitted walk edits from a repair sweep another window was
running while this was measured — where that matters it is said explicitly).

**Owner's ask, verbatim:** *"launch a thorough assessment of the current process to see
if we can pull out more of what LLM's are doing in the whole rimflow, northstar, and all
other aspects of this rimworld build system into deterministic Python code to make it
more robust. This is a critical maturation of our system and will speed us up a LOT."*

Every number below is marked **CONFIRMED** (measured on disk in this session, with the
command in §11 so it can be re-derived) or **UNCERTAIN**. Nothing is taken from a doc's
own assertion. Where a fact could not be established on this machine it says
**UNMEASURABLE HERE** and names why.

## 0. Machine caveats that bound this assessment

- **CONFIRMED** No def dump on this laptop: `measure count TerrainDef` answers
  `UNMEASURED dumpdb — no defs.sqlite at /mnt/c/…`. So any candidate needing
  post-patch def truth is **Desktop-only**; candidates below that need identifiers
  index **our own XML and C# on disk**, which is fully available here.
- **CONFIRMED** No RimSage on this laptop (CLAUDE.md, re-confirmed: no `mcp__rimsage__*`
  in the toolset). No candidate below needs engine internals.
- **CONFIRMED** `python3 src/RimMandrake/Utils/run_selftests.py` → `43/54 passed
  (wall 25.4s, 8 workers)`. 8 of the 11 failures are `dotnet.exe not found` /
  Windows-only. **A new selftest costs well under a second in a 25-second budget.**

---

## 1. The one structural finding everything else hangs off

**The system's join key is a mod's folder name, and nothing asserts the join.**

Five independent registries are keyed on the same bare string — a mod folder name —
and each has drifted from disk on its own schedule:

| Registry | keyed by | who writes it |
|---|---|---|
| `src/<tier>/<Name>/` | the folder itself | FOUNDRY |
| `design/validation_walks/<tier>/<Name>.md` | file basename (`northstar.find_walk`) | agents |
| that walk's `subject:` header line | a path, written by hand | agents |
| `infrastructure/state/modcheck_status.json` | `<Name>` | `modcheck/status.py` |
| `rimflow capability` | `<Name>` | `rimflow capability set` |

`modcheck` resolves a mod by folder name in **two places that never check each other** —
`runner.find_mod_dir(mod)` (walks `src/{RimMandrake,RimStarWars,RimUtinni}/<mod>`) and
`northstar.find_walk(root, mod)` (globs `design/validation_walks/*/<mod>.md`). Two
reorganisation waves (`MOD_CONSOLIDATION_SPRINT_1`, and `cade628c1` FlowWorks Phase 1,
2026-09-16) moved mods *inside* other mods. Result, all **CONFIRMED** today:

- **24 of 78 walk basenames resolve to no `src/<tier>/<Name>` folder at all.**
  `modcheck run <that name>` raises `RuntimeError: no mod folder named …` — 24 walks are
  unrunnable by the only tool that reads them.
- **9 subject paths are claimed by more than one walk, covering 30 of the 78 walks.**
  `src/RimStarWars/SWBestiary` is the declared subject of **7** walks; `MandrakePatches`
  of **6**. Only one basename per folder can ever be reached by `modcheck`, so the other
  6 and 5 north stars can never bind however carefully authored.
- `src/RimMandrake/Pits` **contains only `__pycache__`** — Pits was merged into FlowWorks
  at `cade628c1` — yet `Pits.md` still declares `subject: src/RimMandrake/Pits
  (packageId mandrake.rm.pits)`, that packageId exists in **no** `About.xml`, and Pits'
  north star is **VALIDATED with 11 binding bars**.
- `modcheck status` (no arg) prints **`FluidCanals  GREEN`**. That mod was renamed
  2026-09-16 and does not exist; `modcheck status FluidCanals` **tracebacks**.
  `modcheck status FlowWorks` — the mod that does exist, and holds a VALIDATED 13-bar
  checklist — prints **`NEVER RUN`**.
- `modcheck status` (no arg) prints **`Pits  GREEN`** while `modcheck status Pits`
  prints **`STALE`**. The aggregate view reads the recorded field; the per-mod view
  re-derives. **The summary lies where the detail tells the truth.**
- `rimflow capability list` carries **3** entries whose name resolves to no folder
  (`FireEcology`, `FluidCanals`, `ManyWaters`) and has **no entry for `FlowWorks`**.

The maturity board therefore reports `FluidCanals function=validated` for a mod that
does not exist, and reports nothing for the one that does.

🔑 **And the ledger already knows.** `rimflow capability list` records, in its own
evidence strings: *"SWBestiary … absorbed SeaBeasts+Livestock+HelixTellurox+JawaIkee+
BeastNorm+SeasWaterline"*, *"MandrakePatches … absorbed GravshipAstronautFix+
PhytokinBarkHeadFix+ResearchKitEastFix+SauridFrillFix+ToolBeltFix"*, *"RimProperty …
absorbs SalvageClaim+TheftHauler"*, *"WeatherSuite … tier move RSW to RM, packageId
mandrake.rm.weathersuite"*. Every orphaned walk in the list above is named in that
registry as absorbed. **The facts needed to detect all of this were recorded weeks ago
and nothing cross-references them.** That is the waste.

This is why the top three candidates are all "assert the join", not "be smarter".

---

## 2. Ranked candidates

Ranked by (value × confidence) / cost. "Cost" is build effort for one agent-sitting
including a selftest; every candidate is stdlib-only Python, offline, no game.

| # | Candidate | Live findings today | Cost | Verdict |
|---|---|---|---|---|
| **C1** | `walklint` — every identifier a walk names must exist | **25 tests that cannot fail**; 39 bad packageId lines in 33 walks; 5 unknown `RM_/RSW_/RUT_` ids | ~150 LOC + selftest, ½ sitting | **do first** |
| **C2** | `modcheck doctor` — assert the five registries join to disk | 24 unrunnable walks; 30 walks on 9 shared folders; a GREEN dead mod; 3 dead capability rows | ~120 LOC + selftest, ½ sitting | **do second** |
| **C3** | Bar-scoped north-star hash (`NORTHSTAR_HASH_SCOPE_1`) | **47–57 % of every validated hash is prose**, and a walk is knowingly carrying false text to protect a hash | ~80 LOC in `northstar.py` + selftest, ½ sitting | **do third** |
| **C4** | `modcheck floor --all` + visual-surface triage as a script | reproduces a 20-min / 196 k-token triage in **0.38 s**; 44 bound bars, **0 covered**, **zero `shows=` in the whole repo** | ~90 LOC, ½ sitting | high value, trivial |
| **C5** | `modcheck validate` refuses a zero-bar validation | live defect: a mis-formatted section parses to 0 bars and `validate` still writes VALIDATED | ~15 LOC + selftest, 1 h | trivial, do with C3 |
| **C6** | `rimflow lint --citations` — a doc may not cite a closed item as live | 289 gate-language citations of terminal items in 164 files; 14 explicit live-state lies | ~120 LOC + selftest, ½ sitting | good, noisier |
| **C7** | Run `code_review_status.py prune --apply`; widen the untracked census | **97 of 227 DIRTY entries are dead paths** — the review backlog reads 43 % too big | 1 command + ~20 LOC | free |
| **C8** | Canon-ruling census as a derived number + ruling-format lint | 24 `**RULED**` + 1 free-form = **25**, matching CLAUDE.md's corrected figure; 2 non-conforming shapes | ~50 LOC, 2 h | cheap, ends a recurring argument |
| **C9** | Make `selftest_documented_commands.py` green again | fails on 3 items only because `./game`, `./bridge`, `show.sh` lack the exec bit on macOS | ~10 LOC, 30 min | free; a red checker is a disbelieved checker |

---

## 3. C1 — `walklint`: every identifier a validation walk names must exist

### What an LLM does today

Nothing systematic. Walk documents are prose executed by an agent by hand; `modcheck`
parses only the `## north star` section and never reads `## must be true` or
`## the walk`. So the correctness of ~78 documents' worth of packageIds, file names,
defNames and class names is maintained purely by whoever last edited each file.

Today's session found **one** instance of the resulting defect — FlowWorks step 1
asserting the absence of an error naming `mandrake.rm.fluidcanals`, a packageId that
stopped existing at the 2026-09-16 rename — and it cost a bench sitting plus two
commits (`875bada07`, `ce96c5b7d`) to find and fix. The subject-path half of the same
class cost **a full agent run** to discover and a `sonnet` repair sweep to fix (still in
flight in the working tree as this was written).

**CONFIRMED, measured in 0.11 s:** that was not one instance.

- **73** walk steps assert *"contains no Config error in `<packageId>`"*.
  - **48** name a packageId that exists → the check can fail.
  - **25** name a packageId that exists in **no** `About.xml` → **the check cannot
    fail**, in **24 distinct walks**: `BeastLairs`, `BeastNorm`,
    `BlastDoorFrameAsyncFix` (×2), `CereanManeFix`, `DesertFixtures`,
    `DesertVehicleReskin`, `FactionSlate`, `GravshipAstronautFix`, `HelixTellurox`,
    `JawaIkee`, `Livestock`, `PhytokinBarkHeadFix`, `Pits`, `ResearchKitEastFix`,
    `RiverSteam`, `SalvageClaim`, `SauridFrillFix`, `SeaBeasts`, `SeasWaterline`,
    `TheftHauler`, `ToolBeltFix`, `UtinniShell`, `VaultDungeons`, `WeatherSuite`.
- **39** walk lines across **33** walks name a `mandrake.*` packageId no `About.xml`
  declares (30 distinct bad ids). Two are third-party-shaped false positives
  (`mandrake.jawadoctrine.core` is a Harmony ID, not a packageId).
- With a combined index of our own XML `<defName>`/`Name=` **and** our own C# class /
  `RM_*|RSW_*|RUT_*` identifiers (6,372 symbols, built in 0.68 s), only **5** distinct
  backticked `RM_/RSW_/RUT_` tokens in all 78 walks are unknown to the repo — and they
  are real: `WeatherSuite.md` asserts six times over `RSW_WS_TerminatorFront`,
  `RSW_WS_DarkAurora`, `RSW_WS_WeatherInstrument`, while the defs on disk are
  `RM_WS_*`. **That whole walk is untestable**: wrong tier prefix on every defName *and*
  a vacuous packageId check. The ledger recorded the tier move on 2026-09-08.
- At HEAD, **26 of 78** `subject:` paths named a directory that does not exist. The
  in-flight repair has that at **1** (`AtmosphericBase`), plus **1** more the
  existence test misses: `Pits`, a directory holding only `__pycache__`.

### The deterministic replacement

`src/RimMandrake/Utils/modcheck/walklint.py`, exposed as `modcheck lint [<mod>…]`,
plus `.claude/hooks/selftest_walklint.py` in the standard suite.

**Reads:**
- every `design/validation_walks/*/*.md`;
- every `src/*/*/About/About.xml` → the set of packageIds we declare (171 today, 146
  `mandrake.*`);
- every `src/**/*.xml` → `<defName>` and `Name="…"`;
- every `src/**/*.cs` → `class|struct|enum|interface <Name>` and any bare
  `RM_*|RSW_*|RUT_*` token;
- every basename under `src/`.

**Asserts, per walk, in order of severity:**

1. 🔴 `VACUOUS` — a step asserting the ABSENCE of a string that names an identifier
   which does not exist. Pattern: `(contains|produces) no … Config error (in|for)
   <pkg>` where `<pkg>` is not a declared packageId. **This is the class that makes a
   test incapable of failing and is the reason the checker exists.** Generalise the
   negative-assertion detector beyond `Config error`: any step matching
   `contains no|produces no|does not (appear|log|contain)|never (logs|appears|names)|
   zero errors` **must** name at least one identifier that the index resolves. Today
   **70 of 110** absence-asserting steps name no backticked identifier at all — those
   are `WARN`, not `FAIL` (a prose absence claim is still executable by a human), but
   they are the population the next `VACUOUS` will come from.
2. 🔴 `BAD_SUBJECT` — `subject:` path missing, **or** present but holding no
   `About/About.xml` (this is what catches `Pits`).
3. 🔴 `BAD_PACKAGEID` — any `mandrake.*` token in the file not declared by any
   `About.xml`.
4. 🟠 `UNKNOWN_ID` — a backticked `RM_/RSW_/RUT_` token unknown to the XML+C# index.
5. 🟠 `BAD_FILE` — a backticked `*.xml|*.cs|*.png|*.dll` basename absent from `src/`,
   with a fixed allowlist for game-side files (`ModsConfig.xml`, `Player.log`) and
   skipping tokens containing `*` or starting with `_` (patterns, not filenames).

**Escape hatch, copied verbatim in spirit from `block_canon_contradiction.py`:**
`<!-- walklint-ok: <reason> -->` on the line or the line above suppresses one finding.
This is required, not optional — `FlowWorks.md:29` legitimately names the dead
`mandrake.rm.fluidcanals` *in order to record that it was dead*, and a block with no
escape gets disabled, after which nothing is guarded.

**Where it runs:** three places, cheapest first.
- `python3 …/modcheck/cli.py lint` — a CLI verb, exit 1 on any 🔴.
- A **selftest** (`selftest_walklint.py`) that fails the suite on any 🔴 in the live
  walks. 0.8 s in a 25 s budget. This is the one that catches a rename the day it lands.
- 🟠 findings print but never fail, and never gate a commit.

⚠️ Do **not** make it a `PreToolUse` commit hook. The rename that creates these
findings touches `src/` and `design/` in the same change; a blocking hook would refuse
the commit that is *fixing* it, and per `queue_lint.py`'s own docstring a hook that
refuses correct work gets disabled.

### What it cannot capture

- **Whether the assertion is the RIGHT assertion.** `walklint` proves
  `mandrake.rm.flowworks` exists; it cannot know that step 1 should also be watching for
  a terrain-load error, or that the step tests something the mod no longer does. That is
  the judgement the FlowWorks walk-through with the owner produced (three rulings that
  *deleted* lines), and it stays a bench sitting.
- **Whether a walk is complete.** A walk can name only real identifiers and still prove
  nothing.
- **Whether an absence assertion with no identifier is meaningful.** 70 such steps
  exist; a human reading `Player.log` can execute them. Only a human can say which of
  them is worth keeping.
- **Third-party identifiers.** `vanillaracesexpanded.phytokin`,
  `PeteTimesSix.ResearchReinvented` and every def they own are UNMEASURABLE offline;
  the linter must scope itself to `mandrake.*` and `RM_/RSW_/RUT_` and say so, or it
  will invent findings.

### Cost and risk

~150 LOC, half a sitting with a selftest. Two failure modes if the checker is wrong:

- **False negative** (misses a bad id): status quo. No regression.
- **False positive** (flags a good id): a seat is blocked by a red selftest on correct
  work. Mitigated by (a) `walklint` failing only on the four highest-precision classes,
  measured at 0 false positives today except the two Harmony-ID lines; (b) the
  `walklint-ok` comment; (c) 🟠 never failing.
- **The dangerous mode is a checker that passes because its own index is empty.** If the
  `About.xml` glob matches nothing, every packageId reads "undeclared" (loud) — but if
  the *walk* glob matches nothing, it reports 0 findings and exits 0 (silent, and
  exactly this repo's register of failure). **The selftest must assert a positive count:
  "78 walks were read, 171 packageIds indexed, 6,372 identifiers indexed" — and fail on
  zero.** A count that would be convenient is a query bug until proven otherwise
  (LESSONS_INBOX, 2026-09-16).

### Who catches a wrong answer

Per `Agent_Policy.md`'s table: **a selftest, before anyone reads it → row 1 → haiku is
safe to build it.** The checker's own correctness sits on row 1 too, because
`selftest_walklint.py` asserts against fixtures with known-bad and known-good walks.
The `walklint-ok` escapes are row 2 — the next agent reading the file re-derives the
reason. **The one row-3 decision is scoping** (which id classes are in scope at all),
which belongs in this document and to whoever reviews it, not to the builder.

---

## 4. C2 — `modcheck doctor`: assert that the five registries join to disk

### What an LLM does today

Discovers the drift by accident, one instance at a time, at full agent-run cost. Today's
run of that pattern is documented in `f873119d9`'s own commit message. LESSONS_INBOX
carries the same class twice more: *"A walk file filed under a mod's old name is
invisible to the tool that validates it: `find_walk("FlowWorks")` returned None while
`FluidCanals.md` sat on disk, so yesterday's walked checklist could not have been
validated at all"* (2026-09-17), and *"An index/table column can be CONFIDENTLY WRONG
rather than merely empty"* (2026-09-15).

### The deterministic replacement

`modcheck doctor` (new verb in `modcheck/cli.py`, logic in `modcheck/doctor.py`).
Pure Python, no game, no bridge, ~0.5 s.

**Reads:** the walk directory; `src/{RimMandrake,RimStarWars,RimUtinni}/*/About/About.xml`;
`infrastructure/state/modcheck_status.json`; `rimflow`'s replayed capability registry
(`model.replay().capabilities` — 0.06 s).

**Asserts:**

| Assertion | Findings today (**CONFIRMED**) |
|---|---|
| every walk basename resolves to exactly one `src/<tier>/<name>` | **24 fail** |
| that folder holds an `About/About.xml` | **1 more fails** (`Pits`) |
| the walk's `subject:` path == the resolved folder | measures the two keys against each other for the first time |
| the walk's declared packageId == that `About.xml`'s first `<packageId>` | 26 match, 2 unverifiable |
| no two walks declare the same `subject:` | **9 collisions over 30 walks** |
| every `modcheck_status.json` key resolves to a folder | **`FluidCanals` fails** |
| the aggregate `status` verdict == the per-mod `check()` verdict | **`Pits` disagrees: GREEN vs STALE** |
| every `capability` name resolves to a folder | **3 fail** |
| every mod with a walk has a capability entry, and vice versa | **24 walks have none; 4 capability rows have no walk** |

Exit 1 on any failure. Print, for every finding, the **remedy verb** —
`rimflow capability retire <name> --owner-said …`, `git mv <walk>`, or "this walk's mod
was absorbed into `<X>`; merge or delete it (owner's call)".

**Two structural fixes that belong with it, both small:**

- `modcheck status` (no arg) must call `status.check(mod, dir)` per row instead of
  printing `entry["status"]`, and must print `ORPHANED (no such mod folder)` rather than
  raising when the folder is gone. **A summary must never be able to disagree with the
  detail it summarises** — the same defect as the statusline drawing its bar and its
  number from two fields (LESSONS_INBOX, 2026-09-16).
- `northstar.find_walk` and `runner.find_mod_dir` should be called through one
  `resolve(mod)` that returns both or refuses, so the two keys cannot silently diverge
  again.

**Where it runs:** a selftest (fails the suite on any 🔴) **and** a CLI verb. Not a
commit hook — same reason as C1.

### What it cannot capture

- **Which walk should OWN a shared mod folder.** When 7 walks point at `SWBestiary`, the
  right answer is a design decision: merge the six into `SWBestiary.md`, keep them as
  per-feature walks with a new `feature:` key, or delete them. The item file for today's
  repair says exactly this — *"the three ownership decisions are his and are not
  delegated."* `doctor` must **report and stop**, never repoint.
- **Whether an absorbed mod's walk still describes real behaviour.** Absorption can
  preserve or destroy a feature; only reading the code says which.
- **Whether a capability rung is honest.** 13 of 58 rows carry evidence
  `"owner-ruled promotion 2026-09-08 (UNCERTAIN tier accepted…)"` — his call, recorded,
  not derivable.

### Cost and risk

~120 LOC + selftest, half a sitting. If wrong: a false positive is a red selftest on a
correct layout, cured by fixing the resolver; a false negative is status quo. **The
dangerous mode is again an empty read** — if `modcheck_status.json` fails to load,
`doctor` must say `UNMEASURED`, never `0 findings`.

### Who catches a wrong answer

Row 1 (a selftest) for the assertions. **Row 3 for the ownership calls it surfaces** —
they become owner cards, which is why `doctor` reports and never repairs.

---

## 5. C3 — Bar-scoped north-star hash — 🔴 DECLINED BY THE OWNER, 2026-09-17

⛔ **Do not build this.** Put to him as a card the day this assessment landed; his answer,
verbatim: *"Change no code — you just re-validate when prose is corrected."*
`NORTHSTAR_HASH_SCOPE_1` is **dropped — declined, not deferred.**

The whole-section hash therefore stands as designed, and the remedy for false text inside a
hashed section is to **correct it and re-validate in the same sitting**, never to leave it
standing to protect a hash. The measurement below is kept because it is now the evidence for
what that remedy COSTS, not an argument for changing the cut. The build plan that followed it
(canonical-form surgery, a `rehash` verb, the migration) is deleted — git holds it at
`d11280cda`.

🔑 One consequence he ruled on separately, and KEPT: the spec's **§6a per-axis cut** survives.
It is a different, narrower change that costs no re-validation, and without it no read line can
be added to an already-validated walk. See `design/RimMandrake/north_star_validation_spec.md`
§6a — that is where this rule now lives.

🔑 A second consequence, built the same day (`4447ba4f6`): because re-validation is now the
standing remedy, `modcheck validate` had to stop accepting a **zero-bar** section — see §7,
which was a latent defect and is now on the critical path.

### The measurement that justified asking him

### What an LLM does today

Works around the defect, in writing, and pays for it. **CONFIRMED**, measured over the
canonical bytes `northstar._canonical()` actually hashes:

| walk | state | hashed bytes | bar lines / total | **prose under the hash** |
|---|---|---|---|---|
| `Pits.md` | VALIDATED | 3,189 | 26 / 53 | **48 %** |
| `Graffiti.md` | VALIDATED | 5,659 | 35 / 83 | **54 %** |
| `WreckedMachines.md` | VALIDATED | 6,171 | 43 / 85 | **47 %** |
| `FlowWorks.md` | VALIDATED | 10,328 | 54 / 134 | **57 %** |
| `AtmosphericBase.md` | DRAFT | 15,643 | 88 / 194 | 53 % |
| `Oracle.md` | DRAFT | 8,860 | 74 / 129 | 40 % |

So **roughly half of every one of the owner's validations is bytes that carry no bar**,
and correcting any of them silently reverts VALIDATED → DRAFT, at which point
`bar_for()` returns `[]`, `visual_floor` finds nothing uncovered, and **the mod quietly
stops being refused.** The failure is silent in the worst direction: it makes a gate
disappear.

The current cost is visible in the tree. `FlowWorks.md:197-205` reads:

> *"The `## north star` section still opens with a DRAFT banner and still says the
> checklist 'has never bound'. Both are FALSE as of 2026-09-17 … The false text is left
> standing **deliberately** … ⛔ Do not 'tidy' the banner; that is the trap, not the fix."*

That is a document knowingly carrying false statements to protect a hash, with a
paragraph of prose spent explaining why, plus the matching warning in CLAUDE.md. It has
already fired live once (Graffiti, 2026-09-16). **Documentation hygiene and validity are
in direct conflict, and the conflict is a choice about which bytes get hashed.**

### The deterministic replacement

Extend `modcheck/northstar.py`. Spec §6a already specifies the narrower half of this and
**already measured that it costs no re-validation**; this candidate finishes it.

1. **Axis scoping (spec §6a, already ruled).** The show-axis canonical form excludes
   every line from a `### must read`/`### cannot read` heading to the next `### `; the
   read axis hashes only those, under its own `read-state:` / `read-validated-hash:`.
   §6a's own table records that Pits and Graffiti keep their existing hashes under this
   cut — verify that by re-deriving it before writing, do not take the table's word.
2. **Bar scoping (the `NORTHSTAR_HASH_SCOPE_1` half).** The canonical form keeps, per
   axis: every `- [ ] \`id\` …` line **and its indented continuation lines** (the
   continuation *is* the bar — `text_for()` hands that prose to the judge verbatim, so it
   must be hashed), plus the `### ` subheading each list sits under (polarity is
   load-bearing: `_checklists()` uses it to separate must from cannot, and getting that
   wrong once already put a rejection line into the visual floor). Everything else in the
   section — banners, `### the experience` quotes, `🔑` through-lines, `⛔` notes,
   bold group labels — is **excluded**.
3. **`modcheck validate` prints the migration.** Bar scoping *does* change all four
   recorded hashes, so it needs either his word or a re-record on his word. Ship it as
   `modcheck rehash <mod> --owner-said "…"`, which prints old hash, new hash, and **a
   diff of the bar lines only** — proving no bar text changed — then rewrites the header.
   If any bar line differs, it refuses. That way the migration cannot smuggle a bar edit
   through, which is the only real risk in the change.

**Where it runs:** `northstar.py` (the parser), `selftest_northstar.py` (which already
exists, 22 KB), and one new owner-authorised CLI verb.

### What it cannot capture

- **Whether a re-worded bar is the same bar.** If someone rewrites
  `canal_partial_fill_distinct`'s prose from "distinguishable at a glance" to
  "distinguishable", that IS a change to what he validated and *must* break the hash.
  Bar scoping keeps that property; it must not be softened into "hash the ids only",
  which would let the substance be rewritten under a stable hash. **Recommend: id +
  prose in, commentary out. Take his word on that boundary before building.**
- **Whether the commentary matters.** Some of it does — the `### the experience` block is
  his verbatim words. Excluding it from the hash means an agent can edit his own quoted
  words without tripping anything. Mitigation is deterministic and cheap: hash the
  experience block **separately** as a third, non-gating fingerprint and have `walklint`
  report a change to it as 🟠. That converts a silent rewrite into a visible one without
  charging him a re-validation for a typo two paragraphs away.
- **Nothing about whether the bars are the right bars.** Untouched. That is his sitting.

### Cost and risk

~80 LOC in one well-tested module, half a sitting. **Highest-risk candidate here**,
because it changes the meaning of an owner approval that four mods already carry. Risks:

- **Cut too wide** → a bar edit no longer breaks the hash → an agent can quietly rewrite
  what he approved. This is the failure that matters and the `rehash` bar-diff refusal is
  aimed squarely at it.
- **Cut too narrow** → status quo, no harm.
- **Migration writes a wrong hash** → the mod reads DRAFT and stops being refused,
  silently. So `rehash` must **read back** the file after writing and re-parse it to
  `VALIDATED` before reporting success. Never trust the write.

### Who catches a wrong answer

The parser is row 1 (`selftest_northstar.py`). **The scoping decision is row 3 — nobody
catches it, it becomes the definition of what his approval covers — so it is opus work
and the boundary in the bullet above goes to him as a card before a line is written.**
`block_forged_validation.py` already prevents an agent hand-writing the header, and that
protection must survive the change: `rehash` is the only new writer, and it must be added
to that hook's allowlist explicitly, not by loosening the pattern.

---

## 6. C4 — `modcheck floor --all`: the triage, and the join nobody has used

### What an LLM does today

**A `sonnet` subagent spent ~20 minutes and ~196 k tokens** classifying 72 walks by
"does this mod ship real visual surface", returning `32 bar owed / 38 no bar /
2 uncertain`; BENCH then re-measured it rather than trusting the number (correctly — the
briefed-number trap in CLAUDE.md).

**CONFIRMED: the same buckets fall out of a 0.38-second walk of the tree.**

- 78 walks, **40** whose subject folder ships ≥1 PNG, **38** that ship none. The
  negative bucket is *exactly* the subagent's 38.
- The item's own headline figure — *"the four biggest art mods … 3,426 PNGs"* — is
  Armoury 1,081 + SWBestiary 948 + StarWarsRaces 889 + Droidworks 508 = **3,426**,
  reproduced exactly.
- **27** walks whose mod ships ≥1 PNG have **no `[S]` (LOOK) step at all** — including
  `StarWarsRaces` (889 PNGs), the five walks sharing `SWBestiary` (948), and
  `Droidworks` (508). `FlowWorks.md` records that "this walk was one of the 7 that
  dismissed the visual pass in writing"; measured across all walks the figure is 27
  (25 once the two with a VALIDATED north star, which supply the bar another way, are
  excluded).

And the finding that changes the picture:

- **CONFIRMED: there is not one `shows=` claim anywhere in the repo.** All 17
  `validation.py` files: zero. So all four VALIDATED north stars bind **44 must-show
  bars with 0 covered**, and `runner.run()` **REFUSES** each of them before touching the
  game — Pits 11, WreckedMachines 12, FlowWorks 13, Graffiti 8. `Pits` has no
  `validation.py` at all, so `modcheck run Pits` cannot even load.

The north-star system is specified, hash-protected, judge-wired, and **structurally
unable to green anything today** — and nothing reports that. It is not broken; the join
has simply never been populated. But it is exactly the kind of state that reads as
working from every summary view.

### The deterministic replacement

`modcheck floor --all` — one screen, offline, ~0.5 s, per mod:

```
mod  walk?  subject-ok?  PNGs  [S]?  northstar  bars  covered  uncovered  verdict
```

plus a footer: *"N mods ship visual surface and owe a bar; M bars bind; K are covered."*
It reuses `northstar.parse`, `runner.visual_floor` and `floor.uncovered_shows` — the
existing functions, called for every mod instead of one under test. Add it to the
selftest as a **positive-count** assertion only (`≥1 walk read`, `≥1 mod indexed`), never
as a threshold on the counts themselves.

### What it cannot capture

- **The `2 uncertain`.** A mod shipping one PNG may be a functional icon (no bar owed) or
  the whole point of the mod. `MSEDroidFix` (1 PNG) and `StructureInjectionsSW` (1 PNG)
  are the live examples. The script reports the count and **must not bucket them** —
  "1 PNG, owner call" is the honest cell.
- **Whether a mod's visual surface is its EXPERIENCE.** `MandrakePatches` ships 10 PNGs
  across 6 walks' worth of one-texture fixes; whether that owes a north star is his call.
- **Everything the bar itself says.** Untouched.
- **Whether a `shows=` claim is honest** — that a component really does photograph the
  thing it claims. That is what the judge is for, and the judge is not in scope.

### Cost and risk

~90 LOC, no new concepts. If wrong: a wrong PNG count mis-sorts a triage list — cheap
and visible. **The real value is not the triage, it is that "44 bars bind, 0 covered"
becomes impossible not to know.**

### Who catches a wrong answer

Row 1. The counts feed a *triage list*, not a verdict; the verdict path
(`runner.visual_floor` → `refusal`) is unchanged and already refuses on the same data.

---

## 7. C5 — `modcheck validate` must refuse a zero-bar validation

**CONFIRMED live defect, by reading `cli.py:142-186`:** `_validate` refuses only when
there is no `## north star` section. If the section is present but its lines are in the
wrong format, `_checklists()` returns `[]`, `validate` prints *"These lines BIND once
validated…"* followed by **nothing**, and with `--owner-said` it writes
`state: VALIDATED` anyway. `bar_for()` then returns `[]`, `visual_floor` finds nothing
uncovered, and the mod greens against an empty checklist. LESSONS_INBOX records the
near-miss (2026-09-17: *"a north-star walk whose lines are in the wrong format parses as
ZERO lines and still exits 0"*).

**Fix, ~15 lines:** `validate` refuses when `must_show` is empty, naming the expected
line format and pointing at a VALIDATED walk to copy. Print the counts
(`13 must-show + 3 cannot-show`) **before** the `--owner-said` gate as well as after, so
a zero is visible in the dry run he reads. Add the case to `selftest_northstar.py`.

**Cannot capture:** whether a non-empty checklist is a *good* checklist. Nothing here
touches that.

**Risk:** a walk that legitimately has only `### cannot show` lines and no `### must
show` would be refused. Decide that deliberately — I would allow `must_show == [] and
cannot_show != []` and refuse only when both are empty.

**Who catches it:** row 1 (selftest). Build with C3, same file, same sitting.

---

## 8. C6 — `rimflow lint --citations`: a doc may not cite a closed item as live

### What an LLM does today

Notices one at a time, usually after acting on it. `NAMING_SCHEME_EXECUTION_1` closed
2026-08-31 at `54a8e28d` and was still cited as a live gate 16 days later; FlowWorks
shipped under the wrong name because of it. CLAUDE.md now carries three paragraphs about
this, and `STALE_RENAME_GATE_SWEEP_1` exists to clean up by hand.

**CONFIRMED, whole repo, 0.66 s including a full ledger replay** (1,329 items, 1,106
terminal; 2,084 tracked text files; 9,679 candidate id tokens):

- **3,813** `(file, terminal-item)` citations across **1,076** files. Most are legitimate
  provenance and must not be flagged.
- **289** citations in **164** files sit within ±1 line of gate language
  (`blocked by|waits on|until|do not|ahead of|pending|gated on|deferred to|…`) with no
  closure language (`closed|done|landed|superseded|✅|<sha>`) nearby.
  `NAMING_SCHEME_EXECUTION_1` accounts for 9 of them, still, today.
- **14** citations in **9** files explicitly assert a live state (`| open |`,
  `| doing |`, `still open`, `open item`) for an item the ledger says is terminal —
  including `MACBENCH_REBOOT_HANDOFF_202609162042.md` and
  `infrastructure/state/items/BESTIARY_ARMOURY_DESC_BACKFILL_1.md`.

### The deterministic replacement

`rimflow lint --citations` (new subcommand; `render.py` already replays the ledger).

- **Reads:** `model.replay()` → `{id: state}`; every tracked `.md|.txt|.yml` outside
  `Transient/`, `state/ledger/` and `state/queue/`.
- **Asserts, two severities:**
  - 🔴 `STATE_LIE` — a line asserting a live state for a terminal item. **14 today.**
    High precision, cheap to fix, exit 1.
  - 🟠 `STALE_GATE` — gate language near a terminal item with no closure marker.
    **289 today.** Report only; too noisy to gate.
- **Escape hatch:** `<!-- citation-ok: <reason> -->`, same shape as `canon-ok`.
- **Where it runs:** the selftest suite for 🔴 only, plus the CLI verb for the 🟠 sweep.
  🔑 A `handoff.py --check` addition is the highest-leverage placement for the 🟠 list:
  a handoff is precisely when stale gates get copied forward into the next session.

### What it cannot capture

- **Whether a gate is genuinely stale.** An item can close and its *constraint* remain
  true for an unrelated reason. Only reading decides — which is why 🟠 never gates.
- **A gate cited by DESCRIPTION rather than by id** — "don't rename until the naming
  work lands". Invisible to this checker, and the most likely residual form.
- **Whether the correct fix is deletion or a rewrite.** CLAUDE.md's ruling is *delete*;
  the linter can only point.
- **Items with no ledger entry** (legacy `B*`/`C*`/`W*` ids) — unresolvable, and must be
  reported as `UNKNOWN`, never as clean.

### Cost and risk

~120 LOC + selftest, half a sitting. False positives are the whole risk, and 🔴 is kept
to the 14-instance high-precision class specifically to stay believable. **The failure
mode to avoid is a 289-line red wall that gets muted, after which the 14 real ones
disappear with it.**

### Who catches a wrong answer

🔴 row 1 (selftest). 🟠 row 2 — the next agent re-derives before acting, which is
already the standing rule ("check an item's STATE before believing a doc").

---

## 9. C7–C9 — free wins

**C7 — the review backlog is 43 % phantom.** **CONFIRMED:** `code_review_status.py list
--show-untracked` reports 2,296 CLEAN, **227 DIRTY**, 250 never-entered. **97 of the 227
DIRTY are `file no longer exists on disk`** — orphan entries from moves and deletes.
`prune` exists and reports exactly 97; nobody has run `--apply`. The real review debt is
130 changed files + 250 never-reviewed. Anyone planning review capacity off "227" is
planning against a number that is 75 % too big in its most alarming component.
Two additions: run `prune --apply`; and have the codebase-health publisher report DIRTY
and ORPHANED as **separate** numbers so they can never merge again.
*Also worth a decision, not a change:* `find_untracked` scans only `src/` for
`.py|.cs|.xml`, so `.claude/hooks/*.py` (23 files, one of which gates every commit) and
`skills/**/*.py` are outside the census entirely — **CONFIRMED** from
`UNTRACKED_SCAN_DIR = "src"`. Whether they should be in scope is his call.

**C8 — the canon census, ended.** **CONFIRMED, 0.03 s:** 137 entry dirs (23 `droid_*`);
**24** carry `**RULED**`; `gizka` carries a ruling in free-form prose (a dated owner
quote with no marker) → **25**, exactly CLAUDE.md's corrected figure; **111** carry the
`(empty — owner has not reviewed…)` boilerplate in **seven** different wordings
(re-MEASURED 2026-09-18 — this said four, and four is wrong: they differ by
"owner"/"the owner", by the noun race/creature/species/chassis, and one droid entry
carries a trailing sentence inside the parens. Counts: 66/19/17/5/2/1/1); `zeer`'s
ruling section is genuinely blank. So: a `canon census` verb that prints
`ruled / unruled / non-conforming`, plus a lint that a `## ruling` body must be either
the boilerplate empty marker or a `**RULED**` block. **That converts the number two
subagents once disagreed about (2 vs 25) into a derived one.** Residue: whether an entry
*needs* a ruling — his, per `AGENT_BRIEF.md` ("he rules only on ambiguity, deliberate
departures and contested regens"). Do not add a "needs ruling" heuristic.

**C9 — a red checker is a disbelieved checker.** `selftest_documented_commands.py` fails
with 3 findings, all *"documented as ./game but not executable"* — the exec bit on
`./game`, `./bridge`, `src/RimMandrake/Utils/show.sh`, absent on this macOS checkout of
a Windows-authored tree. **CONFIRMED.** The finding is spurious here and it is one of 11
red selftests, which is how a suite stops being read. Make the exec-bit assertion
platform-conditional (or assert a shebang instead), and separate the 8 genuinely
`UNMEASURED` (no `dotnet.exe`) results from real FAILs in `run_selftests.py`'s summary
line. **`UNMEASURED` is not `FAILED`, and printing them identically is the same defect
`probe.py` fixed for "bridge silent".**

---

## 10. What is NOT worth converting

This list is as important as the ranked one. Each of these looks convertible and is not.

1. **Whether art looks right.** His standing rule is *"iterate by LOOKING"*; realism is
   not scoreable. The repo already holds the counterexample:
   `Gizka_north.png` scores **0.845** mirror-symmetry and passes the 0.80 floor in
   `art_checks.facing_symmetry` while being an unmistakable right-facing side profile —
   *"use this case as the counterexample whenever someone argues a numeric gate makes
   visual judgement unnecessary"* (LESSONS_INBOX, 2026-09-15). ⛔ Do not add a numeric
   art gate.
2. **Sound.** He ruled today that sound is validated by playtesting, never by a script.
   Spec §12 already records `must hear` as *"ruled, and deliberately not a gate"*. Leave
   it.
3. **`judge.py`.** It is already correctly shaped: one narrow factual question per bar,
   the bar's own prose supplied verbatim, `UNJUDGEABLE` is not a pass, polarity applied
   in Python rather than told to the model. There is nothing to pull out of it — the
   thing it does is the thing only a judge can do. The one improvement worth having is
   *deterministic* and belongs to spec §4b, not here: refuse to *bind* a `(change)` bar
   until the evidence artifact is a frame sequence, because `shots[-1]` under a
   single-image prompt cannot settle a claim about motion (10 of AtmosphericBase's 23
   bars were that shape).
4. **Distilling `### must show` lines from his vision prose.** This is Fable work by
   design (`NORTH_STAR_WALK_AUTHORING_1`), and today's FlowWorks sitting is the proof:
   reading the checklist to him line by line produced three rulings that **deleted** art
   and collapsed two art systems into one. No script produces that.
5. **Auto-repointing a stale `subject:` path.** Tempting — 25 of 26 were repointed by a
   sweep this morning — and it is exactly where the automation should have stopped. The
   repoint is what **created** the 9-way collisions in §1: 7 walks now legitimately
   claim `SWBestiary`. `doctor` must report; the merge-or-delete call is his.
6. **Stale-drop rulings.** The Charter's *"one grep/probe — if it doesn't prove the item
   live, drop"* is a judgement with real cost when wrong, and `Agent_Policy.md` already
   puts it on row 3. A script can surface *candidates* (no event in N days, no citing
   commit) — `selftest_undocumented_work.py` and `warn_unclosed_queue_item.py` already
   do adjacent work — but the drop stays a decision.
7. **Deriving capability rungs from disk.** `content=authored` is a claim that art is
   *authored*, not that PNGs exist; **10 of 58** rows already carry a folder survey as
   their evidence, and turning that into the rung itself would launder a file count into
   a maturity claim. 13 more rows are explicit owner promotions on UNCERTAIN evidence.
   The right conversion is C2's *existence* check, not the rung.
8. **`block_canon_contradiction.py` / `check_canon.py`.** Already the pattern we want,
   already blocking, already with a reasoned escape hatch. It should be *copied*, not
   re-solved.
9. **Making any of these a blocking `PreToolUse` commit hook.** `queue_lint.py`'s
   docstring records the owner's 2026-08-15 ruling — *"a hook that refuses a commit
   costs more than the miscount it prevents, and a seat that hits it mid-flow will work
   around it"* — and the compound-command trap (a `PreToolUse` refusal kills the file
   write chained ahead of it) makes it actively dangerous for checkers whose findings are
   fixed by the very commit being refused. **Selftest + CLI verb, not a hook.**

---

## 11. Reproduce every number

Each of these was run in this session, on this laptop, offline, in the times shown.

| Claim | How |
|---|---|
| 78 walks; 26→1 bad `subject:` paths | compare `git show HEAD:<walk>` vs worktree, test `os.path.isdir(subject)` and `About/About.xml` |
| 25 vacuous "no Config error" checks / 73 total; 39 bad packageId lines | index `<packageId>` over `src/*/*/About/About.xml`; regex `(contains\|produces) no … Config error (in\|for) (mandrake\.\S+)` over the walks — 0.11 s |
| 5 unknown `RM_/RSW_/RUT_` ids | index `<defName>`, `Name="…"` from `src/**/*.xml` + `class\|struct\|enum\|interface` and `RM_*\|RSW_*\|RUT_*` from `src/**/*.cs` (6,372 symbols, 0.68 s), diff against backticked walk tokens |
| 24 unresolvable walk names; 9 shared subjects over 30 walks | `os.path.isdir("src/<tier>/<basename>")`; group walks by `subject:` |
| `FluidCanals GREEN`, `FlowWorks NEVER RUN`, `Pits GREEN` vs `STALE` | `modcheck/cli.py status`, then `status Pits` / `status FluidCanals` / `status FlowWorks` |
| 3 dead capability rows; 10 folder-survey rows; 13 owner-promotion rows | `RIMFLOW_SEAT=BENCH rimflow capability list`, resolve each name against `src/` |
| 47–57 % prose under the hash | `northstar._section_lines` → `_canonical`, classify each canonical line as bar-line-or-continuation vs not |
| 44 bars bind, 0 covered; zero `shows=` in the repo | `northstar.parse` per walk × regex `shows\s*=` over all 17 `validation.py` |
| 40/38 PNG split; 3,426 PNGs in the top four; 27 walks with PNGs and no `[S]` | walk each subject folder counting `*.png`; regex `^\s*\d+\.\s*\[([LDBS])\]` — 0.38 s total |
| 3,813 / 289 / 14 stale citations | `model.replay()` → `{id: state}`; scan 2,084 tracked text files — 0.66 s including replay |
| 2,296 CLEAN / 227 DIRTY / 250 never-entered / 97 orphans | `code_review_status.py list --show-untracked`; `code_review_status.py prune` |
| 24 `**RULED**` + gizka = 25 of 137 | parse the `## ruling` section of each `canon_references/*/description.md` — 0.03 s |
| 43/54 selftests, 25.4 s | `run_selftests.py` |

**Total runtime of every checker proposed here: under 3 seconds.** The LLM work it
replaces, on today's evidence alone, is a bench sitting plus a full agent run plus a
196 k-token subagent — and it recurs on every rename, merge and re-tier.

---

## 11a. What has SHIPPED (keep this current)

- **C1 `modcheck lint` (walklint)** — shipped 2026-09-17. Reports 40 FAIL / 15 WARN today;
  its suite gate is deliberately NOT armed while live findings exist.
- **C2 `modcheck doctor`** — shipped 2026-09-17. 41 FAIL / 28 WARN.
- **C3 bar-scoped north-star hash** — 🔴 **DECLINED by the owner** 2026-09-17, see §5.
- **C5 `validate` refuses a zero-bar section** — shipped 2026-09-17.
- **C7 the phantom backlog** — shipped 2026-09-18 (`4de31d6f5`). `prune --apply` dropped 97;
  `list` now prints a TALLY counting ORPHANED apart from DIRTY, sharing ONE predicate with
  prune. ⚠️ The publisher change this section asked for is NOT needed and was not made:
  `codebase_health.review_verdicts` only ever iterates live files, so an orphan entry never
  entered its census. The merge was in `code_review_status.py list`, and that is where it
  was fixed.
- **C8 the canon census** — shipped 2026-09-18 (`4a022088e`), `Utils/canon_census.py` with
  `--list` and `--lint`. Live: ruled 24 / unruled 111 / non-conforming 2. `gizka` is counted
  **non-conforming on purpose** — keeping "ruled" a mechanical marker test is the point of
  C8, since a prose classifier clever enough to recognise it is the same heuristic that
  produced the disputed "2"; the report prints the human-legible 25 as a note.
- **C9 the red checker** — shipped 2026-09-18 (`ceb78be3e`). ⚠️ This section's premise was
  wrong: the exec-bit finding is NOT spurious. `./game`, `./bridge` and `show.sh` were
  100644 with `core.fileMode=true`, so `./game` genuinely could not run on the Mac. Fixed
  with `git update-index --chmod=+x` rather than by making the assertion
  platform-conditional — the check was right and the tree was wrong. `run_selftests` now
  separates the buckets: **6** unmeasured (not the 8 claimed below), 6 real FAILs.
- **Owed and not built:** C4 `modcheck floor --all`, C6 `rimflow lint --citations`.
- **Also owed:** arming C1's suite gate after a findings cleanup, and
  `bridgetools/selftest_tool_metadata.py` adopting the UNMEASURED phrase so its
  Windows-toolchain absence stops counting as a failure.

The walk-findings decision sheet the owner asked for is built:
`Transient/walk_decisions_sheet.html`, rulings in
`design/validation_walks/WALK_DECISIONS.json`, regenerate with
`python3 src/RimMandrake/Utils/make_walk_sheet.py`.

---

## 12. Where to start

**C1 `walklint`, then C2 `modcheck doctor`, then C3 the bar-scoped hash.** In that order,
for three different reasons:

1. **C1 makes wrong answers loud where they are currently silent.** 25 live tests cannot
   fail. A test that cannot fail is worse than a missing test, because it reports
   success. It is also the cheapest thing here and its evidence base is 100 % measured.
2. **C2 stops the class from recurring and needs no new concepts** — it only asserts
   that five registries agree about a name, using facts the ledger already holds. It also
   surfaces the three ownership cards the owner has to rule on before any more north-star
   authoring is worth doing.
3. **C3 removes the only place in this system where correct documentation and a valid
   approval are in direct conflict.** Half of every validation is prose today, a walk is
   knowingly carrying false sentences to protect a hash, and it has already fired once.
   It goes third only because it is the one candidate that needs his word first — the
   id-plus-prose boundary in §5 is a card, not a decision for the builder.

C4 and C5 are an hour each and should ride along with C2 and C3 respectively. C7 is one
command.

⛔ **Do not build any of these as a blocking commit hook** (§10.9). ⛔ **Do not let any of
them repair a document** — every one reports, and the remedy is a named command a person
runs. ⛔ **Every checker's selftest must assert a positive input count**, because the only
way any of them fails dangerously is by reading nothing and exiting 0.
