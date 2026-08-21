## spec

🔴 **OWNER, 2026-08-21, after seven instruments were caught returning confident wrong
numbers in one session:** *"Plan with me now on fixes to these files and how we use them to
avoid this once and for all in the future. Do we need new file formats that have guaranteed
fields we can search? Is this another JsonL type solution that our Dump should be providing
instead? At the same time, how can we keep the searches as deterministic as possible to
avoid flooding tokenization and context?... The same fix would be applied to any dump-style
file or other large resource we routinely scan."*

⚠️ **This item is the ANALYSIS and the OPTIONS. It is `proposed` on purpose.** The owner
selects an option; only then does it become buildable. Do not start building from this
without his choice recorded in `## ruling` below.

---

### 1. The problem is not "grep is bad". It is a causal chain, and the middle link is size.

```
the artifact is too large to READ
        ↓
so an agent reaches for a SCANNING tool (grep, strings, wc)
        ↓
the scanning tool does not understand the artifact's ENCODING
        ↓
it returns a NUMBER, plausibly shaped, with no error
        ↓
the number decides something expensive
```

**Measured 2026-08-21, and the size number is the one that explains the behaviour:**

| artifact | size | cost if ever read whole |
|---|---|---|
| `DefDump/` total | **646 MB** | — |
| `defs/ThingDef.json` | **315.7 MB** | **~82 million tokens** |
| `defs/RecipeDef.json` | 80.4 MB | ~21 M tokens |
| `defs/BodyDef.json` | 80.3 MB | ~21 M tokens |
| 536 def files | | |

⇒ **No agent can ever read these, and every agent knows it.** That is precisely why they
reach for `grep` and `strings`. **Any fix that does not make the correct path CHEAPER than
grepping will be routed around**, exactly as a freeze that annoys people gets overridden by
reflex. This is the central design constraint.

🔑 Note what already worked: every correct measurement tonight came from a small Python
script that loaded the file, computed a scalar, and printed **one line**. The failures came
from `grep`/`strings`. **The good pattern exists; it is just more effort than the bad one.**

### 2. Taxonomy — seven incidents, three root causes

Register with per-tool status: `infrastructure/state/BUILDABLE.md`, "INSTRUMENTS THAT
RETURN A CONFIDENT WRONG ANSWER".

**Cause A — the tool cannot read the encoding at all** (a byte scan of a structured file)
- `strings -a -el` on a .NET DLL → 16 of 115 tool names. Attribute strings live in metadata blobs.
- `grep` on a `.rws` for biome defNames → 2, where the answer was 3 / 233 / 31. World biomes are indices into a compressed grid.
⇒ **Format cannot fix the `.rws`** — it is Ludeon's, not ours. Only a correct reader or the bridge can.

**Cause B — the artifact silently lost or flattened the evidence**
- Def dump keyed `defs/<Type>.json` on the SIMPLE type name; 532 types share 517 names, so 13 files were overwritten and **824 defs destroyed**. `AbilityDef` reads 0 having written 612.
- Cherry Picker NEUTERS cut defs rather than deleting them, so a fully-cut tag is **absent** from a dump-built index rather than **empty** in it — making `emptied by the cut: 0` arithmetically guaranteed.
⇒ **This is the class a format change genuinely fixes.**

**Cause C — the checker's semantics are narrower than reality**
- `texture_audit` assumes vanilla `Graphic_Multi` suffixing → called 39 present textures dead.
- `first_light` treats "no weaponTags" as "deliberate civilian" → hides a disarmed combat role.
⇒ **No format fixes these.** They need the tool to be able to say *"I cannot judge this"*.

### 3. Design goals, in priority order

1. **Absence must be distinguishable from ignorance.** `0` must never be ambiguous between
   "measured zero", "not captured" and "cannot judge". This is the single highest-value property.
2. **The correct path must be cheaper than grep**, or it will not be used.
3. **Answers are scalars by default**, records only on request — context is the budget.
4. **Deterministic and reproducible**: same artifact + same question ⇒ same answer, and the
   answer carries what it was measured against.
5. **Applies to artifacts we do not own** (`.rws`, third-party DLLs) as well as ours.
6. **Cheap to adopt.** A perfect system nobody uses loses to `grep`.

---

### 4. The options

#### Option A — Keep JSON, add a coverage manifest and refuse on gaps
The dump already writes a `manifest.json`. Extend it: every def type gets
`{count, coverage: complete|partial|failed, reason}`. A thin reader library loads the
manifest first and **refuses to answer** about a type not marked `complete`.

| pros | cons |
|---|---|
| Smallest change; the collision fix (`d7cf154`) is already half of it | Does nothing for the 315 MB read cost — the reason people grep |
| Kills Cause B's "0 means unmeasured" directly | Nothing for Cause A or C |
| No new dependency, no new mental model | Still whole-file `json.load` per question |

#### Option B — JSONL + a sidecar index (the owner's suggestion)
One def per line, stable ordering, append-only. A companion index maps `defName → byte
offset`, plus secondary indexes on hot fields (`defType`, `packageId`, `weaponTags`,
`texPath`). A query tool seeks rather than parses.

| pros | cons |
|---|---|
| **Line-addressable**: read ONE def without loading 315 MB — directly attacks goal 2 | Index can drift from the data; needs a fingerprint check |
| Still greppable in an emergency, and a grep hit is now a whole valid record | Secondary indexes must be chosen in advance; an unindexed question is a full scan again |
| Streamable — constant memory | Two files to keep in step |
| Diffable, git-friendly | Does not by itself express "cut" vs "never had" |

