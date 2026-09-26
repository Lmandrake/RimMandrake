# Exposure gear matrix — design spec

Item: `SEA_DIVE_MAPS_BUILD_1` (§8.8 Q3, "the dive suit across seas"). Owner ruling, typed
2026-09-25 16:47, verbatim:

> *"There's vac/liquid (no air), extreme heat/cold (temp threat). Those are the two axes. Space
> suits are well known. Locals make their own. Vary them along that axis. Cheap tier, moderate
> tier, then delux set (all the way to space)."*

Status: PROPOSED design on a ruled frame. The two axes, the three tiers, "locals make their own"
and "deluxe reaches space" are **ruled**; every item name, number and cell assignment below is
**proposed** unless it cites an earlier ruling. Nothing built. Open questions are §6, as choices.
Tier line: every def here is invented and franchise-free → `RM_` (Q11a); Star Wars skins are
§4b and live in the `RSW_`/`RUT_` patch layer.

Supersedes: `sea_dive_maps_spec.md` §4's one-def "dive suit" and its §8.6 "the Scald ladder IS
the dive suit" (both rewritten to point here); `scald_steam_and_hazards_spec.md` §5's ladder is
now the **heat column** of this matrix, unchanged in its numbers.

## 0. Read first — what already exists (MEASURED 2026-09-25)

| exists | where | what it gives the matrix |
|---|---|---|
| `Apparel_Vacsuit` + `Apparel_VacsuitHelmet` (Odyssey) | RimSage def read | body `VacuumResistance 0.32`, helmet `0.69` (sum 1.01 = sealed); `ArmorRating_Heat 0.66`; body `Insulation_Cold 90`, `Insulation_Heat 15`; `MoveSpeed −1.25`; Spacer, `OrbitalTech` — **the deluxe set the owner means by "space suits are well known"** |
| `VacuumResistance` StatDef + `VacuumResistance_Partial/Total` genes | Odyssey | the vacuum hook; exists only with Odyssey ⇒ every reference is `MayRequire="Ludeon.RimWorld.Odyssey"` |
| `Apparel_GasMask` (Biotech) | RimSage | `ToxicEnvironmentResistance 0.8`, Industrial, 20 steel + 20 chemfuel — the **shape** of a cheap head-worn filter; not a no-air answer (it filters, it does not supply) |
| `Apparel_Parka`, `Apparel_Tuque` (Core) | RimSage | stuffed cold gear: the cheap cold cell needs **no new def**, only a local material |
| `HediffCompProperties_EnvironmentalExposure.protectionStat` | Core; used by `RM_SheenProtection` (TheRot), `RM_WetBulbProtection` (EnvironmentalHazards) | the apparel-stat slowdown for any exposure clock — the liquid hook is one more StatDef on this shape |
| `RM_Apparel_ScaldWrap`, `RM_Apparel_BoilSuit`, `RM_Apparel_RindCoat`, `RM_ScaldProtection` | `scald_steam_and_hazards_spec.md` §5/§5a — specced, unbuilt | the heat column, with numbers already ruled |
| Royal Rind (`RM_RoyalRind` stuff) | `greatbole_harvest_spec.md` §3b — ruled, unbuilt | *"immune to heat and cold to extreme levels"* (owner) ⇒ the one material that fills **both** temperature cells at the moderate tier; its vacuum use is ruled Odyssey-gated |
| KotOR flight suits (`guy762_FlightArmor`: `ArmorRating_Heat 0.65`, `Insulation_Cold 20`; `guy762_RebelPilot_suitbox`: `Insulation_Cold 100`) | `src/RimStarWars/Armoury/.../Absorbed_KotorCore_Apparel_SWGenericFlightSuits.xml` | Star Wars **skins** for moderate cells, patch layer only (§4b) |
| No breath stat, no drowning, no pressure in 1.6 | `sea_dive_maps_spec.md` §4 (MEASURED) | "no air" in liquid is expressed as an exposure clock, never a lung |

Nothing else in `src/` carries `VacuumResistance`; no `RM_`/`RSW_`/`RUT_` apparel def exists
beyond a chitin helmet (TheRot) and a pendant (TrophyCraft).

## 1. The two axes

