# Designer Cleanse and the definition of a bar (2026-11-16, v2 after GPT's review)

Item: `RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED`. The brief the runs receive:
`src/RimMandrake/rimflow/roles/designer_cleanse.md`. Written by the Designer window of the Conductor with the owner.

## 1. What the owner asked for (2026-11-16, about 10:15 to 10:30 PM PST; his words are on the item)

A more aggressive Designer: a comprehensive definition of each mod before it is built or built further; frivolous
aspects moved to the next version or recommended for retirement; a re-examination of what a bar is, *"all the way
through. And Designer is the very first part of it"*; offline simulations, geometry and other models specified ahead of
time; then a mass of runs, on Codex, over every biome other than Pyrelands, with no blocking questions (*"just put them
all together. I'll attend to them afterwards."*).

His card answers, same sitting:

| question | his answer |
|---|---|
| what a biome's first version (0.1.0) may contain | land, life, one signature |
| default fate of an extra and its code | next version, switched off |
| how much the runs come to him | (typed) two pages per mod, dense, concise, very clear questions; and the models specified ahead of time |
| what gates a cleansed design | one whole-mod check instead of the cold-reader exam and the coverage judge |

## 2. What the measurements say [measured 2026-11-16, 10:10 to 10:30 PM PST]

- Leaning Scrub's locked tree has 64 bars, 60 proposed for the live tier. Cauldron 18 (18 live), Contagion 25 (17),
  FeverWood 23 (21), Stillsand 14 (14), Gelatinous Slime 13 (13). Their inventories hold 44 to 86 capabilities each.
- `designer_stage.py` checks a contradiction only when the Designer itself recorded one (line 1322). It has no check
  that two bars can hold together, that a scene runs with the mod's mechanics on (a scene's `start` need only be
  non-blank), that a figurative word is marked, or that a bar did not come from a builder's habit. `bar_rule.py` (no
  tuning numbers) is applied by the coverage judge, not by the Designer's launcher.
- Pyrelands: six bars pinned numbers, every in-game scene ran with fire off and the sky locked clear, one promised
  mechanic had no spec, and "a line of fire" was held literally until he loosened it. Slack: five bars and checks read
  the same 0.6 cell of cord and nobody had listed them together; a builder's habit stood in an impossibility proof.
- 23 biome members of Baroque Biomes other than Pyrelands have source; 6 of them have a concept folder.

## 3. The definition of a bar (proposed; replaces the leaf fields `experience`, `false_pass`, `red` in spirit)

**Three kinds of statement, never mixed.**

| kind | what it is | whose | part of passing | may hold a number |
|---|---|---|---|---|
| bar | an experience a player would notice, without which he would reject this version | the owner's | yes, and nothing else is | no |
| check | a regression reading kept so a later change cannot silently break something | ours | no | yes |
| rule | a choice we made about how to build it | ours, attackable | no | yes |

(v2: the wording a run applies is the brief's; where this section and the brief differ, the brief is newer. GPT's
review changed: a judge passes on bars alone but the inherited floor still applies and a red check is the builder's;
numbers are legal in `range` and `sees`; no example quota, but the laziest build that satisfies the words is always
tried; `sees` carries a control against the cheapest other explanation; meetings are written once per shared thing,
with loops and three-way meetings hunted; Seeable and Stranger are the reviewer's tests and mean repair; the signature
is one chain of cause and effect whose parts may cross land, life and code; coupling in code is not need.)

**A bar's six parts:** `says` (one sentence: who notices what, where) · `meant` with its source, and `figurative`
(each word not to be held literally, and what it stands for) · `accept` (two or more pictures that pass, one departing
from the literal wording) and `reject` (two or more that fail, one satisfying the literal wording) · `range` (the
situations it holds across: what varies, what is left out) · `sees` (the cheapest instrument that truly tells pass from
fail, what must be switched on for its reading to count, and for a live-only bar why nothing cheaper can) · `touches`
and `meets` (every other bar and rule on the same state, geometry or moment, each `holds_together`: argued, measured,
or unknown with the model that would settle it).

**Five tests; failing one means it is not a bar:** Reject (alone false, he rejects the mod) · Renormalize (true and
unchanged after every number is retuned and an art variant added) · First version (land, life, the signature, or
strictly needed by one) · Seeable (an instrument can tell pass from fail with the whole mod on) · Stranger (a cold
reader sorts the accept and reject pictures the same way).

