## spec
🔴 **36 of 37 factions show a leader title that came from their generated ideoligion, not
from the def.** Measured live 2026-08-22 with `jawa/faction_leader_get`, which reports it in
one field: `ideoOverrodeDefCount: 36`.

| faction | what a player reads | what the def says |
|---|---|---|
| Homestead Defense League | `Divine Warden` | `High Marshal` |
| Blackstar Company | **`Ethical Thug`** | `Captain` |
| Galactic Empire | **`High Stellarch`** | `Emperor` |
| the Junkers | **`Awoken Cheese`** | `Scraplord` |
| Deep Desert Tribes | `Earthly Chief` | `War Chief` |
| Jawa Trade Moot | `High Chief` | `Prime Trader` |
| Hutt Cartel | `Ruthless Councilor` | `Lord` |
| Wildsteam Clan | `First Neodruid` | `Elder` |
| Deepwater Compact | `Moral Keeper` | `High Warden` |
| Ascendant Helix | `First Councilor` | `Director` |
| Geonosian Foundry Hive | `Prime Secretary` | `Archduke` |
| Free Droid Enclaves | `Mecha Secretary` | `First Speaker` |

`Faction.LeaderTitle` prefers the primary ideoligion's `leaderTitleMale`/`leaderTitleFemale`
and only falls back to `def.leaderTitle`. ⇒ **Every authored title in the campaign is
invisible**, and every offline check of them passes.

## 🔴 why this is a pre-worldgen item
An Ideo is generated **once at world creation and cannot be retrofitted**. Whatever title
the generator picks on the day is the title that ships inside the frozen savegame, forever.
`Awoken Cheese` is not a placeholder — it is what the Junkers' leader is called.

⚠️ It is also invisible to every offline instrument we own. `validate_ideoligion.py`,
`derive_matrix.py` and the def dump all read `def.leaderTitle`, which is correct and unused.
**Only a live world shows the real string.**

## what to decide
1. ⭐ **Set the title on the ideo, not the def.** The `FactionDef` ideo block cannot carry a
   leader title, so this means either a precept that supplies one, or a post-worldgen bridge
   pass that writes `ideo.leaderTitleMale/Female` on each of the twelve and then SAVES.
   ⚠️ The bridge route is viable precisely because the world is authored once by hand — but
   it must happen in the same session as worldgen, before the freeze.
2. **Accept the generated titles.** They are not all bad — `First Neodruid` for the
   Wildsteam Clan and `Moral Keeper` for the Compact read well. `Ethical Thug` and
   `Awoken Cheese` do not.
3. **Hybrid** — accept where the roll is good, override the handful that are not. Needs the
   same mechanism as (1), so it is not cheaper.

## criteria
On the world that will be frozen, `jawa/faction_leader_get` reports the intended title in
`effectiveTitle` for the twelve authored factions — or a recorded ruling that the generated
titles stand.

⚠️ **Whatever is decided, it must be verified on the real world before the freeze**, not on
a quicktest, because the titles are per-ideo and each world rolls its own.

## related, and separate
`IMPERIAL_RAID_ROSTER_1` is about the Empire's leader *kind* being Royalty's high stellarch
pawn. This is the Empire's leader *title* also reading `High Stellarch`, from the ideo. Two
defects, one faction, different causes — fixing `fixedLeaderKinds` will not change the title.

Evidence: `infrastructure/state/observed/2026-08-22/faction_labels/`.