| axis | the threat | the two ends | engine hook (§3) |
|---|---|---|---|
| **A — no air** | you cannot breathe here | **liquid** (the four sea floors: the `RM_DeepExposure` clock) · **vacuum** (space, Odyssey) | liquid: `RM_DiveProtection` (new); vacuum: `VacuumResistance` |
| **B — temperature** | the air (or water) itself hurts | **extreme heat** (Scald 55 °C ambient, contact burn, steam) · **extreme cold** (Propane −79 °C, the nightside) | `Insulation_Heat`, `ArmorRating_Heat`, `RM_ScaldProtection` · `Insulation_Cold` |

A cell is (tier × axis-end). An item may fill several cells — a sealed suit is sealed against
liquid *and* vacuum, and its shell insulates — which is why the deluxe set is one set, not four.
The biome-specific hazard clocks (`RM_WetBulbProtection`, `RM_SheenProtection`, the Miasma's
owed stat) are **not** a third axis: they are local flavours riding as extra stat offsets on
whichever local garment the biome makes (§4).

## 2. The matrix

Three tiers. "Cheap" is Neolithic and local; "moderate" is Industrial or a hard fight; "deluxe"
is Spacer and reaches space. Numbers are INVENTED except where marked MEASURED/ruled.

| tier | A — liquid | A — vacuum | B — heat | B — cold |
|---|---|---|---|---|
| **cheap** (Neolithic, tailoring bench, local materials) | **`RM_Apparel_AirBladder`** (new): a chitin-framed bladder worn on the back (Shell, Torso); `RM_DiveProtection 0.35` (clock ≈1.5× slower); 8 `RM_ScaldWalkerChitin` + 2 `RM_ShullaBladder` (new butcher product of the shulla) | **none, by design** — there is no cheap vacuum answer; "space suits are well known" means vacuum *starts* at deluxe | **`RM_Apparel_ScaldWrap`** (ruled numbers: `ArmorRating_Heat 0.30`, `RM_ScaldProtection 0.45`) | **`Apparel_Parka` / `Apparel_Tuque` in a local cold leather** (vanilla defs; the local material carries `StuffPower_Insulation_Cold` ≈ 2× plain leather, the megasloth-wool shape) |
| **moderate** (Industrial research, or the rind fight) | **`RM_Apparel_Rebreather`** (new, Overhead, `FullHead`, Industrial via `RM_ScaldWorking`): `RM_DiveProtection 0.45`; **`RM_Apparel_BoilSuit`** body adds `RM_DiveProtection 0.30` — worn together 0.75 (≈4× slower) | **partial** — boil-suit + rebreather are sealed, so with Odyssey a patch gives them `VacuumResistance 0.25 + 0.30` (a sealed suit is a sealed suit, §9 ruling 4 of the Scald spec); enough for a minute on a hull, never a walk | **`RM_Apparel_BoilSuit`** (ruled: `ArmorRating_Heat 0.55`, `RM_ScaldProtection 0.85`) · **`RM_Apparel_RindCoat`** (ruled: 0.45 / 0.60 + extreme insulation) | **`RM_Apparel_RindCoat`** (ruled: extreme cold insulation — the same coat, both ends of axis B) |
| **deluxe** ("all the way to space") | **the sealed set**: Odyssey `Apparel_Vacsuit` + `Apparel_VacsuitHelmet`, patched with `RM_DiveProtection 0.40 + 0.55` (sum 0.95 → clamped, floor 8%) | **the same set** — MEASURED `VacuumResistance 0.32 + 0.69` | **the same set** — MEASURED `ArmorRating_Heat 0.66`; patch `Insulation_Heat +40` (the vanilla 15 is a spacer's, not a diver's) and `RM_ScaldProtection 0.35 + 0.30` (ruled, Scald spec §5) | **the same set** — MEASURED `Insulation_Cold 90` |

Reading across a row: cheap gear answers **one** cell each and is local; moderate gear answers
**two** (a sealed body helps both the clock and the burn; rind helps both temperatures); deluxe
is one set that answers all four. Reading down a column: the same threat, answered longer.

