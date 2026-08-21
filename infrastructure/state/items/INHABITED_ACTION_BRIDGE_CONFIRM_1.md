## spec

**One bridge call. The cause is already settled from the source; this is the confirmation
BUILD cannot take, because BUILD does not drive the bridge.**

`INHABITED_DEBUG_ACTION_ABSENT_1` reported that `Inhabited` / `Spawn authored character`
"does not exist in the running game" after a walk of the debug tree found no match among
`Actions`' 146 children. ⛔ **That walk was one level deep, and the action is two.**

`src/Jawa/Inhabited/Source/DebugActions_Inhabited.cs:40` sets
`private const string Cat = "Inhabited"` and all seven `[DebugAction]`s pass it as their
FIRST argument — the category. So they are children of a **category node named
`Inhabited`**, never of `Actions` itself, and a single-level listing of `Actions` returns
the category and not its leaves. `allowedGameStates` is satisfied (`PlayingOnMap`, and a
map was loaded) and there is no `godMode` gate; both of the other candidates are ruled out
from the same read.

⭐ **Do not walk. The bridge ships the tool that makes walking unnecessary** —
`rimworld/search_debug_actions`, *"search the full debug-action tree globally … so callers
do not need to walk one subtree at a time"*.

🔑 **Never construct a leaf path.** The category and the label below are quoted out of the
source, not composed:  category `Inhabited`, label `Spawn authored character`.

## verify

1. `rimworld/search_debug_actions  {"query": "Spawn authored character"}`
   ⇒ expect one match whose category is `Inhabited`. **Record the `path` it returns
   verbatim** — that string is the thing nobody has ever had.
2. If it returns nothing, re-run with `"includeHidden": true`. ⚠️ `includeHidden` defaults
   to **false** on all four discovery tools, so a hidden node reads exactly like an absent
   one. Only if BOTH come back empty is "not registering" on the table.
3. `rimworld/get_debug_action` on the path from step 1, to confirm it resolves and reports
   `supported`.
4. ⛔ Do not EXECUTE it as part of this item. Spawning an authored pawn changes the map,
   and `CAST_ROSTER_269_LOAD_1` is what wants the spawn.

⚠️ The game must be UP with a MAP LOADED. `AllowedGameStates.PlayingOnMap` means a
world-only session will legitimately hide it, and that would be a false negative.

## criteria

The path resolves and is written down — or both searches come back empty with
`includeHidden: true`, which is the first evidence anyone has that the action genuinely
fails to register, and reopens the question with the two cheap candidates already
eliminated.

## notes

⚠️ Also found while settling this, and NOT part of it: `Player.log`'s
`[Inhabited] ready: … 269 characters` is not a loader defect. 294 are authored and
`CastRoster_DEEPWATER.xml`'s 25 are simply not deployed — 294 − 25 = 269, exact. That is a
deploy-window action and belongs to `CAST_ROSTER_269_LOAD_1`, not here.

The hook-versus-traits half that `CAST_ROSTER_269_LOAD_1` was blocked on **no longer needs
this action at all**: `src/RimMandrake/Utils/cast_hook_audit.py` reads the hook and the
traits out of the generated XML, offline, for all 294.
