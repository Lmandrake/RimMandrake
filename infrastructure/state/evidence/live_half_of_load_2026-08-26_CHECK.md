# LIVE_HALF_OF_LOAD_1 — first live pass, 2026-08-26, seat CHECK

Full 582-mod list (`ModsConfig.xml`), `game_loaded`, one map, `ticksGame 1174` (paused debug
map). Every reading below is **off a live INSTANCE**, never off a def.

## Answered — the pet-naming block (P2 · P3 · P4 · P5)

**P2 — PASS, 15 for 15.** Fifteen wild animals were brought into the colony
(`jawa/set_pawn_faction … faction: player`) and every one came out with a **corpus name**.
Not one `"<Race> N"`:

```
Qormot        -> Chief Financial Officer, Tauntaun, Chuba
Bolotaur      -> Undocumented Feature, Overstock, Vornskr
IridonianReek -> Threepio, Luggabeast, Ronto
Lothcat       -> Nerf          JRWGeralinura -> Sheik
Uvak          -> Best Offer, Yavin
Manka         -> The Management, Logistics
```

⇒ The Harmony patch is landing. The JIT-inlining failure mode the item braced for did **not**
occur, so the `PawnBioAndNameGenerator.GeneratePawnName` postfix fallback is **not needed**.

**P3 — consistent with 2:1, and NOT proven at this n.** The corpus declares the ratio itself,
so this is checkable against its own labels rather than my taste —
`src/Jawa/Jawa_Patches/Defs/RulePackDefs/Jawa_PetNames.xml`:

```
<li>r_name(p=6)->[loreName]</li>      <- weight 6
<li>r_name(p=3)->[jokeName]</li>      <- weight 3      = exactly 2:1
```

Of the 15 names, **8 are `loreName`, 6 are `jokeName`** — 57/43 against a declared 67/33.
⚠️ At n=14 the 95% interval on 8/14 runs about 0.29–0.82 and contains 0.67, so this is
**consistent with the declared weights and does not confirm them.** Do not quote 57/43 as the
real ratio.

🔑 **One name, `Sheik`, is in NEITHER list** — it is not among the 134 `<li>` in
`Jawa_PetNames.xml`. So our namer is not the only thing naming tamed animals here; something
else supplied that one. Worth knowing before anyone tunes the ratio by editing the corpus.

**P4 — PASS.** Mechanoids are excluded, as required:

```
Mech_Scyther -> "Scyther 1"      Mech_Lancer -> "Lancer 1"
```

Numeric style, no corpus name. (`Mech_Centipede` is not a defName; the tool refused it by
name rather than substituting.)

**P5 — PASS.** A player-set name is never overwritten:

```
taming-assigned : Chuba
player rename   : OWNERSET_KEEPME     (jawa/set_pawn_identity single=…)
re-tamed        : OWNERSET_KEEPME
```

A taming-assigned name also survives the same round trip unchanged (`Tauntaun` → `Tauntaun`).

## Answered — N3 and J6

**N3 — PASS.** Seven xenotypes spawned with `ForcedXenotype` and read back off the instance
with `jawa/pawn_genes`. **None carries both `MinTemp_SmallDecrease` and
`MinTemp_SmallIncrease`:**

| xenotype (read back) | genes | temperature genes on the instance |
|---|---|---|
| RimMandrakeUgnaught | 22 | *(none)* |
| RimMandrakeTwilek | 33 | *(none)* |
| RimMandrakeKelDor | 20 | *(none)* |
| MandrakeJawa | 40 | `MinTemp_SmallDecrease`, `MaxTemp_SmallIncrease` |
| RimMandrakeChiss | 15 | `MinTemp_LargeDecrease`, `MaxTemp_SmallDecrease` |
| RimMandrakeWookiee | 29 | `Furskin`, `MinTemp_SmallDecrease`, `MaxTemp_SmallIncrease` |
| Baseliner | 3 | *(none)* |

