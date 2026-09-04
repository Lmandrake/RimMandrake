# Skills

Each loads itself when its `description` matches the task. Read one when you are
about to do the thing it names — not before.

## 🔴 A skill is INVISIBLE until it is wired — and `skills/` is not where Claude looks

Authoring is `skills/<name>/SKILL.md`. **Discovery is `.claude/skills/<name>`, a symlink
back into it.** A skill with no symlink loads for nobody, triggers on nothing, and has no
symptom — the work it encodes simply never happens.

```
ln -s ../../skills/<name> .claude/skills/<name>            # a skill in THIS repo
ln -s /mnt/d/Luke/dev/<name> .claude/skills/<name>         # one that lives OUTSIDE it
```

⚠️ **A skill outside this repo must be linked by ABSOLUTE path.** The relative form
resolves inside the checkout and dangles the moment the skill is not there.

✅ **Enforced since 2026-08-22**: `.claude/hooks/warn_skill_unwired.py` warns (never
blocks) when a `SKILL.md` is written or committed with no working symlink, and hands over
that exact command. ⚠️ A **dangling** symlink is as invisible as none, and the hook treats
it the same. Verified 2026-08-23: **25 skills in this repo + 1 linked in from outside it** (`review-sheets`, below) = 26 symlinks under `.claude/skills/`, all working.

## Who owns a skill

