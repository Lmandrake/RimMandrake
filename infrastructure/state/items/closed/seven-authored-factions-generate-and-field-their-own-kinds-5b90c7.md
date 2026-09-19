# All seven authored factions appear, settle, and raid as themselves — PROVEN

## spec
Carries the live half of **B45 · B46 · B47 · B48 · B49 · B50 · B51** — Hutt
Cartel, Free Droid Enclaves, Wildsteam Clan, Deepwater Compact, Geonosian
Foundry Hive, Ascendant Helix, Junkers. All seven `FactionDef`s are in
`src/Jawa/Jawa_Patches/Defs/FactionDefs/` and deployed.

## verify
done offline against the 578-mod list: **8 files, 0 errors, 1 warning** — the
warning is `iconPath UI/Deities/DeityGeneric`, which is the exact path vanilla
Anomaly's `HoraxCult` uses; the texture lives in a Unity bundle, so no loose-file
checker can see it. Every one of the 45 pawn kinds named across the eight defs
resolves in the live def dump. All four naming/art fields present and non-null on
every faction. `humanlikeFaction` was MISSING on four (Helix · Deepwater ·
Junkers · Wildsteam) and was added — R3 requires it explicitly. No
`combatPower 99999` kind in any `options`, no `minTotalPoints`, no invented
`basicMemberKind`, no `<li>`-shaped `xenotypeChances`.

## criteria
each of the seven appears on the Configure Factions page, generates settlements
at worldgen, and its raids arrive as ITS OWN pawn kinds — not vanilla ones.
🔴 The vanilla-pawn failure is the one to watch: it is what `Inherit="False"` on
`pawnGroupMakers` and on `xenotypeSet` exists to prevent, and it looks like a
working faction until you read the pawn names.
⚠️ Five design values are unresolved and filed to DECIDE as
`five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea`: no
`maxCountAtGameStart` on seven of eight, the Geonosian two-outposts ruling has no
mechanism, the Hutt's `ideoDescription` disagrees with the religions spec, the
Free Droid Enclaves field a biological species against a 0%-biological dossier,
and baseliners generate in five factions. None of them stops this check.

- [x] **appear + settle** — all seven present on a 584-mod quicktest world, with
      settlements: Hutt 5 · Deepwater 4 · Junkers 4 · Helix 3 · Geonosian 2 ·
      FreeDroid 1 · Wildsteam 1.
- [x] **every `Combat` group maker fields only our own kinds**, read post-inheritance and
      post-patch; all kinds resolve. Every authored `FactionDef` carries
      `<pawnGroupMakers Inherit="False">`, so no vanilla list merges in.
- [x] **raids arrive as ITS OWN kinds — 7 of 7, measured live.**

## notes

### 🔴 THE RAID CRITERION, SETTLED 2026-08-31 (FOUNDRY) — seven of seven
Evidence: `infrastructure/state/evidence/seven_faction_raids_2026-08-31_FOUNDRY.md` ·
raw rows `infrastructure/state/evidence/seven_faction_raids_2026-08-31/results.json` · screenshot
`infrastructure/state/evidence/seven_faction_raids_2026-08-31/raid_letters_all_seven.png`. 584 mods (the owner's 585 with `leo.raidprotectionfee`
removed for the round, restored afterwards), fresh quicktest, paused, `ticksGame` 1.
**One firing each, first try**, 3000 points, `ImmediateAttack` / `EdgeWalkIn`, the
target the only authored faction hostile at that moment.

| faction | substituted | pawns | kinds fielded, counted off the map |
|---|---|---|---|
| `Jawa_HuttCartel` | false | 42 | Grunt 25 · Heavy 9 · Specialist 7 |
| `Jawa_FreeDroidEnclaves` | false | 33 | Grunt 19 · Specialist 4 · Heavy 4 · Leader 2 |
| `Jawa_WildsteamClan` | false | 26 | Grunt 15 · Heavy 5 · Specialist 4 |
| `Jawa_DeepwaterCompact` | false | 34 | Grunt 16 · Heavy 10 · Specialist 5 · Leader 2 |
| `Jawa_GeonosianFoundryHive` | false | 56 | Grunt 26 · Heavy 18 · Specialist 7 · Leader 4 |
| `Jawa_AscendantHelix` | false | 21 | Grunt 13 · Heavy 4 · Specialist 3 |
| `Jawa_Junkers` | false | 38 | Heavy 16 · Grunt 12 · Specialist 7 · Leader 3 |

