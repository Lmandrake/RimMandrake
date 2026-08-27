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

---

# 🔑 THE FIX IS AVAILABLE TO US, AND THE TARGET IS NAMED — measured 2026-08-27, BUILD

Method: `dnfile` + `dncil` parsing the ECMA-335 `#~` / `#Strings` heaps and disassembling
the method body. **A real TypeDef/MethodDef/Field census, not a `strings` scan** — so its
negatives are worth something, subject to the caveat at the bottom.

## The assemblies
```
<workshop>/294100/3727949765/1.6/Assemblies/RimBridgeServer.dll                       1,305,600
<workshop>/294100/3727949765/1.6/Assemblies/RimBridgeServer.Core.dll                    252,928
<workshop>/294100/3727949765/1.6/Assemblies/RimBridgeServer.Sdk.dll                      33,280
<workshop>/294100/3727949765/1.6/Assemblies/RimBridgeServer.Contracts.dll                22,528
<workshop>/294100/3727949765/1.6/Assemblies/RimBridgeServer.Extensions.Abstractions.dll    5,632
```

## 🔴 The root cause, from the IL — it is a PULL LOOP, not a scan
```
RimBridgeServer.AnnotatedExtensionCapabilityProvider
private static object[] BindArguments(
    MethodInfo method,
    IReadOnlyDictionary<string, object> arguments,
    RimBridgeServer.Sdk.IRimBridgeContext sdkContext,
    CancellationToken cancellationToken)                              RVA 0x3fb28
```
It iterates **`method.GetParameters()`** and, for each parameter that is not
`IRimBridgeContext` or `CancellationToken`, calls `arguments.TryGetValue(param.Name, out v)`
then `ConvertArgument(v, param.ParameterType)`. ⇒ **It never enumerates `arguments`.** A key
with no matching parameter is never read, never counted, never reported. The 90-instruction
body contains **no count or length comparison** between the two — CONFIRMED absent, not merely
unmeasured.

Call path: `InvokeMethodAsync(toolClass, method, arguments, sdkContext, ct)` → `InvokeAsync(…)`
→ `BindArguments`. Upstream, `RimBridgeServer.ReflectedCapabilityBinding.NormalizeInvocationArguments(object)`
(public static) turns the raw JSON payload into the dictionary — kebab-case, `JObject`/`JArray`
and legacy shapes — before `BindArguments` sees it.

## ⛔ THE CHEAP FIX DOES NOT EXIST — do not go looking for it
`ctx` is `RimBridgeServer.Sdk.IRimBridgeContext`; the only implementation is
`RimBridgeServer.RimBridgeContext`. A full field/property census of both types returns
**exactly** `OperationId · CapabilityId · Tools · Game · MainThread` (concrete class carries
only those five `k__BackingField`s). **No member holds the raw argument dictionary**, so a
JawaBench tool cannot self-check its own unknown keys. That route is closed.

## ✅ The route that IS open
A Harmony prefix or postfix on `BindArguments` — the one place where the full raw
`arguments` dictionary and the declared `method.GetParameters()` are both in scope:
```csharp
var unknown = arguments.Keys.Except(method.GetParameters().Select(p => p.Name)).ToList();
```
Then either throw, or stash `unknown` in a `[ThreadStatic]`/`AsyncLocal` that JawaBench's own
tools read and surface as `droppedParameters[]`. `BindArguments` is **private static**, which
`AccessTools.Method` handles — it simply is not reachable as a public API.

## What is still unmeasured
- Whether `ConvertArgument` or `NormalizeInvocationArguments` throw or log on some malformed
  shapes — only their signatures were pulled, not their bodies. UNMEASURED.
- Whether RimBridgeServer has a **settings-menu** strict-mode toggle — not checked; this was
  a binary-only investigation.
- The name census found no type or member containing `Strict`, `Unknown`, `Unrecognized`,
  `ExtraParam` or `DroppedParam` as a parameter-handling concept. ⚠️ **That is a strong
  negative but not a complete one** — it cannot rule out such logic living inside a method
  body under an unrelated name.

## Watch out for whoever writes this
- ⚠️ **The patch target is a THIRD-PARTY PRIVATE METHOD.** It carries no compatibility
  promise; a RimBridgeServer update can rename or inline it and the patch then silently stops
  applying. Make the Harmony patch **assert its target resolved** and log loudly if not —
  a Harmony patch that fails to find its method is exactly the silent no-op this item exists
  to abolish.
- 🔑 **This changes behaviour for ALL 291 live tools, not just ours**, because it sits in the
  shared binder. Refusing outright would break any caller that has been passing a stray key
  and getting away with it. **Prefer reporting `droppedParameters[]` first**, look at what a
  session actually surfaces, and only then decide whether to refuse.
- 🔴 **Deploying it needs the game DOWN** — assemblies are locked by the OS while RimWorld
  runs. It rides a shutdown window, unlike every XML fix in this queue.