⭐ **SUPERSEDED IN PART 2026-08-27 (redesign #4, `infrastructure/agents/CHARTER.md`):
the four seats are retired.** The table below survives as a DOMAIN map (whoever is
doing that kind of work maintains that skill), not a seat roster. Skills are edited
only in fresh-context curation sessions; lessons land one-line in
`infrastructure/state/LESSONS_INBOX.md` until then. ⚠️ Known roster gap: the
generated table below is missing `rimworld-layout-layers` — regenerate on the next
curation pass.

**Owner's ruling, 2026-08-15: a skill is owned by the seat that USES it. A skill
used broadly by everyone is REP's.** No seat owns `skills/` as a directory.

🔑 **"Uses it" means the seat whose DOMAIN it is — owner's ruling, 2026-08-22.** Seat
names are subject domains, not ranks: **DECIDE** the world (vision, lore, `design/**`,
capability specs) · **BUILD** implementation entirely (defs, patches, xpaths, art, DLLs,
deploy) · **CHECK** the live game · **REP** the board, the queues and what reaches the
human. See `infrastructure/agents/POLICY.md > DECIDE IS A DOMAIN, NOT AN AUTHORITY`.

The point is that the seat which pays for a wrong instruction is the seat that
fixes it — a bridge trap belongs to whoever drives the bridge, not to whoever
happens to own the folder. **Edit the skill you use, in the same commit as the
work that taught you the lesson**, and repackage it: `python3
src/RimMandrake/Utils/package_skill.py <name>`. Writing the folder does not ship
it, and the `.skill` zips are gitignored.

| owner | skills |
|---|---|
| **CHECK** — the live game | `rimbridge` · `rimworld-world-editing` · `rimworld-debug-testing` · `rimworld-load-round` · `rimworld-savegame` · `rimworld-start-prep` (the mod list before a launch is the same domain as the launch) |
| **BUILD** — how it is made | `rimworld-modding` · `rimworld-layout-layers` (a layout's circuits, pipes, roof, floor and access — implementation) · `rimworld-deploy` · `rimbridge-companion` (a companion DLL is implementation, 2026-08-22) · `rimworld-quests` · `rimworld-xenotypes` · `rimworld-scenario-building` · `gravship-layout` · `generating-rimworld-sprites` · `generating-images` · `editing-images` · `reading-rimworld-graphics` (art is BUILD's; a reader of it is not a separate domain) · `rimworld-ideoligion` (**authoring** half) |
| **DECIDE** — the world | `rimworld-content-moderation` (a keep/cut call is what v1 contains) · `rimworld-ideoligion` (**the judging rubric** — judging a religion is world vision; authoring it is BUILD's) |
| **REP** — shared, and what reaches the human | `verify-before-you-escalate` (every seat reads docs and every seat escalates) · `efficient-subagents` · `agent-fanout-research` · `calibrating-binary-formats` · `frozen-artifacts` · `deciding-and-superseding` (⚠️ moved from DECIDE 2026-08-22 — it is about **propagating** a ruling into items and queues, which is the board; DECIDE makes rulings, it does not own the machinery for spreading them), and this README |

_Assignments came from the seats that use them, not from a guess at the table.
DECIDE claimed `rimworld-content-moderation` and disclaimed the other on
2026-08-15; if a skill is listed under the wrong seat, the seat that uses it says
so and the table changes._

⚠️ **Ownership is about who repairs it, not who may read it.** Any seat reads any
skill. A seat that finds a defect in another seat's skill files a queue item
rather than editing it — except where the fix is a fact it just measured, which
it should write directly and say so.

## ⭐ Two skills live OUTSIDE this repo, and are installed machine-wide

**They are generic. This project merely uses them** — so they are their own git
repos, symlinked into `~/.claude/skills/`, and **every project on this machine
gets them.** ⚠️ The generated roster below reads `skills/` and therefore **cannot
see either one**; a skill missing from that table is not necessarily missing.

| skill | lives at | remote | wired by |
|---|---|---|---|
| `measuring-large-artifacts` | `D:\Luke\dev\measuring-large-artifacts` | `Lmandrake/measuring-large-artifacts` | `~/.claude/skills/` only |
| `review-sheets` | `D:\Luke\dev\review-sheets` | `Lmandrake/review-sheet` (⚠️ singular; the **skill** is `review-sheets`, plural, everywhere) | `~/.claude/skills/` **and** `.claude/skills/` |

🔑 **No seat in this repo owns them.** The ownership table above is about who
repairs a skill *in this checkout*; these are repaired in their own repos, and a
fix is committed and pushed THERE. Filing a queue item against one is pointless —
nothing in `infrastructure/state/queue/` reaches a different repository.

⚠️ **`package_skill.py` cannot package them either**, for the same reason it
cannot see them: it walks `skills/`. Their distribution is `git clone` plus the
`ln -s` in each one's own README.

🔴 **`review-sheets` moved out on 2026-08-23.** Anything still naming
`skills/review-sheets` as a path is stale — the skill is unchanged and still
loads under the same name; only its location moved.

<!-- doc_roster:BEGIN — generated, do not hand-edit -->
| skill | when it loads |
|---|---|
| _(generated from each skill's own `description` — the text that actually decides when it loads, so no second copy can disagree)_ | |
| `agent-fanout-research` | Answer a broad question by launching several agents at once on different evidence domains, then compose returns that contradict… |
| `calibrating-binary-formats` | Decode an opaque binary or packed numeric format by making the producing application print its own value for a record you can… |
| `deciding-and-superseding` | Issuing a ruling that survives contact with other agents — recording a decision so it is executable, propagating it into every… |
| `editing-images` | Modifies an existing image with a text prompt by attaching it to Codex's built-in $imagegen tool, then verifies what actually… |
| `efficient-subagents` | Decide whether to spawn a subagent, and how to scope, feed and bound it so it returns 1-2k tokens instead of flooding the parent |
| `frozen-artifacts` | Protect a file that holds a human's decisions from the generator that would silently regenerate over it — and, more often, decide… |
| `generating-images` | Generates raster images from a text prompt by driving the Codex CLI's built-in $imagegen tool, then retrieves, inspects and… |
| `generating-rimworld-sprites` | Produces RimWorld-ready sprite art that matches an existing reference asset — correct canvas, real alpha, silhouette inside the… |
| `gravship-layout` | Author, save and load RimWorld gravship layouts (ShipLayoutDefV2) as XML — write a ship directly with no map, no build and no… |
| `reading-rimworld-graphics` | Finding and reading RimWorld texture assets from disk — loose PNGs, Unity AssetBundles, and the base game's resources.assets — so… |
| `rimbridge` | Drive a live RimWorld from outside via the RimBridgeServer GABP bridge and its JawaBench companion - author the planet, author… |
| `rimbridge-companion` | Write, build, deploy and prove new [Tool] methods in the JawaBench companion DLL so the RimBridge bridge can do something it… |
| `rimworld-content-moderation` | Deciding what content stays in a RimWorld campaign out of a large mod stack — building contact sheets of real sprites straight… |
| `rimworld-debug-testing` | Testing anything in RimWorld without spending a cold load — starting and destroying throwaway dev quicktest colonies through the… |
| `rimworld-deploy` | Writing a file is not deploying it — RimWorld loads C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>, never… |
| `rimworld-ideoligion` | Design, author, validate and judge RimWorld ideoligions |
| `rimworld-layout-layers` | Assess a RimWorld structure on its INDEPENDENT LAYERS - power circuits, mod pipe networks (Helixien gas, chemfuel, deepchem… |
| `rimworld-load-round` | How to spend a RimWorld cold load — and how to stop needing one |
| `rimworld-modding` | Author, patch, validate and debug RimWorld mods — XML PatchOperations, custom Defs, C#/Harmony assemblies, def inheritance that… |
| `rimworld-quests` | Design, author, validate and debug RimWorld quests |
| `rimworld-savegame` | Reading, grepping and editing a RimWorld `.rws` savegame — plain XML plus base64/raw-DEFLATE map grids of 2-byte def shortHashes |
| `rimworld-scenario-building` | Authoring a RimWorld scenario and the game-creation settings around it — ScenarioDefs, .rsc scenario files, ScenParts, Custom… |
| `rimworld-start-prep` | Getting the mod list and load order into the state you actually intend BEFORE RimWorld launches — the three uncoordinated writers… |
| `rimworld-world-editing` | Author RimWorld's PLANET from the bridge - tiles, biomes, elevation, rivers, roads, mutators, landmarks, named regions and… |
| `rimworld-xenotypes` | Authoring, moving, spawning and debugging RimWorld xenotypes and the genes that give them a face |
| `verify-before-you-escalate` | Run the one command that settles a written claim before acting on it, escalating it, or raising an alarm about it |
<!-- doc_roster:END -->

⚠️ **Editing `skills/<name>/` is not shipping it.** Claude Code installs from a
`.skill` zip and those are gitignored. Rebuild at hand-off:
`python3 src/RimMandrake/Utils/package_skill.py --all` — read its exit code and the
named failures, never the directory listing.
