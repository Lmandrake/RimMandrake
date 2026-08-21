🔴 **CORRECTED 2026-08-21 by `CUT_DISARMED_VANILLA_KINDS_1` — read that first.**
This item's PREMISE is wrong: it says our cherrypick was not the cause, and the cut IS the
cause for **11 of the 14** dead tags. `weapon_tag_audit.py`'s `emptied by the cut: 0` was a
structural artefact, never a measurement — Cherry Picker NEUTERS a cut weapon in place
rather than deleting it, so a tag whose every carrier was cut never enters a dump-built
index at all. ✅ **The discriminator here — *does this kind ever spawn HERE* — survives
untouched.** ⇒ Three base-game kinds were reopened and ruled back IN SCOPE:
`Mech_Pikeman`, `Drone_Sentry`, `Tribal_Archer_Fire`/`Tribal_Hunter_Fire`.

---

## spec
`weapon_tag_audit.py`, run 2026-08-21 against a dump captured 08:20:20Z that MATCHES the
live 578-mod list, reports **15 pawn kinds whose every weapon tag resolves to an empty
set**. Such a kind spawns bare-handed with no red error and nothing in `Player.log`.
Independently confirmed by the owner's 01:23 `first_light` run against the live process,
which found the same 15 among 710 tool-using kinds.

