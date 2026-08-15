# Skills

Each loads itself when its `description` matches the task. Read one when you are
about to do the thing it names — not before.

## Who owns a skill

**Owner's ruling, 2026-08-15: a skill is owned by the seat that USES it. A skill
used broadly by everyone is REP's.** No seat owns `skills/` as a directory.

The point is that the seat which pays for a wrong instruction is the seat that
fixes it — a bridge trap belongs to whoever drives the bridge, not to whoever
happens to own the folder. **Edit the skill you use, in the same commit as the
work that taught you the lesson**, and repackage it: `python3
src/RimMandrake/Utils/package_skill.py <name>`. Writing the folder does not ship
it, and the `.skill` zips are gitignored.

| owner | skills |
|---|---|
| **CHECK** — the live game | `rimbridge` · `rimworld-debug-testing` · `rimworld-load-round` · `rimworld-savegame` |
| **BUILD** — artifacts and art | `rimworld-modding` · `rimworld-deploy` · `rimworld-ideoligion` · `rimworld-quests` · `rimworld-xenotypes` · `rimworld-start-prep` · `gravship-layout` · `generating-rimworld-sprites` · `generating-images` · `editing-images` |
| **DECIDE** — what ships | `rimworld-content-moderation` (the cherrypick method — a keep/cut call is a scope call) |
| **REP** — shared | `efficient-subagents` · `reading-rimworld-graphics` (art, contact sheets and audits all reach for it), and this README |

_Assignments came from the seats that use them, not from a guess at the table.
DECIDE claimed `rimworld-content-moderation` and disclaimed the other on
2026-08-15; if a skill is listed under the wrong seat, the seat that uses it says
so and the table changes._

⚠️ **Ownership is about who repairs it, not who may read it.** Any seat reads any
skill. A seat that finds a defect in another seat's skill files a queue item
rather than editing it — except where the fix is a fact it just measured, which
it should write directly and say so.

| skill | when |
|---|---|
| `rimworld-modding` | any def, patch, xpath, load-order or `Player.log` question. Read before writing into a mod folder — RimWorld XML has silent-failure modes. |
| `rimworld-deploy` | putting a build on the game copy. Plan-first, `--mod` scoping, `DEPLOY_HOLD.txt`. |
| `rimworld-load-round` | calling or queueing a game load. How to spend 25 minutes. |
| `rimbridge` | driving a live game — spawn, build, screenshot, measure. |
| `rimworld-debug-testing` | reproducing a defect in-game without a full campaign. |
| `rimworld-savegame` | editing a `.rws`. Rarely the right route. |
| `rimworld-quests` | `QuestScriptDef` authoring and firing. |
| `rimworld-ideoligion` | memes, precepts, ideoligion authoring. |
| `rimworld-xenotypes` | xenotypes, genes, head types, species mods. A XenotypeDef is only a gene list; spawning needs a PawnKindDef, and most failures here are silent. |
| `rimworld-start-prep` | scenario and starting-state setup. |
| `gravship-layout` | gravship deck design and export. |
| `generating-rimworld-sprites` | any PNG destined for a `Textures/` folder. Wraps the two image skills with the game's constraints and an offline validator. |
| `rimworld-content-moderation` | Curating a big mod stack down to one campaign — contact sheets built from the defs, cutting with Cherry Picker, and the traps that make a cut do nothing |
| `reading-rimworld-graphics` | Finding and reading texture assets from disk — loose PNGs, AssetBundles, and the base game's resources.assets |
| `generating-images` · `editing-images` | raster art from or onto an existing image. |
| `efficient-subagents` | before spawning one. Bounded ask, minimal inputs, stated return. |

⚠️ **Editing `skills/<name>/` is not shipping it.** Claude Code installs from a
`.skill` zip and those are gitignored. Rebuild at hand-off:
`python3 src/RimMandrake/Utils/package_skill.py --all` — read its exit code and the
named failures, never the directory listing.
