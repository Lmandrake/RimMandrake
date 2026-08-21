<!-- status: live -->
# The Galactic Empire — gap audit against vanilla `Empire`

_DECIDE, 2026-08-20, answering `queue/DECIDE.md` **D-EMP1**. Measured against the shipped
Royalty def and our shipped patch; nothing inferred from a summary table._

> 🔴 **OWNER RULING 2026-08-20:** *"I've been very clear. OuterRim_GalacticEmpire is no
> longer in the game, we patch Empire."*

⛔ **This document cites no quarantined file.** The two audits in
`infrastructure/disposing/` are treated as absent, as the ruling requires. They did not
merely go stale — they audited the wrong vessel.

⚠️ **Blast radius: the Empire's VESSEL only.** Other `OuterRim_*` defs — pawn kinds, gear,
the droid factions — are untouched and staying. 🔑 **Do not sweep by the `OuterRim_`
prefix.** `Neronix17.OuterRim.GalacticEmpire` **is still an active mod** and supplies our
stormtrooper kinds; only the faction *def* was retired as the vessel. DECIDE nearly got
this wrong while auditing and records it here so nobody else does.

---

## 0. The vessel, and the two things that cannot change

**Vessel: `Empire`, from Royalty.** Royalty is always loaded on this stack, so ⛔ **no
`MayRequire` and no `PatchOperationFindMod` wrapper is needed for anything Royalty-side.**

🔴 **NON-NEGOTIABLE — changing either silently breaks the game:**

| must keep | why |
|---|---|
| `<defName>Empire</defName>` | `FactionDefOf.Empire` backs `Faction.OfEmpire` and has **~25 consumers** — `GenStep_Settlement`, throne-room and landing-pad resolvers, `IncidentWorker_CaravanArrivalTributeCollector`, psylink reward gating, `PermitsCardUtility`, six QuestNode roots. Rename it and `Faction.OfEmpire` goes null **silently** |
| six `Empire_*` PawnKind defNames | pinned in `PawnKindDefOf`: `Empire_Royal_Bestower`, `Empire_Royal_NobleWimp`, `Empire_Fighter_Janissary`, `_Trooper`, `_Cataphract`, `Empire_Common_Lodger`. **Reskin labels and apparel, never the defNames** |

✅ **Everything else is data and patchable** — label, description, art, titles, permits,
apparel, name makers, and the ~140 Keyed strings.

---

## 1. What our shipped patch already delivers — VERIFIED

`src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml`, **deployed**
2026-08-19 20:38. Every field the spec calls for is present and correct:

| specced | in the patch |
|---|---|
| `label` The Galactic Empire · `fixedName` Galactic Empire | ✅ |
| `leaderTitle` Emperor · `pawnSingular/Plural` stormtrooper(s) | ✅ |
| `description` · `settlementGenerationWeight 0.45` | ✅ |
| `permanentEnemy` **false** + `permanentEnemyToEveryoneExcept` whitelist | ✅ shipped — ruling (b) of §2 is IN the patch, not pending |
| `fixedIdeo` + `ideoName` The Rising Order + deities | ✅ |
| Combat groups → `OuterRim_Imp*` kinds | ✅ 12 entries, 9 `MayRequire`-gated on an **active** mod |

⭐ **And the xpath shape is proven in production**:
`/Defs/FactionDef[defName="Empire"]/pawnGroupMakers/li[kindDef="Combat"][commonality="100"]/options`
plus the `[commonality="10"]` variant. **Both values verified present** in
`Data/Royalty/Defs/FactionDefs/Faction_Empire.xml` — vanilla Empire's four group makers are
Trader / Combat(100) / Combat(10) / Settlement, and **none of them carries a `Class=`
attribute**, which is why any xpath selecting on a pawnGroupMaker *class* matches nothing.

---

## 2. 🔴 THE FINDING — `permanentEnemy` is broader than anyone ruled

Read off `FactionDef.cs:463`:

```csharp
public bool PermanentlyHostileTo(FactionDef otherFactionDef)
{
    if (permanentEnemy) return true;               // ← short-circuits FIRST
    if (permanentEnemyToEveryoneExcept != null && !...Contains(otherFactionDef)) return true;
    ...
}
```

