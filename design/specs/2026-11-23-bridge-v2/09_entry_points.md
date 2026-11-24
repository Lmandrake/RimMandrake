# BRIDGE v2.0, pass 3: a few rich entry points

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`. Written 2026-11-23.
The argument for Python scenes is `08_where_tests_live.md`. Tags as there: READ, MEASURED, GUESS n%.

## The owner's steer

2026-11-24 00:52Z: "I would also like to interject that I exposed you to some alternative thinking that "Claude does
better when it has a small number of very rich entry points into programs with excellent documentation" more than "a
thousand entry points to sort through and remember." That seems germane to BUILD's architecture here. Find that
discussion and ingest it into the current designs and plans please."

## What I found of that discussion, and how sure I am

| where I looked | what I found |
|---|---|
| the 2,197 conversation records of this repo (`conversations/*.md`), by phrase | "rich entry point": 0 files. "thousand tools / entry points": 0. "fewer tools", "tools for agents", "too many tools": 0. "deep module": 1 file, 2026-11-07 `[MEASURED: grep]` |
| the same records, by name | "Pocock", "Ousterhout" or "deep modules": 11 files, 2026-11-07 to 2026-11-09 `[MEASURED]` |
| `~/dev/Lodestar/docs`, `~/dev/Lodestar/conversations`, `~/dev/MandrakeWorkflows`, by the same phrases | one hit: `MandrakeWorkflows/skills/research-plan/references/sources/anthropic.md` §11, a three-line digest of Anthropic's "Writing effective tools for agents" that does not carry its point about the number of tools `[MEASURED]` |
| the owner's rulings in the ledger | his words above are the first record of the phrase `[MEASURED: owner_rulings.py --grep "entry point"]` |

**The nearest record is the Pocock study of 2026-11-07.** On that day he wrote: "I got all this from mattpocock/skills a
talk I just watched, arguing that I should be more involved in the design of the interfaces and modules within our code
than I normally am" `[READ: conversations/2026-11-07-2051-e0f06144.md]`. The study is
`design/RimMandrake/mattpocock_design_suggestions.md` and `design/RimMandrake/2026-11-07-pocock-design/03-merged.md`.

Two public texts state the idea. I fetched and read both today (the study of 2026-11-07 had read only search
summaries):

- Matt Pocock, "How to make codebases AI agents love" (aihero.dev, page updated 2026-02-26) `[READ]`: "The idea is
  simple: lots of implementation controlled by a simple interface." and "Instead of holding hundreds of interrelated
  modules in your head, you keep seven or eight chunks."
- Anthropic, "Writing effective tools for agents" (2025-09-11) `[READ]`: "More tools don't always lead to better
  outcomes." and "Too many tools or overlapping tools can also distract agents from pursuing efficient strategies." Its
  example replaces `list_users`, `list_events` and `create_event` by one `schedule_event` tool. On documentation:
  "think of how you would describe your tool to a new hire on your team." On results: tools "should take care to return
  only high signal information back to agents."

**How sure.** That the Pocock talk and study are the discussion he means: `GUESS 70%`. His wording ("entry points into
programs", "a thousand entry points") is nearer to the Anthropic text about tools than to Pocock's about modules, so he
may have met it elsewhere (another project's session, or something he read): `GUESS 30%`. I found no record of such a
session. The two sources say the same thing for our purpose, so the design below does not depend on which one it was.

**What to take from them** (the study's own list, which stands): depth is a property of the interface; the interface is
everything a caller must know (types, order, error modes, performance); **the deletion test** (delete the thing in your
head: if the complexity vanishes it was a pass-through, if it comes back in N callers it earned its place); one adapter
is a hypothetical seam, two are a real one.

## What an agent faces today

`[MEASURED in this run: grep over the tree; scratch D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3\tool_use.json]`

| | count |
|---|---|
| tools in the bridge's schema record (`northstar_driver/tool_schemas.json`) | **563**: 430 `jawa/`, 107 `rimworld/`, 18 `rimbridge/`, 8 `deepfire/` |
| live scripts (proofs, validations, north-star runners, mod scripts) that call the bridge | 436 files, 227,107 lines |
| distinct tools that those scripts name | 335 (268 `jawa/`, 67 of the server's) |
| `jawa/` tools that no live script names | 172 of 430 |
| `jawa/` tools that no Python file of any kind names | 123 of 430 |
| tools that one live script names | median 6; one script in ten names 25 or more; the most is 76 |
| share of call sites covered by the most used tools | top 10: 36%; top 20: 51%; top 50: 72%; top 100: 87% |
| tools named in one live file only | 107 |
| Python driver layers between a script and the bridge | at least five: `rimbridge_client.py` (68 functions), `validation_core.py` (111), `modcheck/helpers.py` (47), `scenes/scenelib.py` (50), `modcheck/quiet_site.py` (22). `ticks` is defined in five places |

Limit of these counts: a tool that an agent calls by hand in a session leaves no Python file, so "no Python names it"
does not mean "nobody uses it". The bridge's call journal would say; nobody has counted it `[UNMEASURED]`.

**Reading.** A live test really uses about 6 tools, and half of all use is 20 tools. But the 20 are low-level
(`list_things`, `spawn_pawn`, `set_terrain_batch`, `step_game_ticks`, `static_call`), so every script builds its own
staging, waiting and reading out of them. That is the shallow shape that both sources warn about: many small entry
points, and the knowledge of how to combine them repeated in 436 files.

## The entry points

One Python module, `src/RimMandrake/Utils/scene.py`, is the whole interface for a test author and for an agent. It has
**ten names**. The 563 tools are its implementation.

The count, stated honestly (GPT's objection, taken): ten names are not ten operations. `s.act` is a family of ten verbs
with different preconditions and failure modes; `s.read` has a batch form; `s.raw` has a search beside it. A caller
learns **ten names and about twenty operations**, against 563 tools and five driver layers today.

| # | name | accepts | returns | what it hides |
|---|---|---|---|---|
| 1 | `scene.contract(claim, kind, opportunity, exposure, success, forbidden, end, limit, budget)` | the scene's contract as data. **Nothing touches the game** | the contract, with its hash. It refuses a success with no exposure, a kind B scene with no budget, a def name that is not in the frozen dump, a condition on a value that no track or tap records | the lint duties of pass two's compiler; the list of tracks and taps that the conditions need |
| 2 | `scene.open(game, needs, contract)` | the game's name; the mods, the map kind, a fixture save or "fresh map", the calm profile; the contract | a session, and a **phase report**: for each of lock, identify, load, settle, calm, arm: done or refused, what it changed, and what was put back when a later phase refused. The receipt is in it: loaded DLL hashes, mod list, game state | the driver lock, the handshake, the load and its settle, the game watcher, calm, arming the recorders for the whole session |
| 3 | `s.stage(cast, things, terrain)` | the cast by alias (kind, faction, health, gear, skills, position), things, terrain, on a clean station | each alias bound to the object that the game really made, read back **in the same call that made it**; a staging fault when the game made something else; on a failure half way, what was made and what was not | the station allocator, clean, the batch tools, the capability checks |
| 4 | `s.run(until, limit, speed)` | a condition (built by `scene.cond` helpers) or a tick count; a tick limit | a **run handle** with the result: the tick on which the condition turned true, the values, why it ended; the game is paused on that tick. The handle has `status()` and `cancel()`, so a lost reply is not a lost run | `jawa/run_until`: the game's own loop, the end-of-tick evaluation, the exact pause, the comparison of the sample after the pause with the sample at the end of the tick |
| 5 | `s.act.<verb>(...)`, and `s.act.batch([...])` | one act on the paused game: `order` (through the game's own work giver or float menu code), `job`, `damage`, `explode`, `incident`, `weather`, `setting`, `place`, `remove`, `reload`. `batch` does several acts in one call, with **no frame between them** | the effect, read back; a giver's refusal as a fact. Each act has a request id (a repeat is refused, not done twice) and a start and an end record in the trace, with the tick, the frame count and the force level | which present tool does it, `jawa/act_batch`, the deviation record, the load barrier of `reload` |
| 6 | `s.read(alias, path)`, and `s.read_many(...)` | an alias and a field path, or a reader from the reviewed list; a rectangle | the value with its state: ok, gone, unbound, error. Never 0 for "could not read" | the probes, the batch reads. A reader has no effect on the game |
| 7 | `scene.judge(run_dir)` | a run's folder (commit hash, contract, trace, receipt) | one of the seven outcomes, the first failed condition with its values. It checks the evidence contract first and answers COULD NOT LOOK when a point fails. `--rejudge` judges a kept trace again | the classifier, the evidence contract, the run's history |
| 8 | `s.shot(rect, name)` | a rectangle of the map, a name | the path of a picture that is known to be fresh, with the tick | the off-screen capture, the settle of drawn positions, the unique file name |
| 9 | `scene.attach(game)` | a game's name | the open session of that game after a driver died or a reply was lost: its state, its last run, its trace so far; then `close()` or `abort()`, each of which writes the trace's closing record and leaves the game paused | the session's lease, the reconnect, the durable end of a trace |
| 10 | `s.raw(tool, **args)`, and `scene.tools(words)` | any tool of the 563 by name; search words | the tool's reply; a short list of tools that match, one line each | the exploring layer. The game side writes every raw call into the trace. **Any raw call of a changing tool stamps the run EXPLORED**; there is no list of allowed tool names, because a name does not say what a call does (`jawa/static_call` can read or write). An acceptance script that needs a raw changing call needs a verb first |

**What a condition's words mean.** Each act writes a start record and an end record. "Unchanged since the blast" compares
with the last sample **before the start record** of the act named "blast", so a victim hurt by the explosion itself is
seen (GPT's case: a baseline taken after the effects would pass a harmed victim).

A scene on this library (pass one's worked example 1, the spared carrier; a sketch, not run):

```python
import scene
from scene import cond as c

contract = scene.contract(
    claim="a carried pawn is spared by the blast", kind="A",
    exposure=[c.count("damage", victim="control", instigator="blast") >= 1],
    success=[c.unchanged("victim.health", since="blast"), c.alive("victim")],
    forbidden=[c.count("spawn", duplicate_of="victim") > 0],
    end=c.ticks_after("blast", 120), limit=600)
with scene.open("ArchSmall", needs={"mods": ["ExplosiveKnockback"], "map": "settlement"}, contract=contract) as s:
    cast = s.stage(cast={
        "carrier": dict(kind="Colonist", at="center", hold="pin"),
        "victim":  dict(kind="Colonist", downed=True, carried_by="carrier"),
        "control": dict(kind="Colonist", downed=True, at=("mirror", "victim"))})
    s.run(until=c.ticks(30))
    s.act.explode("Bomb", cell=cast["carrier"].cell.offset(2, 0), radius=3.9, name="blast")
    s.run(until=contract.end)
print(scene.judge(s.run_dir))
```

It is 18 lines, against 21 lines of YAML for the same scene in `02_needs_design.md`.

**Changing a test in progress** needs an interactive session, because an edit of a script's file does not change a
script that is already running. `python.exe src\RimMandrake\Utils\scene.py explore <game>` opens a Python prompt on a
session; a test pilot runs, reads, acts and runs again there, line by line. Every run made there is stamped EXPLORED.
An acceptance run is `scene.py accept <script>`: a clean tree, the commit hash on the receipt, no keyboard.

### The documentation of each entry point

Each name has **one page**, and the page is the function's docstring: `python3 src/RimMandrake/Utils/scene.py
help <name>` prints it, and `help` alone prints the ten names with one line each. One home, so it cannot drift from the
code's signature (a selftest compares the two). Three catalogs are printed from the code in the same way, because a
docstring cannot hold them: `help cond` (every condition helper), `help readers` (the reviewed readers), `help verbs`
(the ten verbs of `s.act`, each with its preconditions, when it is complete, and its failure modes). One more page,
`help order`, states what all ten names share: the life of a session, the order of records in the trace, and what a
request id is. A page holds, in this order (Anthropic's test: "how you would describe your tool to a new hire"):

1. what it does, in two sentences, and when to use another entry point instead;
2. every argument, with its unit and an example value;
3. what it returns, field by field, and what each of "zero", "none", "could not look" and "failed" looks like;
4. every refusal by name, each with its repair;
5. what it changes in the game and what is put back at close;
6. one complete example that runs;
7. its limits (what it does not see, what it does not survive).

The `rimbridge` skill then points at `scene.py help` for testing and keeps its own text for world and map authoring.
(Skills are edited in curation sessions; that edit is a line for the next one.)

## What happens to the other tools

Three layers, by the deletion test.

| layer | what | how many | rule |
|---|---|---|---|
| **entry points** | the ten names of `scene.py` | 10 | the only thing a scene imports; the only thing the testing docs teach |
| **instruments** | the tools that the ten call: the batch stagers, `jawa/run_until`, the recorders, calm, the gates, the forcing tools, the readers | about 60 `[GUESS 60%: the tools that 20 or more live files name are 58]` | kept, each with its promise on a boundary page when it is next touched; not taught to scene authors |
| **exploring layer** | every other tool | about 500 | kept, hidden from the default docs, reached by `s.raw` and found by `scene.tools`. A test pilot uses them in a hunt. A tool that three scenes call through `s.raw` is promoted into a verb of `s.act` or a reader |
| **deletion candidates** | tools with no Python caller and no call in the bridge's journal over 30 days | at most 123 of 430 `[MEASURED upper bound; the journal is UNMEASURED]` | not deleted on today's evidence. First count the journal. Then delete in one curation pass, each with its name in the commit |

The world and map authoring tools (`jawa/world_*`, the paint and biome tools) are not test tools. They stay as they
are; this design does not touch them.

The five Python layers become one. `scene.py` is built by **extracting** what `validation_core.py`, `modcheck/helpers.py`,
`quiet_site.py` and `scenelib.py` already do, not by writing it again; each of them then imports `scene.py` or retires
when its last caller converts. This is the owner's ruling of 2026-11-22: "single source python scripts rather than ...
multiply implemented competing systems ... Extract, simplify, generalize, prove coverage, retire old cruft".
The 436 scripts do not convert for this design. A script converts when its mod next advances.

## The same question, asked of pass two's plan

| what an author or an agent must learn | pass two (`05`, `06`) | this pass |
|---|---|---|
| new languages | 2: the YAML scene file; the JSON run plan | 0 |
| new vocabulary inside them | 11 top-level keys of a scene file; the functions of its expressions (`mirror_of`, `inside_radius_of`, `carried_by`, `duplicate_of`, `at()`, `count() where`); 9 act ops; about 6 stage ops | the 10 verbs of `s.act`; the helper functions of `scene.cond` |
| new bridge tools | `jawa/run_plan`, `jawa/run_status`; later `scene.py run`, `compare`, `both-ways`, `sweep` | `jawa/run_until` (the landed slice, widened), `jawa/act_batch`; a bounded rule later, if measured (`08`) |
| new C# attributes that a mod author must know | 5: `RMProbe`, `RMFixture`, `RMReset`, `RMDigest`, `RMTrace` | 3: `RMReset`, `RMDigest`, `RMTrace` (decision 8 of `05`, kept) |
| new Python programs | `scene_compile.py`, `scene_judge.py`, `scene_verdicts.py`, `scene.py` | `scene.py` (the judge is its name 7; `accept` and `explore` are its two launchers), `scene_verdicts.py` |
| the condition tree language | kept (it exists) | kept, behind `scene.cond` helpers |

Pass two's plan would have added a third way to write a scene (after Python scripts and `[RMTest]` C#) with its own
language. By the deletion test its compiler is mostly a pass-through: delete it, and the same knowledge sits in the
library calls of the scene, in a language that the agent already knows. What does not pass through is the compiler's
lint; that duty moves to `scene.contract` and must not be lost.

## What I am not sure of

- **Ten is a design, not a measurement.** Whether an agent writes better scenes on ten names than on 563 tools
  is the owner's hypothesis and both sources' claim; nobody has measured it here. The cheap test: convert three scenes
  that failed for harness reasons, give a fresh agent only `scene.py help`, and count lines, calls and reruns against
  the old scripts `GUESS 75%` that it is clearly better.
- **The counts of trouble above do not show that many entry points caused it.** A full disk fails a run under any
  interface. The counts show how the work is spread today; the cause is the hypothesis under test.
- **`scene.open` does six things.** The phase report makes each one visible. If agents still cannot diagnose a refusal
  from it, `open` is split.
- **The contract as data is a small language too** (`scene.cond`). It is Python functions that build the condition tree
  that exists, so it adds no parser. It can still grow without limit; the rule is that a helper is added only when two
  scenes need it.
- **A library can rot into a sixth layer.** The guard is the retire rule above: each older layer imports `scene.py` or
  is deleted when its last caller converts, and no new script may import an older layer.
