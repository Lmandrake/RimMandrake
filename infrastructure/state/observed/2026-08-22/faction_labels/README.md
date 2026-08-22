# FACTION_LABELS_ONE_LOOK_1 — the names are right, the titles are all wrong

**CHECK, 2026-08-22 ~08:20 PDT. 578 mods, generated quicktest world, 37 visible factions.**
Read with `jawa/faction_leader_get`, `jawa/list_factions` and `jawa/world_info_get`.
Every string below is **the text the game reports**, not a judgement.

## The four rows

| # | row | observed | verdict |
|---|---|---|---|
| 1 | Homestead Defense League + **High Marshal** | name **`Homestead Defense League`** ✅ · title **`Divine Warden`** | 🔴 **FAIL** |
| 2 | Blackstar Company + **Captain** | name **`Blackstar Company`** ✅ · title **`Ethical Thug`** | 🔴 **FAIL** |
| 3 | Jawa Trade Moot settlements present | **`Jawa Trade Moot`, 4 settlements** | ✅ **PASS** |
| 4 | world named **Ash'karr**, correct apostrophe | **`Ash'karr`** — `U+0041 U+0073 U+0068 U+0027 U+006B U+0061 U+0072 U+0072` | ✅ **PASS** |

### ⭐ Row 4, the stop condition — CLEAR
The apostrophe is **U+0027 APOSTROPHE**, and `ASHKARR_WORLD_DEFINITION.md` uses **U+0027**
in both places it writes the name. **They match.** The name arrives even on a throwaway
quicktest because `Jawa_Patches/Patches/JawaWorld_Name.xml:30` sets it as a name rule
(`r_name->Ash'karr`), so it does not depend on the owner typing it correctly on the day.
⇒ **The unretrofittable half of this item is safe.**

⚠️ Row 4's other clause — *"the Sundered scenario and AmbientHorror are in the save"* — is
**UNMEASURED**. This is a dev quicktest, not the campaign save; there is nothing here to
read it off. It needs the real start.

## 🔴 The cause, and it is not two factions

`jawa/faction_leader_get` reports it in one line:

    37 factions · ideoOverrodeDefCount: 36

**Thirty-six of thirty-seven factions show a leader title that came from their generated
ideoligion, not from the def.** Every authored title is buried:

| faction | on screen | the def says |
|---|---|---|
| Homestead Defense League | `Divine Warden` | `High Marshal` |
| Blackstar Company | **`Ethical Thug`** | `Captain` |
| Galactic Empire | **`High Stellarch`** | `Emperor` |
| Deep Desert Tribes | `Earthly Chief` | `War Chief` |
| Jawa Trade Moot | `High Chief` | `Prime Trader` |
| Hutt Cartel | `Ruthless Councilor` | `Lord` |
| the Junkers | **`Awoken Cheese`** | `Scraplord` |
| Wildsteam Clan | `First Neodruid` | `Elder` |
| Deepwater Compact | `Moral Keeper` | `High Warden` |
| Ascendant Helix | `First Councilor` | `Director` |
| Geonosian Foundry Hive | `Prime Secretary` | `Archduke` |
| Free Droid Enclaves | `Mecha Secretary` | `First Speaker` |

This is `Faction.LeaderTitle` preferring the primary ideoligion's `leaderTitleMale`/`Female`
over `def.leaderTitle` — precisely the trap `jawa/faction_leader_get` was written to catch,
and it says so in its own description: *"a campaign that authored a title on the FactionDef
can be silently overridden by a generated ideoligion, and the def keeps reading correct
offline."* ⇒ **Offline validation of these twelve titles will pass forever and the game will
never show one of them.**

🔴 **And it bakes.** The ideo is generated at world creation and cannot be retrofitted, so
whatever title the ideo picks on the day is the title that ships. `Awoken Cheese` is not a
placeholder — it is what a player would read on the Junkers' leader, permanently.

⚠️ Note the Galactic Empire row against `IMPERIAL_RAID_ROSTER_1`, which is about the leader
*kind* being Royalty's high stellarch. The **title** is `High Stellarch` too, and that is a
second, separate defect on the same faction — the ideo, not `fixedLeaderKinds`.

## Verdict
**FAIL** on the item's criteria: rows 1 and 2 mismatch. The stop-class row 4 is clear.
The single-faction framing was wrong — this is 36 of 37 and it belongs on the pre-worldgen
path.
