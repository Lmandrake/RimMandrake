# BRIDGE_SELECT_NONCOLONIST_PAWN_1 — the bridge cannot drive a non-colonist pawn's ability

## what is wrong

MEASURED live 2026-09-20 (FOUNDRY, during `PORTED_BEAST_MECHANICS_REBUILD_1`'s
verification pass): **`rimworld/select_pawn` and `ToolMapForPawns` both REFUSE a
non-colonist pawn.** There is no bridge route to select, or to force a mental state on,
a hostile or wild creature.

## why it matters

It is the sole blocker on three criteria of a build that is otherwise proven:

- `PORTED_BEAST_MECHANICS_REBUILD_1` criteria **4, 5 and 6** — the ability gizmo and its
  AI use, the cindermite's chemfuel cone, and settings persistence — all require making
  a **hostile predator** fire a ranged ability on command. Criterion 2 (ferroclaw eats
  steel, 75 → 60, exactly 1/5) and criterion 3's core mechanism are **DEFINITIVELY
  confirmed live**; only this capability gap stands between the item and closing.

More generally: every creature mechanic we rebuild from a donor framework is a mechanic
on a *wild or hostile* pawn. Without this, none of them can be verified except by
waiting for the AI to volunteer the behaviour, which is not a test.

## the two candidate routes

1. **A companion `[Tool]` that selects an arbitrary pawn** and/or forces a mental state
   / triggers a verb on it, bypassing the colonist check. This is the direct fix and the
   `rimbridge-companion` skill is the how-to — the C# pattern, the edit-build-deploy-test
   cycle on a minimal mod list, and `build.py`'s guards.
   ⚠️ **A companion DLL cannot be written while RimWorld is running.** This lands in a
   shutdown window.
2. **A scripted colonist-attacks-first provocation** — spawn a colonist in reach, have it
   attack, and let the predator retaliate. Cheaper, needs no DLL, but it proves the
   ability fires under AI control rather than that the gizmo works, so it cannot close
   criterion 4 on its own.

⇒ Route 1 is the real answer; route 2 is worth doing first if a shutdown window is far
off, because it would close criterion 5 (the cone) immediately.

## spec

A bridge call that takes a pawn id or defName and selects it, and a call that makes it
use a named ability or verb, with neither refusing on faction. Named tools, wired the way
`rimbridge-companion` describes, and verified by the tool appearing in the live tool list
— a newly added tool missing from that list is the known silent failure.

## verify

`PORTED_BEAST_MECHANICS_REBUILD_1` criteria 4, 5 and 6 can be exercised on
`RSW_Voltmaw` and `RSW_Cindermite` in a quicktest without a colonist provoking them.

## criteria

A wild or hostile creature's mechanic can be tested from outside the game, on demand.

## progress 2026-09-20 — route 1 written and COMPILING, deploy owed