⚠️ Seven xenotypes, not all of them. N3 is PASS **over this set**.

**J6 — PASS.** The Jawa instance carries **`AptitudeTerrible_Plants`** and no work-disabling
gene at all. ⇒ `Plants disabled` is `False`; Plants is crippled by aptitude, not disabled.
🔑 That is also the mechanism behind J4/J5 and it predicts them: an aptitude penalty leaves
harvesting, cutting and chopping available, which is exactly what J5 warns is the failure mode.

## UNMEASURED, with the reason — T1 · T2 · N1 · N2

🔴 **There is no bridge tool that reads a pawn's StatDef value.** Checked exhaustively across
all 246 live tools: `jawa/pawn_get` returns identity, apparel, equipment, hediffs, needs,
skills, traits and xenotype and **no stats**; `rimworld/get_map_target_info` returns the same
shape; `jawa/inspect_string` is the inspect pane, which does not carry it. The UI route is shut
too — `rimworld/select_pawn` is **colonist-only** and refused the Jawa, and
`rimworld/open_window_by_type` cannot construct `Dialog_InfoCard` (no public parameterless
constructor).

⇒ `ComfortableTemperatureRange` **cannot be read from outside the game today.** These four rows
are UNMEASURED, not passed. Filed as `PAWN_STAT_READ_HAS_NO_TOOL_1`.

**What the gene evidence does say**, short of the number:

* **T1** Ugnaught, Twilek and KelDor carry **no temperature gene whatsoever** — consistent with
  the expected vanilla −40…+45, and it means any deviation would have to come from elsewhere.
* **T2 / N1** the Jawa instance carries the **Small** tier both ways
  (`MinTemp_SmallDecrease` + `MaxTemp_SmallIncrease`). ⇒ **the LARGE tier has not come back**,
  which is what N1 was really watching for.
* **N2** the Wookiee does carry `Furskin` **stacked on top of** `MinTemp_SmallDecrease`, which
  is the stacking N2 asks about.

🔴 **T2 and N1 contradict each other in the item and one of them must be wrong.**
T2 says Jawa ≈ **−40…+65**; N1 says Jawa PASS = **−50…+55**. The measured genes are one Small
step each way off the −40…+45 baseline, which is N1's number. ⛔ Do not grade T2 against −40…+65
without settling this first — I did not substitute my own criterion, per POLICY.

## Not attempted this pass

J4 · J5 (need a growing zone and two pawns) · G3 · T3 · T5 (need specific biomes) · J7 · J8 ·
N5 · K6/K7 (need raids) · H4 · H5 · H6 (need `Page_SelectStartingSite`, and the game is past it).

---

# Run 2, same session — four more rows, all PASS

