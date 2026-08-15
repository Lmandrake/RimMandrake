# Skills

Each loads itself when its `description` matches the task. Read one when you are
about to do the thing it names — not before.

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
| `rimworld-start-prep` | scenario and starting-state setup. |
| `gravship-layout` | gravship deck design and export. |
| `generating-rimworld-sprites` | any PNG destined for a `Textures/` folder. Wraps the two image skills with the game's constraints and an offline validator. |
| `generating-images` · `editing-images` | raster art from or onto an existing image. |
| `efficient-subagents` | before spawning one. Bounded ask, minimal inputs, stated return. |

⚠️ **Editing `skills/<name>/` is not shipping it.** Claude Code installs from a
`.skill` zip and those are gitignored. Rebuild at hand-off:
`python3 src/RimMandrake/Utils/package_skill.py --all` — read its exit code and the
named failures, never the directory listing.
