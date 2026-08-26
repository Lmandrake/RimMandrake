# The religion test — 2026-08-26, seat CHECK

🔴 **The question `ASHKARR_IDEOLOGY_MODE_CALL_1` turns on: do the twelve authored ideoligions
actually generate on a world that is NOT in classic mode?**

**They do. All twelve, by name, with their own cultures and structure memes — and the leader titles
come out correct with no work at all.**

Taken free on the quicktest world the debug game generated (seed `entrails`, coverage 0.3,
**119,904 tiles** — a different planet from Ash'karr's 21,872, which is exactly what the load-round
skill says a quicktest produces). Full 582-mod list, `[JawaBench] ready: 166 tools`.

## 45 ideoligions, and every one of our twelve CultureDefs is in use

```
the Contract                 Jawa_Culture_Blackstar     Structure_Ideological      (x3)
the Sun-Debt                 Jawa_Culture_DeepDesert    Structure_Animist
the Balance                  Jawa_Culture_Deepwater     Structure_Ideological
the Continuity Protocol      Jawa_Culture_Droid         Structure_Ideological
The Rising Order             Jawa_Culture_Empire        Structure_TheistEmbodied
Meckgin                      Jawa_Culture_Geonosian     Structure_Ideological
the Ascendant Genome         Jawa_Culture_Helix         Structure_Ideological
the Covenant of Free Wells   Jawa_Culture_Homestead     Structure_TheistAbstract
the Reckoning of Debts       Jawa_Culture_Hutt          VME_Structure_Corporate
the Weight                   Jawa_Culture_Junkers       AM_Structure_Scavenger
The Salvation                Jawa_Culture_TradeMoot     AM_Structure_Scavenger
the Green Oath               Jawa_Culture_Wildsteam     Structure_Animist
```

**12 distinct `Jawa_Culture_*` in use, 4–5 memes each.** `ideologyActive: true`, `ideosTotal: 45`,
**178 non-player believers**.

⇒ Compare Ash'karr: **`ideosTotal: 1`**, vanilla `Astropolitan`, `Classic_*` precepts. The content was
never broken. Classic mode was simply never letting any of it run.

## 🔑 And `LEADER_TITLES_ON_THE_IDEO_1` needed nothing built

Every one of our factions reads its **def title exactly**, with `effective == ideo == def`:

```
Jawa_Junkers            Scraplord     Jawa_IndigenousTribes   Prime Trader
Jawa_HuttCartel         Lord          Jawa_WildsteamClan      Elder
Jawa_AscendantHelix     Director      Jawa_DeepwaterCompact   High Warden
Jawa_FreeDroidEnclaves  First Speaker Jawa_GeonosianFoundryHive  Archduke
```

⇒ On Ash'karr every one of these read the single word `leader`. On 2026-08-22, on a third world,
they read `Awoken Cheese` and `Ethical Thug`. **Here they are right**, because `fixedIdeo` makes the
ideo take the def's title instead of rolling one.

🔑 That item was closed FAILED with a corrective escalation. The corrective is not a build task at
all — **it is the world-creation setting**, and this reading proves the rest of the chain works the
moment that setting changes. Third-party factions on this same world still roll generated titles
(`Prime Many-as-One`, `Cyber Dog`, `Archic Archist`, `Wise Rebbe`), which is what ours would do
without `fixedIdeo`.

## Two things worth knowing before anyone celebrates

⚠️ **Six ideoligions borrowed our cultures and generated their OWN names** — `The School` and
`Human Academy` and `Hominid University` and `Nightmare Deep` are sitting on `Jawa_Culture_Droid`,
`Jawa_Culture_Junkers` and `Jawa_Culture_TradeMoot`. Our authored CultureDefs are in the general
pool, so unrelated factions can roll them. Cosmetic on this throwaway world; on the shipped one it
means a random outlander faction can be culturally Jawa.

⚠️ **`the Contract` appears three times** on `Jawa_Culture_Blackstar`. Three separate Ideo objects
with the same authored name. Not investigated — flagging it, not explaining it.

⚠️ **`jawa/world_info_get` reported `factions: 0` on this world** while `jawa/faction_leader_get`
listed 30+. Do not read a faction count off `world_info_get` on a quicktest.

## What this does to the decision

`ASHKARR_IDEOLOGY_MODE_CALL_1` offered: re-create in full Ideology, ship classic, or prove the import
first. The owner chose to prove the import. **This reading settles the other half of that choice for
free:** the twelve religions and their leader titles are not a hope, they are measured working. What
remains unproven is only whether the *terrain* survives the port — `IDEOLOGY_REBUILD_TRIAL.md`.