Three ungated `[Tool]` methods added to the JawaBench companion, in one new file
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchAbilityTools.cs`:

- **`jawa/select_things`** — select any spawned thing or pawn, no faction check.
  `action` = `select` | `add` | `clear` | `get`, comma-separated `ids`, optional
  `jumpCamera`. Reads the selection back out of `Selector.SelectedObjects`; the
  accept bool is never treated as selection.
- **`jawa/pawn_use_ability`** — `action='list'` reads every AbilityDef the pawn
  holds with its real `CanCast` report, cooldown and verb; `action='cast'` fires
  one at `targetId` or `x`/`z`. Three modes, `resetCooldown`, `force`, `draft`,
  and an order_pawn-shaped `waitTicks`/`timeoutSeconds`/`unpause` wait with the
  speed restored in a `finally`.
- **`jawa/pawn_use_verb`** — the same for a raw `Verb`, enumerated from five
  sources (race `VerbTracker`, equipment, apparel `CompApparelVerbOwner`,
  `HediffComp_VerbGiver`, and each ability's verb). Ambiguous names are refused,
  never resolved silently.

**Already covered, deliberately not rebuilt:** forcing a mental state on an
arbitrary pawn is `jawa/pawn_mental`, which resolves through `FindPawn` and has
never had a faction check. Granting an AbilityDef is `jawa/grant_ability`.

### what was MEASURED, from 1.6 source via RimSage

- `Selector.SelectInternal` (`RimWorld/Selector.cs:300`) has **no faction or
  colonist gate**. It refuses four things — null, a non-Thing/Zone/Plan, a
  destroyed thing, a world pawn — and each is a `Log.Error` that pops the dev
  console. The colonist check was the bridge's own, never the engine's. All four
  are pre-checked in `jawa/select_things` so the engine never Log.Errors.
- `Ability.Activate` (`Ability.cs:543`) applies **only the EffectComps** — it
  does not fire the verb, so a projectile ability produces nothing from it. That
  is why `mode='job'` is the default and `mode='effect'` carries a warning.
- `Ability.QueueCastingJob` (`Ability.cs:611`) routes through
  `ShowCastingConfirmationIfNeeded`, which can push a `Dialog_MessageBox` and
  never cast. `mode='job'` therefore builds `Ability.GetJob` itself and calls
  `Pawn_JobTracker.TryTakeOrderedJob` — the identical job, minus the modal.
- `Ability.CanApplyOn` (`Ability.cs:360`) reads the **private** `effectComps`
  field, not the lazy `EffectComps` property, so on a fresh ability it skips
  every comp veto and answers true. The tool touches `EffectComps` first.
- `VerbTracker.InitVerb` sets `verb.caster = directOwner.ConstantCaster` and
  `Ability.ConstantCaster` is the pawn — an ability verb's caster is always
  right and must not be set by hand.
- `HediffSet.GetHediffsVerbs()` returns a **shared static buffer**; copied out.
- `Pawn.IsWorldPawn()` lives in `RimWorld.Planet`, not `RimWorld`.

### state

**COMPILES — CONFIRMED.** `dotnet build -c Release`, 0 warnings, 0 errors, both
with and without `/p:JawaGmTools=true` (`TreatWarningsAsErrors` is on).
`tool_metadata.tool_names_from_dll` on the GM build reads **335** tool names
against 332 before — exactly the three new ones, no phantom, no truncation, and
`build.py --gm` printed no "WOULD REMOVE TOOLS". Selftests 67/67.

**NOT DEPLOYED AND NOT PROVEN LIVE.** RimWorld was running and FOUNDRY held the
bridge, so the companion DLL could not be written. The repo artifact at
`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`
is current; the game copy is one commit behind and lacks the three tools.

### deploy + verify in the shutdown window

Five minutes, from a WSL shell, once the game is down and the bridge free.
⚠️ Note the destination is the game root's **`BridgeTools\JawaBench`** folder,
not `Mods\`. From `/mnt/d/Luke/dev/Rimworld`:

```
taskkill.exe /F /IM RimWorldWin64.exe                                  # MUST be first; the DLL is memory-mapped
python.exe src/RimMandrake/bridgetools/build.py --gm --apply           # check the output says "deployed"
src/RimMandrake/bridgetools/launch_and_wait.sh                         # waits for Player.log truncation, not a stale marker
python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools      # the three names MUST appear; missing = the known silent failure
```

Then prove it, on the minimal list with `RSW_Voltmaw`/`RSW_Cindermite` loaded
(`modset_builder.py`'s beastmechanics tier), from a `python.exe` prove script
shaped like the others in that folder — `rimworld/start_debug_game_ready` with
`readiness="mapData"`, then poll `rimworld/get_ui_state` for
`programState == "Playing"` before anything touching the camera:

1. `jawa/spawn_pawn` a `RSW_Voltmaw` (faction-less/wild) and a colonist target.
2. `jawa/select_things ids=<voltmaw id>` → `selectedCount` must be 1 and the row
   must name the voltmaw. **This alone closes the item's criterion.**
3. `jawa/pawn_use_ability pawn=<voltmaw> action=list` → `RSW_VoltmawPlasmaVolley`
   present with `canCast=true`. (The comp grants it on `CompTickRare`, so let the
   game tick first, or `jawa/grant_ability` it directly.)
4. `jawa/pawn_use_ability pawn=<voltmaw> action=cast ability=RSW_VoltmawPlasmaVolley
   targetId=<colonist> waitTicks=600` → expect `accepted=true` and, in
   `readBack`, `lastCastTickAdvanced=true` plus `onCooldown=true`. Those two are
   the evidence; `success:true` is not.
5. Repeat for `RSW_CindermiteFuelSpew` with `x`/`z` (its verb targets locations,
   not pawns) and confirm `Filth_Fuel` appeared with `jawa/list_things`.
6. Exercise a refusal: cast at a cell past `verbProps.range` with `mode='verb'`
   and check `refusedBy` names `CanHitTarget`, not a bare false.

That discharges `PORTED_BEAST_MECHANICS_REBUILD_1` criteria 4, 5 and 6 without a
colonist provoking anything, which is what route 2 could never do.