**The blanket flag returns before the exception list is ever consulted.** Vanilla `Empire`
ships `permanentEnemyToEveryoneExcept` naming `OutlanderCivil`, `TribeCivil`, `PlayerTribe`,
`PlayerColony`, `Ancients` and four DLC factions. ⇒ **our `permanentEnemy true` makes that
entire list dead code.**

**So the Empire is permanently hostile to EVERY faction on this planet:**

| | in this campaign |
|---|---|
| `OutlanderCivil` | **the Homestead Defense League** |
| `TribeCivil` | **the Deep Desert Tribes** |
| all eight `Jawa_*` | Hutt Cartel · Junkers · Free Droid Enclaves · Geonosian Foundry Hive · Deepwater Compact · Wildsteam Clan · Ascendant Helix · Jawa Trade Moot |

🔑 **The owner ruled `permanentEnemy` for the PLAYER relationship and the spec accepts that
consequence explicitly** — *"this is the Galactic Empire, not a patron you petition."*
⚠️ **Nobody has ruled on the other ~~eleven~~ twelve factions** — corrected 2026-08-20:
the roster is **13** (`infrastructure/state/canon.yml > factions.count` — the 8 `Jawa_*`
we define plus `Empire`, `OutlanderCivil`, `TribeCivil`, `Pirate` and `Mechanoid`), so
**twelve** besides the Empire. *Eleven* counted a dead world. ⚠️ The table above names
only ten of them: it omits `Pirate` (4 settlements) and the hidden `Mechanoid` — the
blanket flag makes the Empire permanently hostile to those two as well. And the side
effect makes a real
design claim: **the Hutt Cartel can never deal with the Empire.** A faction whose own
`ideoDescription` is *"we sell to the farmer, and we sell to the fleet that burned the
farmer"* is, by this flag, forbidden from selling to the fleet.

⭐ **Note the asymmetry with today's other relations ruling.** `ASHKARR_WORLD_DEFINITION.md`
§12.5b says NPC-to-NPC relations have **no FactionDef field** and must be set by the
importer. That is true of *friendly* relations. **`permanentEnemy` is the one exception —
it sets hostility for everybody, from a def, in one boolean.**

### ⇒ DECIDE OWES A RULING. Three options, none of them free:

| option | effect | cost |
|---|---|---|
| **(a) Keep `permanentEnemy true`** | Empire at permanent war with all twelve. Simple, absolute, arguably correct for an occupier | the Hutts, the Helix and the Cartel-adjacent factions can never trade with or serve the Empire — a real loss of texture |
| **(b) Swap to `permanentEnemyToEveryoneExcept`** and list who MAY deal with the Empire | the player stays permanently hostile *if* `PlayerColony` is omitted; chosen factions may collaborate | ⚠️ **must be re-derived carefully** — the list is a whitelist of who is NOT a permanent enemy, and omitting the player is what keeps the ruling intact |
| **(c) Keep the flag, add collaborators over the bridge** | importer sets specific friendly relations after worldgen | ⛔ **does not work** — `PermanentlyHostileTo` is consulted continuously, not once; a bridge-set relation would be overridden |

### 🔴 RULED 2026-08-20 — **OPTION (b). Owner: *"Option (b) please."*** 

⇒ **Set `permanentEnemy false` and author the exception list.** The player stays permanently
hostile by being **omitted**, which is the same outcome by a different mechanism and keeps
the owner's 2026-08-14 ruling exactly intact.

**THE LIST — who the Empire is permitted to tolerate.** Every omission is a deliberate
design statement, so both halves are reasoned:

| ✅ IN the list — not a permanent enemy | why the Empire tolerates them |
|---|---|
| `Jawa_HuttCartel` | ⭐ the whole point of the ruling. Their own `ideoDescription` sells *"to the fleet that burned the farmer"* — the old flag forbade the sentence their faith is built on |
| `Jawa_DeepwaterCompact` | ⭐ their def says they sell to the Imperial tanker fleet **by name**. Same defect, same fix |
| `OutlanderCivil` *(Homestead Defense League)* | an occupier taxes farmers, it does not wage permanent war on them. They are subjects, not enemies |
| `TribeCivil` *(Deep Desert Tribes)* | a nuisance to be suppressed, not a war to be prosecuted. Let ordinary goodwill carry it |
| `Pirate` *(Blackstar Company)* | contractors. A company whose faith is *the Contract* is exactly who an Empire hires |
| `Jawa_IndigenousTribes` *(Trade Moot)* | vermin who fix things, and useful for it — which is also an uncomfortable position for the player's own kin, deliberately |
| `Jawa_Junkers` | they sell scrap to whoever pays |
| `Ancients` | vanilla's own entry. No reason for permanent war with sleepers |
| `Beggars` · `ResearchExpedition` · `GravshipCrew` · `TradersGuild` | vanilla's DLC entries, kept with their `MayRequire` attributes intact |

| ⛔ OMITTED — permanent enemies | why |
|---|---|
| **`PlayerColony`** and **`PlayerTribe`** | 🔴 **THE RULING.** Omitting them is what makes the Empire permanently hostile to the player. *"This is the Galactic Empire, not a patron you petition."* |
| `Jawa_FreeDroidEnclaves` | ⭐ machines that declared themselves people. To a `HumanPrimacy` · `Supremacist` Empire this is not a faction, it is property in revolt |
| `Jawa_GeonosianFoundryHive` | ⭐ **the Empire sterilised their species.** Canon says Geonosians are considered extinct; every one of them here is a refugee from that. Permanent enmity is the only honest setting |
| `Jawa_WildsteamClan` | already specced hostile to the Empire (`FACTION_SPEC.md` relations table). Consistent |
| `Jawa_AscendantHelix` | a religion of engineered improvement, under forced memes `HumanPrimacy` and `Supremacist`. They are an affront by doctrine |

⚠️ **BUILD MUST READ THIS BEFORE PATCHING** — the semantics invert:
`permanentEnemyToEveryoneExcept` is a **whitelist of who is NOT a permanent enemy**. Anything
absent is hostile. So the list must name **every** faction the Empire tolerates, and a
faction added to the world later and forgotten here becomes a permanent enemy silently.
🔑 And `permanentEnemy` **must be set to `false`**, not merely left — `FactionDef.cs:463`
returns on it first and would keep the list dead.

✅ **BUILT AND SHIPPED.** `GalacticEmpire.xml` carries `permanentEnemy false` and the
twelve-entry whitelist exactly as ruled. Nothing here is outstanding.

---

~~**DECIDE's recommendation: (b).**~~ *(ruled above)* It is the only option that preserves the owner's ruling
about the *player* while letting the planet's politics exist. The player is kept hostile by
**omitting `PlayerColony` from the exception list**, which is the same outcome by a
different mechanism.
⚠️ Verify against `FactionDef.cs:463` before building: with `permanentEnemy` set to
`false`, the second branch governs, and it returns hostile for **anything not in the list**
— so the list must name every faction the Empire is permitted to tolerate.

---

## 3. What Royalty gives free — and what the ruling switches off

**The vessel's headline asset is the title/permit/quest ladder, and `permanentEnemy` darkens
all of it by design.** Recorded so nobody re-discovers it as a defect:

| surface | status under our ruling |
|---|---|
| **11 `RoyalTitleDef`s** (Freeholder → Emperor; Freeholder→Count is 65 honour / 5 permit points) | ⛔ **DARK.** A permanent enemy grants no titles |
| **13 `RoyalTitlePermitDef`s** — troop calls, orbital strikes, resource drops, the shuttle | ⛔ **DARK** |
| **~25 quest defs** — bestowing ceremony, decrees, hospitality, `EndGame_RoyalAscent` | ⛔ **DARK** |
| **Prestige/cataphract armour, persona weapons, psychic apparel** | ✅ **still reachable** — craftable or lootable; not faction-gated |
| **`Empire_Fighter_*` / `Empire_Royal_*` pawn kinds** | ✅ still spawn, still fight us. This is what the Empire IS for v1 |

✅ **That is the correct outcome, not a gap.** The Empire is v1's antagonist and its
occupier. A player who cannot petition it is the point.

---

## 4. The actual v1 gap list — re-measured 2026-08-21