#### Option C — SQLite as the dump format
One `defs.sqlite`: `defs(defName, defType, packageId, json)`, extracted columns for hot
fields, a `capture` table with per-type coverage, a `provenance` table with the mod-set
fingerprint.

| pros | cons |
|---|---|
| **Strongest determinism**: `SELECT COUNT(*)` returns one number, no parsing, no context cost | Binary — not diffable, not greppable, cannot be eyeballed |
| `NULL` vs `0` vs missing row are three *different* things — goal 1 falls out of the schema | New mental model for every seat |
| Joins make tag→weapon→cut-status correct by construction, which is exactly what `weapon_tag_audit` got wrong | A corrupt file is opaque in a way a text file is not |
| `sqlite3` is in the Python **stdlib** — verified 3.46.1, no new dependency | Harder to hand-repair |
| One file to fingerprint and freeze | |

#### Option D — Leave the formats; wrap every question in a typed Measurement
A small library where every query returns `Measured(n, evidence)` / `Unmeasured(reason)` /
`Refused(reason)`. It knows which instrument is valid for which question and refuses the rest.

| pros | cons |
|---|---|
| The **only** option that addresses Cause C | Only works if everyone routes through it |
| Format-agnostic — covers `.rws` and third-party DLLs too (goal 5) | Does not reduce the read cost |
| Cheap; composable with any of A/B/C | A library is not enforcement |

#### Option E — Enforce it at the tool call, with a PreToolUse hook
Refuse `grep`/`strings`/`wc` against known-structured artifacts (`DefDump/**`, `*.rws`,
`*.dll`) and name the correct instrument in the refusal.

| pros | cons |
|---|---|
| **The only option that acts BEFORE the wrong number exists** | Enforcement without a cheap alternative is just an obstacle (see goal 2) |
| Exactly the idiom this repo already trusts — `queue_lint`, `block_blanket_git_stage` | Needs a careful allowlist; grepping a `.rws` for a *literal string* is sometimes legitimate |
| Teaches at the moment of error, where the reader is standing | Another hook to maintain |

---

### 5. BUILD's recommendation

**C + D + E, layered — and E only after C is usable.**

- **C (SQLite)** because goal 1 falls out of the schema for free and goal 3 becomes trivial:
  a count is one number, and no question needs to load 315 MB. It is the only option that
  fixes Cause B *structurally* rather than by convention.
- **D (typed Measurement)** because it is the only thing that touches Cause C, and because
  `.rws` and third-party DLLs can never be reformatted — goal 5 needs it.
- **E (hook)** last, because a refusal without a cheap alternative is the freeze the owner
  warned about: *"this could be annoying if you keep freezing things unnecessarily."*

⚠️ **Keep JSON alongside SQLite for one capture cycle.** The dumper writes both, the
SQLite is checked against the JSON, and only when they agree does the JSON stop being
written. A format migration that is also a trust migration should not be a single step.

⚠️ **And the `.rws` is out of scope for any format work.** It is Ludeon's. The rule there
is D + E: never scan it, use the bridge or `savemap.py`, and let the hook say so.

---

### 6. What the owner must decide

1. **Which option**, or which combination.
2. **SQLite or JSONL** if the dump is reformatted — the real trade is diffability and
   grep-ability (JSONL) against determinism and free tri-state (SQLite).
3. **Does the hook (E) go in**, given it will occasionally refuse a legitimate grep.
4. **Scope**: dump only, or every large scanned artifact — the world CSVs, `Player.log`,
   the savegames, the def dumps.
5. Whether this is v1 or v2. ⚠️ It is tooling, not content: it ships nothing to a player,
   but it protects every measurement that decides what does.

## verify

Depends on the option chosen. Common to all:

- A question whose answer is already known — `ThingDef` count, `AbilityDef` count — is asked
  through the new path and returns the **known-correct** value, where the old path returned
  a wrong one. This is the "validate the instrument against a known answer" rule applied to
  the instrument itself.
- Asking about a def type that was NOT captured returns an explicit *unmeasured*, never `0`.
- The five instrument failures in `BUILDABLE.md` that are format-caused are each re-run and
  each now returns the right number or an explicit refusal.
- A count question costs **fewer than 100 tokens** of output.

## criteria

No question about a large artifact can be answered with a plausible wrong number: every
answer is either measured, or explicitly refused with the reason and the right instrument
named. And the correct path is demonstrably *less* effort than `grep`, or it will not be
used and the criterion is not met however green the tests are.

## notes

Filed by BUILD 2026-08-21 on the owner's instruction, to be executed after a context clear —
so this item is written to be read cold, by someone who was not here.

The seven incidents, with per-tool status, are in `infrastructure/state/BUILDABLE.md` under
"INSTRUMENTS THAT RETURN A CONFIDENT WRONG ANSWER". Three were fixed in code that day
(`validate_patch.py`, `weapon_tag_audit.py`, the dump's `<FullName>.json` collision fix at
`d7cf154`, which is in the **assembly** and undeployed). Two are filed
(`TEXTURE_AUDIT_CUSTOM_GRAPHICCLASS_1`, `PAWNKIND_AUDIT_TAGLESS_BLIND_1`). Two are
techniques rather than tools and have no code fix — only the register and the rule.
