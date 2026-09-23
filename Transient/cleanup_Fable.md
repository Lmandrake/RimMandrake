# Guidance-file and skill-library audit — for Fable

Written 2026-09-23 on the **Laptop** by a BENCH session, at the owner's instruction, for
Fable to examine later the same day. Nothing here has been acted on. **No owner decision
was taken** — a question card was drafted and interrupted before it was answered, so every
"open decision" below is genuinely open.

Scope of the audit: `CLAUDE.md` (project + global), `MEMORY.md`, `infrastructure/state/LESSONS_INBOX.md`,
the 28 project skills, the 41 global skills, and the skill-wiring links. Grounded against the
installed `skill-creator:skill-creator` skill (authoring rules) and the `claude-api` skill's
`shared/prompt-caching.md` (cost model).

⚠️ **This file lives in `Transient/` — tracked and pushed, but ~14 day shelf life.** So it must
never be the only copy of anything, and ⛔ **no committed doc or queue item may cite this path.**
Anything here that survives the reading belongs in a `rimflow` item, a skill, or `CLAUDE.md`
itself. If Fable acts on §4 (the missing skill), the skill is the durable artifact — not this.

---

## 🔴 Correct this premise first: size is an ATTENTION lever, not a cost lever

The audit was asked to look for ways to "reduce the size of our guidance files." The measured
cost model says shrinking them saves very little money, and the reason matters for how the
rest of this document should be read.

Always-loaded context, MEASURED 2026-09-23 (bytes ÷ 4 for tokens):

| Source | bytes | ~tokens |
|---|---:|---:|
| `CLAUDE.md` (project) | 52,062 | 13,015 |
| `~/.claude/CLAUDE.md` (global) | 20,682 | 5,170 |
| `MEMORY.md` (auto-memory index) | 2,272 | 568 |
| Skill frontmatter × 69 skills | 51,478 | 12,869 |
| **Total** | **126,494** | **~31,623** |

Per `shared/prompt-caching.md`: cache **reads** cost ~0.1× base input price; cache **writes**
cost 1.25× at the default 5-minute TTL. That block sits in the cached prefix, so on Opus
($5/1M input) it costs roughly:

- **~$0.016 per warm turn** (cache read at $0.50/1M)
- **~$0.20 when the 5-minute TTL has lapsed** and the prefix is rewritten at 1.25×

⇒ **Cutting 40% of it saves well under a cent per warm turn.** The existing memory note
(`machine_token_cost_shape.md`) that a 5-minute idle gap costs ~6.7× per turn is consistent
with this and is the same phenomenon: the expensive event is the *gap*, not the *size*.

**So the argument for trimming is not cost.** It is that ~13k tokens of mostly-situational
scar tissue competes for attention on every task, including tasks it cannot apply to. That
argument got stronger with Opus 4.7, which per the `claude-api` migration guide "interprets
prompts more literally and explicitly than Claude Opus 4.6" — a file saturated in absolute
prohibitions lands harder, in both the useful and the unhelpful direction.

⚠️ **One thing deliberately NOT claimed:** whether editing `CLAUDE.md` mid-session invalidates
the live cached prefix for this or a concurrent window. Claude Code loads `CLAUDE.md` at
session start; whether a mid-session edit re-enters the prefix was not measured. Do not
assert it either way without measuring — it would otherwise look like a reason to batch
`CLAUDE.md` edits, and that reason is currently UNMEASURED.

---

## Findings

### 1. Skill descriptions are half the fixed budget — and the cheapest real win

MEASURED: 69 skills, descriptions totalling **48,853 chars (~12,213 tokens)**, median **680
chars**, 15 of them over 900. Longest: `claim-provenance` 1221, `evidence-bound-papers` 1175,
`ideogram` 1160, `cowork-bridge` 1146, `knowledge-registry` 1087, `rimworld-start-prep` 1013,
`rimworld-ideoligion` 1011.

`skill-creator` puts the metadata budget at "~100 words" (≈550 chars). So the library median
runs ~25% over and the top fifteen run roughly 2×.

