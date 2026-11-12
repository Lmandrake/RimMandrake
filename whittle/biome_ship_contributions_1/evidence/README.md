# Evidence index — BIOME_SHIP_CONTRIBUTIONS_1

The list being judged is the `## running list` table in `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`.
Rerun the check yourself (offline, ~20 s): `python3 src/RimMandrake/Utils/ship_contributions.py`
(`--inventory` lists every deck-placeable thing per biome mod). Its docstring states the engine rules it applies.

| file | what it is |
|---|---|
| `ship_contributions_run.txt` | the check over the list: one verdict line per shipped biome (24 composed into Baroque Biomes) |
| `ship_contributions.json` | the same run, machine-readable, with every claimed def's judgement and the other deck-placeable defs |
| `deck_inventory.txt` | every player-placeable def each biome mod ships, judged DECK or site-bound, with costs and sources |
| `selftest_ship_contributions.txt` | the checker's selftest: unit checks on real data + 11 mutated lists that must each fail |
| `lints.txt` | the per-mod def lints for the four mods given new defs, Contagion's lint, and the compose collision sweeps |
| `effective_def_lint.txt` | offline load check: the composed Baroque Biomes built from this clone (new defs included), linted in the game's effective def tree (patches applied, inheritance resolved) on a minimal mod list: VERDICT PASS |
| `owner_card.md` | the matrix as a card to the owner (also in the lane's owner-questions file); not answered yet |
| `code_review.md` | the fresh code-review rounds on the checker and what each changed |
| `design_judge.json` | a fresh design judge's KEEP/CHANGE per row (its three changes are applied in the list) |
| `art/` | the five new textures, ring/L/straight renders of both hull atlases, the floor tiled 2x2, the art judge's verdict |

Live play was not run (this lane has no game): nothing here shows a gift placed, flown or used in a running game.
The offline load check reads defs and patches as the game does but runs no C#.