Game still `game_loaded`, one map, **paused throughout** (`paused: true` read back before and after
every hostile spawn, per the skill's §4b rule).

## J8 — vanilla mechanoids have NO relations: **PASS**

`jawa/pawn_relations … action: list` on every mechanoid reachable, spawned and raided:

```
Mech_Scyther   relations 0      Mech_Pikeman     relations 0
Mech_Lancer    relations 0      AM_Daggersnout   relations 0  (x2)
```

⇒ No centipede has a social tab. The guard is right.

## J7 — a raid arrives with no NRE naming `Pawn_RelationsTracker`: **PASS**

`jawa/fire_raid {faction: Mechanoid, points: 500, spawnCenter: '5,240', dryRun: false}` — 4 raiders
arrived (`Mech_Pikeman`, `AM_Daggersnout` ×2, `Mech_Militor`, all *Totharth Mechhive*).
`Player.log` diffed from its exact byte offset before the call: **zero new lines matching
`exception|error|NullReference|RelationsTracker`.** Clean.

⚠️ **Scope honesty: this is a MECHANOID raid, not the droid raid J7 names.** `Jawa_FreeDroidEnclaves`
is **Neutral** to the player on this world (read from `jawa/faction_relations_get`: 10 hostile,
14 neutral, and the Enclaves are neutral), so `RaidEnemy` cannot use it. Making them hostile to
test would edit the owner's authored faction relations, which I will not do. The mechanoid raid
exercises the same `Pawn_RelationsTracker` path on relation-less pawns, which is what the NRE was
about — but if J7 must be the Enclaves specifically, it is still owed.

## 🔴 And a finding: `jawa/fire_raid`'s `resolved.faction` echoes the REQUEST, not what raided

```
request faction Jawa_FreeDroidEnclaves (Neutral)
  -> resolved.faction "Jawa_FreeDroidEnclaves", success true
  -> what actually arrived: 5 x Jawa_Blackstar_Grunt, faction "Blackstar Company" (Pirate)

request faction Mechanoid (Hostile)
  -> resolved.faction "Mechanoid"
  -> what actually arrived: Totharth Mechhive        <- matches
```

`IncidentWorker_RaidEnemy` rejects a non-hostile faction and picks its own; the tool reports the
faction you asked for either way and never says it was overridden. ⇒ **A raid test that names a
faction and reads `resolved` has not verified which faction raided.** Filed as
`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`; census the ARRIVALS instead.

## K6/K7 — a Blackstar Leader spawns holding a KotOR weapon, not bare: **PASS**

```
Jawa_Blackstar_Leader  guy762_ionrifle_baragwin  + guy762_LgtBattleArmor, guy762_HelmetMilitary_OldRepublic
Jawa_Blackstar_Leader  guy762_bpistol_onasi      + guy762_LgtBattleArmor, guy762_HelmetLgtBattle_TSL
Jawa_Blackstar_Leader  guy762_bpistol_onasi      + guy762_LgtBattleArmor, guy762_HelmetMilitary
Jawa_Blackstar_Leader  guy762_bpistol_onasi      + guy762_LgtBattleArmor, guy762_HelmetMilitary
Jawa_Blackstar_Heavy   guy762_lgtrepeater_carbine+ guy762_MandoArmor_battle, guy762_MandoHelmet_supercom
Jawa_Blackstar_Heavy   guy762_lgtrepeater_carbine+ guy762_MandoArmor_battle, guy762_MandoHelmet_supercom
```

**6 of 6 armed**, all with KotOR weapons and KotOR/Mandalorian armour. Never bare.
⚙️ Observation, not a failure: 3 of 4 leaders rolled the same `guy762_bpistol_onasi`. The pool is
real but narrow at the leader tier.

## N5 — the Ancient Arsenal boss draws from a real pool: **PASS**, and the `<nomatch>` half works

Six bosses, **six different weapons, zero repeats**:

```
AncientSoldierBoss    JDSA_E-60R_Missile_Launcher      AncientSoldierBossN  Gun_EmpLauncher
AncientSoldierBoss    JDSA_Westar-35_Blaster_Pistol    AncientSoldierBossN  JDSA_DC-15S_Blaster_Rifle
AncientSoldierBoss    AM_StarfireTurret
AncientSoldierBoss    Gun_HellsphereCannon
```

The item flagged the `<nomatch>` branch as "the untested half" because two of three offline warnings
were `<match>` branches with 0 nodes. It fires and it produces a genuinely varied pool.

⚙️ **All six read xenotype `RimMandrakeRakata`** — the deterministic `useFactionXenotypes: false`
route measured under `XENOTYPE_NONFACTION_SPAWN_ROUTES_1`, now confirmed on the boss kinds too.
⚙️ Every boss wears only `Apparel_Pants`. A Hellsphere Cannon in pants. The weapon pool is rich and
the apparel pool at this tier is not — reported, not graded.

## Map state after run 2

9 hostiles standing paused on a scratch debug map (5 Blackstar, 4 Totharth Mechhive) plus the
dwelling built for `TEMPLATE_ENGINE_ACCEPTANCE_1` and ~40 spawned Jawa. Nothing here is kept.