🔑 **But there is a genuine tension here, not just bloat.** `skill-creator` also says Claude
"has a tendency to *undertrigger* skills" and instructs authors to make descriptions "a little
bit pushy." The long descriptions in this library are long *because* they are pushy — they
enumerate trigger phrases and skip-conditions. Trimming them is the cheapest measurable token
win available (~5k tokens off every session), and it is also the change most likely to silently
break something, because **the description IS the trigger mechanism**.

⇒ If this is pursued, `skill-creator`'s description-optimizer (`scripts/run_loop.py`, 20
should-trigger / should-not-trigger eval queries, 60/40 train/test split) is the only safe
route. A hand-trim with no trigger evals risks a skill that quietly stops firing — and per
the project's own `warn_skill_unwired.py` doctrine, "the only symptom is that the work it
encodes silently never happens."

### 2. 🔴 `LESSONS_INBOX.md` is write-only, and that is where the real loss is

MEASURED: **337 entries, 141,854 bytes (~35,500 tokens), mean 412 bytes per entry, longest
1,730.** The file's own header says "one line each, curated into skills in fresh-context
passes." The newline contract is honoured; the *spirit* is not — the mean entry is a paragraph.

Date distribution: **291 of 337 entries are from 2026-09 alone**; 1 from 2026-08; **45 carry
no date at all.** 226 commits have touched the file.

⇒ At roughly 11 lessons/day accruing and curation never having run at scale, the file doubles
in about a month. Nothing 35k tokens long gets read in a working session, which means **the
lessons in it are not reaching the skills that would fire them.** That is the actual cost —
not the disk, and not the tokens (it is not always-loaded).

Theme distribution (regex classification, entries may match more than one theme):

| matches | theme |
|---:|---|
| 92 | art / texture |
| 92 | XML / patch / def |
| 66 | bridge / live game |
| 57 | git / shared worktree |
| 57 | wrong number / lying instrument |
| 38 | doc rot |
| 38 | crash / cold load |
| 27 | subagent behaviour |

Most of these have an owning skill already (`rimworld-modding`, `rimbridge`,
`generating-rimworld-sprites`, `git-efficiency`, `efficient-subagents`). The drain is a
routing job, not an authoring job — except for the fifth row, which has no owner. See §4.

### 3. `Facts you cannot guess` is 37% of the project instruction file

MEASURED by section, `CLAUDE.md`:

| bytes | section |
|---:|---|
| **19,511** | **## Facts you cannot guess** |
| 5,443 | ## If it flies in the fiction, it flies in the game |
| 2,658 | ## "Star Wars style" naming is NOT Star Wars IP |
| 2,586 | ## A BIOME WITH ZERO TILES IS NOT A DEFECT |
| 2,302 | ## Tools |
| 2,042 | ## Code isn't clean until a review says so |
| 1,996 | ## What is where |
| 1,893 | ## The bridge is passed through one file |
| 1,833 | ## In-game LLM access is the Claude Code CLI |
| 1,792 | ## Git |
| (11 more sections, each < 1,800) | |

`Facts you cannot guess` is one flat bullet list of roughly 30 heterogeneous scars with no
internal grouping — engine facts, instrument failures, tooling traps, naming rulings and
subagent behaviour all interleaved. Finding the one that applies to the task in hand means
reading all of it.

⇒ The cheap, zero-risk change is **clustering with sub-headings and deleting nothing.** It
does not reduce tokens meaningfully; it reduces the cost of locating the relevant scar. Given
§0, that is the lever actually available.

### 4. 🔑 One failure class recurs everywhere and has no skill — strongest extraction candidate

**"A query whose SHAPE returns a confident wrong number."** Not a large-artifact problem, not
a binary-format problem, not a stale-doc problem — a *query construction* problem, where the
instrument answers plausibly and wrongly and the wrongness is invisible in the output.

Instances already recorded in `CLAUDE.md` alone:

