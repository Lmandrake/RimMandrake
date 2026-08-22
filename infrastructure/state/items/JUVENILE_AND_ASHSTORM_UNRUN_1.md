## Spec

Two checks carry `verify pass` in the ledger and **were never run**. Run them, or record
them honestly as unrunnable.

| item | ledger says | the later capture says |
|---|---|---|
| `GRIMTERRA_JUVENILES_RENDER_1` | `verify pass` 2026-08-21T08:24:12Z | *"JUVENILES are UNMEASURED"* · *"Recorded UNMEASURED, not passed"* |
| `ASH_STORM_OVER_PYRELANDS_1` | `verify pass` 2026-08-21T10:00:27Z | *"the ash storm over a stormy-savanna tile — NOT ATTEMPTED"* |

Source: `infrastructure/state/observed/2026-08-21/quicktest_visual/README.md`, lines 5, 25
and 30 — `QUICKTEST_VISUAL_ROUND_1`, 2026-08-21T20:25Z, which **supersedes both passes**.

⇒ A seat following the `pass` events without walking the supersede chain believes two
visual checks are settled that nobody has ever seen.

## Watch out

- 🔑 **The capture already names the routes, so do not re-derive them.** For juveniles:
  hatch an egg and tick; or `rimworld/execute_debug_action` if it exposes an age; or add an
  age argument to `jawa/spawn_pawn` in the companion — ⚠️ **that last one needs the game
  down**, so it is BUILD's and it is a separate item.
- ⛔ **Do not force a juvenile by editing a spawned adult.** The capture rejected exactly
  this: it leaves *"a pawn in a state nothing produced"*, and then neither a draw failure
  nor a draw success is evidence about the juvenile art.
- ⚠️ **The ash storm needs the right TILE, not just the right weather.** The 2026-08-21 map
  was `ExtremeDesert`-flavoured scratch terrain; a stormy-savanna tile is the subject. And
  the planet is being remade (`canon.yml planet.status: remaking`), so **do not spend a
  world-authoring step on this** — a dev-quicktest map on a suitable tile is the cheap route.
- 🔑 **The honest outcome may be UNMEASURED again**, and that is a result. What is not
  acceptable is the current state, where the ledger says `pass`.

## Verify

A capture under `infrastructure/state/observed/<date>/` showing juvenile GRiNDTerra animals
rendering, and an ash storm over a stormy-savanna tile — or a stated reason each remains
unreachable, with the routes tried.

## Criteria

Neither subject is left with a `pass` in the record that its capture contradicts.
