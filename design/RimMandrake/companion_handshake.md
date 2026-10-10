# Companion handshake, safe profile and stale-target guards

For preflight (agent B) and the launcher (agent A): how to ask the running JawaBench companion **what is
actually loaded**, how its runtime profile is decided, and how to make a call refuse a stale target.
Items: `COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED`, `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT`,
`BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD`. Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`
`JawaBenchSafetyCore.cs` (pure rules, unit-tested in `bridgetools/AwarenessSelfTest/UnitsSafety.cs`) and
`JawaBenchCompanionSafety.cs` (Harmony gate, binder check, the tool).

**State: built offline, NOT deployed.** Nothing below has run in a live game. Every live claim is
UNVERIFIED until the acceptance list at the bottom runs.

## 1. The profile: safe unless a file says gm

| layer | what decides it | values |
|---|---|---|
| compile profile | `build.py --gm` (`JAWA_GM_TOOLS`) | `gm` (the 48 world-acting GM tools exist) or `standard` |
| runtime profile | `<SaveData>\JawaBench\companion_profile.json` | `gm` or `safe`; **absent, invalid, expired or unknown = safe** |
| effective | both, plus the loaded save | `safe` or `gm` |

- In the **safe** profile only the reviewed read-only tools in `JawaBenchSafetyCore.SafeAllowList` run
  (73 tools plus the handshake, from a static audit on 2026-10-10). Every other `jawa/` tool returns
  `{success:false, refused:true, error:"REFUSED by the companion's SAFE profile: ..."}` without running.
  A tool added later and never reviewed is refused too: the allow-list is the only way in.
- **gm** needs the file. Nothing a bridge client sends can raise the profile.
- A loaded save named in `campaignSaves` is **safe** even when the file says gm. The save name comes from the
  TPS lifecycle (the `LoadGame` hook), so it is null for a new game and when the sampler is off. In those
  cases the campaign check cannot fire.
- The file is re-read at most every 2 s, so a launcher that rewrites it takes effect within 2 s.
- `rimworld/*` tools belong to RimBridgeServer. They are **not** gated: stripping companion exports does not
  make the host read-only (GPT bridge review 4.8). A truly read-only campaign still means RBS absent.

The file is flat JSON:

```json
{"profile": "gm", "expiresUtc": "2026-10-11T06:00:00Z", "campaignSaves": "Ashkarr, Ashkarr autosave"}
```

`expiresUtc` is optional but recommended: a launcher that dies leaves a gm grant that ends by itself.
Unknown keys are tolerated.

⚠️ **Deploying this build changes behaviour.** Until a launcher writes the file, every live bridge session sees
the safe profile: spawn, edit, world and GM tools all refuse. Agent A's launcher owes the write for test sessions.

## 2. `jawa/companion_handshake` (schema `companion_handshake/1`)

Always allowed, in every profile. Read-only. Top-level keys, **in this order** (`JawaBenchSafetyCore.HandshakeKeys`;
the unit test fails if the composed object differs; changing it means bumping the schema string):

| key | meaning |
|---|---|
| `schema` | `"companion_handshake/1"` |
| `success` | `true` |
| `utc` | when the answer was composed |
| `companionAssembly` | `JawaBench.BridgeTools` |
| `companionVersion` | `AssemblyInformationalVersion`, `<version>+<40-hex commit>` |
| `companionSha` | the commit after the `+` (what `build.py` reads back), or null |
| `companionMvid` | the loaded module's MVID: it identifies the BUILD, it is not a hash |
| `companionFileSha256` | SHA-256 of the file at `companionPath`, or `"unavailable: <why>"` (e.g. loaded from bytes) |
| `companionPath` | `Assembly.Location`, or null |
| `compileProfile` | `gm` or `standard` |
| `runtimeProfile` | what the file DECLARES: `gm`, `safe`, `none`, `invalid` or `unreadable` |
| `effectiveProfile` | what is ENFORCED: `safe` or `gm` |
| `profileWhy` | the reason, e.g. `no profile file: safe by default` |
| `profileFile` | the path the companion reads |
| `gate` | `{status: complete|partial|failed|not installed, detail, guarded, unguarded[], installMs, refusals, lastRefusal, gateErrors, safeAllowList}` |
| `hooks` | `{tps, attribution, awareness, argGuard, wildSpawner}`: install status, detail, runtime error, and per-hook `coverage` (`ok`/`degraded`/`disabled` with counters) |
| `rimBridgeServer` | `{loaded, version, informationalVersion, path}` |
| `harmony` | `{version, path}` |
| `game` | `{available, epoch, programState, save, ticksGame, mapIds[], currentMapId}`, filled on the main thread with a 5 s limit, else `{available:false, why}` |
| `reservedArgs` | `["expectGameEpoch","expectMapId","expectCurrentMapId"]` |

How preflight should read it:

- **The disk identity is joined to the loaded module by `companionFileSha256` from the PATH the module was
  loaded from.** That is stronger than the MVID. It still does not prove the bytes in memory, because the file
  could change after load. Say so wherever exact loaded bytes matter.
- `gate.status != "complete"` means some tool is ungated. `unguarded[]` names each one and why.
- A hook with `coverage: "disabled"` is a recorder that faulted. Its record has a gap, so treat that as a coverage
  failure, never as "nothing happened".

## 3. Stale-target guards (reserved arguments)

Any `jawa/` call may carry these extra keys. No tool declares them. The binder hook
(`JawaBenchArgGuard.Prefix`, a prefix on RimBridgeServer's private `BindArguments`) reads them before the
tool runs, and refuses the call (an exception, the same path strict mode uses) when:

| key | refused when |
|---|---|
| `expectGameEpoch` | the current game epoch differs. Epochs count Game **objects**, so reloading the same save at the same tick is a new epoch, and so is the main menu (epoch 0) |
| `expectMapId` | no map with that `uniqueID` is in the current game (culled, abandoned, or another game) |
| `expectCurrentMapId` | the current map is a different one |

Take the values from `jawa/companion_handshake` (`game.epoch`, `game.mapIds`, `game.currentMapId`) when
targets are captured, and pass them on every later call that uses those targets. Calls without the keys are
unaffected. Limits: if the binder hook is not installed (`hooks.argGuard.installed:false`, after an upstream
rename) the keys are **dropped silently**, so check that field first. A load that lands between the bind and
the tool's main-thread body is not caught (UNVERIFIED window).

## 4. Quiet-world block: game-scoped and dead-man

`jawa/wild_spawner_block action=block minutes=N` (default 30, max 240) releases itself on expiry when no one
renews it (a killed runner), and also on a load, a new game, or the main menu. `lastRelease` says which:
`expired`, `new-game`, `no-game` or `released`. Renew by calling `block` again.

Other persistent switches, from the 2026-10-10 audit. These are **not** auto-released and remain owed:
`JawaBenchLogAutoOpenSuppress.Suppressed` (on by default, by design) and `JawaBenchArgGuard.Strict` (opt-in).

## 5. Live acceptance owed (one bridge session, after the owner releases the deploy)

1. Handshake with no profile file: `effectiveProfile:"safe"`, `gate.status:"complete"`, and `installMs` recorded
   (the cost of patching about 400 methods on Mono is UNMEASURED). `jawa/spawn_pawn` must refuse and
   `jawa/map_info` must answer.
2. Write a gm file: within 2 s the handshake reads gm and `spawn_pawn` runs. Then list the loaded save in
   `campaignSaves`: the handshake reads safe.
3. Capture `game.epoch`, reload the same save, and send any call with the old `expectGameEpoch`: it must be
   refused. Same for `expectMapId` after a map is abandoned.
4. Block the wild spawner, load a save, and read `lastRelease:"new-game"`. Block again with `minutes=1` and read
   `expired` after a minute.
5. The hook coverage of every TPS/awareness hook reads `ok` after 10 minutes of play on the full list.
