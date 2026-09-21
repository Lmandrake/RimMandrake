# What needs you — BENCH, 2026-09-21 (built while you were away)

Ranked. Each one is a decision only you can make; everything downstream of it is
already built or already measured. **`DO:` is the two-minute act. `DON'T:` is what a
wrong call costs.**

---

## 1. 🔴 Two of your own rulings disagree about `RSW_MossBeetle`

You ruled it **CUT** on 2026-09-19 (`Transient/deeps_flora_fauna_review_2026-09-18.decisions.json`,
owner-approved). Your blanket *"replace all of them"* on the desert sheet, 2026-09-20,
sweeps it straight back in. One day apart, opposite answers, same creature.

- **DO:** say which ruling governs. One word.
- **DON'T:** leaving it costs a render and a def nobody wants, or silently drops a
  creature you kept. Nothing else on the desert wave is blocked by it.

## 2. The desert family: 12 rows are waiting on you, the other 96 are done

RE-MEASURED: **96 of 109 rows are ported.** The def half is finished. Two groups need you:

- **7 Droid Depot droids** (`OuterRim_DUMDroid`, `DestroyerDroid`, `FX7Droid`, `GNKDroid`,
  `MSEDroid`, `MuckrakerDroid`, `SalvageAssistDroid`). `neronix17.outerrim.droiddepot` is
  **not in the active mod list**, so they cannot be read from a running game — porting
  means authoring from the donor's files on disk. **Do they come back at all?**
- **5 vanilla/Biotech rows** (`Rat`, `Plant_Bush`, `Plant_HealrootWild`, `Plant_ShrubLow`,
  `Plant_Ripthorn`). Replacing vanilla is a bigger departure than porting a donor, though
  it is consistent with the desert cards' standing ban on instantly-nameable Earth
  organisms — plain `Rat` is in this set.

- **DO:** two answers — droids yes/no, vanilla rows yes/no.
- **DON'T:** a wrong "yes" on the droids spends ~7 ports on content that may never load.

## 3. ~30 drafted creature names are waiting for your reaction

`NONCANON_BEAST_RENAME_1`'s design is *"agent drafts, you react"*. The drafts exist and
are shipping in defs right now, marked as drafted. A sample:

| donor | drafted name |
|---|---|
| `AA_SandSquid` | **Sandmaw** |
| `AA_Terramorph` | **Ferroclaw** |
| `AA_Cactipine` | **Spinerat** |
| `AA_BoulderMit` | **Stoneback** ("korrum") |
| `Plant_Brambles` | **Thornscrub** ("krenna bramble") |
| `RG_Plant_Dervish` | **Whirlbloom** |
| `AB_DessertTree` | **Sweetbark tree** |

- **DO:** skim the full list and strike the ones you dislike.
- **DON'T:** a drafted name that goes unreacted-to becomes a real name by default —
  that is how a placeholder ships.

## 4. The biome mod split is blocked on 8 questions (was 10)

`design/RimMandrake/biome_mod_architecture.md` §7. **Two are now settled by fact and no
longer need you:** Q5's Scarlands collision is **real** (MEASURED: vanilla Odyssey ships
`Scarlands` labelled *"the Scarlands"*, and our `RUT_Scarlands` carries the identical
label), and Q6b's allowlist-vs-temperature tension was already resolved by a closed item.

The three that change the most work:
- **Q2** — the two deserts and the shrubland have **no ruled names**; `RM_DeepDesert` /
  `RM_ShadowDesert` / `RM_FogShrubland` are the designer's inventions.
- **Q5** — Scarlands collides with vanilla. Keep the name, or pick another?
- **Q3** — `RM_FE_Pyrelands` → `RM_Pyrelands` is **cheapest before the split**. MEASURED:
  14 files, 52 occurrences, 3 live C# strings, and **zero references in the canonical
  save** — so the rename costs nothing today and costs a save later.

- **DO:** Q2, Q3 and Q5 first; the other five can wait.
- **DON'T:** nothing starts until Q2/Q3/Q5 land, and Q3 gets more expensive with time.

## 5. The Titanoslime shipped on defaults — six of them are yours to confirm

Built, compiles clean, deployed, 0 validation errors. It grows as it eats (five life
stages, BodySize 6→40, no Harmony) and engulfs prey whole. Six calls were made on your
behalf because you were away; each ships unless you say otherwise:

1. Finished digestion **is lethal** (absorbed, no corpse, gear regurgitated).
2. Colonists **are** fair prey when it is hungry (follows your `predatorsHuntHumanlikes` setting).
3. Prey gate **≤ 0.5 × its own BodySize** — so *"nearly any size"* is earned by growing.
4. Growth **is reversible** — it never becomes permanently huge.
5. **Resident only**, no incident letter; spawns at stages 1–3.
6. The five stage labels **stay** on the inspect string.

- **DO:** overturn any you dislike; silence ships all six.
- **DON'T:** #1 and #3 are the ones that change how it feels to meet one.

## 6. 24 renders are waiting for your eye

The artpipe daemon has been running the desert wave since 09:41 on 2026-09-20 — 24
PASS-validated renders are sitting unreviewed, ~52 more still rendering. A review sheet
is being built now. 🔑 The Rot wave found **4 of 61** renders bad, and only an eye caught
them.

- **DO:** one pass through the sheet when it lands.
- **DON'T:** bad art wired into a def is far more expensive to unpick than to reject.

---

## Not a decision — just worth seeing

🔑 **The planet has no visual hierarchy at all.** MEASURED: all **71** world features on
the canonical save sit at `maxDrawSizeInTiles = 10`, the bottom of the engine's size
curve, so every label draws at the minimum. The 1,692-tile Dune Sea is lettered exactly
as large as Notch. Your Fall Line directive is being applied to one region tonight and a
screenshot is coming — but whether the whole planet gets a hierarchy pass is a separate
call, and it is yours.
