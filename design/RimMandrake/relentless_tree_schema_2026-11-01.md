# The acceptance tree: file format (2026-11-01)

Item: RA_TREE_SCHEMA_DESIGN_TWO_PENS. Shared by `relentless_agent_design_2026-11-01.md` (§3, §4, §3.1, §3.3) and
`concept_agent_design_2026-11-01.md` (§6, §7, §8, §10, §11). Where the two disagreed, this file records what was decided and
which line of which design it corrects. `schema_version` is 1. Nothing reads this yet: step 5 (RA_S05_INTAKE_ENFORCE_TREE_FIRST)
writes the reader and proves it.

## The idea: one pen per file

The rule "the Setter may not add, drop or reword a criterion" is enforced by the shape, not by a diff. Concept's words and the
Setter's bindings live in **separate files, keyed by leaf id and leaf hash.** The Setter never opens the tree for writing, so a
reword cannot happen by accident, and a changed leaf hash voids its binding by arithmetic.

| File | Written by | Readable by | Lives in |
|---|---|---|---|
| `tree.json` | Concept agent; for a tooling goal, its filer. A Setter's unsaid sweep appends `preserve` leaves with `by: setter_sweep` | Everyone, public | `design/concepts/<Mod>/tree.json`; tooling: `<store>/items/<ITEM>/tree.json` |
| `binding.json` | Setter | Build, Marker, public | `<store>/items/<ITEM>/binding.json` |
| `holdouts.json` | Setter | Marker only, behind the wall | `<store>/judge/<ITEM>/holdouts.json` |
| `budget.json` | A program, from history by leaf class | Everyone | `<store>/items/<ITEM>/budget.json` |
| `contract.v<N>.json` | Supervisor, computed from the first, second and fourth | Build, Marker | `<store>/items/<ITEM>/` |

The root stays in `design/validation_walks/<tier>/<Mod>.md` `## north star`, the location he ruled. The tree cites it; it never
copies it, so a second copy cannot drift.

## Field owners

`Done by` is who holds the pen. A cell with two names means the first proposes and the second binds; the proposal stays in `tree.json`, the binding is in `binding.json`, and the binding wins.

| Field | File | Done by | Door check (§3) | Source |
|---|---|---|---|---|
| `id` | tree | Concept | Unique, slug, stable across versions | C§7 |
| `root` | tree | Concept | Each id exists in the walk's `## north star`, or `tool` for a tooling goal | R§4, C§7 |
| `leaf_kind` | tree | Concept | `experience`, `constraint`, `instrument`, `walk` | R§3, §3.2, §4 |
| `clause_kind` | tree | Concept | `change` or `preserve` (§3.1: `preserve` takes guard red only) | R§3.1 |
| `experience` | tree | Concept | Names an observer; a constraint carries number, unit, test machine | R§3, C§7 |
| `scenario` | tree | Concept | Runnable reference or an owed instrument leaf (`needs_instrument`) | R§3, C§7 |
| `false_pass` | tree | Concept | A named wrong world. A motion, timing or salience leaf needs two, of which the Setter writes one in `binding.wrong_worlds` without seeing the other | R§3.1, C§7 |
| `red` | tree | Concept | A specification is present. Receipts are the supervisor's and block done, not intake | R§3.1, C§7 |
| `oracle_proposed` / `oracle` | tree / binding | Concept / Setter | Tier declared; on-screen experience needs a visual or read bar, or `cannot_show` | R§3, C§7 |
| `tier_proposed` / `tier` | tree / binding | Concept / Setter | In the adapter tier list; live needs `tier_reason`; adapter forbids refuse | R§3, C§7 |
| `guard` | binding | Setter | A seeded change that creates the wrong world, or `guard_offline: false` with its tier | R§3.1 |
| `wall_expect_h` | tree | Concept | Optional. Wall-time expectation only | C§7 |
| `budget` | budget | A program | A number, by leaf class. Overrun is a signal, never a hold | R§3, C§7 |
| `owner_part` | tree | Concept | `no`, or `yes: <what he looks at>`. A mod's first GREEN forces `yes` | R§3, C§7 |
| hold-outs | holdouts | Setter | Nothing in the tree. 1-3 per leaf; may not reach into `waived` | R§3.3, C§7 |

**Corrections this file records.** Budget: Relentless §10 said the Producer proposes it; Concept §7 decided a program sets it, as the Producer is token-blind by his ruling. Relentless §10 is corrected to match. Eight fields: Relentless §3 says a goal is accepted when every leaf has all eight **after** the Setter binds; Concept §7 says the tree alone cannot hold all eight. Both hold: door lint A (a program, Concept §5) checks the tree's six, and intake checks the merged eight.

## `tree.json`

