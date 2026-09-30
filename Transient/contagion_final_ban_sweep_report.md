# CONTAGION_FINAL_BAN_SWEEP_1 — verification report

Status: DONE

## 1. Roster confirmation (`RM_Contagion.xml` wildAnimals / wildPlants)

Parsed as XML **elements** (node name = def, text = commonality — never `<li>`),
per the custom `BiomeAnimalRecord`/`BiomePlantRecord` loader.

- `wildAnimals`: **21 rows**, 100% `RM_`-owned. Zero `AA_`/`AB_`/`AG_`/`GR_` donor
  rows. Zero `RUT_Sytheclaw`.
- `wildPlants`: **13 rows** — 12 `RM_`-owned + `RUT_RustPuff` (Rot kit's own
  content, correctly kept per the item text "`RUT_RustPuff` stays — it's already
  ours" — **but see the fix below, its defName had drifted**).
- **Every row resolves to a real `defName` on disk** — confirmed by cross-parsing
  every `*.xml` under `src/` for `<defName>`. One row did NOT resolve until fixed
  (below).
- Checked every UtinniPatches `PatchOperation`'s own `xpath` for one targeting
  `RM_Contagion`: **none exists.** `grep -rl "RM_Contagion" src/RimUtinni/` finds
  nothing; the roster is entirely inline, no patches add rows to it.

**FIX MADE:** `RM_Contagion.xml`'s wildPlants carried
`<RUT_RustPuff MayRequire="mandrake.rut.rotsporekit">0.3</RUT_RustPuff>`. Neither
the defName nor the packageId exists anywhere in the repo — `RUT_RustPuff` was
renamed to `RM_RustPuff` and its mod absorbed into `mandrake.rm.therot` on
2026-09-24 (`THEROT_RM_MOD_BUILD_1`, `df79753dc`), a day **before** `RM_Contagion`
was built by copying the frozen twin verbatim (2026-09-25), so the row was dead
on arrival — it could never resolve and RustPuff could never spawn in this biome,
regardless of The Rot's load state. Fixed to
`<RM_RustPuff MayRequire="mandrake.rm.therot">0.3</RM_RustPuff>` in
`RM_Contagion.xml`, with the header comment and `About.xml`'s stale "pending
absorption" disclosure corrected to match (that absorption is done). Re-parsed
after the fix: all 34 rows (21 animals + 13 plants) resolve; zero bad prefixes.

**FINDING, not fixed (wider than this mod — see §5):** the same stale
`RUT_RustPuff`/`mandrake.rut.rotsporekit` reference (and 18 other RotSporeKit-tier
names: `RUT_Nogtyl`, `RUT_Dewshrooms`, `RUT_FruitingBodies`, `RUT_Nuitae`,
`RUT_Wrinklecap`, `RUT_Arpeau`, `RUT_FlakespireFungus`, `RUT_Pusmelon`,
`RUT_Sagecrust`, `RUT_BleedingTooth`, `RUT_Brightbell`, `RUT_CrimsonCap`,
`RUT_GreyLady`, `RUT_Shinecap`, `RUT_VioletWimple`, `RUT_MortalMorelPlant`,
`RUT_Skulltop`, `RUT_BlastpodShroom`) is still live in `RUT_Contagion.xml` (the
frozen twin), `RUT_Miasma.xml`, `RUT_TheForge.xml`, `RUT_TheRot.xml` and
`RUT_WeepingStones.xml` under `src/RimUtinni/UtinniPatches/` — **confirmed by a
currently-FAILING pre-existing selftest**,
`src/RimMandrake/Utils/selftest_deployed_biome_refs.py` (21 unresolved deployed
references, none of them `RM_Contagion.xml`). This predates my change (it checks
files I never touched) and is out of this item's scope (other mods' rosters).

## 2. Ban sweep — every def this item's four waves produced

### 2a. Fauna (22 species, `RM_ContagionFauna.xml`)

| species | ban 2 (UV-shy/armored) | ban 3 (finished natives) | ban 4 (no edible/no yield) |
|---|---|---|---|
| BloodyMess, Gawpsack, Blisterfloat, Scorchpod*, Bloodlurk, Meltgut, Sparkleech+Grub, Scaldhide*, Doublemaw, Gnashling, ContagionIkee, Shambles, Peeper, Eyestinger, Fleshsop (16 ports) | PASS — architecture-level (see below): every wildAnimals race is in `RM_ContagionSky.NativesOf`; Scorchpod is the ruled leaker (damage, no dive), Scaldhide the ruled armored (no damage); all 14 others dive | PASS — pre-existing ported natives, the ruled table itself | PASS — MeatAmount 0, LeatherAmount 0 on all 16 (MEASURED) |
| Skinflap, Gorekite, Danglemaw, Crispling*, Sloshbelly (5 new, cast bible §3) | PASS — same mechanism; Crispling is the ruled second armored native | PASS — all 5 carry `DeathActionProperties_Vanish` (goo-corpse: dissolve at death, "recurring drafts... not settled species," per cast bible §3/§7) — MEASURED | PASS — MeatAmount 0, LeatherAmount 0 (MEASURED) |
| **RM_Ogleknot** (OGLEKNOT_CREATURE_BUILD_1, not in the cast bible) | PASS — same architecture (in wildAnimals ⇒ in NativesOf ⇒ dives) | **UNRESOLVED — see finding below** | PASS — MeatAmount 0, LeatherAmount 0 |

