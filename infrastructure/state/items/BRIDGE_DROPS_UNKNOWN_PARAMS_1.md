# BRIDGE_DROPS_UNKNOWN_PARAMS_1 — a typo'd argument is invisible

Proven live 2026-08-26, deliberately, after two of my own calls were silently mis-parameterised.

```
jawa/new_allowed_area {label: "CHECK_correct"}              -> success, label "CHECK_correct"
jawa/new_allowed_area {name:  "CHECK_wrong", banana: 42}    -> success, label "Area 3"
jawa/time_clock       {zzz: "nonsense", ticks: "not-a-num"} -> success, full correct payload
```

**`success: true` every time.** A key the schema does not declare is discarded before the tool runs,
with no warning, and the tool proceeds on its defaults.

## Why this is worse than it looks

A wrong parameter name is only ever caught when the tool then misses a **required** field and
refuses. Where a sensible default exists you get a call that succeeds and does something else:

* `jawa/new_allowed_area` — the param is **`label`**, not `name`. Passing `name` gave a default
  `"Area 3"` and a cheerful success.
* `jawa/stop_job` — the param is **`mode`**, not `action`. Passing `action: "StopAll"` ran
  `endcurrent` instead, and only the tool's own `beforeJob`/`afterJob` read-back showed it.

⇒ This affects **all 291 live tools**, not the 45. It is a property of the bridge's argument
handling. `jawa/damage`'s error text already warns about it for its own parameters; it is now
measured on two more and generalised.

## Four different grammars, in one session, on tools that look alike

```
rect     jawa/room_get, jawa/set_terrain_batch (via ops), rimplace's compiled calls
rects    jawa/destroy_batch
ops      jawa/set_terrain_batch, jawa/set_roof_batch, jawa/paint_area, jawa/build_batch
label / name / action / mode      new_allowed_area, stop_job
faction  "player" accepted by spawn_pawn, REFUSED by build_batch (wants PlayerColony)
```

## What to change

**Refuse an unknown key**, or return it in a `droppedParameters[]` array. A caller who passes a key
the tool does not know is always making a mistake, and the current behaviour hides it. A warning
line costs nothing and would have saved four separate losses today.

## Until then

🔑 **Read the schema, not the sibling tool.** `b.list_tools()` gives the accepted keys per tool; diff
your arguments against them before issuing a batch. Recorded in `rimbridge/references/traps.md`.