- `ls <dir> | wc -l` answers **0** for a directory that does not exist → "queue is empty" was
  a wrong-path claim wearing a number; the real figure was **182**.
- `grep -c '<li>'` on `ModsConfig.xml` answers **48** against a real active count of **631**,
  because it counts *lines containing* the tag.
- A texture glob on `*south*` reads the **mask** (`_southm.png`, saturated by convention)
  instead of the art — inverted 4 of 7 decisions in one pass.
- `northstar.parse()` returns a **dict**, so `getattr(w, "must_show")` yields `None` → `len()`
  0 → "all four VALIDATED walks have 0 bars", an alarming wrong number.
- `[ -e src/RimMandrake/Pits ]` passes on a folder holding only `__pycache__` — an existence
  test standing in for an identity test.
- A sweep reading `subject:` from **line 2** reported zero failures across 78 walks while
  missing the only broken file, which carries it on line 3 — a fixed index standing in for a
  field.
- A backtick-only regex reads `None` for **50 of 78** walk subjects, because 34 are bare and
  16 absent.
- `<wildPlants>` uses the shorthand `<DefName>commonality</DefName>` form, so a parser written
  for `<li><plant>` reads every row as empty — two flatly contradictory measurements of one
  file in one session.
- Reading `ASHKARR_WORLDMAP_tiles.csv` for a *live* tile count — a record read as the planet.

Plus **57 inbox entries** matching the same theme.

**Existing coverage is adjacent but does not include this:**

| skill | covers | does not cover |
|---|---|---|
| `measuring-large-artifacts` (global, 282 lines) | files too big to read | a small query that lies |
| `verify-before-you-escalate` (project, 151) | a *written* claim worth checking | a claim you are about to generate yourself |
| `calibrating-binary-formats` (project, 186) | opaque binary encodings | text-shaped queries |

The doctrine exists in **enforcement** — `.claude/hooks/block_blind_scan.py` refuses a blind
scan and names the instrument — but nowhere in **prose**, so an agent learns it only by being
blocked, and only for the cases the hook pattern-matches.

Two heuristics already written down in `CLAUDE.md` that would be the spine of such a skill:

> "A count that is conveniently *or* alarmingly round is a query bug until proven otherwise,
> and the alarming direction is the one you will believe without checking."

> "Two passes agreeing on a round number is **not** corroboration when both share an
> instrument."

⇒ This generalizes well beyond RimWorld and beyond this repo. It is the one candidate in this
audit that would be worth having in **global** `~/.claude/skills/`, not project skills — with
the RimWorld-specific instances staying here as examples.

### 5. Five skills exceed the authoring guideline; progressive disclosure is otherwise healthy

`skill-creator`: "Keep SKILL.md under 500 lines; if you're approaching this limit, add an
additional layer of hierarchy."

Over the line: `generating-rimworld-sprites` **759**, `rimworld-modding` **512**,
`gravship-layout` **510**, `rimworld-xenotypes` **491** (at it), `rimbridge` **485** (near).
Globally: `ideogram` **477**, `review-sheets` **433**.

✅ Otherwise this library is in good shape on structure: **24 of 69** skills carry
`references/`, `scripts/` or `assets/` subdirectories, which is real progressive disclosure
rather than one long file.

### 6. Wiring: 28/28 correct, one orphan link

✅ Every project skill is discoverable — `skills/<name>/SKILL.md` has a working
`.claude/skills/<name>` for all 28.

⚠️ One orphan: `.claude/skills/review-sheets` → `/mnt/d/Luke/dev/review-sheets`, a WSL/Windows
path, dangling on the Laptop. It is the **only absolute-path link of the 29**; all others are
relative (`../../skills/<name>`). The `review-sheets` skill itself is installed globally at
`~/.claude/skills/review-sheets` (433 lines) and appears in the available-skills list, so
**nothing is currently lost** — this is an orphan, not an outage. It may resolve on the
Desktop. ⛔ Not deleted; the owner should say whether it was deliberate.

---

## Open decisions — NOT taken

