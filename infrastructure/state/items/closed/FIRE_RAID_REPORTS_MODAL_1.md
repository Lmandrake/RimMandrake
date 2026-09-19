# FIRE_RAID_REPORTS_MODAL_1 — DONE: the firing tools diff the window stack and say when a modal ate the raid

## spec
`jawa/fire_raid` sets `executed = incident.Worker.TryExecute(parms)`. A Harmony prefix can
set `__result = true`, skip the raid entirely and push a modal instead — `Leo.RaidProtectionFee`
does exactly this on `IncidentWorker_RaidEnemy.TryExecuteWorker` (proven in
`SIX_FACTIONS_NEVER_RAID_1`). The tool then reports `executed: true, arrived: []` and the
caller cannot tell "the raid was cancelled by a dialog" from "pawn generation produced zero".
That ambiguity cost this project three retracted evidence tables.

## what shipped
`Find.WindowStack` is snapshotted **by `Window.ID`** before the call and diffed after, so a
window that was already open (the dev palette, the debug log) is never reported as new.
Two shared helpers in `JawaBenchEventTools.cs` — `SnapshotWindowIds()` /
`WindowsOpenedSince()` plus `DialogSwallowNote()` — and **four** tools now use them, not the
three the spec named:

| tool | file |
|---|---|
| `jawa/fire_raid` | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchEventTools.cs` |
| `jawa/fire_incident` | `…/JawaBenchTerrainTools.cs` |
| `jawa/storyteller_fire` | `…/JawaBenchIncidentTools.cs` |
| `jawa/raid_shape_fire` | `…/JawaBenchGroupTools.cs` — same `TryExecute` path, same blind spot |

`success` is now `executed && !blockedByDialog`; raw `executed` is still reported beside it,
so nothing is hidden — the lie is just no longer the field a caller reaches for first.

## Proven live 2026-08-31, FOUNDRY — 19-mod minimal tier + `leo.raidprotectionfee`
Fresh quicktest, dialogs listed before the firing so "opened during the call" is unambiguous.
Raw: `infrastructure/state/evidence/seven_faction_raids_2026-08-31/modal_results.json` ·
script `infrastructure/state/evidence/seven_faction_raids_2026-08-31/prove_modal.py`.

**ARM A — `PirateWaster`, humanlike, hostile, off cooldown:**

    success=False  executed=True  blockedByDialog=True  pawnsArrivedTotal=0
    windowsOpened=[{"type":"Verse.Dialog_NodeTree","forcePause":true,"isDebug":false,"id":2}]
    note="🔴 A DIALOG SWALLOWED THIS FIRING. 1 window(s) opened during the call
          (Verse.Dialog_NodeTree) and the incident produced nothing. … Clear it with
          jawa/window_list_close {action:'close', typeName:'<the type above>', closeAll:true}"

⇒ `executed` **would have said `true`**, exactly as it did on every retracted table.
The two windows already on the stack (`Verse.ImmediateWindow`, `LudeonTK.EditWindow_Log`)
were correctly NOT reported. `jawa/window_list_close` then closed it, `closedCount 1`.

**ARM B — `Mechanoid`, `humanlikeFaction: false`, which the fee exempts:**

    success=True  executed=True  blockedByDialog=False  pawnsArrivedTotal=9  windowsOpened=[]

The pair is the proof: same tool, same call, one arm extorted and one arm raiding, and the
flag separates them. Confirmed again on the 584-mod round — seven authored factions and the
vanilla `Pirate` control all reported `windowsOpened []` with the fee mod absent, so the
field does not false-positive on a real raid either.

## criteria
- [x] `jawa/fire_raid` returns a `windowsOpened` array (type name + `forcePause`, plus
      `optionalTitle`, `isDebug`, `id`) listing any window added during the firing, and
      `blockedByDialog: true` when one appeared while nothing arrived.
- [x] The `note` field says plainly that a dialog swallowed the raid and names
      `jawa/window_list_close` as the clear.
- [x] Proven live: firing at a humanlike hostile faction off the Protection Fee cooldown
      reports `blockedByDialog: true` rather than a bare `executed: true` (ARM A above).
- [x] Game-down deploy: two, `--gm --apply`, builds `281b011ff737` then `bccc7cf8d87f`;
      the live game registered **302 `jawa/` tools of 427**.

## ⚠️ Two things this round cost, both worth carrying forward
1. **`jawa/set_faction_relation` cannot make an authored faction hostile.** It moves
   goodwill to -100, leaves the kind `Neutral`, and says so — *"READ-BACK DOES NOT MATCH
   THE REQUEST — the engine overrode it"*. A pass that ignored that message had all seven
   of its firings silently substituted. Use
   **`jawa/faction_relations_set faction=<X> other=Player kind=Hostile both=true`**, then
   re-read `hostile` off `jawa/list_factions` before firing.
2. **`rimworld/start_debug_game_ready` while a `forcePause` modal is open killed the
   process** (connection reset, game gone, clean log). One occurrence, not isolated further
   — but clearing dialogs before starting a map costs one call.

## mod-list state
`leo.raidprotectionfee` was removed from `ModsConfig.xml` for the 584-mod round and the
minimal tier carried it back for this proof. **Restored**: 585 active,
md5 `41cda74e837619e200e2a031693f86de`, `modlist_swap --status` reports
`live currently matches: FULL`. Nothing about the mod set is left changed.
