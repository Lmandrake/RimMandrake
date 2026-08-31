# All seven authored factions raid, as themselves, with their own kinds

**Live, 2026-08-31, FOUNDRY.** RimWorld 1.6, **584 mods** — the owner's 585 with
`leo.raidprotectionfee` (Raid Protection Fee) removed for this round only, which is the
one variable this run changed. Fresh quicktest world (`Map_0`, paused, `ticksGame` 1),
bridge up after 942 s, **427 tools / 302 `jawa/`**. Raw rows:
`infrastructure/state/evidence/seven_faction_raids_2026-08-31/results.json`; the script that produced them,
`infrastructure/state/evidence/seven_faction_raids_2026-08-31/prove_seven_raids.py`.

Every row below is **one firing, first try**, `points 3000`,
`strategy ImmediateAttack`, `arrivalMode EdgeWalkIn`, with the target the **only**
authored faction hostile at that moment and every other `Jawa_*` returned to
`Neutral` / goodwill 0 first.

| faction | hostile | substituted | pawns | kinds fielded (counted off the map) |
|---|---|---|---|---|
| `Jawa_HuttCartel` | ✅ | **false** | 42 | Grunt 25 · Heavy 9 · Specialist 7 · *AA_Ravager 1* |
| `Jawa_FreeDroidEnclaves` | ✅ | **false** | 33 | Grunt 19 · Specialist 4 · Heavy 4 · Leader 2 · *4 animals* |
| `Jawa_WildsteamClan` | ✅ | **false** | 26 | Grunt 15 · Heavy 5 · Specialist 4 · *2 animals* |
| `Jawa_DeepwaterCompact` | ✅ | **false** | 34 | Grunt 16 · Heavy 10 · Specialist 5 · Leader 2 · *AA_Gigantelope 1* |
| `Jawa_GeonosianFoundryHive` | ✅ | **false** | 56 | Grunt 26 · Heavy 18 · Specialist 7 · Leader 4 · *AA_RayHound 1* |
| `Jawa_AscendantHelix` | ✅ | **false** | 21 | Grunt 13 · Heavy 4 · Specialist 3 · *AA_Wildpawn 1* |
| `Jawa_Junkers` | ✅ | **false** | 38 | Heavy 16 · Grunt 12 · Specialist 7 · Leader 3 — **nothing else** |

Every humanlike kind in every row is that faction's own `Combat` `pawnGroupMaker` entry
and nothing else. `actual.faction == requested` on all seven; `arrived[]` carried exactly
one faction each, so nothing arrived under another flag.

**Independent channel:** the letter stack in
`infrastructure/state/evidence/seven_faction_raids_2026-08-31/raid_letters_all_seven.png` reads, bottom-up,
*Raid: Hutt Cartel · Raid: Free Droid Enclaves · Raid: Wildsteam Clan · Raid: Deepwater
Compact · Raid: Geonosian Foundry Hive · Raid: Ascendant Helix · Raid: The Junkers* —
seven letters the game wrote itself, from a channel the tool does not touch.

## The control that makes the round mean something
`Pirate` (Blackstar Company) — **extorted on every prior pass, zero pawns every time** —
raided normally here: **39 pawns**, `windowsOpened []`, `blockedByDialog false`. One mod
removed, and the faction that could never raid raids. That is the causal closure of
`SIX_FACTIONS_NEVER_RAID_1` from the other direction.

## The animals are global, and not ours
One to four extra pawns per raid are ANIMALS carrying the raiding faction's flag
(`AA_*` = Alpha Animals, plus `Tibidee`, `Dinocrocuta`, `JRWBagaceratops`). **The vanilla
`Pirate` control got three of them too**, and none of these appears in any authored
`pawnGroupMaker` (all eight authored FactionDefs use `<pawnGroupMakers Inherit="False">`).
⇒ a mod on this stack adds beasts to every raid on the planet. Not a defect in the
authored factions, and not in scope here.

## `Jawa_DeepwaterCompact` raids when told to, and still will not raid in play
Its def carries `raidsForbidden: true`, which keeps it out of
`PawnGroupMakerUtility.UsableFactions` and therefore out of **storyteller** selection.
An explicit `parms.faction` never reaches that gate, so a bridge firing raids anyway —
which is exactly what was wanted: **its kinds are proven to field correctly while the
faction stays non-raiding in real play.** Both halves of the design hold.

## 🔴 The harness defect this run found, and it voided the run's own first pass
**`jawa/set_faction_relation` cannot make these factions hostile.** It moves goodwill to
-100 and leaves the kind at `Neutral`, and says so:

    "Jawa_HuttCartel ('Hutt Cartel'): kind Neutral -> Neutral, goodwill 0 -> -100.
     ⚠️ READ-BACK DOES NOT MATCH THE REQUEST — the engine overrode it."

The first pass of this script used it, believed `hostile` without checking, and every one
of the seven firings was silently substituted to a random hostile
(`KAR_OrcClan`, `Pirate`, `DV_OutlanderRoughBuzzer`, `Horrors`, `GiantAnt_Faction`,
`BS_Niflheim`) — a fourth costume for the substitution trap.
**Use `jawa/faction_relations_set faction=<X> other=Player kind=Hostile both=true`**, which
writes both stored records and calls `Notify_RelationKindChanged`. It reported
`success: true` and `hostile: true` on all seven. ⇒ **read the setter's own `success`, and
re-read `hostile` off `jawa/list_factions`, before any firing.** The script now refuses to
fire at a faction it could not make hostile.

## The `Jawa_Empire_Grunt` anomaly: still unexplained, and it did not recur
No XML route puts `Jawa_Empire_Grunt` in any Hutt group maker — the Hutt def's
`pawnGroupMakers` carry `Inherit="False"` (`src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaHuttCartel.xml:210-243`),
the two factions share no abstract parent, no PatchOperation in the repo or the deployed
tree touches the Hutt's group makers, and the only file naming both is
`Patches/GalacticEmpire.xml`, where `Jawa_HuttCartel` appears solely inside `Empire`'s
`permanentEnemyToEveryoneExcept` list. Repo and deployed copies are byte-identical.
**Seven raids this session produced no foreign humanlike kind at all.** Recorded, not
chased; the same one-extra-pawn shape as the global animal injection is the obvious next
suspect if it ever recurs.

## State restored
All `Jawa_*` relations returned to `Neutral` / goodwill 0. The map, world and save are a
throwaway quicktest. `ModsConfig.xml` restored to the owner's 585 (see the load-round note
in `FIRE_RAID_REPORTS_MODAL_1`). `harvest_log.py` exit 0 on this load.
