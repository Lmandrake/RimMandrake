## spec
🔴 **DECIDE ruled 2026-08-22: wire the nine orphaned role kinds into their factions.**
Full ruling — `design/Jawa/worldbuilding/pawnkind_roster.md`, *"Every authored kind must be
FIELDED"*. "Leave them as a reserve" was rejected outright.

    Jawa_DeepDesert_Grunt  Heavy  Leader  Specialist   -> TribeCivil
    Jawa_Blackstar_Grunt   Heavy  Leader  Specialist   -> Pirate
    Jawa_Empire_Leader                                 -> Empire  (plain omission)

## 🔑 the shape DECIDE ruled — replace the CAST, keep the GROUPS
✅ **Rewrite the `options` inside the COMBAT groups only.** This is the pattern
`GalacticEmpire.xml` already ships and proves — it is why three of four Empire kinds field
today while Deep Desert and Blackstar field none.

⛔ **Do NOT use `Inherit="False"` on `pawnGroupMakers`.** It drops all twelve inherited
groups including **Trader, Peaceful and Settlement**, and the 48-kind roster has **no
trader role** to replace them with. A faction that cannot send a caravan or defend its
settlement is a worse defect than the one being fixed.

⛔ **Do not let a raid mix ours with vanilla.** `pawnGroupMakers` inherits by APPENDING, so
a bare new `<li>` yields half-Tusken, half-generic-tribal raids. No vanilla `Tribal_*` may
appear in a Deep Desert combat group; no vanilla pirate kind in a Blackstar one.

⛔ **Non-combat groups stay vanilla.** Deliberate, not an oversight.

## why it matters — measured
18 live spawns from `TribeCivil` today draw `NerveSpiker`, `BMT_ThrumbungusShroom`,
`VWE_Throwing_Knives` and **bare 6 of 18**. The authored kinds draw gaderffii sticks and
Tusken cyclers — the faction the owner described on 2026-08-22.
Evidence: `observed/2026-08-21/armed_sweep_48/`.

## why it slipped through
`DeepDesertTribes.xml` contains the string `Jawa_DeepDesert` **zero times**; its one
sanctioned group addition is documented as vanilla-Core-only. `BlackstarCompany.xml` states
outright that `pawnGroupMakers` are untouched. Both patches did what they say — nobody ever
wrote the wiring step.

## verify
Spawn a raid from each of `TribeCivil`, `Pirate` and `Empire` and read the kinds back:
every combat pawn must be a `Jawa_*` kind. Then confirm each faction can still send a
trade caravan and still populates its settlement.

## criteria
Zero vanilla kinds in a combat group of the three factions; `Jawa_Empire_Leader` fielded;
Trader/Peaceful/Settlement groups still functional.

## watch out
⚠️ Not the same problem as the weapon cut. `FLAMEBOW_UNCUT_AND_RETAGGED_1` is separate —
doing this first may make the flamebow question moot for Deep Desert, but neither fix
substitutes for the other.
⚠️ Whether Blackstar generates at all is `BLACKSTAR_IN_DEFAULT_LIST_1` (CHECK, doing).
That one IS baked at worldgen; this one is not.
