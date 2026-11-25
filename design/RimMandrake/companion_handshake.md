# Companion handshake, campaign/test profiles and stale-target guards

For preflight (agent B) and the launcher (agent A): how to ask the running JawaBench companion **what is
actually loaded**, how its runtime profile is decided, and how to make a call refuse a stale target.
Items: `COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED`, `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT`,
`BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD`. Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`
`JawaBenchSafetyCore.cs` (pure rules, unit-tested in `bridgetools/AwarenessSelfTest/UnitsSafety.cs`) and
`JawaBenchCompanionSafety.cs` (Harmony gate, binder check, the tool).

**State: the gate runs in the live companions.** Two rules of 2026-11-23 are built and unit-tested. The profile guards a
canonical world save only (§1), and the list of canonical saves is compiled in. All four games (ArchBig, ArchSmall, Steve1,
Steve2) load a companion at or after f3c90ff50c (handshake read 2026-11-24).

## 1. The profile: CAMPAIGN guards a canonical world save, and nothing else

Nobody plays during development (owner, 2026-11-23; `standing_rulings.md` §Nobody plays during development). The only
protected saves are the canonical world saves.

- The bridge stays **fully usable in the CAMPAIGN profile** for authoring. CAMPAIGN is NOT read-only.
- CAMPAIGN refuses the debug, test-only, heavy-diagnostic and quiet-world families while a canonical world save is loaded.
- The cheap always-on recorders stay on in both profiles, so a slowdown is explained, not hidden.
- Each profile declares its recorder budget as a constant. No hook hard-codes it.

| layer | what decides it | values |
|---|---|---|
| compile profile | `build.py` (`JAWA_GM_TOOLS`) | `gm` (the world-acting GM tools exist; the default) or `standard` (`--no-gm`) |
| runtime profile | `<SaveData>\JawaBench\companion_profile.json` | `test` (`gm` is an alias) or `campaign`, and `campaignSaves`: more saves to guard, beside the canonical ones. **Absent, invalid or unknown = campaign on a loaded save** |
| effective | both, plus the loaded save | `campaign` or `test` |

### Policy per profile (`JawaBenchSafetyCore.CampaignPolicy` / `TestPolicy`: data, read by the installers and hooks)

| policy field | campaign | test |
|---|---|---|
| `RecorderBudgetShare` (declared ceiling on recorder slowdown) | **0.10** | 1.00 |
| TPS sampler, TPS attribution | on | on |
| awareness cheap hooks (incident journal, spawn, context scopes) | on | on |
| awareness `GeneratePawn` hook | **off**: arm refuses it, and early install is ignored | on (lazy, or early by option) |
| wild-spawner quiet-world block | **off**: tool refused, and an active block releases (`campaign-profile`) | on |
| denied tool families | refused | none |

The budget is **judged, not enforced**. `JawaBenchSafetyCore.BudgetVerdict` returns `within`, `over` or
`unmeasured`, and the handshake reports it. Silently switching a recorder off when it runs over would hide the
slowdown it explains. The real verdict needs the C0-C5 restart protocol
(`RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP`). Until that runs, the handshake's `policy.budget.verdict` is
`unmeasured`. The only figure it shows is the awareness hook bodies' share of uptime, which is labelled as partial.

### Tool families (`JawaBenchSafetyCore.CampaignDenied`)

| family | campaign | tools |
|---|---|---|
| authoring and read (everything not listed below) | **available** | spawn, edit, terrain, world, pawn, incidents, raids, lords, inhabited, zones, research, render and review, and all read tools |
| `debug-invoke` | refused | `static_call`, `debug_actions`, `debug_action_yielders`, `debug_settings`, `hot_reload_defs`, `stat_cache_bust` |
| `test-only` | refused | `tps_test_block`, `tps_test_attribution`, `playtest_*`, `gss_playtest_*`, `gss_stage`, `oracle_selftest`, `oracle_test_ohm_letter`, `load_stall_probe`, `flowworks_job_probe` |
| `heavy-diagnostic` | refused | `type_visibility`, `startup_types`, `forecast_incidents`, `world_cache_audit`, `tile_cache_audit`, `texture_audit`, `biome_art_audit`, `pawnkind_audit`, `world_mutators_audit`, `world_lint`, `rimdefdump_run`, `export_things` |
| `quiet-world` | refused | `wild_spawner_block` |

- A refused call returns `{success:false, refused:true, error:"REFUSED in the CAMPAIGN profile: <tool> is <family> (...)"}`
  and the tool does not run.
- A tool that is not listed stays available. The unit test (`UnitsSafety.cs`) checks three things against the
  real source census: every listed name exists, the owner's must-stay authoring tools are allowed, and the
  must-be-off tools are refused.
- `jawa/awareness action=arm` still arms disk rows in campaign. Only the `GeneratePawn` hook stays off.
- A new game was loaded from no save, so it is **test** with no file. A loaded save is **test** when the file says test
  and the save is not canonical. Nothing a bridge client sends can change the profile.
- The canonical saves are compiled in, from `infrastructure/state/CANONICAL_SAVE.md`
  (`design/specs/2026-11-23-canonical-save-guard/boundary.md`). A loaded canonical save is **campaign** even when the file
  says test. So is a save named in `campaignSaves`, and a loaded save whose name is unknown. A file that says `campaign` is
  campaign everywhere. The save name comes from the TPS lifecycle (the `LoadGame` hook).
- To work on a canonical save with the test tools, load a copy of it under another name.
- The file is re-read at most every 2 s, on any jawa call. The policy hot hooks read (`CurrentPolicy`) is refreshed
  by the same calls, so a profile change reaches `GeneratePawn` and the wild spawner on the next jawa call.
- `rimworld/*` tools belong to RimBridgeServer and are not gated.

```json
{"profile": "test", "expiresUtc": "2036-01-01T00:00:00Z", "campaignSaves": ""}
```

`expiresUtc` ends nothing. The companion and the host checks (`companion_grant.py`, `ensure_test_profile`) do not
read it. Unknown keys are tolerated.

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
| `runtimeProfile` | what the file DECLARES: `test`, `campaign`, `none`, `invalid` or `unreadable` |
| `effectiveProfile` | what is ENFORCED: `campaign` or `test` |
| `profileWhy` | the reason, e.g. `loaded save '<name>' is a listed canonical save: campaign` |
| `profileFile` | the path the companion reads |
| `policy` | the effective profile's policy: `recorderBudgetShare`, each recorder switch, `deniedFamilies`, and `budget` (`verdict`, plus the partial awareness figure) |
| `gate` | `{status: complete|partial|failed|not installed, detail, guarded, unguarded[], installMs, refusals, lastRefusal, gateErrors, campaignDenied}` |
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

1. Handshake with no profile file and a loaded save: `effectiveProfile:"campaign"`, `gate.status:"complete"`, and `installMs`
   recorded (the cost of patching about 400 methods on Mono is UNMEASURED). `jawa/spawn_pawn` must run and
   `jawa/static_call` must refuse. `jawa/awareness action=arm` must arm and leave `generationHook` not installed.
2. Write a test file: within 2 s the handshake reads test and `static_call` runs. Then list the loaded save in
   `campaignSaves`: the handshake reads campaign. Load the canonical start: the handshake reads campaign with an empty list.
3. Capture `game.epoch`, reload the same save, and send any call with the old `expectGameEpoch`: it must be
   refused. Same for `expectMapId` after a map is abandoned.
4. Block the wild spawner, load a save, and read `lastRelease:"new-game"`. Block again with `minutes=1` and read
   `expired` after a minute.
5. The hook coverage of every TPS/awareness hook reads `ok` after 10 minutes of play on the full list.
