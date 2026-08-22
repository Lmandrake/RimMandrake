## spec
🔴 **`JAWA_SCENARIO_PARTS_1`'s `ScenarioDef` is down to two `ScenPart`s, and BUILD has the
mechanism for both and the CONTENT for neither.** Everything else in that item shipped
2026-08-21/22. This is the last thing standing between it and done.

| ScenPart | mechanism | what is missing |
|---|---|---|
| `ScenPart_GameStartDialog` | trivial — one `<text>` node | **the opening narration itself** |
| `ScenPart_DisableIncident` | trivial — a list of `IncidentDef` names | **which incidents** |

**1. The opening narration is not written anywhere.** `design/Jawa/worldbuilding/SCENARIO_SPEC.md`
has the *situation* in prose — §"The opening": *"The clan has just brought a dead gravship
back to life. The campaign begins the moment it sets down and the hatch opens… The ship is a
house that used to be a vehicle, and getting it airborne again is the campaign."* — and it
says at :330 that **"The Sundered" must appear in player-facing text at least once**, naming
`GameStartDialog` as the obvious place. But the narration prose does not exist.

⛔ **This is the campaign's own voice and BUILD will not invent it.** DECIDE owns `design/`.

**2. `ScenPart_DisableIncident` has no list.** The parent ruling explains WHY the part is
right — it *"stops the storyteller drawing an incident while the def stays loadable for an
authored quest, which cherrypicking cannot express"* — but names **no incident**. Which
incidents is a scope call.

## verify
`SCENARIO_SPEC.md` (or a doc it names) carries the finished opening narration, containing
the string "The Sundered", and an explicit list of `IncidentDef` defNames to disable with a
line of reasoning each.

## criteria
BUILD can write the `ScenarioDef` without inventing a single word or choosing a single
incident.

## notes
🔑 **Everything else in `JAWA_SCENARIO_PARTS_1` is DONE.** For the record, so nobody rebuilds it:
- no planting → `AptitudeTerrible_Plants` on `MandrakeJawa` (`56d2b4d`)
- no digging → `RimMandrake_Jawa_MiningDisabled`, `disabledWorkTags: Mining` (`13c6dd8`)
- the "mining laser" → it is `DrillTurret`, already shipped; `OperateDrillTurret` re-pointed
  to `workType Hunting` (`fe0064c`). ⛔ Nothing authored, no art.
- the `Rule_DisallowDesignator_ZoneAdd_Growing` + `Rule_DisallowBuilding` list → **struck by
  the owner**, 2026-08-21.
