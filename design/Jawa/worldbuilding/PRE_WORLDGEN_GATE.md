<!-- status: live -->
# Before the owner generates the world — what is actually owed

> 🔴 **THE PLANET IS FROZEN — owner's ruling, 2026-08-21. Do not paint, repaint, re-render
> or reference-match it.** Verbatim: *"We need to just freeze the world for now as-is and
> move on to v1. I have to totally rethink how we create that planet. It's really messy and
> horrible compared to what I was hoping for originally."*
>
> ⛔ **Every instruction in this file to edit the paint, re-run the painter, render and judge
> the map by eye, or clear a pre-worldgen gate is DEAD FOR V1** — whether or not it is struck
> below, and whether or not it reads as merely "not started yet". The map that exists IS the
> v1 map. `refmatch.py` is cancelled, not gated, and does not exist.
> ✅ **What survives is CORRECTNESS** in artifacts and tools we still ship — a link CSV
> emitted backwards, a lint excluding the wrong tiles. Fix those.
> 🔮 The rethink of the authoring METHOD is post-v1: `design/V2_DREAMS.md >
> PLANET_METHOD_RETHINK_1`. ⛔ It is **not worldgen**, which is out of every version.
> Ruling: `WORLD_FROZEN_RETHINK_PLANET_1` · canon: `ORTHO_GLOBE_MAP_ACCEPTED_1`.


_DECIDE, 2026-08-21, closing `D-CRIT`. Measured against the disk and the 1.6 source, not
against queue state._

> 🔴 **The rule this file exists to serve.** The owner builds ONE world, by hand, once, and
> it is then frozen and shipped inside a savegame. **Factions and ideoligions are read at
> world creation and cannot be retrofitted** — a faction absent when he clicks is absent
> from every player's game forever. `V1.md` gate rows 2 and 7 are that single event.

---

## 1. 🔴 The ledger says six things are undone. All six are on disk.

`D-CRIT`'s verify asked whether the pre-worldgen faction and ideo work is live. It is.
Every one of these reads `ready` in the ledger and **ships in `src/`** — verified field by
field, 2026-08-21:

| item | what it is | disk |
|---|---|---|
| B40 (the Empire reskin) | `GalacticEmpire.xml` — label, `fixedName`, `leaderTitle`, both combat groups | ✅ shipped |
| B41 (the Homestead Defense League) | `HomesteadDefenseLeague.xml` — label, `High Marshal`, `raidsForbidden`, weight 1.9, the Covenant of Free Wells | ✅ shipped |
| B42 (the Deep Desert Tribes) | `DeepDesertTribes.xml` — label, `War Chief`, the water raid group at commonality 30, the Sun-Debt | ✅ shipped |
| B43 (the Blackstar Company) | `BlackstarCompany.xml` — label, `Captain`, weight, the Contract | ✅ shipped |
| B52 (the Jawa Trade Moot) | `JawaTribes.xml` — all six fields, all three `Jawa_Tribal_*` kinds in the group options | ✅ shipped |
| B54 (the faith text) | **12** files carry `fixedIdeo` + `ideoName` + a non-empty `ideoDescription`; `hiddenIdeo` appears nowhere | ✅ shipped |

⚠️ **Do not re-do any of them, and do not read a `ready` state as evidence of absence.**
Queue state decays; the disk does not. ⇒ Whoever next touches these should close them
against the commits that already built them, not rebuild them.

