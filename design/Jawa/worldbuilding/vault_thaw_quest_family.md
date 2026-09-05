<!-- status: built-offline, owner review owed -->
# The vault thaw quest family — what makes the six Forsaken vaults play

> **Scope.** `VAULT_THAW_QUEST_FAMILY_1`. The six vault layouts exist
> (`VAULT_DUNGEON_BUILD_1`, `src/RimUtinni/VaultDungeons/`); nothing offered,
> gated or resolved a visit. This doc is the design AND the build record for
> the `QuestScriptDef` family that does — built 2026-09-05, FOUNDRY, offline
> only, no bridge, no deploy. Every mechanical claim below was read in the
> decompiled 1.6 source or vanilla Data before it was written; the provenance
> list is the header of `src/RimUtinni/VaultDungeons/Source/gen_vault_quests.py`.
>
> Ruled sources, not re-derived: `dungeons_arc_spec.md` §2.3 (the thaw-gate
> model), §3 (sites, grammar, payoff ladder); `canon.yml`
> `rakata.woken_brutality`, `rakata.reclamation`, `helix_lineage`,
> `rust_cathedral`, `narrator`, `cradle_memory`; `reconciled_lore/03_deep_history.md`;
> `antiquities_design.md` (CARTOGRAPHY reveals vaults; the frozen vault requires
> VOICE); `ASSAILANT_DUNGEON_BUILD_1` (frozen-first-impact).

## 0. Ruled / built / proposed — read this table before anything else

| | |
|---|---|
| **RULED, restated** | six sites and tiles; three types; concentric grammar; wake/loot/leave ladder and its verbatim line; the Reclamation (owner 2026-09-04, card G4) and the two scenes after it; the Helix flip; thaw = "bring an old power core", power core = vanilla `AIPersonaCore`; QuestNode + map signal, no custom C# unless a node is genuinely missing; 325×325; `RUT_` tier; CARTOGRAPHY reveals vault sites, V6 requires VOICE |
| **BUILT this pass (XML, validated offline)** | six vault quests on FIXED tiles; site content through `SitePartDef` → `GenStepDef` → KCSG; the V6 thaw as a real vanilla mechanism (a dead power plant fed one `AIPersonaCore`); V6's three branches wired to named signals; the Claim-Conflict quest; the Reclamation quest with the Helix flip and both scenes; eight `HistoryEventDef`s as the memory substrate; a GiveQuest incident per quest for deterministic firing |
| **PROPOSED by this pass — not canon, flagged for the owner** | §2.2 "the woken who woke others" reading of who walks in the Claim-Conflict; §4 what "dominated-neutral" can and cannot mean without C#; §5 the two C# signal senders and the roster, as the smallest honest gap list; the Reclamation's late-ness expressed as a 45-day chain delay rather than a VOICE gate |

## 1. Shape — one family, three tiers

```
CARTOGRAPHY read ──► RUT_VaultThaw_V1..V5   (natural pool, research-gated)
CARTOGRAPHY+VOICE ─► RUT_VaultThaw_V6_Umbra (the scene)
        wake ──────► RUT_VaultClaimConflict (chained, autoAccept, 8 days later)
        refused ───► RUT_Reclamation        (chained, autoAccept, 45 days later)
```

Eight `QuestScriptDef`s, one file, generated: `Defs/QuestScriptDefs/RUT_VaultThaw.xml`.

### 1.1 Reveal — how a vault becomes a place on the map

The concept doc asked whether vault discoveries ride the cradle-memory reveal
channel like the Assailant dungeon ("one reveal economy, two dungeon
families"). The newer ruling (owner 2026-09-04, the Doctrine of the
Unwritten) puts the vault **coordinates in the urns**, read back at
Antiquities CARTOGRAPHY. The family honours both without inventing a third:

- **The gate is the reading.** `QuestNode_RequirementsToAcceptResearch
  reserach=RUT_Antiq_Cartography` (field spelled that way in vanilla). Its
  `TestRunInt` returns false until the project is finished, so the quest is
  not merely unacceptable before CARTOGRAPHY — it is never generated.
  V6 adds `RUT_Antiq_Voice` (antiquities §7: "the one vault where the payoff
  is a conversation… should require VOICE").
- **The voice is the ship.** Every offer/accept letter is the Narrator: the
  reading gives the place, *the ship gives the name it has not said in an
  age*. Cradle-register only where canon allows (one word "in the
  Cradle-register" for V6; "Kolyska" is never spoken to the player here).
- **Firing route: the natural pool** (`rootSelectionWeight 1.0`) behind the
  gate, plus a named `IncidentDef` per quest (`RUT_GiveQuest_VaultThaw_V#`,
  `baseChance 0`) so a dev-mode or bridge trigger exists — never "wait for
  the storyteller".
- **Once at a time, and re-remembered slowly.** `QuestNode_QuestUnique` blocks
  a second ongoing copy; `minRefireDays 120` (V6: 200). A once-EVER gate is
  not expressible in XML: `QuestNode_GetSameQuestsCount` reads
  `QuestGen.Root`, which is null during `TestRun` — verified, so it cannot
  gate. A vault can therefore be re-offered after its site is gone; for ①
  that reads as the self-replicating Arsenal restocking (canon), for V6 the
  C# sender in §5 is also the right place to refuse a second offer.

### 1.2 The site — a fixed tile, vanilla site machinery, KCSG content

No worldgen, no random tile. `QuestNode_Set siteTile=<tile>` is a literal;
`QuestNode_GenerateSite.tile` is `SlateRef<PlanetTile>` and a string literal
resolves through `ParseHelper`'s registered `PlanetTile` parser to the
**surface layer** (`PlanetTile(int)`). The rest is the exact
`GetDefaultSitePartsParams → Util_GenerateSite → SpawnWorldObjects` sequence
`Jawa_TheClaim.xml` already ships.

| type | `SitePartDef` | site faction | why |
|---|---|---|---|
| ① held | `RUT_VaultSite_Type1` | `Mechanoid` (= the Forgotten Arsenal, relabelled) | KCSG spawns the garrison as the site's faction; `AllEnemiesDefeated` is a real signal here |
| ② breached | `RUT_VaultSite_Type2` | none | the vault belongs to nobody; guardians are factionless by symbol |
| ③ frozen | `RUT_VaultSite_Type3` | `AncientsHostile` | KCSG fills caskets with `map.ParentFaction`; `Building_AncientCryptosleepCasket` gives AncientsHostile contents the assault lord — the wake IS vanilla |

`SiteMaker.MakeSite` never calls `SitePartDef.FactionCanOwn`, so a hidden
faction can own a quest site. Each `SitePartDef` carries `minMapSize
(325,1,325)` (the ruling), `wantsThreatPoints false` (the layout is the
threat), and a `GenStepDef` with `linkWithSite` running
`KCSG.GenStep_CustomStructureGen` on the type's template — the vanilla
`ItemStash` shape, with KCSG where `GenStep_ItemStash` would be.

⚠️ **This is the one deliberate divergence from "authored in place via
`jawa/kcsg_place`".** A vault must exist as a *quest target* to have signals
(`site.MapGenerated`, `site.MapRemoved`, `site.AllEnemiesDefeated`), and a
Site is the only vanilla world object a quest can generate at a fixed tile.
The tile is still fixed and still the ruled one; the landmark on it is still
the hand-authored one; the map is generated on arrival from the same KCSG
template the bridge pass would have placed. The six `world_commit` placements
in §3.9 are therefore **not needed for the vault CONTENT** — they remain
needed only for V5's landmark and any per-site hand-finish.

### 1.3 Outcomes — what vanilla can see

`site.MapGenerated` → arrival letter. `site.MapRemoved` (armed only after
`MapGenerated`) → "you went and came back" → `RUT_VaultVisited` → Success.
Type ① adds `site.AllEnemiesDefeated` → "the garrison is silent" →
`RUT_VaultGarrisonBroken`. Type ② has no loot ladder by ruling; its
completion letter is the *route to ③ knowledge* — the deep-Umbra direction.
There is no expiry after acceptance and no failure state: a vault is a place,
and the only loss is the walk.

## 2. V6 — the thaw, and the three-way scene

### 2.1 Thaw = the Assailant model, made of vanilla comps

The Assailant complex is "frozen and undetected, woken only by the players'
own power core" (ruled). V6 is its sibling one tile away and gets the same
gesture with the same item:

- **`RUT_VaultHeart`** (`Defs/ThingDefs_Buildings/`): a dead `CompPowerPlant`
  (−1000 W as output) whose `CompRefuelable` accepts exactly one
  `AIPersonaCore` — `fuelConsumptionRate 0`, `atomicFueling`, `canEjectFuel
  false` (one-way, as the ruling says), auto-refuel OFF by default so feeding
  it is an order, never an accidental haul. "Bring the old core to the
  socket" is literally the vanilla refuel job. Spawned factionless
  (`RUT_Symbol_VaultHeart`, `spawnPartOfFaction false`) because
  `RefuelWorkGiverUtility.CanRefuel` requires the same faction: the crew
  **claims** it first, which `Thing.FactionPreventsClaimingOrAdopting`
  allows while the sleepers are still *in* their caskets (only spawned pawns
  count) and refuses once they are up. Power first, then wake — the ordering
  is the design.
- **What the thaw does.** The type-③ template now has *no live hostile on
  arrival* (the two `Mech_Centurion` are gone): four `Turret_MiniTurret`
  (80 W, `CompPowerTrader`) hug the core wall, and KCSG lays conduit under
  that wall (`spawnConduits true`). Dark and harmless until the heart is fed;
  then the silent ring stops being silent, and the caskets sit in a lit hall.
  "Dark, frost-locked, no power" (§3.3) is now a state the game holds, not a
  description.
- **The caskets.** `RUT_Symbol_RakataCasket` = `AncientCryptosleepCasket` with
  `containPawnKindAnyOf AncientSoldier` (already Rakata-xenotype by
  `AncientsAreRakata.xml`), four of them, spaced so every interaction cell
  is free. **This replaces a real defect**: the shipped
  `RUT_Symbol_RakataSleeper` named `RUT_Jawa_RakataVaultSchooled`, which is a
  `BackstoryDef`, as a `pawnKindDef` — KCSG would have resolved it to null
  and spawned nothing, silently.

### 2.2 Wake / loot / leave

| branch | trigger | what happens (built) |
|---|---|---|
| **WAKE** | `site.RUT_SleepersWoken` — first casket opened | the ruled line, verbatim, as a `ThreatBig` letter; `RUT_VaultSleepersWoken`; the sleepers fight (vanilla assault lord, `canTimeoutOrFlee`) ; when the crew leaves the map, an 8-day delay, then `RUT_GiveQuest_VaultClaimConflict` fires and the vault quest ends |
| **LOOT** | `site.RUT_SleepersLooted` — a casket broken with sleepers in it | "kills them, plainly": a `NegativeEvent` letter that says so; `RUT_VaultSleepersKilled`; the quest ends |
| **LEAVE** | `site.MapRemoved` with neither touch (disarmed by either) | "the Narrator remembers": the letter says the ship will remember you did not decide for them; `RUT_VaultLeftSleeping`; Success |

**The C# gap, stated plainly.** No vanilla `QuestPart` sends a signal when a
casket is opened or broken, and `Site.AllEnemiesDefeated` fires once per map
the moment no hostile active threat remains — on a type-③ vault that is the
moment of arrival, so it cannot stand in. The wake and loot branches are
fully wired and inert; **only LEAVE can fire today.** This is exactly the
"if a node is genuinely missing, that is a finding to file" case from the
2026-09-01 ruling; the finding is §5.

Who walks in the Claim-Conflict if the crew killed every sleeper they woke?
**Proposal, mine:** canon says every garrison's children slept and "each
learned only its fragment" — sleepers exist in every ancient ruin's caskets
on this world, not only in V6. The claim is carried by *the ones you woke,
and the ones they woke on the way*. The letter says so. If the owner wants
the claim to follow only survivors, the sender in §5 adds one signal
(`RUT_WokenDeparted`) and one `inSignalEnable` changes.

## 3. The ship-claim thread — `RUT_VaultClaimConflict`

The ruled payoff says waking "opens a claim-conflict thread over the ship
itself"; `plot_mechanisms_wave.md` proposed "demand, refusal, departure with
a grudge; feeds the Reclamation". Built as one `isRootSpecial`, `autoAccept`
quest fired only by its incident:

1. **Demand** — the accept letter, in the woken's register through the
   Narrator: the vessel is Rakata property, the short ones a cargo error.
   *There is no version of this in which you hand her over* — the refusal is
   the player's only line, and the game says so rather than faking a choice.
2. **Arrival** — 2 days, then `QuestNode_Raid`: faction `AncientsHostile`
   (a forced `RaidEnemy` with `parms.faction` set ignores `raidsForbidden`),
   `raidPawnKind AncientSoldier`, walk-in, `canTimeoutOrFlee true`, points
   floored at 1200. Tag `woken`.
3. **Departure with a grudge** — `woken.AllEnemiesDefeated` (the lord's own
   signal: dead *or* gone) → "the first hearing" letter →
   `RUT_WokenClaimRefused` → a 45-day delay → `RUT_GiveQuest_Reclamation` →
   Success. The quest card stays open through the wait and says why
   ("The claim is not settled").

Goodwill is not touched: `AncientsHostile` is `permanentEnemy`, and the grudge
lives in the history event and the chain, not in a number.

## 4. The Reclamation — `RUT_Reclamation`

"Reclamation" is **not** a gap: it was ruled 2026-09-04 (canon.yml
`rakata.reclamation`, `09_arcs_dungeons_quests.md` §2b). Built, one quest:

1. Accept letter (the Narrator: *all of them*, and *the Helix boons stop
   today — you could have seen that coming*).
2. **The Helix flip** — `QuestNode_ChangeFactionGoodwill
   faction=Jawa_AscendantHelix change=−100 ensureHostile=true`, reason
   `RUT_HelixSidedWithTheWoken` (the line on the faction tab). This ends the
   Ascendant Ladder boon economy by the only lever vanilla has.
3. **Two waves** — the woken (`AncientsHostile`, points floored at 2500,
   `canTimeoutOrFlee false`: a concentrated effort), then the Helix a day and
   a half behind (their own group makers; *local collaboration*, not one
   column).
4. **Survived** — `QuestNode_AllSignals` on both `AllEnemiesDefeated` → the
   ruled Helix true-heart line, verbatim, and *dominated* named as the word →
   `RUT_ReclamationSurvived` → one day → the Cathedral's ruled refusal line →
   Success. Colony map lost → Fail.

**What "permanently neutral / dominated" cannot be in XML, and is proposed
instead:** `AncientsHostile` is a permanent enemy and future casket contents
are assigned by vanilla; nothing in XML can make *later* woken sleepers
neutral. The honest options for the owner: (a) a C# post-Reclamation flag the
casket sender in §5 reads — contents of any casket opened after
`RUT_ReclamationSurvived` spawn as `Ancients` (the neutral hidden faction that
already exists) instead of `AncientsHostile`; or (b) accept that "dominated"
means *no further claim quests* (already true: the chain has no re-entry) and
leave individual sleepers as they are. This pass recommends (a) and builds
neither.

**Late-ness.** The ruling sequences the Reclamation after the VOICE Call-Out
"seems to settle it". A research gate on a chained quest would silently drop
it if VOICE were unfinished when the delay expired (`IncidentWorker_GiveQuest`
generates directly, but the quest's own gate would refuse at generation), so
late-ness is the 45-day chain delay instead. Tunable; flagged.

## 5. Findings to file — the smallest honest C# list

None of these is a licence to write a DLL ahead of the owner; each is a
node/comp vanilla does not have, named so the build is a decision, not a
discovery.

| # | what | why vanilla can't | smallest shape |
|---|---|---|---|
| 1 | **Casket signal sender** | no `QuestPart` observes `Building_AncientCryptosleepCasket` open/destroy; `Site.AllEnemiesDefeated` is spent on arrival | a `MapComponent` or Harmony postfix on `EjectContents`/`Destroy` that calls `QuestUtility.SendQuestTargetSignals(map.Parent.questTags, "RUT_SleepersWoken" / "RUT_SleepersLooted")` — the quest already listens for exactly those; loot-kills-them is the same patch (destroy contents on a damage-eject instead of waking them) |
| 2 | **"Everyone you ever woke"** | no engine memory of pawns across maps; a site's pawns die with its map | `GameComponent_OldFriends` from `plot_mechanisms_wave.md` Part 1 with the `WOKEN_ANCIENT` role; until it exists the Reclamation's first wave is a fresh `AncientSoldier` group, which the letters are written to survive |
| 3 | **Dominated-neutral after the Reclamation** | `AncientsHostile` is `permanentEnemy`; casket contents' faction is vanilla's | §4 option (a), one flag read by #1 |
| 4 | **Once-ever offer** | `QuestGen.Root` is null in `TestRun` | #1 refuses a second V6 offer once any touch is recorded; ①/② re-offers are canon-consistent as-is |

Not filed, noted: type ①'s `Mech_Lancer`/`Mech_Centurion` cells rely on
KCSG's auto-symbol table, where those names are BOTH a `ThingDef` and a
`PawnKindDef`; which wins is unverified. Type ②'s `AA_GreenGoo`/`GR_Boomsnake`
spawn factionless and without a lord, so they may read as wildlife rather
than guardians. Both are `VAULT_DUNGEON_BUILD_1`'s template files, out of
this pass's scope, and both are quicktest questions.

## 6. Alignment with `ASSAILANT_DUNGEON_BUILD_1`

Same player-facing shape on purpose: inert on arrival → the crew's own
delivered `AIPersonaCore` is the irreversible step inward → the place wakes
→ the reveal is *in* what wakes. Same item, same fiction ("only an archotech
core runs hot enough"), same one-way rule, and the V6 heart is a reusable
answer to the Assailant complex's own still-held "thaw-trigger concrete
implementation": a refuelable plant needs no custom node. Divergences, all
deliberate: the vaults use the natural pool behind a research gate where the
Assailant chain is trust-gated through the Cathedral; V6's thaw wakes
*defences and light*, not guardians (the guardians here are the sleepers,
and waking them is the player's second, separate act); and the vaults are
Sites generated at fixed tiles rather than bridge-placed structures (§1.2).

## 7. What is left for a human / live pass

- Quicktest each `SitePartDef` (dev → Incidents → `RUT_GiveQuest_VaultThaw_V#`
  with CARTOGRAPHY/VOICE dev-finished): map is 325×325, the template is at
  centre, conduits carry power from a fed heart to the turrets, caskets open
  and the sleepers wake hostile and Rakata-skinned, the claim raid walks in
  eight days later, the Reclamation follows the refusal.
- Owner: the §0 PROPOSED row; the dialogue register on every letter (all
  authored here in the Narrator voice, none owner-ruled except the two
  verbatim lines); whether the V6 heart is also the Assailant's answer.
- V5's landmark and any per-site hand-finish remain held per §3.9.