🔑 **THE CUT IS NOT THE CAUSE, and that is the whole reason this needs a ruling rather
than a fix.** The audit's own headline reads `weapon tags in the dump: 390 — emptied by
the cut: 0`. Our cherrypick emptied NONE of these. They were already empty in this mod
set, so `WeaponTags_Renormalise.xml`'s remedy — re-tag the survivors into the vanilla
vocabulary, which repaired 49 kinds — has nothing to work with here: the audit
classified **0** of the 36 untagged survivors into any of these roles.

**The 15, grouped by what they probably are:**

⚠️ **Probably DELIBERATE upstream, and a fix would be wrong:**
  `DP_ArtilleryPirate` · `DP_RocketPirate` — tags are literally `DP_CannonNoEquipTag`
  and `DP_RocketNoEquipTag`. The names say the weapon is not equipped from a tag pool.
  `VFEP_Footsoldier` — `WarcasketBasic`; VFE-Pirates equips warcaskets by its own system.
  `Mech_Pikeman` · `Drone_Sentry` — mechs and drones normally carry built-in weapons.

🔴 **Probably GENUINE — a raider or hunter that will arrive with empty hands:**
  `BS_Crossbowman` · `BS_CrossbowDvergr` · `BS_DvergrTraditionalist` (three tags each,
  all empty: `BS_CrossbowTag`, `DankPyon_Arbalest`, `VFEM2_Arbalest` — this reads like a
  mod expecting a crossbow mod we do not have)
  `AncientSoldierBoss` · `AncientSoldierBossN` (`AMHP`) · `AncientMallGuards` (`PKM`)
  `Tribal_Archer_Fire` (`NeolithicRangedFlame`) · `VEE_Hunter` · `VEE_TribalHunter`
  `OuterRim_ImperialTrader` (`ORImperialOfficer`)

**THE RULING NEEDED, and it is scope, not mechanism:** do we repair other mods' pawn
kinds at all? BUILD can do it — the mechanism is proven, it is more `PatchOperationAdd`
ops in `WeaponTags_Renormalise.xml` mapping each empty tag onto a surviving weapon of
the right role — but choosing WHICH weapon a Blackstar crossbowman or an Ancient boss
should carry is a content decision, and picking it silently would put weapons in raiders'
hands that nobody chose.
⛔ Do not rule "fix all 15": at least five are upstream-deliberate and arming them would
break the mod's own design.

## verify
after whatever DECIDE rules, `weapon_tag_audit.py` reports a kinds-with-every-tag-empty
list containing only the kinds DECIDE explicitly declared out of scope, by name.

## criteria
DECIDE's, and it is a written ruling naming which of the 15 are in scope and what role
of weapon each in-scope kind should receive. No artefact is owed by this item itself.

## notes
BUILD measured this and stopped at the scope line deliberately. The instrument is
`python3 src/RimMandrake/Utils/weapon_tag_audit.py`; it REFUSES to report unless the
dump's mod set matches `ModsConfig.xml`, and it did match at the time of writing.
⚠️ `first_light`'s version of this check EXCLUDES kinds with no `weaponTags` field at
all as deliberately-unarmed civilians (291 of them), so a combat role that loses its
tags entirely will read clean there. The audit tool does not have that blind spot.

## ruling
🔴 **DECIDE, 2026-08-21. THREE of the fifteen are in scope. Twelve are not, and seven of
those twelve are out for a reason BUILD could not have known.**

### The discriminator is not "is it broken" — it is "does it ever spawn HERE"

⭐ Repairing another mod's pawn kind is only worth doing if that kind reaches our planet.
Scanned every v1.6-loaded `Defs/` tree for what actually places each of the ten "probably
genuine" kinds:

| kind | placed by | ⇒ |
|---|---|---|
| `AncientSoldierBoss` | ⭐ `AncientMarket_Libraray.CustomMapDataDef` — `AM_Reserve` · `AM_ReserveRailway` · `AM_Supermarket_*` | 🔴 **IN SCOPE** |
| `AncientSoldierBossN` | same, plus `AM_ReserveBunker` | 🔴 **IN SCOPE** |
| `AncientMallGuards` | `AM_Supermarket_L` · `AM_Supermarket_S` | 🔴 **IN SCOPE** |
| `BS_Crossbowman` · `BS_CrossbowDvergr` | only `BS_Dvergr_Medieval_Union`'s group makers | ⬜ out — a medieval-fantasy faction, the exact class `WORLDGEN_FACTION_CHECKLIST.md` unticks |
| `BS_DvergrTraditionalist` | only `BS_LittlePeople` | ⬜ out, same |
| `Tribal_Archer_Fire` | only `TribeSavageImpid` | ⬜ out — not one of our thirteen |
| `OuterRim_ImperialTrader` | ⭐ only `OuterRim_GalacticEmpire`'s group makers | ⬜ out — **that vessel is struck.** Our Empire is vanilla `Empire`, whose trader group carries Royalty's own `Empire_Common_Trader` |
| `VEE_Hunter` · `VEE_TribalHunter` | 🔑 **NO REFERENCES ANYWHERE** — no faction, no group maker, no map data | ⬜ out — orphan defs nothing spawns |

⚠️ **"No group makers" nearly misread three of these as safe.** The ancient kinds carry no
`defaultFactionDef` and appear in no `pawnGroupMakers` — they are placed by **Ancient urban
ruins' map set pieces**, which is an entirely different route and is live on every map that
mod decorates. ⇒ **a kind can be unreachable through factions and still arrive constantly.**

✅ The five BUILD flagged as upstream-deliberate stay out, unchanged and for its reasons:
`DP_ArtilleryPirate` · `DP_RocketPirate` · `VFEP_Footsoldier` · `Mech_Pikeman` ·
`Drone_Sentry`.

### What the three get — the plainest possible answer, and it is not invented content

⭐ **Add the vanilla tag `Gun` to each, alongside its existing dead tag.** Not a chosen
weapon — the pool their own lighter sibling already uses.

`AncientSoldier` (Core) carries `weaponTags: [Gun]` and `weaponMoney 300~900`, and it is
**not** on the tagless list — so `Gun` is proven non-empty by this very audit.

🔑 **The budget already does the "these are elite" work, so the tag pool must not try to.**

| kind | CP | `weaponMoney` | dead tag kept |
|---|---|---|---|
| `AncientSoldier` *(working sibling)* | 85 | `300~900` | — |
| `AncientSoldierBoss` | 225 | `2100~7500` | `AMHP` |
| `AncientSoldierBossN` | ? | `2100~7500` | `AMHP` |
| `AncientMallGuards` | 425 | `2100~7500` | `PKM` |

Same pool, **eight times the money.** They will draw the expensive end of it, which is
exactly what a heavy variant should do, and **nobody had to pick a gun.**

⛔ **Keep the dead tags — do not delete `AMHP` or `PKM`.** They are additive. If the donor
mod is ever installed its weapons rejoin the pool on their own, and deleting the tag would
make that silently impossible.

⚠️ **`AncientMallGuards` and `AncientSoldierBoss`/`BossN` are also being relabelled** by
`FORSAKEN_LABELS_FINISHED_1`. Same three defs, same file. **Do them in one pass** — and note
the stakes: `Forsaken sentinel` at combat power 425 currently walks out of a supermarket set
piece **with empty hands and no error in the log.**

⇒ Filed as `THREE_ANCIENT_KINDS_ARMED_1`.
