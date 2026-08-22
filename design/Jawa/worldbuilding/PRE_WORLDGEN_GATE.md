<!-- status: live -->
# Before the owner generates the world — what is actually owed

> ✅ **THE MAP IS ADOPTED, AND AUTHORING IS OPEN AGAIN — owner, 2026-08-22.** Verbatim, after
> looking at the four-globe sheet: *"That world, upon examination, really isn't very bad at all…
> we're thinking of trying to adopt it."* ⇒ **Ash'karr as it stands IS the v1 planet**, and work
> on it continues: continuity repairs, landmarks, named places, settlements, terrain detail.
>
> ⛔ **This REPLACES the 2026-08-21 freeze banner**, which said the opposite and is struck. The
> freeze lasted one evening and did its job — it stopped a redraft nobody wanted.
> ⚠️ **What did NOT come back:** re-running `ashkarr_paint.py` to regenerate the bundle, the
> reference-match harness (`refmatch.py` stays cancelled), and worldgen, which is out of every
> version and always was. **The map is edited DIRECTLY, one map, in place** — that is the whole
> method, per `the_one_map.md`.
> 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` stands as history, not as a plan.
> Ruling: `WORLD_ADOPTED_AUTHORING_OPEN_1` · supersedes `WORLD_FROZEN_RETHINK_PLANET_1`.


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
| 1 | ~~Four ratified KEEP rows are missing from the Configure Factions screen~~ 🔴 **REWRITTEN by CHECK, 2026-08-22.** The described cause is FIXED: `OnlyOurFactions.xml` no longer touches `maxConfigurableAtWorldCreation` (its own header now forbids it) and zeroes `startingCountAtWorldCreation` instead; exactly one visible FactionDef in the game reads 0, and it is `OuterRim_RebelAlliance`. ⚠️ **But a larger defect is real and was never the patch's fault:** **seven of our eight authored `Jawa_*` factions read −1** because we never set the field and their abstract parents do not carry it, and the engine's query is `> 0`. Only `Jawa_Junkers` is configurable, by inheritance accident. ⇒ `AUTHORED_FACTIONS_OFF_THE_SCREEN_1`; evidence `infrastructure/state/observed/2026-08-22/configure_factions/` | `SLATE_KEEPS_CONFIGURABLE_1` → `AUTHORED_FACTIONS_OFF_THE_SCREEN_1` | ⭐ **still the checklist's trap, for a different reason** |
| 2 | ~~**The Blackstar Company's vessel is dropped from the default worldgen list.** Biotech's `PirateWaster` declares `replacesFaction: Pirate`~~ ✅ **DISCHARGED — `PIRATE_VESSEL_RESTORED_1` closed at `42ad3ec`, and re-measured 2026-08-22.** `src/Jawa/Jawa_Patches/Patches/PirateWaster_Yield.xml` removes the field and zeroes the count, and the LIVE 578-mod dump confirms it: `PirateWaster` carries no `replacesFaction` at all. ⚠️ The shipped Biotech XML still declares it at `Data/Biotech/Defs/FactionDefs/Factions_Misc.xml:576` — **reading the vanilla file will make this look unfixed.** Read the dump. | `PIRATE_VESSEL_RESTORED_1` | the faction roster is fixed at creation |
| 3 | **The Galactic Empire's leader is Royalty's high stellarch**, not Palpatine — `fixedLeaderKinds` unpatched | `IMPERIAL_RAID_ROSTER_1` | the leader pawn is generated at creation |
| 4 | ~~**Eleven of the twelve NAMED factions have no `fixedName`**~~ 🔴 **RETIRED — measured live by CHECK, 2026-08-21: all TWELVE carry a `defFixedName` and all twelve wear it on a generated world** (`jawa/faction_name_get`; evidence `infrastructure/state/observed/2026-08-21/faction_names/`). `FACTION_FIXEDNAME_ELEVEN_1` has landed. ⚠️ What IS still random is **fifteen third-party mod factions** — `TradersGuild` → "Cosmic Nexus", `VFEP_Junkers` → "The Anti-Love Imps" and thirteen more — which is a scope call, not a gate item | `FACTION_FIXEDNAME_ELEVEN_1` | the faction's name is stored at creation |
| 5 | **Thirteen faction world-markers, designed and accepted, not installed** — plus four `colorSpectrum` changes that ship with them | `FACTION_ICONS_BESPOKE_1` | the map is frozen with them on it |

| 6 | 🔴 **Every authored leader title is invisible — the ideoligion overrides the def.** `jawa/faction_leader_get` reads `ideoOverrodeDefCount: 36` of 37. The Junkers' Scraplord is called **`Awoken Cheese`**; Blackstar's Captain is **`Ethical Thug`**. DECIDE ruled 2026-08-22 (`FACTION_SPEC.md`): **override all twelve on the IDEO**, in the same session as world creation, before the save | `LEADER_TITLES_ON_THE_IDEO_1` | ⭐ **an Ideo is generated once at world creation and cannot be retrofitted** |

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

⛔ **Only `Pirate` was hit, and it no longer is.** 🔴 **RE-MEASURED 2026-08-22 against the
live 578-mod `FactionDef` dump — 86 FactionDefs, post-inheritance, post-patch — and the
census below replaces the one this paragraph used to carry:**

    TribeRoughNeanderthal            -> TribeRough
    TribeSavageImpid                 -> TribeSavage
    OutlanderRoughPig                -> OutlanderRough
    VRESaurids_OutlanderRoughSaurid  -> OutlanderRough
    BS_LittlePeople                  -> OutlanderRough

**FIVE, not six, and none of them targets `Pirate`** — because `PirateWaster_Yield.xml`
removes the one that did. Two corrections to what was written here: `BS_LittlePeople` was
never listed and is real, and `PirateWaster -> Pirate` is listed and is gone.
✅ Nothing declares it at `OutlanderCivil` or `TribeCivil`, so the Homestead Defense League
and the Deep Desert Tribes are still safe.

🔑 **And the removal loop does not check the count.** `Page_CreateWorldParams.ResetFactionCounts`
runs `factions.RemoveAll(x => x == faction.replacesFaction)` over EVERY configurable faction,
whatever its `startingCountAtWorldCreation`. So zeroing a replacer does not protect the
faction it replaces — only removing the field does, which is what our patch does.
⚠️ **Re-run the scan against the DUMP if a mod is ever added**, because nothing warns — and
because a scan of the vanilla XML would report the field our patch has already removed.

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
