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
nine entry points. The 563 tools are its implementation.

| # | entry point | accepts | returns | what it hides |
|---|---|---|---|---|
| 1 | `scene.open(game, needs)` | the game's name; the mods and map kind the scene needs; a fixture save or "fresh map"; the calm profile's name | a session, and the **receipt**: the loaded DLL hashes, the mod list, the profile, the game's state. It refuses, by name, the wrong game, the wrong build, a broken game, a game that another process drives | the driver lock, the handshake, the load and its settle, the game watcher, arming calm, arming the recorders, the put-back at close |
| 2 | `s.contract(claim, kind, opportunity, exposure, success, forbidden, end, budget)` | the scene's contract as data, before the game is touched | the contract's hash. It refuses a success with no exposure, a kind B scene with no budget, a def name that is not in the frozen dump, a condition on a value that no track or tap records | the lint of pass two's compiler; the tracks and taps that the conditions need are armed from it |
| 3 | `s.stage(cast, things, terrain)` | the cast by alias (kind, faction, health, gear, skills, position), things, terrain, on a clean station | each alias bound to the object that the game really made, **read back**; a staging fault when the game made something else (a replaced pawn kind, a blocked cell) | the station allocator, clean, the batch tools, the capability checks ("can do this work type", "has a ranged attack") |
| 4 | `s.run(until, limit, speed)` | a condition (built by helper functions) or a tick count; a tick limit | the tick on which the condition turned true, the values that made it true, why the run ended. The game is **paused on that tick** | `jawa/run_until`: the game's own loop, the end-of-tick evaluation, the exact pause, the handle and the status reads for a long run |
| 5 | `s.act.<verb>(...)` | one act on the paused game: `order` (through the work giver or the float menu), `job`, `damage`, `explode`, `incident`, `weather`, `setting`, `place`, `remove`, `reload` | the effect, read back; a giver's refusal as a fact. Every act is written into the trace with its tick and its force level | which of the present tools does it, the read-back, the deviation record |
| 6 | `s.read(alias, path)` and `s.read_many(...)` | an alias and a field path, or a named reader; a rectangle | the value with its state: ok, gone, unbound, error. Never 0 for "could not read" | the probes, the batch reads, the reviewed list of readers |
| 7 | `scene.judge(run_dir)` | a run's folder (script hash, contract, trace, receipt) | one of the seven outcomes, the first failed condition with its values. It checks the evidence contract first and answers COULD NOT LOOK when a point fails. `--rejudge` judges a kept trace again | the classifier, the evidence contract, the run's history |
| 8 | `s.shot(rect, name)` | a rectangle of the map, a name | the path of a picture that is known to be fresh, with the tick | the off-screen capture, the settle of drawn positions, the unique file name |
| 9 | `s.raw(tool, **args)` and `scene.tools(words)` | any tool of the 563 by name; search words | the tool's reply; a short list of tools that match, each with one line | the exploring layer. Every raw call is written into the trace. A raw call that changes the game stamps the run EXPLORED unless the tool is on the reviewed list |

A scene on this library (pass one's worked example 1, the spared carrier; a sketch, not run):

```python
import scene
from scene import cond as c

with scene.open("ArchSmall", needs={"mods": ["ExplosiveKnockback"], "map": "settlement"}) as s:
    s.contract(claim="a carried pawn is spared by the blast", kind="A",
               exposure=[c.count("damage", victim="control", instigator="blast") >= 1],
               success=[c.unchanged("victim.health", since="blast"), c.alive("victim")],
               forbidden=[c.count("spawn", duplicate_of="victim") > 0],
               end=c.ticks_after("blast", 120), limit=600)
    cast = s.stage(cast={
        "carrier": dict(kind="Colonist", at="center", hold="pin"),
        "victim":  dict(kind="Colonist", downed=True, carried_by="carrier"),
        "control": dict(kind="Colonist", downed=True, at=("mirror", "victim"))})
    s.run(until=c.ticks(30))
    s.act.explode("Bomb", cell=cast["carrier"].cell.offset(2, 0), radius=3.9, name="blast")
    s.run(until=s.end)
print(scene.judge(s.run_dir))
```

It is 17 lines, against 21 lines of YAML for the same scene
in `02_needs_design.md`. Between any two lines a test pilot can stop, read with `s.read`, and change what comes next.

### The documentation of each entry point

Each entry point has **one page**, and the page is the function's docstring: `python3 src/RimMandrake/Utils/scene.py
help <name>` prints it, and `help` alone prints the nine names with one line each. One home, so it cannot disagree with
the code. A page holds, in this order (Anthropic's test: "how you would describe your tool to a new hire"):

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
| **entry points** | the nine of `scene.py` | 9 | the only thing a scene imports; the only thing the testing docs teach |
| **instruments** | the tools that the nine call: the batch stagers, `jawa/run_until`, the recorders, calm, the gates, the forcing tools, the readers | about 60 `[GUESS 60%: the tools that 20 or more live files name are 58]` | kept, each with its promise on a boundary page when it is next touched; not taught to scene authors |
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
| new bridge tools | `jawa/run_plan`, `jawa/run_status`; later `scene.py run`, `compare`, `both-ways`, `sweep` | `jawa/run_until` (the landed slice, generalized) |
| new C# attributes that a mod author must know | 5: `RMProbe`, `RMFixture`, `RMReset`, `RMDigest`, `RMTrace` | 3: `RMReset`, `RMDigest`, `RMTrace` (decision 8 of `05`, kept) |
| new Python programs | `scene_compile.py`, `scene_judge.py`, `scene_verdicts.py`, `scene.py` | `scene.py` (the judge is its entry point 7), `scene_verdicts.py` |
| the condition tree language | kept (it exists) | kept, behind `scene.cond` helpers |

Pass two's plan would have added a third way to write a scene (after Python scripts and `[RMTest]` C#) with its own
language. By the deletion test its compiler is a pass-through: delete it, and the same knowledge sits in the library
calls of the scene, in a language that the agent already knows.

## What I am not sure of

- **Nine is a design, not a measurement.** Whether an agent writes better scenes on nine entry points than on 563 tools
  is the owner's hypothesis and both sources' claim; nobody has measured it here. The cheap test: convert three scenes
  that failed for harness reasons, give a fresh agent only `scene.py help`, and count lines, calls and reruns against
  the old scripts `GUESS 75%` that it is clearly better.
- **`s.act` is ten verbs under one name.** Counting it as one entry point is fair only if the verbs share one shape
  (target by alias, read-back, a trace record). If they do not, it is ten entry points and the count is 18.
- **The contract as data is a small language too** (`scene.cond`). It is Python functions that build the condition tree
  that exists, so it adds no parser. It can still grow without limit; the rule is that a helper is added only when two
  scenes need it.
- **A library can rot into a sixth layer.** The guard is the retire rule above: each older layer imports `scene.py` or
  is deleted when its last caller converts, and no new script may import an older layer.