⭐ **Re-measured from the shipped files, not from the previous revision of this table.**
Two of the old five gaps are closed, one moved to v2, and **four new ones surfaced** that
the earlier pass never looked for. The column that matters is the last one: the owner's
hand-built world is created **once**, so a gap that bakes has a deadline and a gap that is
read live does not.

| # | gap | owner | bakes into the world? |
|---|---|---|---|
| 1 | ~~`permanentEnemy` blast radius unruled~~ | — | ✅ **CLOSED.** Ruled (b), built, shipped (§2) |
| 2 | ~~No Force/psycast patch~~ | — | 🔴 **v2, by the owner's ruling** — *"No force powers in v1."* Not a v1 gap and must not be re-filed as one. The `lee.theforce.lightsaber` **weapons** are a separate, live thing |
| 3 | ~~Four authored Imperial pawn kinds have no spawn route~~ ✅ **CLOSED 2026-08-21, `IMPERIAL_RAID_ROSTER_1`, commit `2e6d550`.** Both combat groups in `GalacticEmpire.xml` now field `Jawa_Empire_Grunt` 5 / `_Heavy` 2 / `_Specialist` 1.5; the three Outer Rim 200-power specialists stay in the RARE group only. All six `weaponTags` on the four kinds resolve to ≥1 surviving weapon (3/4/6/2/8/1), so none spawns bare-handed. ORIGINAL FINDING: `Jawa_Empire_Grunt` · `_Heavy` · `_Specialist` · `_Leader` (*"Emperor Palpatine"*) exist in `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml:31-110` and are referenced by **nothing else in `src/`**. Both combat groups were replaced with `OuterRim_Imp*` kinds instead, and `defaultFactionDef` does **not** make a kind spawn — only a `pawnGroupMaker` does | **DECIDE**, then BUILD | no — group makers are read at raid time |
| 4 | ~~`fixedLeaderKinds` is still `Empire_Royal_Stellarch`~~ ✅ **CLOSED 2026-08-21, `IMPERIAL_RAID_ROSTER_1`, commit `2e6d550`.** Replaced (not added — the vessel WRITES the field at `Faction_Empire.xml:90`) with `Jawa_Empire_Leader`. ⚠️ Still bakes: the leader pawn is generated at world creation, so this had to land before the owner builds the world. ORIGINAL FINDING: Nothing in `src/` patches the field (zero hits). The Galactic Empire's leader generates as a Royalty stellarch under the title *Emperor* | BUILD | ⚠️ **YES.** The leader pawn is generated at world creation and saved |
| 5 | **Sophian names.** ⚠️ *Downgraded from "the sleeper" — the earlier reading overstated it.* The three Imperial settlements are **hand-named** by `src/RimMandrake/Utils/ashkarr_settle.py:55-59` (Sunspire · Oxalate Watch · Ashgarrison), so `NamerSettlementEmpire` never fires for them, and ordinary Imperial pawns are named **at spawn**, live. **Only the leader pawn's name bakes** — and gap 4 replaces that pawn anyway | BUILD | ⚠️ leader pawn only |
| 6 | **`Jawa_AscendantHelix` wears the Empire's world icon.** `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaAscendantHelix.xml:62-64` borrows `World/WorldObjects/Expanding/Empire` plus both Empire namers. Two factions, one icon, on a map that is frozen | DECIDE → `FACTION_ART_SPEC_1` | ⚠️ the icon is drawn live, the settlement names are not |
| 7 | **26 Imperial `CharacterDef`s bind to nothing.** `src/Jawa/Inhabited/Defs/CastRosters/CastRoster_EMPIRE.xml` ships 26 named Imperials with xenotype, pawnKind and apparel **deliberately absent** (its own header, `:5-11`). Until they bind, the named cast and the raid roster are two unrelated populations | DECIDE spec | depends on how `Inhabited` places them |
| 8 | ~~Vocabulary~~ ✅ **CLOSED 2026-08-21, `IMPERIAL_VOCABULARY_KEYED_1`.** `royalFavorLabel` → `Imperial favor` and `royalFavorIconPath` → the faction badge, both **Replaces** (the vessel writes both, `Faction_Empire.xml:16-17`). Strings: **178** of Royalty's 319 English Keyed entries carry the royal vocabulary — re-counted, the old `~140` was low — and `ImperialVocabulary.xml` overrides **20**, deliberately not the rest: §3's darkening makes ~150 unreachable. 🔴 **The first pass shipped 17 keys and 8 were DEAD, corrected same day** — the whole `MinimumRoyalTitle` / implant-law family. Measured: **0 of 86 FactionDefs declare `royalImplantRules`; 0 ThingDefs and 0 HediffDefs use `CompProperties_RoyalImplant`.** ⭐ **That is row 9 of this very table**, which already said `royalImplantRules` is absent from every shipped FactionDef — so row 9 is not merely a v2 extension point, it is the reason an entire class of Royalty law strings is unreachable, and anything built on Imperial *law* needs row 9 built first. ⚠️ Also corrected: `Empire_Royal_*` is in **no** pawnGroupMaker — it raids nobody. The only titled kind in a group is `Empire_Fighter_Cataphract`, which gap 3 has now removed from both COMBAT groups, so a titled Imperial is met via the untouched **Settlement and Trader** groups. ⚠️ Residual left open: `{TITLE}` splices a **`RoyalTitleDef` label** (freeholder … stellarch), which no Keyed file can reach — renaming those 11 is a DESIGN call | BUILD | no |
| 9 | ⭐ **`royalImplantRules` absent from every shipped FactionDef** — a free extension point if the Empire should ever restrict implants | DECIDE, `[v2]` | no |

