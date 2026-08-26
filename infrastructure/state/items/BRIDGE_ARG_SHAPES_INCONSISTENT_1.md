## ✅ FIVE OF THE SEVEN ARE FIXED — 2026-08-26, seat BUILD, built clean and NOT yet deployed

Written and compiled in the companion (`--gm`, 0 warnings, 0 errors, 166 tools, no removal).
⛔ **The game is UP, so none of it is live**; the deploy rides `NEXT_RELOAD.md` §25.

| # | tool | what changed |
|---|---|---|
| 1 | `FindPawn` (every `jawa/` tool that takes a pawn) | accepts **both id forms** — `Thing_Human45731` and `Human45731` — and its refusal now names every accepted form and says `jawa/list_pawns` reports the bare one |
| 2 | `jawa/pawn_gear` | its description opens by saying **it is a WRITE tool** and names `jawa/pawn_get` as the read; a call with no `def` refuses with that same pointer and an explicit *do not read a list off this refusal* |
| 3 | equipment + apparel rows | carry **`defName` as well as `def`**, same value, so reading `.defName` can no longer come back null for an armed pawn |
| 4 | `jawa/pawn_genes` | description now names the real verbs `add`/`remove` instead of the engine's `AddGene`/`RemoveGene` |
| 5 | `jawa/pawn_genes` | the head re-roll is **documented as ordering** — gene first, appearance second — rather than suppressed, exactly as this item asked |

**Row 7 was already fixed** before this pass: `prove_world_cache_audit.py` calls the MCP method
`tools/list` through `_request`, with the reason written above the line.

⛔ **Row 6 is NOT ours and cannot be fixed here.** `rimworld/save_game` and
`rimworld/load_game_ready` belong to RimBridgeServer, not to the JawaBench companion — we can
document the trap but not change the guard. Treat `saveName` as required whatever the schema says.

---

## spec

**Seven places where the bridge's argument and result shapes disagree with each other or
with their own documentation.** Every one of these cost a wrong reading during the
2026-08-22/23 session, and four of them produced a *confident wrong answer* rather than
an error.

| # | tool | the trap | what it costs |
|---|---|---|---|
| 1 | `rimworld/set_draft` vs `jawa/set_pawn_rotation` | `set_draft` wants **`Thing_Human45731`**; `set_pawn_rotation` wants the bare **`Human45731`**. `jawa/list_pawns` reports the bare form | 🔴 `set_draft` returned "undrafted 0 of 18" with **no per-pawn error**. A silent zero |
| 2 | `jawa/pawn_gear` | it is a **WRITE** tool (equip/wear/clear). The READ is `jawa/pawn_get` | 🔴 reading `.equipment` off its refusal gave `[]` for every pawn — "all Jawa spawn bare-handed", the opposite of the truth |
| 3 | equipment entries | keyed **`def`**, not `defName` | 🔴 `[None]` for twelve armed droids — read as "the Free Droid Enclaves field unarmed droids" |
| 4 | `jawa/pawn_genes` | description says `AddGene`/`RemoveGene`; the binder accepts only **`add`/`remove`** | ✅ loud — refuses and names the valid verbs |
| 5 | `jawa/pawn_genes` | adding a gene **re-rolls the head type** via `Notify_GenesChanged` | 🔴 a head set *before* the gene silently became a different head. Order is gene → appearance |
| 6 | `rimworld/save_game` / `load_game_ready` | parameter is **`saveName`**, not `fileName`; and `saveName` is declared **required** yet a call without it succeeds and auto-names the file | 🔴 the load then failed against a name nobody chose |
| 7 | `rimworld/list_tools` | does not exist. The roster is the MCP method **`tools/list`** via `_request` | 🔴 `prove_world_cache_audit.py` died at step 0 on **every run since it was written** |

## What is worth fixing, in order

🔑 **The silent zeros first (1, 2, 3).** A wrong argument shape that returns an empty
collection is indistinguishable from a true empty result, and this project's whole
method rests on telling those apart. A refusal naming the bad parameter costs one line
and converts each of these from a wrong answer into a retry.

⭐ **Then accept both id forms (1).** `Thing_Human45731` and `Human45731` identify the
same pawn; every tool taking a pawn should accept either, or `list_pawns` should report
the form the setters want.

⚠️ **Do not "fix" 5 by suppressing the head re-roll** — it is `Notify_GenesChanged`
doing its job, and the tool's own description advertises the refresh as a feature.
Document the ordering instead.

## verify

- A pawn-addressing tool given the other id form either resolves it or refuses **naming
  the parameter**; none returns a zero-count success.
- `jawa/pawn_gear` called with no `action` refuses rather than reporting a shape a caller
  could mistake for a read.
- `rimworld/save_game` with no `saveName` refuses, since the schema says required.

## criteria

No bridge call in this repo can return an empty collection that means "you asked wrong".