**What "a breath budget" is.** There is no lung stat (MEASURED). The budget is the
`RM_DeepExposure` clock: severity per day = `exposureDays` per sea (Twilight long, Propane short),
scaled by `1 − RM_DiveProtection` (clamped to 1, floored at 8% — the Scald spec's Ban 3 shape).
Cheap ≈ a short dive, moderate ≈ a working dive, deluxe ≈ the floor's own limits are what stop
you. Surfacing or standing under any sub-roof cell (an air-bell) heals it.

## 3. Stat hooks

| hook | kind | tier of def | notes |
|---|---|---|---|
| **`RM_DiveProtection`** | new StatDef, 0–1, `showOnPawns`, category Apparel | `RM_` (DivingInteraction) | the `protectionStat` of `RM_DeepExposure`'s `HediffCompProperties_EnvironmentalExposure`; sums across worn apparel; one stat for all four seas |
| `VacuumResistance` | Odyssey StatDef (MEASURED) | patch, `MayRequire="Ludeon.RimWorld.Odyssey"` | never referenced from a def that must load without Odyssey; every offset is a `PatchOperationAdd` under `MayRequire` |
| `Insulation_Heat` / `Insulation_Cold` | Core | — | ambient temperature; vanilla heatstroke/hypothermia already scale with it |
| `ArmorRating_Heat` | Core | — | contact burn (`Burn` has `armorCategory Heat` — Scald spec §4) and the feen's stings |
| `RM_ScaldProtection` | StatDef, Scald spec §5 | `RM_` (TerminalBiomes) | the steam clock; Scald-only flavour on the heat column |
| local hazard clocks (`RM_WetBulbProtection`, `RM_SheenProtection`, Miasma owed) | exist / owed | their biomes | ride as offsets on that biome's local garment; not matrix cells |

Rule: **no item zeroes any clock.** Every `protectionStat` sum clamps at 1 and the clock floors
at 8% (Scald spec Ban 3, Grey ban 1 spirit).

## 4. "Locals make their own" — per-biome recipes and materials

The owner's phrase means the cheap and moderate cells are **made from what the biome yields**,
by the people who live beside the threat, at the tailoring bench or the machining table — not
bought. Each threatening biome contributes one material and the garments it makes:

| biome | local material (source) | cells it fills | garments |
|---|---|---|---|
| **The Scald** | `RM_ScaldWalkerChitin` (vu'uul hunt drop, shipped) + `RM_ShullaBladder` (new shulla butcher product) | cheap heat, cheap liquid, moderate heat + liquid | `RM_Apparel_ScaldWrap`, `RM_Apparel_AirBladder`; `RM_Apparel_Rebreather` + `RM_Apparel_BoilSuit` (Industrial, `RM_ScaldWorking`) |
| **The Greentide** | **Royal Rind** (`RM_RoyalRind` stuff from `RM_GreatboleFruit`, ruled, unbuilt) | moderate heat AND moderate cold; plus the Contagion/Scald/Miasma clocks as stuff offsets | `RM_Apparel_RindCoat`; any vanilla leather garment made of rind |
| **The Propane Lakes / nightside** | a cold-native leather (the Propane sheet's cold-loving natives, R-H10 — **which species is that biome's sitting's call**) with `StuffPower_Insulation_Cold` ≈ 2× | cheap cold | vanilla `Apparel_Parka`/`Apparel_Tuque` stuffed with it — **no new def** |
| **Grey Sea / Twilight Sea** | none of their own in v1 — the liquid cells are shared sea gear (the Scald's chitin bladder works on any floor) | — | a Grey brine-cured hide is a candidate later (§6 Q4) |
| **Space** (deluxe) | steel + plasteel + components — nobody local | all four | Odyssey vacsuit + helmet, patched |

So a Scald colony builds the liquid column and the heat column from its own sea; a Greentide
colony builds the moderate temperature cells from one fight; a nightside colony builds cold from
its own hunt; and only the deluxe set is imported technology. That is the ladder the owner asked
for: *vary them along the axis*, tier by tier, biome by biome.

### 4a. The Scald ladder, re-expressed on the matrix

`scald_steam_and_hazards_spec.md` §5 rules **wrap → Royal Rind → boil-suit → vacsuit**. On the
matrix that ladder is the **heat column** read downward, and it was missing the liquid column:

| Scald rung (ruled) | matrix cell(s) | what the matrix adds beside it |
|---|---|---|
| `RM_Apparel_ScaldWrap` (Neolithic) | cheap × heat | cheap × liquid: `RM_Apparel_AirBladder` — the first dive and the first suit come from the same walker hunt |
| Royal Rind coat (Neolithic, a fight) | moderate × heat, moderate × cold | imported from the Greentide; makes the 55 °C ambient *comfortable* |
| `RM_Apparel_BoilSuit` (Industrial) | moderate × heat, moderate × liquid (body half) | moderate × liquid (head half): `RM_Apparel_Rebreather`, same research |
| Odyssey vacsuit + helmet (Spacer) | deluxe × all four | nothing — it is the top |

The Scald spec's numbers stand; this table only says which cell each rung occupies.

### 4b. The Star Wars layer

Nothing above is IP. The `RSW_`/`RUT_` layer may **reskin**, never replace: the KotOR flight
suits already in the Armoury are natural skins for the moderate cells (`guy762_FlightArmor` reads
as a heat-armoured flight suit; `guy762_RebelPilot_suitbox` as a cold one) and a Utinni patch may
add `RM_DiveProtection`/`RM_ScaldProtection` offsets to them so a Star Wars colony's pilots can
dive. The free `RM_` matrix must be complete without them (Q11a).

## 5. Build order — each step shippable, XML-first

1. **`RM_DiveProtection` StatDef + `RM_Apparel_AirBladder` + `RM_ShullaBladder`** (DivingInteraction,
   with `sea_dive_maps_spec.md` §6 step 3). Proof: quicktest, diver with the bladder on a Scald
   floor — `RM_DeepExposure` severity after 1 h is ≈65% of a naked diver's.
2. **The vacsuit patch** (TerminalBiomes, `MayRequire` Odyssey): `RM_DiveProtection`,
   `RM_ScaldProtection`, `Insulation_Heat` offsets onto `Apparel_Vacsuit`/`Apparel_VacsuitHelmet`
   (extends the Scald spec's ruled patch — one file). Proof: `validate_patch.py --live --defs`
   clean; a vacsuited diver's clock reads the 8% floor.
3. **`RM_Apparel_Rebreather`** + the boil-suit's `RM_DiveProtection 0.30` (with the Scald spec's
   gear step 5, same research). Proof: boil-suit + rebreather = 0.75 in the pawn's stat readout.
4. **Sealed-moderate vacuum patch** (Odyssey `MayRequire`): `VacuumResistance` 0.25/0.30 onto
   boil-suit/rebreather. Proof: stat readout with Odyssey loaded; absent Odyssey, the defs load
   with no error (`Player.log` grep for the defNames).
5. **Cold-native leather** — lands with the Propane Lakes build, not here; this spec owes that
   build one line: *"the native leather's `StuffPower_Insulation_Cold` ≈ 2× plain leather"*.
6. **Rind stuff offsets** — land with the Greentide's rind (Scald spec §5a); nothing to do here.
7. **Mod Settings** (rule: every mod ships superb settings): in DivingInteraction's screen —
   `Gear.DiveProtection` multiplier (1.0×; 0 labelled "gear does not slow the dive clock"),
   `Gear.VacsuitPatch` on/off (leave the Odyssey suit vanilla), `Gear.SealedModerateVacuum` on/off;
   in TerminalBiomes' — `Gear.LocalRecipes` on/off (hides the Scald recipes; the items still load
   for existing saves). Defaults = shipped; all-off = vanilla apparel only, diving at the naked
   clock.

## 6. Owner rulings on this matrix (2026-09-25, SEA_DIVE_MAPS_BUILD_1 ledger notes)

1. **Deluxe is Odyssey's vacsuit set.** Design assumes every DLC is present (*"Always assume all
   the dlcs."*, CLAUDE.md) — no expansion-free top tier is owed; `MayRequire` guards remain for
   load safety only.
2. **One `RM_DiveProtection` stat for all four seas**; heat stays on its own stats.
3. **A separate `RM_Apparel_Rebreather`** at the moderate liquid tier, stacking with any body
   piece (boil-suit or Royal Rind coat).
4. **Local sea gear is the Scald's only in v1**; the other seas get theirs when their floors are built.
5. **The KotOR flight suits are patched** with our dive and heat offsets so they protect divers.