Ban 2 mechanism (architecture-level, not per-def): `RM_ContagionSky.NativesOf`
= every race in the biome's `AllWildAnimals` + `extraNatives` (`RM_TheUnfinished`).
`RM_GameCondition_ContagionBurn.Pressure` burns every native caught exposed every
250 ticks UNLESS in `armoredNatives` (`RM_Scaldhide`, `RM_Crispling` — no damage,
they hunt), and orders a dive UNLESS in `leakerNatives` (`RM_Scorchpod` — damage,
no dive, it cooks). Confirmed all 22 wildAnimals rows route through this with no
opt-out. **PASS for every fauna def — no UV-immune native exists.**

**FINDING (not fixed — judgement call):** `RM_Ogleknot` is a normal breeding
animal (`lifeExpectancy 8`, standard `lifeStageAges`, **no**
`DeathActionProperties_Vanish`) — unlike every other new-species admission this
sitting, which all explicitly carry the goo-corpse vanish mechanism that the cast
bible cites as *why* ban 3 is satisfied ("recurring drafts the goo keeps
re-issuing, not settled species"). Ogleknot was never part of the cast bible
(`contagion_grotesque_cast_2026-09-27.md` §3/§7 lists only Skinflap/Gorekite/
Danglemaw/Crispling/Sloshbelly) — it was built later by `OGLEKNOT_CREATURE_BUILD_1`
off a salvaged render, and that item's spec never discusses ban 3 at all. This
reads as exactly the shape ban 3 forbids ("a long-lived, stable new resident def
contradicts open-throttle"), but I have not fixed it — adding a vanish mechanism
changes gameplay (no corpse/no breeding-population read) and needs an owner call
on whether Ogleknot is meant to be a goo-bud draft or a genuine standalone
species. **Recommend the coordinator get a ruling or file a follow-up item.**

### 2b. Flora (13 species, `RM_ContagionFlora.xml`)

Zero `Nutrition` stat, zero `<ingestible>` block on any of the 13 plants
(MEASURED via grep across the file). Every `harvestedThingDef` yields an item —
`WoodLog` (Eyebark, HalfmadeTree, HalfmadeTreeBlighted), `RM_RedSap`
(Sapblister), `RM_SeedFistFertilizer` (BloodyFist), `RM_WombpodSac` (Wombpod) —
none food, and none of those four downstream items carries `Nutrition`/
`ingestible` either (checked). Biome `forageability` is `0.0` with no
`foragedFood` def. **Ban 4: PASS, all 13.** Ban 3 (Meatvine/Toothmoss/Wombpod,
the 3 new flora): cast bible §5 frames all three as infection-front organisms,
same "unfinished by construction" logic as the fauna goo-buds; no counter-evidence
found. **PASS.**

### 2c. Mechanics / devices (ban 6 — no net-positive mutation)

- **Grown limbs** (`RM_GrownLeg`/`RM_GrownArm`, `RM_InstallGrownLeg`/`Arm`
  recipes): parented directly off vanilla `BodyPartNaturalBase`, installed via a
  thin subclass of vanilla `Recipe_InstallNaturalBodyPart` — mechanically a
  **restoration** (replaces a missing limb at natural-part parity), not an
  enhancement; no stat bonus beyond what the vanilla parent already carries.
  **PASS.**
- **Install-match bonus** (`GenomeMatchBonusUtility`, `RM_GenomeMatchedInstall`
  thought): +8 mood for 10 days, granted only when a colonist gets a limb/organ
  grown from their **own** genome back — flavour/immersion only, no stat effect,
  and a mismatch grants "no bonus... no penalty either" per its own header.
  **PASS.**
- **Amoeba gestation** (`RM_AmoebaGestation` hediff, `Hediff_AmoebaGestation.cs`,
  `AmoebaHostUtility.cs`): consumes the host amoeba to produce the organ/limb
  batch; no stat grant to any pawn. **PASS.**
- **Sunbeam** (`RM_Sunbeam`, `DamageWorker_RM_UV`): a weapon — low damage/scarring
  vs people, multiplied vs Contagion natives via `RM_ContagionSky.IsNative`. Grants
  nothing to whoever is hit. **N/A to ban 6** (not a mutation path).
- **Unfinished hediffs** (`RM_UnfinishedClaw/Spike/Fang/Stump/VestigialWing/
  UselessJaw/Monstrous/Unraveling`): applied only to `RM_TheUnfinished` itself at
  spawn (`CompRandomizeUnfinished.cs`), never to a colonist or visitor. **N/A to
  ban 6** — this is creature-flavor randomization, not a Contagion-touch outcome
  on a person.

**Ban 6: PASS across everything checked — no def or mechanism grants a colonist a
net-positive outcome from Contagion contact.**

### 2d. Bans 1, 5, 7, 8

- **Ban 1** (no green squares) — n/a, no def here touches world-tile placement.
- **Ban 5** (red fog ×0.4 stands) — `RM_ContagionBloom`'s
  `accuracyMultiplier` is still `0.4` (MEASURED, `RM_ContagionWeathers.xml`
  line 41). **PASS, untouched.**
- **Ban 7** (Assailant arsenal, never Wasteland) — Sunbeam and Cloud Repulsor are
  both explicitly "Helix" hardware in every description (MEASURED: 5 occurrences
  across their two files); no Wasteland flavor text found. **PASS.**
- **Ban 8** (recognizability) — descriptions read (Ogleknot, Sloshbelly, the
  flora) show no Earth-animal/Earth-plant silhouette claimed as literal; the cast
  bible's own §7 states the two closest echoes (a tick, a moss) are each broken in
  the brief. Not independently re-verified against art (out of scope — no live
  render). **PASS on text; no art check performed.**

## 3. `CONTAGION_IKEE_NAME_COLLISION_1` state

**Already CLOSED** (2026-09-29, sha `7cfd4c0b4`), resolved by owner ruling on a
question card: Contagion keeps the label "ikee"; Stillsand's `RM_Ikee` gets a
new distinct label as a separate follow-up. The rename executed for this item's
scope (`RM_Ikee` → `RM_ContagionIkee` in the Contagion mod, label unchanged) is
already live in `RM_ContagionFauna.xml` and `RM_Contagion.xml`'s wildAnimals row
— confirmed present. Nothing left to do here.

## 4. Fixes made

1. `src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml` — wildPlants row
   `RUT_RustPuff`/`mandrake.rut.rotsporekit` (dead, unresolvable) → `RM_RustPuff`/
   `mandrake.rm.therot` (real, resolves); header comment corrected.
2. `src/RimMandrake/Contagion/About/About.xml` — the roster disclosure paragraph
   described the pre-port donor roster (stale since Wave A/flora port) and
   described the RustPuff absorption as still "pending" when it landed a day
   before this mod was built; corrected to the current state.

Verified: `python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"` on
`RM_Contagion.xml` — OK. `run_selftests.py`: 76/78 passed, 1 unmeasured (needs
Windows .NET SDK, unrelated), 1 FAILED —
`selftest_deployed_biome_refs.py`, which is **pre-existing** (fails on
`RUT_Contagion.xml`/`RUT_TheRot.xml`/`RUT_Miasma.xml`/`RUT_TheForge.xml`/
`RUT_WeepingStones.xml`, none of which I touched) and independently confirms
finding §5 below at a larger scale (21 dangling refs, not just 1).

## 5. Items to file (for the coordinator)

1. **`RM_Ogleknot` ban-3 ambiguity** (§2a above) — not in the cast bible, lacks
   the goo-corpse vanish mechanism every other new admission uses to satisfy ban
   3, and its own build item never discusses the ban. Needs an owner call:
   goo-bud draft (add vanish) or accepted standalone species (leave as-is, but
   then it should probably be recorded as a ruled exception the way the cast
   bible records the other five).
2. **Wider stale RotSporeKit-tier rename propagation** — `THEROT_RM_MOD_BUILD_1`
   (2026-09-24) renamed `RUT_RustPuff` etc. to `RM_*` and moved the mod to
   `mandrake.rm.therot`, but 21 references across `RUT_Contagion.xml` (the frozen
   Contagion twin — 1), `RUT_Miasma.xml` (1), `RUT_TheForge.xml` (1, no
   MayRequire at all), `RUT_TheRot.xml` itself (18), and `RUT_WeepingStones.xml`
   (1) were never updated, and `selftest_deployed_biome_refs.py` is currently
   FAILING on exactly this. Out of the Contagion mod's scope to fix. Recommend
   filing e.g. `ROTSPOREKIT_RENAME_PROPAGATION_1`.
