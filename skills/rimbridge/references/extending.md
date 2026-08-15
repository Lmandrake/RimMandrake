# Extending the bridge — writing a companion DLL

Read this when you are about to conclude "the bridge cannot do X".

---

## Companion DLLs are a supported path

RimBridgeServer 2.x loads mod-authored `[Tool]` methods from `BridgeTools`
folders. This is documented and supported, not a hack:

* `vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/SKILL.md`
* `vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/references/companion-dll-guide.md` (243 lines: csproj, load model,
  authoring pattern, validation checklist)

**This stopped being a proposal.** The three methods sketched here originally —
`set_terrain`, `destroy_at`, `damage` — became the 14 tools in §5; `destroy_at`
generalised into `jawa/destroy_batch`, because call count turned out to be the
only cost that matters (§8). Source and build:

```
src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs   all 14 [Tool] methods
src/RimMandrake/bridgetools/build.py                                        build + verify + deploy
```

The pattern that made them cheap to add: **compile against the running game's own
assemblies** (`Assembly-CSharp.dll` from the install, `RimBridgeServer.Sdk.dll`
from the workshop copy). The compiler then verifies every API you guessed at —
`FilthMaker.TryMakeFilth`, `ThingMaker.MakeThing`, `GenSpawn.Spawn`,
`thingGrid.ThingsListAtFast` were all confirmed that way, and **a compiler is a
better checker than IL archaeology.**

`IRimBridgeContext` also exposes `ctx.Tools.CallAsync` for composing existing
tools, `ctx.Game.StepTicksAsync/RunUntilAsync`, and `RimBridgeEvidenceManifest`
— a built-in screenshot-plus-assertion result format that is RimBench already
designed for us.

Gotcha the guide flags: `ExcludeAssets="runtime"` so the companion never bundles
`RimBridgeServer.Sdk.dll`; the host resolves it.

