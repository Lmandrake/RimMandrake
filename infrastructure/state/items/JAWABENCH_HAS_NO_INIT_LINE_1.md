## spec
**JawaBench.BridgeTools writes nothing to `Player.log` when it loads, so a load in
which the companion never loaded at all is indistinguishable from a healthy one.**

Measured 2026-08-22 against the 08:40 log (578 mods, rev591): **zero** lines
matching `JawaBench`. Not an error — an absence of any instrument. Every `Log`
call in the assembly is a `Log.Warning` inside a `catch`:

```
JawaBenchEventTools.cs:69    Log.Warning("[JawaBench] weather_get conditions: " …)
JawaBenchMapTools.cs:1026    Log.Warning("[JawaBench] prefab_capture: …")
JawaBenchWorldTools.cs:86    Log.Warning("[JawaBench] world_layers: …")
```

⇒ **silent when it works, silent when it is absent.** RimBridge itself announces
(`[RimBridge] Applied 56 optional Harmony patch classes.`); its companion does not.

⭐ **Why this costs real money.** `INHABITED_DLL_FIX_AT_SHUTDOWN_1` has to prove
`112 -> 115` tools after a deploy, and today the only route is *bring the bridge up
and ask it*. That means a game, a load, and CHECK holding the bridge — to answer a
question a single log line would have answered for free before anyone connected.
A companion that fails to load is also exactly the failure most likely to happen
after a deploy, and the current answer to "did it load?" is a shrug.

## verify
Add ONE `Log.Message` at companion startup, naming the assembly, its build id and
the number of tools it registered:

```
[JawaBench] ready: 115 tools, build e3e8a89c037a
```

PREDICTION after the next cold load: that line is present, and the count reads
**115** — the 112 already shipping plus `jawa/faction_name_get`,
`jawa/faction_name_set` and `jawa/faction_create`, all three confirmed present in
`JawaBenchFactionTools.cs` (lines 64, 156, 344) and built with 0 errors.

Then add it to `EXPECTED` in `src/RimMandrake/Utils/harvest_log.py`, where a
comment currently holds its place and explains why it is not there yet.

## criteria
The line appears in a cold-load `Player.log` with a tool count on it, and
`harvest_log.py` reports it under EXPECTED PRESENT.

## Watch out
- 🔑 **Emit the count, not just a greeting.** `[JawaBench] loaded` proves the
  assembly initialised and proves nothing about whether a deploy took. The whole
  value is that `115` is checkable against what was built.
- ⚠️ **Print it even on partial failure.** If tool registration throws halfway, a
  line reading `ready: 84 tools` is the single most useful thing in the log; a
  swallowed exception and no line is the situation we are already in.
- Include the build id. The deploy script already computes one (`e3e8a89c037a` vs
  the game's previous `7df3c51b01fb`), and it is the only way to tell a stale
  companion from a current one without md5-ing files.
- ⛔ Do NOT add `JawaBench` to `EXPECTED` in the harvest tool before the line
  exists — it would read RED on every load and train everyone to ignore it.
