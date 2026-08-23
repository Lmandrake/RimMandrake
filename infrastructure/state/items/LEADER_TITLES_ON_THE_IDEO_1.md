## spec
🔴 **DECIDE ruled 2026-08-22: write the leader title onto the IDEO for all twelve authored
factions.** Full ruling — `design/Jawa/worldbuilding/FACTION_SPEC.md`, *"Leader titles must
be written onto the IDEO"*. **Pre-worldgen: an Ideo is generated once at world creation and
cannot be retrofitted.**

`Faction.LeaderTitle` prefers the primary ideo's `leaderTitleMale`/`leaderTitleFemale` and
only falls back to `def.leaderTitle`. Measured live 2026-08-22, `jawa/faction_leader_get`:
**`ideoOverrodeDefCount: 36` of 37.**

| faction | player reads | def says |
|---|---|---|
| the Junkers | **`Awoken Cheese`** | `Scraplord` |
| Blackstar Company | **`Ethical Thug`** | `Captain` |
| Galactic Empire | `High Stellarch` | `Emperor` |
| Jawa Trade Moot | `High Chief` | `Prime Trader` |
| Hutt Cartel | `Ruthless Councilor` | `Lord` |
| Homestead Defense League | `Divine Warden` | `High Marshal` |
| Deep Desert Tribes | `Earthly Chief` | `War Chief` |
| Wildsteam Clan | `First Neodruid` | `Elder` |
| Deepwater Compact | `Moral Keeper` | `High Warden` |
| Ascendant Helix | `First Councilor` | `Director` |
| Geonosian Foundry Hive | `Prime Secretary` | `Archduke` |
| Free Droid Enclaves | `Mecha Secretary` | `First Speaker` |

⛔ **All twelve, not the bad ones only.** DECIDE rejected the hybrid explicitly: it needs the
identical mechanism so it saves nothing, and it leaves the result per-world — a re-roll
produces a different set of "good" titles and the whole judgement must be redone.

⛔ **The 25 non-authored factions are out of scope.**

## 🔑 the mechanism is YOURS and must be READ, not guessed
The `FactionDef` ideo block carries no leader-title field. Two candidate routes:
1. a precept that supplies the title, or
2. a post-worldgen bridge pass writing `leaderTitleMale`/`leaderTitleFemale` onto each of
   the twelve ideos, then SAVING.

⚠️ **Do not guess the field name or the PreceptDef.** Read it. **If neither route exists,
that is a finding — report it and DECIDE will re-rule.** Do not invent a third route that
edits the savegame by hand.

⚠️ **The bridge route must run in the SAME session as world creation, before the save.**
Once frozen, the ideos are inside the savegame.

## verify
🔴 **Live-only, and on the world that will actually be frozen — not a quicktest**, because
each world rolls its own ideos. `jawa/faction_leader_get` must report the intended title in
`effectiveTitle` for all twelve.

⚠️ **No offline instrument can see this.** `validate_ideoligion.py`, `derive_matrix.py` and
the def dump all read `def.leaderTitle`, which is correct and unused. An offline pass will
report success while the defect is fully present.

## criteria
Twelve authored factions report their authored title in `effectiveTitle` on the pre-freeze
world.

## related, and separate
`IMPERIAL_RAID_ROSTER_1` is the Empire's leader *kind* being Royalty's high stellarch pawn.
This is the *title* also reading `High Stellarch`, from the ideo. Same faction, different
cause — fixing `fixedLeaderKinds` will not change the title.
Evidence: `observed/2026-08-22/faction_labels/`.


---

## 🔴 CORRECTION — BUILD, 2026-08-23, against capture `2026-08-23T07-12-04Z`

**A third route was found and shipped, and this item says not to look for one.**

⛔ *"Two candidate routes… Do not invent a third route."* The third route exists and is the one
in the game: **`CultureDef.leaderTitleMaker`**, shipped at `3bbe6a99`. Measured: 12
`Jawa_Culture_*` defs each name their own `Jawa_LeaderTitle_*` rule pack.

⇒ The instruction not to look further was written before the answer was found. Only the live
`effectiveTitle` reading on the pre-freeze world is still owed.
