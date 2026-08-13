# Lightsaber availability in the live stack — 2026-08-13

Offline read by OPS. Game DOWN, no load spent. Every count below is quoted with
the command that produced it.

## 🔴 Verdict in one line

**The owner is right and the earlier claim was wrong: this campaign DID have
lightsabers — 14 wieldable ones — and every single one came from
`lee.theforce.lightsaber`, whose Workshop folder has since been DELETED from
disk. Nothing else in the 570-mod stack defines a lightsaber, so the next load
has zero.**

The absence is **silent** (no cross-reference errors) and therefore easy to miss,
which is exactly how it got missed.

---

## 0. What corrected the record — the def dump, not a grep

The decisive source is not the workshop tree. It is the game's own def dump,
which records what the loader actually built:

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\manifest.json`
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\ThingDef.json` (848,902,784 bytes)

```json
"capturedUtc": "2026-08-13T14:51:58Z",
"gameVersion": "1.6.4871 rev591",
"timingsMs": { "total": 33416, "animals": 438, "allDefs": 32977 }
```

That `total: 33416` matches the harvested log's
`[RimDefDump] done in 33419 ms (animals 438 ms, all-defs 32977 ms)` — **this dump
is from the very session `2026-08-13_log_harvest_1004.md` reports on.** It is the
authoritative record of that mod set, and it survives the mod that produced it.

The manifest lists **573 loaded mods** (570 `activeMods` + Core + DLCs), and entry
**563** is:

```json
{ "loadOrder": 563,
  "name": "Star Wars : The Force - Lightsaber",
  "packageId": "lee.theforce.lightsaber",
  "rootDir": "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\294100\\3466124712" }
```

**It loaded. It contributed 333 defs.**

