# BRIDGE_SELECT_NONCOLONIST_PAWN_1 — a direct, headless route to cast a non-colonist pawn's ability

## what is wrong

MEASURED live 2026-09-20, and RE-MEASURED the same day: **`rimworld/select_pawn` and
`ToolMapForPawns` both REFUSE a non-colonist pawn** — `select_pawn` resolves
`IsColonistPlayerControlled`, which no animal satisfies even after
`jawa/instant_recruit` puts it in `PlayerColony`. That much is true and permanent.

🔴 **What is NOT true, and was corrected on 2026-09-20: this is not a wall.** Three
existing tools already reach a wild or hostile pawn, all three MEASURED working that day:

| need | existing tool |
|---|---|
| select any pawn | **`rimworld/click_cell`** — returns `selectionAfter.selectedObjects`; selected a wild-spawned, faction-less animal and a `PlayerColony` animal alike |
| read/press its ability gizmo | **`rimworld/list_selected_gizmos`** + **`rimworld/execute_gizmo`**, then `click_cell` on the target |
| make the AI use the ability | **`jawa/lord_assault_spawn`** — a real `LordJob_AssaultColony`; six hostile creatures cast unprompted within ~1000 ticks |
| force a mental state | **`jawa/pawn_mental {action:"start", state:"Manhunter"}`** — `started: true` on a faction-less wild pawn; it has never had a faction check |
| check the ability was granted | **`jawa/grant_ability`** — its `alreadyHad` field is a READ of `Pawn_AbilityTracker` |

## why it still matters

`PORTED_BEAST_MECHANICS_REBUILD_1` closed on those tools alone — all six criteria PASS,
no new C# required. So this item is **an ergonomics and rigour improvement, not a
blocker on anything**:

- Gizmo-clicking needs the camera on the subject and gives no refusal reason; a cast
  that silently queues instead of firing reads identically to one that failed (that
  cost one measurement cycle — the answer was `"Ability already queued."`).
- `lord_assault_spawn` proves the AI *will* cast, not that a *named* ability casts on a
  *named* target at a *named* cell.
- `jawa/pawn_use_ability`'s `refusedBy` (below) names which engine predicate said no,
  which neither route above can.

More generally: every creature mechanic we rebuild from a donor framework is a mechanic
on a *wild or hostile* pawn, and a direct cast-and-report call is the instrument that
makes each one a one-call test instead of a staged scenario.

## the route

**A companion `[Tool]` that selects an arbitrary pawn and casts a named ability or verb
on it, bypassing the colonist check.** The `rimbridge-companion` skill is the how-to —
the C# pattern, the edit-build-deploy-test cycle on a minimal mod list, and `build.py`'s
guards. ⚠️ **A companion DLL cannot be written while RimWorld is running.** This lands
in a shutdown window. The code is already written and compiling; see below.

## spec

A bridge call that takes a pawn id or defName and selects it, and a call that makes it
use a named ability or verb, with neither refusing on faction. Named tools, wired the way
`rimbridge-companion` describes, and verified by the tool appearing in the live tool list
— a newly added tool missing from that list is the known silent failure.

## verify

A named ability on a wild `RSW_Voltmaw` / `RSW_Cindermite` casts at a named target in
ONE call, in a quicktest, with a refusal that names the predicate that refused.

## criteria

A wild or hostile creature's mechanic can be tested from outside the game, on demand,
without staging a selection through the camera.

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

⚠️ **Step 5 is now a re-confirmation, not a first proof.** `Filth_Fuel` in a cone with
zero fire was MEASURED three ways on 2026-09-20 (player-driven cast, AI-driven casts
under an assault Lord, and a cast onto 45 cells of `WoodLog x40` that left 19 coated and
started no fire over 1500 ticks) — `PORTED_BEAST_MECHANICS_REBUILD_1`'s closing section
holds the numbers. Use it as a calibration target for the new tool: if
`jawa/pawn_use_ability` cannot reproduce that cone, the tool is wrong, not the mechanic.
