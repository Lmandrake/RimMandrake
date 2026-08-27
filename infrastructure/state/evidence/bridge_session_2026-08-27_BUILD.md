# Live bridge session — BUILD, 2026-08-27

Game RUNNING and PAUSED throughout (`curTimeSpeed: Paused`, verified by reading `ticksGame`
twice, delta 0). Map held **one** colonist — a scratch map. 582 mods. Bridge: 291 tools,
**166 `jawa/`**, which is the expected companion surface, so the deploy is intact.

🔴 **Load boundary, established before any test.** `Player.log` holds **0** occurrences of
`required apparel can't be worn together`, so the `apparelRequired Inherit="False"` fix
(`854bee3d`) IS live in this process. Today's `ApparelTags_DeadTagRepair.xml` and the
`combatPower` regeneration are NOT — both were deployed after this game loaded, and defs
parse only at startup.

⚠️ **`Player.log` is useless as an error channel in this process.** It carries
`Reached max messages limit. Stopping logging to avoid spam.` and its mtime is frozen at
07:38. `jawa/drain_log` returned 0 lines. ⇒ "no error in the log" proved nothing all session
and no conclusion here rests on it.

## The seven authored factions

All seven present in the world, all with settlements:

    Jawa_HuttCartel 4 · Jawa_Junkers 4 · Jawa_FreeDroidEnclaves 2 · Jawa_DeepwaterCompact 2
    Jawa_AscendantHelix 2 · Jawa_WildsteamClan 1 · Jawa_GeonosianFoundryHive 1

**Every `Combat` pawnGroupMaker on all eight authored factions fields ONLY our own kinds,
and every kind named resolves in the live def set.** Read from `FactionDef.pawnGroupMakers`
in capture `2026-08-26T14-20-04Z`, which is post-inheritance and post-PatchOperation.
The only foreign entries are `carriers` (pack animals — banthas, dewbacks, muffalo) and the
Free Droid Enclaves' `OuterRim_ProtocolDroid` trader / `OuterRim_KXSecurityDroid` guard.
⇒ **The watched failure — vanilla kinds in a combat group — is absent.**

`jawa/spawn_pawn` for all four Hutt kinds, 2 each, in-faction: **8 spawned, 7 armed and
clothed**, species mix Klatoonian · Nikto · Aqualish · Gamorrean · Falleen · Hutt.

    Jawa_Hutt_Grunt       guy762_ionpistol              apparel 2
    Jawa_Hutt_Grunt       guy762_sonpistol              apparel 2
    Jawa_Hutt_Heavy       guy762_slugrifle_cinnagar     apparel 2
    Jawa_Hutt_Heavy       guy762_lgtrepeater_carbine    apparel 2
    Jawa_Hutt_Specialist  guy762_slugrifle_cinnagar     apparel 3
    Jawa_Hutt_Leader      guy762_ionrifle_baragwin      apparel 7
    Jawa_Hutt_Leader      guy762_ionrifle_baragwin      apparel 8
    Colonist  (baseliner) *** BARE ***                  apparel 4   <- NOT one of ours

## 🔴 The raid criterion is BLOCKED, and it is not hostility

`jawa/fire_raid` on `Jawa_HuttCartel` produced **zero pawns**, twice, under conditions that
leave nothing to blame:

* the faction was genuinely hostile — `hostile: true`, `goodwill: -100`, and it appears in
  `jawa/raid_preview`'s `hostileFactions` with **`canStageAttacks: true`**;
* strategy and arrival were pinned explicitly (`ImmediateAttack` + `EdgeWalkIn`), so the
  worker chose nothing;
* 2000 points; `executed: true`, `note: "Raid fired."`;
* **~4,900 ticks stepped** afterwards, in stages, censusing each time. Nothing arrived.

⭐ **The same map raids fine for other factions**, so the mechanism works: the two
substituted raids below delivered 19 and 12 pawns within 300 ticks.

## Findings that cost time, each measured

**1. `jawa/fire_raid` substitutes the faction and reports the one you asked for.**
`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`, confirmed live twice. Asked `Jawa_HuttCartel` while
it was neutral → `resolved.faction: "Jawa_HuttCartel"`, and **19 `AG_XenohumanPirates`**
arrived. A second attempt delivered **12 `GiantAnt`**. The echoed faction is worthless as
evidence; read the spawned pawns' own faction.

**2. A raid census must STEP TICKS before concluding.** The instant census after firing
showed **0 new pawns** and was wrong — the raid was in flight and landed between +60 and
+300 ticks. A zero taken immediately is indistinguishable from a raid that never fired.

**3. `jawa/set_faction_relation` cannot make a neutral faction hostile.** It writes the
goodwill and never flips the relation kind: `kind Neutral -> Neutral, goodwill 0 -> -100`,
then `success: false` with *"READ-BACK DOES NOT MATCH THE REQUEST — the engine overrode it."*
⭐ **The refusal is the tool working** — it verified its own write and refused to lie.
⛔ But its description claims it *"Exists to unblock aimed raids"*, which it does not do.
✅ **`jawa/faction_relations_set` does it correctly** — `kind Neutral->Hostile (reverse
Neutral->Hostile), goodwill -100->-100`, and `list_factions` then reads `hostile: true`.

