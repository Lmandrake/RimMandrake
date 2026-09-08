## spec
Found 2026-09-08, FOUNDRY code-review loop (subagent review of `gl_emit.py`,
verified by hand). Not currently live — filed as a known gap, not fixed
blindly, since `gl_emit.py` is under active development (MAPGEN_GL_SHEET_1 /
MAPGEN_CONVERGENCE_LOOP_1) and the correct fix needs calibrating against a
real GL-authored landform the way the sibling bug below already was.

`build_desertplateau()` (or whichever function currently plays that role)
parses every source node's `<FloatRange>` entries into a local `floatranges`
dict per node. That dict is only ever consumed inside the `worldTileReq`
branch (`g.tile_req(..., hilliness=floatranges.get("HillinessRequirement"),
road=floatranges.get(...), ...)`, each field named explicitly). The generic
fallback branch for every OTHER node type —

    node = g.node(type_, sn["name"], pos=sn["pos"], **kwargs)

— only forwards `kwargs` (scalar + variable fields). `floatranges` never
reaches it. So a `<FloatRange>` field on any node type other than
`worldTileReq` is silently dropped from the emitted XML.

**This is the exact same shape as a bug already fixed once in this file**,
documented right there in `Graph._variable_field`'s own docstring: "a
Variable is never dropped just because it isn't one of that builder's named
parameters (found live 2026-09-06: 14/44 landforms carry
`AllowedRiverTypes` on `worldTileReq`, which `tile_req()` did not accept)."
That fix routed `variable`-typed fields generically through `node()`'s
`**fields` -> `_variable_field()`. The analogous fix for `floatrange`-typed
fields was never made.

**Why not fixed blind**: today's 44 shipped landforms only ever put a
`FloatRange` on `worldTileReq` (confirmed — `--selftest` passes clean, and
no other node type in the corpus carries one), so nothing currently breaks.
The prior `AllowedRiverTypes` bug was caught the same way this one wasn't
caught yet: by actually authoring a landform that hit it live, then reading
the emitted XML against what GL's deserializer expects. A fix written now,
without a real FloatRange-on-a-non-worldTileReq-node landform to calibrate
against, risks getting the XML shape wrong in a way nothing here would catch
until it's tried live — same trap the `_var_meta` mechanism exists to avoid
for Variables (deserializer rejects `List<String>` where the graph declares
`List<MapSide>`, found live, not offline).

## verify
```
PROVE   floatrange fields on non-worldTileReq nodes survive a round trip
        through gl_emit.py unchanged
EXPECT  author (or find) a landform with a FloatRange on some other node
        type; a fix should make g.node()'s generic path route floatrange-
        typed fields the same way _variable_field() routes variable-typed
        ones, calibrated against that real node's expected XML shape
LIES    "the selftest still passes" is not evidence this is fixed or that
        it isn't a live problem -- the selftest only covers today's 44
        landforms, none of which exercise this path
```
Not started — offline-safe to read, but the calibrating landform doesn't
exist yet. Whoever is already driving `gl_emit.py`'s development (BENCH,
per MAPGEN_GL_SHEET_1/MAPGEN_CONVERGENCE_LOOP_1) is closest to knowing
whether this is worth fixing ahead of hitting it, or waiting to hit it.