These were drafted as a question card and the card was interrupted. **No option below has been
chosen, and none should be recorded as the owner's preference.**

**Q1 — which work to take on.** Four candidates, with the interaction that matters:

1. Drain the 337-entry lessons backlog into the owning skills. Buys: lessons reach the point
   of use; the file stops doubling monthly. Costs: multi-session; each entry needs a
   keep/fold/discard judgment that is partly taste.
2. Tighten the 69 skill descriptions toward ~550 chars. Buys: ~5k tokens off every session;
   mechanical and verifiable. Costs: the description is the trigger, so this needs
   `skill-creator`'s trigger-eval loop or it silently stops skills firing.
3. Extract the wrong-number skill (§4). Buys: names a failure class that has cost this project
   at least nine times, and generalizes to any project. Costs: one more skill in a large
   library; risks duplicating in prose what a hook already enforces.
4. **(3) while doing (1)** — these compound: 57 of the 337 backlog entries are instances of
   that one class, so the drain supplies the skill's evidence and the skill gives the drain a
   destination. Costs barely more than the drain alone, and is the largest single commitment.

The audit's recommendation was **(4)**, on the reasoning that the drain is the expensive half
either way and doing it with no destination is what produced the backlog in the first place.

**Q2 — what happens to the project instruction file.** Four options:

1. **Restructure in place, cut nothing** — cluster the flat 30-item scar list under
   sub-headings. Buys: identical coverage, far faster to locate the applicable scar, zero risk
   of losing a hard-won rule. Costs: token count barely moves; it is a legibility fix.
2. **Leave it exactly as is** — buys: nothing breaks, every scar stays guaranteed-read. Costs:
   ~13k tokens of situational lore competing for attention on every task.
3. **Move situational lore into the owning skills** (e.g. the 5.4KB flyer-animation section
   into a RimWorld skill). Buys: real size reduction, lore lands where the work happens.
   Costs: a skill only loads if it triggers, and every 🔴 in that file exists *because*
   something was missed once — moving it reintroduces exactly that exposure.
4. **Cut hard to a short charter** — buys: smallest fixed cost, sharpest remaining signal.
   Costs: highest risk of re-learning something expensive; most of the file is a record of a
   failure that already happened.

The audit's recommendation was **(1)**, on the reasoning in §0: once caching is accounted for,
size buys little, so legibility is the lever actually available without risking a scar.

---

## How every number here was produced

Re-measure rather than trusting this file — it is a record, and per house doctrine a record
is not the thing it records.

```bash
# always-loaded budget
wc -c CLAUDE.md ~/.claude/CLAUDE.md \
  ~/.claude/projects/-Users-mandrake-dev-RimMaster/memory/MEMORY.md

# skill sizes and description lengths: parse YAML frontmatter of every SKILL.md
#   under ~/.claude/skills/*/ and skills/*/ — extract the `description:` field,
#   measure len(); do NOT grep -c, which counts lines not fields.

# lessons inbox: count lines starting '- ', regex a YYYY-MM-DD out of each,
#   histogram by month, mean len(). 'wc -l' alone answers 343 (includes the
#   header and blanks) against 337 real entries.

# CLAUDE.md section sizes: split on '\n(?=## )', len() each chunk.

# wiring: for each skills/*/SKILL.md, test .claude/skills/<name>/SKILL.md exists
#   (os.path.exists follows links, so a dangling link correctly reports missing).
```

⚠️ Two instrument warnings earned during this audit itself, in the spirit of §4:

- `wc -l` on `LESSONS_INBOX.md` answers **343**; the real entry count is **337**. The
  difference is the header and blank lines. A line count is not an entry count.
- A first attempt to total added/deleted lines from `git log --numstat` summed the commit
  metadata lines along with the counts and returned **378,913,720 added** — an obviously
  absurd figure that would have been quietly plausible had it been off by 10× instead of 10⁵×.
  The deletion figure quoted in §2 (~4.2k) comes from the deletions column only and should be
  re-derived before being repeated.