⛔ **Two things that LOOK like gaps and are not — do not re-file either:**

- **The Empire's xenotype mix is not wrong.** `VanillaFaction_Xenotypes.xml` gives Baseliner
  0.411 · Echani 0.411 · Chiss 0.137 · Chadra-Fan 0.041, and its header records that it is
  **generated from the owner's own race/faction matrix**. That supersedes the 78/7/6/4/3/2
  mix in `faction_roster_v2.md:711`, which is design-tier prose the matrix overtook. The
  matrix is the source; the roster is not.
- **The Trader and Settlement pawn group makers still field Royalty kinds** — villagers,
  janissaries, cataphracts. That is the spec (`FACTION_SPEC.md:130`, combat groups only)
  and §3's ruling: for v1, `Empire_Fighter_*` spawning and fighting us **is** the Empire.

~~⚠️ One stale sentence outside this file: `About.xml:32` still describes `permanentEnemy` as **true**.~~ ✅ **FIXED 2026-08-21, commit `2e6d550`.** The manifest now says FALSE and names the whitelist that carries the hostility instead.

---

## 5. The two checks that were closed against the wrong def — both now answered

**1. The Force-patch xpath.** ✅ Answered, then **retired**. The xpath shape is proven and
in production (§1) — `li[kindDef="Combat"][commonality="100"]` selects, and no
`PatchOperationFindMod` wrapper is needed because Royalty is always loaded. 🔴 **But the
patch itself is v2**: the owner ruled *"No force powers in v1."* The shape is recorded here
so v2 does not re-derive it; nothing is owed for v1.

**2. Pursuit eligibility — all three pass on vanilla `Empire`:**

| flag | value | how read |
|---|---|---|
| `displayInFactionSelection` | **true** | **absent from the def**, so `FactionDef`'s default applies. Verified the field is not written in `Faction_Empire.xml` |
| `canStageAttacks` | **true** | explicit, line 14 |
| `defName != "PColony"` | **passes** | it is `Empire` |

⇒ **The eligibility rule survives intact. Only the worked example died with the old def.**

---

## 6. Verify

- `grep -c "OuterRim_GalacticEmpire" src/Jawa/**` → the faction def is not the vessel anywhere
- `GalacticEmpire.xml` patches `FactionDef[defName="Empire"]` and nothing else
- `validate_patch.py --defs` clean on the patch
- **this document cites no path under `infrastructure/disposing/`**
- `grep -rn "Jawa_Empire_" src/ | grep -v JawaFactionRoster` → empty proves gap 3
- `grep -rn "fixedLeaderKinds" src/` → empty proves gap 4