**4. `jawa/spawn_pawn` silently substituted a vanilla kind.** Asked for
`Jawa_Hutt_Specialist` ×2, reported *"Spawned 2/2 Jawa_Hutt_Specialist"*, and the census
shows **1 Specialist + 1 vanilla `Colonist`** (baseliner). The `Colonist` is the only bare
pawn of the eight. 🔑 **This is a candidate explanation for the roster's bare-hands rolls**
— a substituted vanilla kind rather than our kind failing to arm — and it is testable.

**5. `pawn_get` nests its payload in `pawns[0]`.** Reading `.equipment` off the top level
returns nothing and prints as *"8 of 8 BARE"*. That is the documented false reading that
once produced "all Jawa spawn bare-handed"; it was hit and corrected inside this session.
Equipment entries are keyed **`def`**, not `defName` — `BRIDGE_ARG_SHAPES_INCONSISTENT_1`
row 3, still live because that fix is in the undeployed DLL.

## Faction names

    fixedName "Blackstar Company"  -> 0 FactionDefs   (namer-based since 5d1c1908)
    fixedName "Galactic Empire"    -> 2 FactionDefs   Empire · OuterRim_GalacticEmpire
    fixedName "Ancients"           -> 2 FactionDefs   Ancients · AncientsHostile

Live `jawa/list_factions`: exactly one faction reads **Blackstar Company** (`Pirate`), and
**two** read **Galactic Empire**.
⭐ **This world can finally test the Blackstar half** — the 2026-08-24 attempt was voided
because only one `PirateBandBase` faction existed. This world carries **four**: `Pirate`
("Blackstar Company"), `PirateYttakin` ("The Ohnaka Gang"), `AG_XenohumanPirates`
("Black Sun"), `DV_PirateKeshig`. **No leak.**

## State restored
Every non-player pawn destroyed; `Jawa_HuttCartel` returned to `kind Neutral, goodwill 0`
(its measured baseline) on both sides; map back to 1 colonist; game left PAUSED.
⛔ Nothing was saved.

---

# The bare-hands cohort, settled — 150 spawns, 2026-08-27

Two runs, both live, both censusing **requested kind vs kind read back** — which no previous
harvest did, and which is the whole reason this was unexplained.

## Run A — 16 kinds × 5, the kinds `roll_arm_harvest_2026-08-24.md` names as bare-rolling

    80 spawned : 76 of our own kinds, 4 SUBSTITUTED to a vanilla kind
    bare among our own kinds        7
    bare among the substituted      4      <- 4 of 4. Every substituted pawn was bare.

Substitution hit only `Jawa_Empire_Heavy`, `Jawa_Empire_Specialist`, `Jawa_Hutt_Grunt` and
`Jawa_Hutt_Leader` — 1 pawn each — and the tool reported `Spawned 5/5` of the requested kind
every time.

## Run B — 7 kinds × 10, every bare pawn's backstory resolved

    70 spawned : 70 of our own kinds, 0 substituted
    bare among our own kinds        5
      of which a violence-disabling backstory   5
      of which UNEXPLAINED                      0

The pacifist set is the **59** `BackstoryDef`s carrying `Violent` in `workDisables`, measured
from the capture rather than hand-listed.

## 🔑 The conclusion, and it removes a defect nobody could find

**Every one of the 11 bare pawns across 150 spawns is explained by exactly two causes:**

| cause | evidence |
|---|---|
| a violence-disabling backstory | 5 of 5 bare-among-ours in run B |
| the kind was silently substituted for a vanilla one | 4 of 4 substituted pawns in run A |

⇒ **There is no third cause, and in particular there is no `weaponMoney` defect.**
`weapon_affordability.py`, corrected the same day to read the emitted XML instead of the
generator's stale shadow table, reports **always arms 49 · sometimes 0 · never 0 · unmeasured
0**. The live evidence now agrees with it.

⭐ **This retires the "8 combat-capable bare pawns" of 2026-08-24.** That harvest recorded the
**requested** kind, so a substituted vanilla `Colonist` — bare, and carrying whatever backstory
a Colonist rolls — was counted as one of our kinds arriving bare with no pacifist excuse. The
rate agrees: 5 bare in 70 is **7.1%**, against that harvest's 21 in 285 = **7.4%**.
⚠️ **Strongly supported, not proven.** Confirming it means re-reading that harvest's raw rows
for a `kindDef` that differs from the one requested; if it did not record the actual kind, the
question is closed by this run instead and cannot be closed by that data at all.

---

## ⚠️ A side effect of the cleanup that I did not anticipate, and the correction

Destroying spawned pawns to keep the map clean **tanked their factions' goodwill**. A final
state check found five authored factions at `hostile: true, goodwill: -75` against a measured
baseline of neutral / 0 — caused by my own tidying, not by any test.

**Restored:** all eight authored factions plus `Empire` and `OutlanderCivil` set back to
`Neutral / 0` on both sides and read back individually. Map: 1 colonist. Game: PAUSED.
Nothing saved.

⚠️ `Jawa_IndigenousTribes`' pre-session goodwill was **never measured** — only the seven were
censused at the start — so it was restored to 0 by assumption rather than to a recorded value.
🔑 **Census every faction you might touch BEFORE the first write, not just the ones under
test.** Killing a faction's pawns is a relation change, and the cheapest instrument that would
have caught it is the one read that was skipped.
