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