⚠️ 🔴 **CORRECTED by CHECK, 2026-08-21, against the running game — this paragraph used to
say four and it was wrong.** There are **three** `deityPresets` holders: `GalacticEmpire.xml`,
`HomesteadDefenseLeague.xml`, `JawaHuttCartel.xml`. `JawaTribes.xml` has none, deliberately —
its own comment at line 97 says a `deityPresets` block there *"would be an error, not an
improvement"*, because `AM_Structure_Scavenger` allows **zero** deities. `grep -c
'<deityPresets>'` returns 1/1/1/0 across the four files. The live game agrees: `jawa/ideo_of`
on two quicktest worlds reports exactly three deities — `Palpatine`, `the Withdrawn`,
`the Ledger` — and The Salvation comes back `keyDeityName: null`, `deityCountRange: "0"`.
⇒ **B54's original audit of three was right.** Evidence:
`infrastructure/state/observed/2026-08-21/B54_faction_faiths/`.

---

## 2. What is genuinely still owed, and only this

Three things, all small, all filed. **Nothing else in the faction or ideo layer blocks the
click.**

| # | what | filed as | why it bakes |
|---|---|---|---|
| 1 | 🔴 **Four ratified KEEP rows are missing from the Configure Factions screen.** `OnlyOurFactions.xml` zeroes `maxConfigurableAtWorldCreation`, which deletes a row from `FactionGenerator.ConfigurableFactions` rather than capping it — so the owner cannot restore them where the checklist tells him to | `SLATE_KEEPS_CONFIGURABLE_1` | ⭐ **the checklist is a trap until this lands** |
| 2 | **The Blackstar Company's vessel is dropped from the default worldgen list.** Biotech's `PirateWaster` declares `replacesFaction: Pirate` | `PIRATE_VESSEL_RESTORED_1` | the faction roster is fixed at creation |
| 3 | **The Galactic Empire's leader is Royalty's high stellarch**, not Palpatine — `fixedLeaderKinds` unpatched | `IMPERIAL_RAID_ROSTER_1` | the leader pawn is generated at creation |
| 4 | **Eleven of the twelve NAMED factions have no `fixedName`** (only `Empire` carries one), so a generated world names them at random | `FACTION_FIXEDNAME_ELEVEN_1` | the faction's name is stored at creation |
| 5 | **Thirteen faction world-markers, designed and accepted, not installed** — plus four `colorSpectrum` changes that ship with them | `FACTION_ICONS_BESPOKE_1` | the map is frozen with them on it |

⚠️ **Items 1 and 2 are the same class of bug and it is worth naming:** a faction can be
*silently absent* from the screen the owner ticks. Nothing logs it, and the checklist reads
as if the row will be there.

⭐ **What is NOT on this list, deliberately.** `RAIN_DRY_THE_LOWLANDS_1`,
`OCULAR_FOREST_SUMMITS_1` and `META_JSON_NAMES_DEAD_PIRATE_1` all edit the **paint**, which
W9 stamps onto the world *after* generation. They must land before the stamp, not before the
click. `NINE_XENOTYPES_AUTHORED_1` and everything `Inhabited` are later still — people are
placed on a finished planet.

✅ **The ideoligion artifacts are measured and clean** — `The Salvation.rid` 250/266 with
**no dangling names**, `MandrakeJawa.xtp` 36/36, both against the 2026-08-20 dump
(`validate_save_artifact.py`, 2026-08-21). ⛔ This is **not** an open gate item and the old
*"82 precepts unmeasured"* framing is dead. The one residue —
`IDEO_ABILITY_DEFS_UNREAD_1`, 16 ritual `AbilityDef`s the dump cannot see — was **closed
2026-08-21, offline: 16 of 16 resolve** in folders 1.6 actually loads. ⇒ **the player's
ideoligion is fully measured and nothing about it is open.**

⚠️ **All three must be DEPLOYED, not merely committed.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never this repo.

⚠️ **`WORLDGEN_FACTION_CHECKLIST.md`** (`infrastructure/state/`) is ratified — 21 untick,
**4 keep** as of 2026-08-21 — and needs no build. It is one screen the owner ticks during
the run. 🔴 **But four of its rows currently do not appear on that screen.**
`JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes `maxConfigurableAtWorldCreation`,
which deletes a faction from `FactionGenerator.ConfigurableFactions` rather than capping it.
⇒ `SLATE_KEEPS_CONFIGURABLE_1` must land before the run, or the checklist is a trap.

---

## 3. The trap that produced #1, stated once so it is not re-derived

**`replacesFaction` silently removes the replaced faction from worldgen.** Two engine
paths, and they behave differently — which is why this was reported both as "impossible"
and as "fine", and neither was right:

| path | what happens to a replaced def |
|---|---|
| `WorldGenStep_Factions.cs:11` → `InitializeFactions(layer, info.factions)` — **the normal path**, a list the player configured | added verbatim. No skip test runs at all. But `Page_CreateWorldParams.cs:83-85` already removed the replaced def from the **default** list, so it is absent unless the player adds it back by hand |
| `InitializeFactions(layer, null)` — no list configured | `FactionGenerator.cs:78` skips the def outright if any faction with `requiredCountAtGameStart > 0` replaces it |

🔑 **So the replaced faction is not impossible — it is *silently defaulted away*.** On a
world that is generated once and frozen, that distinction does not help: a faction that
survives only because someone remembered an unwritten step is a faction we will lose.

⛔ **Only `Pirate` is hit.** Measured across every active mod: six defs declare
`replacesFaction`, at `Pirate`, `OutlanderRough`, `TribeRough` and `TribeSavage`. Nothing
declares it at `OutlanderCivil` or `TribeCivil`, so the Homestead Defense League and the
Deep Desert Tribes are safe. ⚠️ **Re-run that scan if a mod is ever added**, because
nothing warns.

---

## 4. Verify

```
# nothing schedules the run — it is the owner's event, not ours
grep -rln "worldgen" infrastructure/state/items/ | xargs grep -l "schedule\|run the worldgen"

# the three open blockers are deployed, not merely committed
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches

# the replacesFaction scan, re-run after any mod-list change
#   -> expect exactly: PirateWaster->Pirate, OutlanderRoughPig->OutlanderRough,
#      TribeRoughNeanderthal->TribeRough, TribeSavageImpid->TribeSavage,
#      VRESaurids_OutlanderRoughSaurid->OutlanderRough
```

⛔ **Nobody tells the owner the world is ready to make until §2 is empty and deployed.**