```json
{
 "schema_version": 1,
 "subject": "<Mod or ITEM_ID>",
 "kind": "mod | tool",
 "authored_by": "concept | filer:<who>",
 "root_ref": "design/validation_walks/<tier>/<Mod>.md#north-star",
 "root_state": "VALIDATED | DRAFT | none",
 "root_hash": "<the walk's validated-hash, or null>",
 "coverage": {"signed_by": "Arbiter", "at": "<iso>", "tree_hash": "<sha256>"},
 "floor": {"ref": "concept_floor.json", "hash": "<sha256>", "off": [{"line": "<floor id>", "words": "<his words>", "ref": "<ledger event>"}]},
 "exam_waived": null,
 "waived": [{"id": "w1", "scope": "<his words>", "date": "<iso>", "ref": "<ledger event>"}],
 "advisory": ["<does line nobody blocks on>"],
 "leaves": [{
   "id": "spill_conserves_litres",
   "by": "concept | filer | setter_sweep",
   "root": ["ms1"],
   "leaf_kind": "experience",
   "clause_kind": "change",
   "bundle": null,
   "experience": "The tank falls, stain count rises to match",
   "scenario": "<setup and action>",
   "scenario_informed_by": ["<exam scenario id>"],
   "needs_instrument": null,
   "false_pass": ["Tank falls, no filth"],
   "red": "<what red must look like>",
   "oracle_proposed": "<instrument and what it must read>",
   "tier_proposed": "offline",
   "tier_reason": null,
   "cannot_show": null,
   "owner_part": "no",
   "wall_expect_h": 0.5
 }]
}
```

`tree_hash` is the sha256 of the canonical JSON (sorted keys, no whitespace) of everything except `coverage`. `leaf_hash` is the same over one leaf. A leaf changing changes both, and a change bumps the version as Relentless §4 and Concept §10 say.

The tree holds no `later`, `open` or `does` lines: those are the sheet's (Concept §6). An `open` on a core line stops the tree before it exists. A `does not` is a leaf with `cannot_show` set, never a waiver.

**Exactly one `walk` leaf per mod** (`leaf_kind: walk`, Relentless §4, Concept §7), whose `scenario` includes a reload from a save made mid-way, a repeat of the core action, and a second order of the main actions. A tooling goal has none.

**An `instrument` leaf** names, in `scenario`, the instrument it will build. Other leaves depend on it through `needs_instrument: <leaf id>`, and it orders first (§3.2). Its base red is the instrument's absence, as a refusal.

**A mechanical constraint** has `leaf_kind: constraint`, and `experience` shaped `<limit> <unit> on <test machine>`. Floor constraints are not copied into the tree: intake expands `floor.ref` by hash, less `floor.off`, into leaves with `by: floor`. Numeric floor lines stay advisory until calibrated (Concept §8), so an expanded floor leaf carries `advisory: true`.

## `binding.json`

```json
{
 "schema_version": 1,
 "subject": "<as tree>",
 "tree_hash": "<sha256 the Setter read>",
 "repo_sha": "<base sha>",
 "setter": {"run": "<unit>", "model": "<id>", "at": "<iso>"},
 "second_read": {"model": "<other vendor>", "verdict": "agree | ambiguous", "leaves": ["<core leaf ids>"]},
 "leaves": {
  "<leaf id>": {
   "leaf_hash": "<sha256>",
   "oracle": {"cmd": "<exact command>", "reads": "<what it must read>", "signature": "<regex a red must match>"},
   "tier": "offline",
   "guard": {"kind": "patch | live", "patch": "<path in the item store>", "offline": true},
   "wrong_worlds": ["<the Setter's own, required for motion, timing, salience>"]
  }
 },
 "refused": [{"leaf": "<id>", "field": "<field>", "why": "<cannot bind because>"}]
}
```

A non-empty `refused` sends the goal back to the tree's author through `needs`. `tree_hash` must equal the tree's at intake and at the gate; a binding on an old hash is void.

## `contract.v<N>.json`

Computed, hash-locked, one clause per bound leaf plus clauses added by a tighten. Each clause: `{clause_id, leaf_id, leaf_hash, kind, oracle, tier, guard_ref, added_by, cites}`. The clause id survives versions so that a receipt can name it. `contract_hash` is what every report cites (Relentless §1). `advisory` floor leaves are reported and never block.

## Who may change what

| Change | Who | Effect |
|---|---|---|
| Add a clause under a leaf (tighten) | Marker, escape, finding | New `contract.v<N+1>`, old PASSes on that leaf void, tree untouched |
| Add a `preserve` leaf | Setter's unsaid sweep, tooling goals only, before lock | New tree hash, `by: setter_sweep` |
| Edit or remove a leaf, a waiver, floor line off | His word (`--owner-said`, or the Conductor's tag) | A loosening: new tree hash, Arbiter re-signs |
| A new concept | Concept agent, in an amendment | New tree hash, Arbiter re-signs |
| A worker, anywhere | Nothing | Build reads; it holds no pen on any of these files |

## Not decided here

- The adapter's tier list and forbids: step 5, from `selftest` and `modcheck` tiers.
- `concept_floor.json`'s schema: Concept's build order, and only its `hash` and line ids matter to this file.
- `<store>/judge/` permissions: the wall (step 1) denies the whole of it to Build, and holds no hold-outs until step 8.
