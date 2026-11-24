# `s.raw`: call any bridge tool by name while you explore

**For:** it reaches every one of the 563 bridge tools from inside a session, for a hunt or for a need that no other
name serves yet. `scene.tools(words)` finds a tool.

## Accepts

| call | arguments | example |
|---|---|---|
| `s.raw(tool, **args)` | the tool's full name and its own arguments | `s.raw("jawa/static_call", type=PROOF, method="StageStoreroomPit", args="")` |
| `scene.tools(words)` | search words; no session is needed | `scene.tools("power net")` |

## Returns

`s.raw`: the tool's reply as the bridge gave it, wrapped with a receipt. `scene.tools`: at most ten tools, one line
each: the name, what it does, whether it is declared read-only.

Receipt of `s.raw`: `did`: "raw call of <tool>; the library does not know what it changed" (or `[]` for a tool that is
declared read-only); `hands`: that tool, 1 call; `could_not_look`: "the effect of a raw call is not read back";
`stamps`: **EXPLORED**, unless the tool is declared read-only in the bridge's schema record.

## State changes

Whatever the tool does. The game side writes every raw call into the trace, with its tool name and arguments. A raw
call of a tool that can change the game marks the **game process** EXPLORED until the game restarts: every later
session in that process carries the stamp, and so does a save written in it. A run with that stamp counts for no bar.

A tool is read-only only when its C# declaration says so. A tool with no declaration is treated as changing.
`jawa/static_call` can never be declared read-only, because its name does not say what the called method does.

## Refuses

| name | when | repair |
|---|---|---|
| `UNKNOWN_TOOL` | the name is not in the schema record | the message lists the nearest names; or `scene.tools(words)` |
| `BAD_ARGS` | the arguments do not fit the tool's schema | the message prints the schema |
| `SESSION_CLOSED` | the session has ended | open a session |
| `LIFE_CYCLE_TOOL` | the tool would end or replace the session (load a game, quit, change the mod list) | use `s.act.reload`, or close the session first |

## Example (Explosive Knockback: `knockback_runner.py` stages and judges each scene through a C# helper in a PROOF build)

```python
reply = s.raw("jawa/static_call", type="RimMandrake.ExplosiveKnockback.<the proof class>",
              method="<the stage method of the storeroom pit>", args="")
print(reply.receipt.stamps)        # ['EXPLORED']
```

This is how that scene runs today (`jawa/static_call` is the most used tool: 844 call sites in 204 files). On the
library it still runs, and it is stamped, so it cannot pass a bar on a build that we do not ship. That is the signal to
convert it: the staging becomes `s.stage`, the blast `s.act.explode`, the verdict `scene.judge`.

## The red check

`test_raw_refuses_*` (one for each row), `test_raw_changing_call_stamps_explored`,
`test_raw_undeclared_tool_is_treated_as_changing`, `test_raw_call_is_in_the_trace`. Planted fault: a raw call of
`jawa/static_call` that leaves no stamp.

## Limits

It gives no read-back and no undo. It is the exploring layer, not a way around the other nine names.
`python3 src/RimMandrake/Utils/scene.py raw-census` lists every raw call in the committed scenes, as a proposal for a
reviewer. It groups by the typed operation, not by the tool: two calls of `jawa/static_call` into different methods are
two different things, and a generic dispatcher is never promoted itself.