**One whole bar per mod:** the mod complete, every mechanic on, nothing locked, across its cycle, with a mid-way reload
and a second order of the main actions. It absorbs today's `walk` leaf.

Why each part exists: `figurative` and `accept`/`reject` answer the "line of fire" held literally; `range` answers
bars proven on one staged scene; `sees` answers scenes that could not see the mechanic and the 60 live-only bars;
`meets` answers the conflicts found only by rescue; the rule kind answers the builder's habit in a proof; the check
kind answers the tuning numbers (`standing_rulings.md` §A passing bar is an experience).

What this asks of the later stages (not built by this item; each is a ticket when the definition is accepted):
the builder receives `rules` as attackable and `checks` as its own regression set; the offline tester builds the
`range` generator and prints worst value and what it sampled; the in-game tester refuses a reading taken with
anything in `sees` switched off; a judge's refusal must name which of the six parts the build fails.

## 4. The cleanse run

One run per mod, on Codex (the mass run) or Fable (a single mod worked as a whole). It writes only the proposal folder
`design/concepts/<Mod>/cleanse/` (files: the brief's table). It asks nothing and waits for nothing.

**The whole-mod check** (the only gate): a fresh reviewer that did not write the proposal, on a different model from
the author, reads the proposal against the brief and the mod's source and returns refusal records (evidence,
`would_pass`, `smallest_fix`) under these heads only: two bars or a bar and a rule that cannot hold together; a kept
mechanic with no definition; an instrument or scene that would read with a mechanic off or the sky locked; a number,
count or "every field" in a bar; a figurative word unmarked; a rule or check dressed as a bar; a bar with no range; an
extra left in the first version without its `needed_by` deletion argument; a contradiction with a standing ruling or
the lore; a moved extra still relied on by a kept bar; a sourced core promise omitted or weakened; evidence that
cannot tell success from a plausible false pass; a claim of his authority with no source. The reviewer is given his
words and the source before the proposal, sorts each bar's pictures blind (the Stranger test), and must name one
capability the census missed and one loop or three-way meeting, or say it looked and found none. One round of fixes by the author, one second look. What the second look still
refuses is printed on his pages in the reviewer's words and the proposal cannot be applied until it is resolved or he
accepts it; nothing loops.

**Applying a proposal** (only on his word after his look at the two pages; it changes a tree):
a program writes the new tree, sheet and next-version file from the proposal and files the tickets. Not part of
tonight's mass run.

## 5. Build plan

1. `src/RimMandrake/rimflow/designer_cleanse.py`: `case <Mod>` (builds the CASE: concept folder if any, source
   folders, items, rulings and lore list, output folder), `run <Mod> [--runner codex|claude]` (a pool clone, the brief
   plus the CASE, `agent_runner.py`, the Codex quota gate, publishes only the proposal folder), `check <dir>` (the
   proposal's shape: every file present, every census row has a fate, every bar has its six parts, no number in a bar
   by `bar_rule.py`'s detector, every old bar id mapped, `owner_pages.md` within length, counts in `result.json` equal
   the files), `review <Mod>` (the whole-mod check and its one fix round), `fleet --all-biomes-but Pyrelands
   --parallel N` (detached; a status file), `status`.
2. The owner's hold stays on builds; a design-only pass is allowed on a held mod when the hold row carries his words
   for it (`mod_owner_hold.py allow-design <Mod> --said "…"`), and the launcher refuses a held mod without it.
3. Selftest `selftest_designer_cleanse.py`, red first: `check` refuses a proposal with a bar holding "30%", a bar with
   no `range`, a census row with no fate, an old bar unmapped, a three-page `owner_pages.md`; accepts a minimal good one.
4. Later, on his acceptance of §3: the stage machine's Write stage emits the six-part bar, `concept_tree.py` carries
   `checks` and `rules`, the Exam and the coverage judge are replaced by the whole-mod check, and the apply program.

Acceptance test for this item: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_cleanse` passes
(fails on the base commit: the file does not exist), and `designer_cleanse.py status` shows a `proposed` or `blocked`
result with a passing `check` for each of the 23 biomes other than Pyrelands.
