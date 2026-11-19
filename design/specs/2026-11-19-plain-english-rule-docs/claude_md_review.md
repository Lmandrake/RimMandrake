# Review of `CLAUDE.md`: what belongs in it, and which lines a cold reader cannot act on

Item: `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. Run 1, 2026-11-19. The review read `CLAUDE.md` at
commit `328611932d`. The drain of the same day (commit `52a6cb4195`) kept each rule. This review asks two new questions.

1. Does each section belong in `CLAUDE.md`?
2. Can a cold reader act on each line?

## The result in short

- `CLAUDE.md` has 51 sections. The review keeps 39. It names 11 sections to move out and 1 section to merge.
- The review found 24 lines that a cold reader cannot act on. This run rewrote 17 of them in place.
- The run proposes a sentence for 1 more line. The run could not determine the meaning of 6 lines.
- The run moved no section. Each move is a choice for the Conductor, with its gain and its cost.
- Both no-loss checks pass on the new `CLAUDE.md`. Each check failed first on a planted loss. [measured]
- The file grew from 39,902 to 41,072 bytes. A plain sentence is longer than a coined term.
- The STE lint went from 1.51 to 1.48 per 100 words. Sentences over 20 words went from 2 to 1. [measured]

## The test for "belongs in `CLAUDE.md`"

A rule belongs in `CLAUDE.md` when both statements are true:

- each agent that loads `CLAUDE.md` needs the rule in most sessions;
- a break of the rule is costly.

These sessions load `CLAUDE.md`: the Conductor window, each detached helper and each role run. A subagent does not
load it. Each `.claude/agents/rm-*.md` file sets `omitClaudeMd: true`. A subagent gets a short list of rules from
`.claude/rm_agent_shared_block.md`. That block tells the subagent to search `CLAUDE.md` by topic.

So a move out of `CLAUDE.md` must leave one pointer line with the topic words. Then a subagent's search still finds
the home file.

## Each section

| section | chars | verdict | reason |
|---|---|---|---|
| RimMandrake: a RimWorld 1.6 mod project (a Jawa scavenger clan on a desert world) | 418 | keep | Each agent needs the pointer rule for this file. |
| Read these first | 885 | keep | Each agent needs the reading order. |
| Where the full text lives | 818 | keep | The table is the map to each home file. |
| How we debug | 611 | keep | Each builder and each tester needs it. A looser bar is a costly error. |
| There is no worldgen feature, in any version | 802 | keep | Each designer and builder can break it. A break wastes a whole build. |
| A biome with zero tiles is not a defect | 736 | keep | Each agent that reads a tile count can report this false defect. |
| The pipelines before the Maturation Pipeline are retired | 1095 | keep; choice "FOUNDRY lines" | Each agent needs lines 1 to 5. Three lines bind only the Conductor and Operations. |
| Six biome mods are held by the owner; Pyrelands is the only biome mod that advances | 976 | keep | A launch on a held mod is a costly error. Each launcher needs it. |
| No mod runs forward on a broken pipeline | 858 | keep | Each launcher needs it. |
| Biomes, rosters and seas | 1644 | move out; choice "biome and naming rules" | The rule binds only an agent that designs or builds a biome or a roster. |
| Star Wars style naming is not Star Wars IP | 629 | move out; choice "biome and naming rules" | The rule binds only an agent that names a creature or a roster. |
| Facts you cannot guess | 2569 | keep | Each agent meets these facts in most sessions. A wrong guess costs a game load. |
| North-star validation | 524 | keep | Each agent that edits a north-star section needs it. It is short. |
| In-game LLM access is the Claude Code CLI, never a hosted API key | 437 | move out; choice "feature rules" | The rule binds only a builder of an in-game LLM feature. |
| A pit is a superdeep cell, not a building | 390 | move out; choice "feature rules" | The rule binds only a builder of pits. |
| One Direct Sun, a pure function of geometry | 1044 | move out; choice "feature rules" | The rule binds only a builder of heat or shade. |
| Every DLC is assumed | 572 | keep | Each tester and designer can break it. A test tier without a DLC wastes work. |
| Shipping names are three-tier | 595 | keep | Each agent that adds a def, a namespace or a mod folder needs it. |
| Sittings with the owner keep the advanced-zoom mod | 281 | move out; choice "sitting rules" | The rule binds only the agent that builds a mod list for a sitting. |
| Every mod ships superb Mod Settings | 589 | keep | Each mod builder and designer needs it. It is short. |
| If it flies in the fiction, it flies in the game | 785 | move out; choice "feature rules" | The rule binds only a builder of creatures. The flight test stays in the five acts. |
| Queue items are NAMED, not numbered | 684 | keep | Each agent files items. |
| Correctness outranks seat ownership; wrong material is deleted | 385 | keep | Each agent edits files. |
| Only five acts stay his; the Conductor may do the rest, mindfully | 1709 | keep | Each agent must know which acts wait for the owner. |
| The Conductor speaks with the owner's authority | 673 | keep | Each agent receives Conductor instructions. |
| Owner authority on the ledger: one field per kind of authority | 715 | keep | Each agent writes ledger events. |
| The Evidence-for-Ask rule | 718 | keep | Each agent can pause for the owner. |
| A limit from before the Maturation Pipeline is suspect | 333 | keep | Each agent can refuse an act on an old limit. |
| The pipeline fixes its own defects | 679 | keep | Each agent in the pipeline meets pipeline defects. |
| No trial is spent by a system failure | 572 | keep | It is short. An agent that refuses a void costs the owner a trial. |
| No limit without the danger it guards | 828 | keep | Each agent that writes code or a brief can add a limit. |
| A passing bar is an experience, never a tuning number | 517 | keep | Each designer, builder and judge writes or reads bars. This run added the meaning of "bar". |
| The judge refuses flaws, not polish | 1134 | move out; choice "judge rules" | The rule binds only a judge and the agent that writes a judge brief. |
| No launched agent is told its spend | 481 | keep | Each agent that writes a brief can break it. |
| Spend in weighted tokens; never hold the game for his look while he is away | 490 | keep | Each agent reports spend. The second rule binds each agent that holds the game. |
| Nothing reaches the owner unread | 464 | keep | Each agent that hands work to the owner needs it. |
| An operational item is done only when it is running | 846 | keep | Each agent that closes a timer, hook or alarm item needs it. |
| Git | 1189 | keep | Each agent commits. |
| Each mod has its own Design Version | 365 | keep | It is short and it binds each mod builder. |
| The test is built with the item, offline and live | 339 | keep | Each builder needs it. |
| A refusal carries its path to pass | 608 | move out; choice "judge rules" | The rule binds only a judge, a gate and the agent that writes one. |
| Code isn't clean until a review says so | 424 | keep | Each agent that writes code needs it. |
| Pipeline machinery is under a different rule | 1092 | keep | Each agent that edits pipeline code needs it. A wrong review costs a day. |
| What is where | 706 | keep | Each agent needs the map. |
| Transient | 596 | keep | Each agent writes output files. |
| Art | 594 | move out; choice "art rules" | The rule binds only an agent that makes or judges art. |
| Options he must LOOK at ship as a savegame | 416 | move out; choice "sitting rules" | The rule binds only the agent that stages options for the owner. |
| Tools | 2152 | keep | Each agent uses these commands. |
| Never send him to a computer you can reach yourself | 132 | merge; choice "Tailscale line" | Two lines. The rule is a user-level rule with one local fact. |
| The bridge is passed through one file | 2342 | keep | Each agent that drives the game needs it. A wrong take stops the owner's game. |
| Skills | 483 | keep | Each agent reads skills. |
| Compact Instructions | 1072 | keep | The harness reads it at each compaction. |
## The lines that a cold reader cannot act on

The review read each rule line and asked one question: can a new agent point at what each noun means? The review
graded a line together with the bullets that travel with it. That method is from the clear-findings skill.

### Rewritten in this run (17 lines)

Each rewrite keeps the old slogan where the slogan is a name that people search for.

| old line | what a cold reader lacks | source of the plain sentence |
|---|---|---|
| "Game-state relays are stamp-only. Longer relays use tokens and rarely inform." | "stamp-only" has no meaning in the file | `src/RimMandrake/Utils/broadcast.py` lines 28 to 35; `standing_rulings.md` §The bridge is passed through one file |
| "To run a mod forward is to … release a ceiling for the mod, or launch its build or visit." | "ceiling" and "visit" are coined | `standing_rulings.md` §No mod runs forward; `design/specs/2026-11-19-stage-ceiling/boundary.md` |
| the same line | the drain lost the word "fix" ("a build, fix or in-game visit") | `standing_rulings.md` line 984. Restored. |
| "It names every component … It marks each open ticket …" | two sentences with no subject | the subject "the readiness list" is now in each sentence |
| "Evictions are stopped." | evictions of what | `biome_rulings.md` |
| "A composed member's packageId never loads." | "composed member" is coined | `skills/rimworld-modding/references/project-engine-facts.md` line 33 |
| "The frozen `official` dump is the only design target." | no path to the dump | `src/RimMandrake/Utils/refresh.py` line 377 |
| "Walk-finding traps and the rest: …" | "the rest" of what | plain pointer wording |
| "It is not the 1127-line spec, which is older than ten changed answers." | which spec; what the reader must do | `standing_rulings.md` line 153 |
| "The tick classes such a run `void_system`." | "the tick" is coined | `rm-maturation-dispatch.service` runs `maturation_dispatch.py tick` |
| "Do not answer that the record is frozen or append-only." | answer to whom, about what | `standing_rulings.md` §No trial is spent by a system failure |
| "The dials are who confirms a refusal and the number of looks (2)." | "the dials" is coined | `standing_rulings.md` line 807 |
| "… the code has had two looks." | "looks" is coined | `standing_rulings.md` line 1198 |
| "Writers above 4 may use a pool …" | "above 4" of what | `standing_rulings.md` line 321 |
| "`host_guard` holds the same line across clones." | which line | `standing_rulings.md` line 560 |
| "If each new question … adds a clause to a procedure, stop. That work is human review work." | what to do after the stop | `biome_rulings.md` line 113: review sheets are the existing machinery |
| "Authority: … §7 Q11a." | a coded id with no title | `biome_mod_architecture.md` line 615 |
| "a change to the account order or the leave line" | whose leave line | `standing_rulings.md` line 29: "the shared account's leave line" |
| "No bar pins a yield rate …" (and each other use of "bar") | "bar" has no meaning in the file | `design/specs/2026-11-13-maturation-pipeline.md` line 193 |

The table has 19 rows for 17 lines. Two lines have two rows each.

### Proposed, not applied (1 line)

- Old: "When a tier or provenance question makes more sub-questions, first ask if the category is necessary at all."
- Proposed: "A question about a naming tier or about provenance can make more sub-questions. Then stop. First ask the
  owner if the category itself is necessary."
- The reason to wait: `biome_rulings.md` does not say who asks or whom. The proposed sentence adds "the owner".

### Could not determine (6 lines)

| line | what is not known | who knows |
|---|---|---|
| "The check is the mod's readiness list." | Where the list is kept, and which command writes it. The ruling says only "like the GimmeSomeSlack one". | the Conductor |
| "An `RM_` twin biome gets its real cast from patches." | What a twin is. `biome_rulings.md` line 59 uses "twin" for a `RUT_` def, not for an `RM_` def. | the Conductor; `instrument_traps.md` has a "twin trap" entry |
| "A limit from before the Maturation Pipeline is suspect." | The date that divides before from after. The spec is dated 2026-11-13. The limit in the ruling's own incident is dated 2026-11-14. | the owner |
| "Every mod list for a sitting with the owner includes the advanced-zoom mod." | The mod's packageId. Old test mod lists hold `ray1203.simplecamerasetting` [guess ~50% that this is the mod]. | the owner |
| "Revert the pool if a clone strands work or the pool passes 80 GB." | The state that the pool reverts to. | the Conductor |
| "… and so does the FlowWorks lane (`infrastructure/state/flowworks_lane.json`, field `seat`)." | What the FlowWorks lane is. | the Conductor |

One more term is half open. This run wrote "the leave line of the shared account". The file still does not say what a
leave line is. The `rimflow-operations` skill holds the meaning.

## Choices for the Conductor

Each choice has a full name in the item grammar and a short name in quotes. Each choice moves text out of `CLAUDE.md`. The full text of each section is in its home file now. So a move loses no
text. A move does change which agents see the rule without a search. Only the Conductor can accept that cost.

| choice | sections | chars saved | where the rule goes, and who then reads it | cost |
|---|---|---|---|---|
| `RIMMANDRAKE_MOVE_FOUNDRY_LINES_TO_CONDUCTOR_ROLE_THREE_LINES` ("FOUNDRY lines") | three lines of "The pipelines before the Maturation Pipeline are retired" (`rm-findings-judge.timer`, the two FOUNDRY lines) | about 500 | `roles/conductor.md` and `roles/operations.md`. The Conductor and Operations read them at each start. | A helper that meets the name FOUNDRY in a path gets no help from `CLAUDE.md`. |
| `RIMMANDRAKE_MOVE_BIOME_AND_NAMING_RULES_TWO_SECTIONS` ("biome and naming rules") | "Biomes, rosters and seas"; "Star Wars style naming is not Star Wars IP" | 2,273 | `roles/designer.md` gets a "read `biome_rulings.md` first" line. A detached helper gets the same line in its brief. | A helper that edits a roster without that brief line can leave `animalDensity` unset. Then no animals spawn. |
| `RIMMANDRAKE_MOVE_FEATURE_RULES_OUT_FOUR_SECTIONS` ("feature rules") | "In-game LLM access"; "A pit is a superdeep cell"; "One Direct Sun"; "If it flies in the fiction" | 2,656 | One pointer line for each topic stays. The full text is in `standing_rulings.md`. The brief of a builder of that feature names the section. | A builder who gets a brief with no section name builds from memory. For flight, the costly rule stays in the five acts. |
| `RIMMANDRAKE_MOVE_SITTING_RULES_TO_CONDUCTOR_ROLE_SAVES_LITTLE` ("sitting rules") | "Sittings with the owner keep the advanced-zoom mod"; "Options he must LOOK at ship as a savegame" | 697 | `roles/conductor.md`. Only the Conductor builds a sitting or stages options for the owner. | A Test Pilot that builds a mod list for a joint sitting does not see the zoom rule. |
| `RIMMANDRAKE_MOVE_JUDGE_RULES_OUT_TWO_SECTIONS` ("judge rules") | "The judge refuses flaws, not polish"; "A refusal carries its path to pass" | 1,742 | One pointer line stays. The full text is in `standing_rulings.md`. Each judge brief already carries its own rules. | An agent that writes a new judge brief can miss the four rules. |
| `RIMMANDRAKE_MOVE_ART_RULES_TO_ARTIST_ROLE_SAVES_LITTLE` ("art rules") | "Art" | 594 | `roles/artist.md` and the art skills. | A builder who installs art by hand does not see "`art install` only". |
| `RIMMANDRAKE_MERGE_TAILSCALE_LINE_INTO_FACTS_TWO_LINES` ("Tailscale line") | "Never send him to a computer you can reach yourself" | 132 | Merge the one local fact (Tailscale) into "Facts you cannot guess". | Other files cite the heading. Each citation needs a new target. |

- All seven choices together save about 8,600 chars before the pointer lines. [measured]
- The pointer lines cost about 1,200 chars [guess ~70%]. So the net is about 7,400 chars, or 18% of the file.
- Recommended: the choices "biome and naming rules", "feature rules" and "judge rules". Those sections bind the fewest
  agents. Each home file holds the full text.
- Not recommended: the choices "sitting rules" and "art rules". Each one saves little. Each one moves a rule that the
  wrong agent can break at a cost.
- Each move needs the no-loss check with the home file as `--also`. Each move needs a search for citations of the
  heading.

## Conflicts between files (listed, not decided)

1. **"twin".** `CLAUDE.md` says "an `RM_` twin biome". `biome_rulings.md` line 59 says "every other `RUT_` def is a
   frozen twin". The two files use one word for two things, or one of them is wrong.
2. **The date of "before the Maturation Pipeline".** See the table above.
3. **The shared block for subagents.** `.claude/rm_agent_shared_block.md` says that `CLAUDE.md` "cost ~23k tokens per
   call". The file is 41,072 bytes now, which is about 10k tokens [guess ~70%]. The block also sends a subagent to
   `/home/mandrake/rm/bench/CLAUDE.md`. A subagent of a detached helper works in a different clone.
4. **`infrastructure/agents/CONDUCTOR.md`.** The file says "nothing is written twice". Then it repeats the first rule
   and the authority rule of `roles/conductor.md`.
5. **Three homes for "who may change a bar".** Three sections each state a part: "How we debug", "North-star
   validation" and "Only five acts stay his". The drain report listed this conflict. It is still open.
6. **Two clocks of 45 minutes in the bridge section.** A stale hold counts from the last event. His OWNER hold counts
   from his last deliberate interaction. The drain report listed this. Both lines are kept.
7. **Two homes for the naming-tier rule.** `biome_mod_architecture.md` §7 Q11a is the authority. `biome_rulings.md`
   holds the full text. The drain report listed this. It is still open.

One conflict is closed. The drain dropped "fix" from the list of acts that run a mod forward. This run put the word
back, from `standing_rulings.md` line 984.

## The checks on the new `CLAUDE.md`

| check | command | result |
|---|---|---|
| no-loss, check 1 | `python3 ~/dev/MandrakeWorkflows/skills/crystallize/scripts/checkable.py compare git:328611932d:CLAUDE.md CLAUDE.md` | 75 items, 0 lost, exit 0 |
| check 1 on a planted loss | the same compare against a copy with one path line removed | 1 lost, exit 1 |
| no-loss, check 2 | `python3 design/specs/2026-11-19-plain-english-rule-docs/rule_doc_lint.py keep git:328611932d:CLAUDE.md CLAUDE.md` | 254 spans, 0 lost, exit 0 |
| check 2 on a planted loss | the same `keep` against the same copy | 1 lost, exit 1 |
| pointers | each `file.md §Heading` pointer in `CLAUDE.md` resolves to a heading in that file | 0 unresolved |
| STE lint | `rule_doc_lint.py lint CLAUDE.md` | 1.48 per 100 words; 1 sentence over 20 words |
| names of people | read of the diff | no name added or removed |

The one sentence over 20 words is rule 1 of "The judge refuses flaws, not polish". The lint joins the rule to its
three list lines.

## Not tested

- No live session read the new `CLAUDE.md`. The effect on agent behaviour is not measured.
- The two no-loss checks read numbers, names, paths, quotes and code spans. They do not read prose. This run compared
  each rewritten line with its source by eye.
- No second reader checked the 17 rewrites.