```
TOTAL defs from lee.theforce.lightsaber: 333
   HiltDef 112 | HiltPartDef 60 | ThingDef 32 | SoundDef 30 | RulePackDef 12
   RecipeDef 10 | DamageDef 7 | HediffDef 7 | TraitDef 7 | AnimDef 6 …
```
*(python pass over all 528 files in `DefDump\defs\`, counting `packageId ==
"lee.theforce.lightsaber"`)*

### And the folder is gone now

```bash
ls "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" | wc -l   # 1238
ls "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3466124712" # No such file or directory
grep -rl "<packageId>lee.theforce" --include='About.xml' <workshop> <Mods>
#  → 2938932438, 3379096669, 3557220601, 3557220783  (all four are *references*
#    inside <modDependencies>, none declares the lightsaber mod)
grep -n -A6 '"3466124712"' "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/appworkshop_294100.acf"   # no match
```

⚠️ **The item is not in Steam's `appworkshop_294100.acf` either** (file last
written 2026-08-13 16:22). Steam does not think it is subscribed. Between the
07:51 def dump and now, the item left the machine. `ModsConfig.xml` still lists
it — **line 567**, not 565; the file has been rewritten since the earlier read:

```bash
grep -n "lee.theforce" "…/Config/ModsConfig.xml"
# 567:    <li>lee.theforce.lightsaber</li>
```

`lee.theforce.standalone` (folder `3557220601`) and `lee.theforce.factions`
(folder `3557220783`) are **installed but NOT active** — they appear nowhere in
`activeMods` and nowhere in the dump manifest. They are not part of this problem.

---

## 1. The 14 wieldable lightsabers, with the numbers O10 needs

All from `lee.theforce.lightsaber`. Extracted from `DefDump\defs\ThingDef.json`
(`is.meleeWeapon == true`). Tool-level `armorPenetration` is **0 on every one**;
the penetration lives on the DamageDef the tool capacity routes to (§1.1).

| defName | label | hilt (Blunt) | tip/point | edge | WorkToMake |
|---|---|---|---|---|---|
| `Force_Lightsaber_Crossguard` | Crossguard Lightsaber | 64 / cd 3 | **92** / cd 4 | **120** / cd 3.5 | 4500 |
| `Force_Broadsaber` | Broadsaber | 35 / cd 4 | **92** / cd 4 | **120** / cd 3.5 | 3000 |
| `Force_Lightsaber_UniqueAnakin` | Lightsaber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_Lightsaber_UniqueObi` | Lightsaber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_Ezra_BlasterLightsaber` | Blaster Lightsaber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_Protosaber` | Proto-saber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_SoulSaber` | Soul Saber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_Lightsaber_BuildYourOwn` | Lightsaber | 41 / cd 2 | 96 / cd 2 | 96 / cd 2 | 3000 |
| `Force_Lightsaber_Custom` | Lightsaber | 41 / cd 4 | 88 / cd 2.5 | 88 / cd 2.5 | 3000 |
| `Force_Darksaber` | Darksaber | 41 / cd 4 | 88 / cd 2.5 | 88 / cd 2.5 | 3000 |
| `Force_Lightsaber_Dual` | Dual-Bladed Lightsaber | 20 / cd 1.5 | 88 / cd 2.5 | 88 / **cd 1** | 4000 |
| `Force_Lightsaber_Inquisitor` | Dual Lightsaber | 20 / cd 1.5 | 88 / cd 2.5 | 88 / **cd 1** | 3500 |
| `Force_Lightsaber_Curved` | Curved Lightsaber | 34 / cd 5 | 88 / cd 1.5 | 88 / cd 2.5 | 3200 |
| `Force_Lightsaber_Shoto` | Lightsaber(Shoto) | 33 / cd 4 | 80 / cd 2 | 80 / cd 2 | 2800 |

All `techLevel: Ultra`, `thingClass: Verse.ThingWithComps`, with
`CompProperties_LightsaberBlade` and `CompProperties_LightsaberStance`
(`compClass: Lightsaber.Comp_LightsaberStance`, severity 1–7 — the stance system).
Non-weapon saber defs also lost: `LightsaberThrow`, `Force_NonVPELightsaberThrow`,
`Force_LightsaberWhipProjectile`, `Force_MoteLightsaberWhip`,
`Mote_LightSaberReturn`, plus 112 `HiltDef` and 60 `HiltPartDef` (the whole
build-your-own-hilt system).

### 1.1 Armour penetration — the chain, and the honest caveat

Two different damage routes, both from the dump:

| tool capacity | → ManeuverDef | → DamageDef | DamageDef `defaultArmorPenetration` |
|---|---|---|---|
| `Force_SaberSlash` / `Force_SaberStab` | `Force_SaberSlash` / `Force_SaberStabM` | `Force_SaberSlash` / `Force_SaberStab` | **0.70** |
| `guy762_ToolCapacity_SaberSlash` / `…SaberStab` | `guy762_Maneuver_SaberSlash` / `…SaberStab` | `guy762_MeleeDamage_ecut` / `…estab` | **-1** (derived) |

The Anakin/Obi/Ezra/Proto/Soul/BuildYourOwn sabers use the first row (AP 0.70).
Custom/Dual/Inquisitor/Curved/Shoto/Crossguard/Darksaber/Broadsaber use the
second, which is `-1` and therefore **derived at runtime, not readable from the
defs**. The `guy762_ToolCapacity_*` capacities come from `guy762.mm.kotorcore`,
which is still present — but with no lightsaber ThingDefs to attach to.

⚠️ **This is why O10's "27.5 through that suit" cannot be re-derived purely
offline.** Half the saber roster resolves its AP at runtime, and
`Comp_LightsaberStance` sits on top of it. The measurement was the right method;
it just needs the mod back on disk.

---

## 2. What the campaign still has — vibro and Yautja, both intact

`OuterRim_*` (`neronix17.outerrim.core`, load 533), `guy762_v*`
(`guy762.kotorweapons`, load 566), `JDSA_Vibro*`
(`m3.continued.jangodsoul.starwars.bti`, load 27), `ABYautja_Melee_*`
(`biotechrace.yautja.alleyballey`) — all present in the dump and all unaffected.

Best of each family, for the O10 three-way:

| weapon | mod | best edge power | tool AP |
|---|---|---|---|
| `OuterRim_VibroCleaver` | Outer Rim Core | 41 Cut / cd 2.1 | **0.95** |
| `OuterRim_VibroBlade` | Outer Rim Core | 38 Cut / cd 1.2 | 0.91 |
| `guy762_vaxe` (Vibroaxe) | KotOR Weapons | 42 Cut / cd 4.5 | **1.60** |
| `guy762_vglaive` (Vibroglaive) | KotOR Weapons | 32 Cut / cd 3 | 1.51 |
| `guy762_vdubblade` | KotOR Weapons | 38 Cut / cd 1 | 1.42 |
| `JDSA_Vibroblade` | JDS Armory | 52 Stab / cd 1.9 | 0.96 |
| `ABYautja_Melee_ElderSword` | Yautja | 38 Cut / cd 1.4 | **0.60** |
| `ABYautja_Melee_BladedMaul` | Yautja | 45 Stab / cd 2.6 | 0.60 |

Note the shape this gives O10: **KotOR vibro weapons already out-penetrate
everything** (AP 1.05–1.60 vs the saber DamageDef's 0.70), while the sabers win
on raw power (88–120 vs 31–52). That is a genuinely interesting comparison and it
is worth finishing — but only with the saber back.

---

## 3. The trap that made this hard to see — KotOR 1.6 dropped its own sabers

`guy762.kotorweapons` **used to** ship lightsabers. It still does — in its
**`1.5/`** folder, which RimWorld 1.6 never reads:

```bash
ls "…/294100/2938932438/1.5/Defs/ThingDefs_Weapons/"   # kotorlightsaber_{single,dual,curve,cross,short}.xml, Immortalus_SithSabers.xml
ls "…/294100/2938932438/1.6/Defs/ThingDefs_Weapons/"   # vibro + blasters only; the ONLY saber file is lightsabernames.xml (a RulePackDef)
grep -c "SWSaber_KotOR_" DefDump/defs/ThingDef.json    # 0
```

**Zero `SWSaber_KotOR_*` defs in the live dump** — 47 saber ThingDefs that a raw
grep of the workshop tree finds are all dead 1.5 content. Its `LoadFolders.xml`
makes the delegation explicit:

```xml
<v1.5>
  <li IfModActive="lee.theforce.lightsaber">1.5/AdditionalMods/_TheForceLightsabers</li>
  <li IfModNotActive="lee.theforce.lightsaber">1.5/AdditionalMods/_NO_ForceLightsabers</li>
</v1.5>
<v1.6>
  <li IfModActive="lee.theforce.lightsaber">1.6/AdditionalMods/_TheForceLightsabers</li>
  <!-- <li IfModNotActive="lee.theforce.lightsaber">1.6/AdditionalMods/_NO_ForceLightsabers</li> -->
</v1.6>
```

🔴 **The 1.6 fallback is commented out and the `_NO_ForceLightsabers` folder does
not exist under `1.6/`.** In 1.5 KotOR could stand alone; in 1.6 it hands
lightsabers to The Force entirely and has no plan B. `1.6/AdditionalMods/_TheForceLightsabers/`
holds only crystals and balance patches that sit *on top of* Force's defs.

**Generalises to:** a mod's version subfolders are not history, they are the load
set. Grepping a workshop folder without honouring `LoadFolders.xml` and the game
version over-counts badly — here by 47 defs, in the exact direction that would
have produced a confident wrong answer.

---

## 4. Does anything break? No — and that is the problem

**None of the 25 cross-reference errors in `2026-08-13_log_harvest_1004.md` are
saber- or Force-related.** They are fully itemised there and account for
themselves exactly:

| §1.6 `Pawn_Melee_Punch_HitBuilding` | 16 |
| §1.11 `BMT_*` (7 PawnKind + 1 Thing) | 8 |
| §1.1 `VWE_Tool_Whip` | 1 |
| **total** | **25** |

That log is from the session where the lightsaber mod **was** loaded, so it says
nothing about the future either way. The forward-looking check is what references
the saber defNames from mods that are *still* active:

| referencing file | gate | verdict |
|---|---|---|
| `…/2938932438/1.6/AdditionalMods/_TheForceLightsabers/Patches/*.xml` | `IfModActive="lee.theforce.lightsaber"` in LoadFolders | folder never loads — silent |
| `…/2938932438/1.6/AdditionalMods/ShowMeYourHands/…_LightsaberMod.xml` | `IfModActive="Mlie.ShowMeYourHands"` — **and SMYH is not in `activeMods`**; each def also carries `MayRequire="lee.theforce.lightsaber"` | doubly safe |
| `…/3254370945/1.6/AdditionalMods/_DroidsBase/Defs/AlienRace_KotORDroidBase.xml` | folder DOES load (`guy762.KotORDroids` active, ModsConfig line 574) but every saber `<li>` is `MayRequire="lee.theforce.lightsaber"` | suppressed — silent |
| `…/3557220783/1.6/Defs/FactionDefs/FactionDefs_{Jedi,Sith}_Enclave.xml` | `lee.theforce.factions` is **not active** | never loads |

```bash
grep -n -B4 -A2 "Force_Lightsaber_Custom" "…/_DroidsBase/Defs/AlienRace_KotORDroidBase.xml"
#  99:  <li MayRequire ="lee.theforce.lightsaber">Force_Lightsaber_Custom</li>
```

**Conclusion: zero new errors, zero warnings, no hard `<modDependencies>` on it.**
The game will load green and the player will simply never see a lightsaber. A
green log is the *symptom*, not the all-clear.

One player-visible residue: `guy762.kotorweapons` still ships
`Techprint_guy762_ResearchKotOR_lightsabers` and `…_advsabers`, and
`guy762.mm.kotorcore` still ships `guy762_saberpart_{lens,emitter,pcell}` — a
research line and three components leading to nothing buildable.

---

## 5. What I could NOT have seen

Stated so nobody re-runs it:

- The mod folder is **deleted**, so its XML cannot be re-read. Everything in §1
  comes from the 07:51 dump — a snapshot, not the source.
- **AP for 8 of the 14 sabers is `-1` (runtime-derived)** and is not recoverable
  from defs alone (§1.1).
- The dump predates the current `ModsConfig.xml` write (07:51 vs 10:01) and the
  current `appworkshop` ACF (16:22). It describes the 10:04 session's stack, not
  necessarily what the *next* load will build.
- I did **not** determine *why* the folder vanished. Absent from the ACF is
  consistent with an unsubscribe, an in-progress Steam repair, **or a Workshop
  delisting** — and if it was delisted, re-subscribing will not work.

---

## 6. PLAYER-ZERO VERDICT — option (b), and it is not close

Not (a) invisible, not (c) erroring: **(b) — it costs the player the single most
iconic weapon in the setting, silently.**

The scoring, plainly: 333 defs gone, including 14 wieldable lightsabers, a
112-hilt/60-part crafting system, a 7-severity stance mechanic, and 7 traits. The
active stack retains a KotOR research line and three saber components that now
lead nowhere. On a Star Wars campaign, "the log is clean" is not the bar.

### One action

🔴 **Re-subscribe Steam Workshop item `3466124712` ("Star Wars : The Force -
Lightsaber") before the next load, and confirm the folder exists at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3466124712`
before launching.** It is already at position 567 in `ModsConfig.xml`, so no load
order work is needed — the slot is waiting for it.

**If it turns out to be delisted and cannot be re-subscribed**, the fallback is
not "do without": it is to re-enable KotOR Weapons' own 1.5 sabers by copying
`2938932438/1.5/Defs/ThingDefs_Weapons/kotorlightsaber_*.xml` +
`Immortalus_SithSabers.xml` and the `_NO_ForceLightsabers` fallback
(`HediffDef_LightsaberStances.xml`, `Patch_LightsaberThingClass.xml`) into a small
`Jawa_*` patch mod. That is a real day of work and should not be started until
the re-subscribe has been tried.

**O10 survives and should be re-queued, not closed** — but it is blocked on the
mod returning, because half the saber roster's AP is runtime-derived (§1.1).

---

### Correction to the record

The claim that *"NO folder on disk declares that packageId, therefore the campaign
has no lightsaber and the missing mod costs nothing"* was **half right and wholly
misleading**. The folder is indeed gone — but the inference was backwards: that
mod was the *sole* provider, and its absence costs 333 defs. The premise inherited
from commit `b5796eb` should not be cited again without this file beside it.

**Method note worth keeping:** `ModsConfig.xml` says what was *asked for*; the
`DefDump\manifest.json` says what was *delivered*. When the two disagree, the
manifest wins, and the difference between them is the finding.