Every humanlike kind is that faction's own `Combat` entry and **nothing else**;
`actual.faction == requested` on all seven; `arrived[]` carried exactly one faction per
raid. The game's own letter stack, in the screenshot, names all seven raids in order — a
channel the tool does not touch.

⭐ **The 18 empty firings of 2026-08-27 were never a defect in these factions.** The
control proves it from the other side: `Pirate`, extorted to zero pawns on every prior
pass, raided for **39 pawns** here with the one mod removed
(`SIX_FACTIONS_NEVER_RAID_1`).

### The animals are global, not ours — `co.uk.epicguru.factionloadout`
One to four extra pawns per raid are ANIMALS under the raiding faction's flag (`AA_*` =
Alpha Animals, plus `Tibidee`, `Dinocrocuta`, `JRWBagaceratops`). **The vanilla `Pirate`
control got three too.** None is in any authored `pawnGroupMaker`, and a grep of ~29,000
XML files across the active mods finds them in no `pawnGroupMakers` context at all.
The injector is **"Rimsential - Total Control: Continued"** (`co.uk.epicguru.factionloadout`,
workshop `3063465133`, active) — a Harmony assembly whose `PawnGroupMakerEdit` machinery
rewrites group makers at generation time and draws from `AllAnimalKindDefs`, with a
`RelationWithExtraPawnChanceFactor` that makes the count vary 0-3. Additive, global, and it
displaces none of our kinds.

### `Jawa_DeepwaterCompact` — both halves of the design hold
`raidsForbidden: true` keeps it out of `PawnGroupMakerUtility.UsableFactions` and so out of
**storyteller** selection. An explicit `parms.faction` never reaches that gate, so a bridge
firing raids anyway — which is what was wanted: **its kinds are proven to field correctly
while the faction stays non-raiding in play.**

### ⚠️ The `Jawa_Empire_Grunt` anomaly: unexplained, and it did not recur
No XML route puts it in any Hutt group maker. The Hutt def's `pawnGroupMakers` carry
`Inherit="False"` (`src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaHuttCartel.xml:210-243`),
the two factions share no abstract parent, no PatchOperation in the repo or the deployed
tree touches the Hutt's group makers, and the only file naming both is
`Patches/GalacticEmpire.xml`, where `Jawa_HuttCartel` sits solely inside `Empire`'s
`permanentEnemyToEveryoneExcept` list. Repo and deployed copies are byte-identical.
**Seven raids here produced no foreign humanlike kind at all.** 🔑 The best remaining
suspect is the same assembly as the animals: `co.uk.epicguru.factionloadout` carries a
`RelationWithExtraPawnChanceFactor` — a chance to add ONE extra pawn beyond the group, which
is exactly the one-in-159 shape and explains why no XML route exists. Not chased further.

### 🔴 The harness defect this round found — it voided the round's own first pass
**`jawa/set_faction_relation` cannot make these factions hostile.** It moves goodwill to
-100, leaves the kind `Neutral`, and says so: *"READ-BACK DOES NOT MATCH THE REQUEST — the
engine overrode it."* A first pass that trusted it had all seven firings silently
substituted (`KAR_OrcClan`, `Pirate`, `DV_OutlanderRoughBuzzer`, `Horrors`,
`GiantAnt_Faction`, `BS_Niflheim`) — a fourth costume for the substitution trap.
**Use `jawa/faction_relations_set faction=<X> other=Player kind=Hostile both=true`**, which
writes both stored records and calls `Notify_RelationKindChanged`, then re-read `hostile`
off `jawa/list_factions` before firing.

### state restored
All `Jawa_*` relations back to `Neutral` / goodwill 0. `ModsConfig.xml` back to 585 active,
md5 `41cda74e837619e200e2a031693f86de`, `modlist_swap --status` → `live currently matches:
FULL`. Map and world are a throwaway quicktest. `harvest_log.py` exit 0 on the 584-mod load.
