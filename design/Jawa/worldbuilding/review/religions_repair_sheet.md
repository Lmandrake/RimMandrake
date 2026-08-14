# Religions repair sheet — the 9 INVALID entries, option by option

_Analysis only. **The spec is not edited by this file** — every design call below is
the requesting seat's to make. Produced 2026-08-14 against
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`._

**Gate as run:**

```
python3 /mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils/validate_ideoligion.py --md \
  /mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/faction_religions_spec.md
→ 2/11 VALID. INVALID: 1, 2, 3, 4, 5, 8, 9, 10, 11
   136 memes · 685 precepts · 41 styles · 585 active mods
   dump 2026-08-14T08:20:26Z, game 1.6.4871 rev591
```

Every claim below was re-read out of
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\`
(`MemeDef.json`, `PreceptDef.json`, `StyleCategoryDef.json`) today. Vocabulary
legality checked against
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`.

---

## §0 · Four facts that reframe every repair. Read once; they are not repeated below.

**1. 🔴 No `FactionDef` field sets precepts.** `disallowedPrecepts` is a blacklist and
that is the only precept field on the def (`references/authoring.md` §1, verified
across all 87 installed `FactionDef`s). The validator says so on all eleven entries:

```
⚠️  WARN  route/precepts-unauthorable  8 precepts listed, but no FactionDef field can set them
```

⇒ **Every precept table in the spec is a *prediction*, not an instruction.** A
`precept/required-meme` error therefore does not mean "the XML will fail" — it means
**the predicted doctrine will not exist in the game and nobody will be told.** So
each repair is one of two things: delete a false prediction, or change the meme set
until the prediction becomes true.

**2. 🔴 `requiredPreceptsOnly: true` deletes the rest of the table.** Factions **1, 4,
5, 7, 8, 11** set it. With it true the ideoligion carries *only* what the memes'
`requireOne` groups force — so on those six, **even the precepts the validator passes
will not appear** unless a meme forces them. This is bigger than any single error on
this sheet and it is called out per-faction where it bites.

**3. The meme cap is a COUNT, not an impact sum.** `MemeCountRangeAbsolute = IntRange(1,4)`
normal memes; the structure meme is outside it. Impact totals are a display label
only. So "add a meme" is free until you hold four normal memes, and impossible after.

**4. A multi-option `requireOne` group is a dice roll.** 63 of 314 installed groups
hold 2+ options and the generator picks. Naming the option you want in the spec does
not make it happen.

---

## 1 · Galactic Empire — the Unmoving Noon

**1. Validator findings, verbatim**

```
🔴 ERROR meme/exclusion               Loyalist + Supremacist all carry exclusionTag 'GroupRelation' — they cannot coexist
🔴 ERROR precept/required-meme        Proselytizing_Frequently requires one of ['Proselytizer']; none is in the meme set
⚠️  WARN  deity/missing                Structure_TheistEmbodied requires 2..4 deities and none are named
```

**2. Root cause** — two of the four normal memes collide on one exclusion tag, and the
entry's ⭐ precept is gated behind a meme it does not hold.

**3. Legal repair options**

| # | option | checked against the dump | cost |
|---|---|---|---|
| a | Drop `Loyalist` | `Loyalist` impact 1; **`requireOne: []`**; whole mechanical footprint is `consumableBuildings: [SacrificialFlag]` — which `Supremacist` and `Structure_Ideological` also supply | **none.** It is a tier-4 mood meme with no forced precept. |
| b | Drop `Supremacist` instead | keeps `Loyalist`, but loses the forced groups `[Slavery_Acceptable, Slavery_Honorable, …]` and `[Execution_Required, Execution_RespectedIfGuilty, Execution_DontCare]` — the two precepts the spec's table names | ✗ **strike.** Under `requiredPreceptsOnly ✅` those two groups are the only reason `Slavery_Acceptable` and `Execution_Required` appear at all. Dropping Supremacist deletes them. |
| c | Add `Proselytizer` in the freed slot | palette line 101, impact 2, `exclusionTags: [IsolationistProselytizer, VME_Proselytism]` — **no overlap** with `VME_GodEmperor` `[VME_GodEmperor]`, `Supremacist` `[GroupRelation, SupremacistIndividualist, …]`, `HumanPrimacy` `[Primacy]` | legal, count stays 4 |
| d | Substitute `VME_Proselytizing_Never` | `requiredMemes: []`, legal — but `ncomps: 0` and it inverts the doctrine | ✗ strike, it says the opposite thing |

⚠️ `Proselytizer`'s group is `[Proselytizing_Occasionally, Proselytizing_Sometimes,
Proselytizing_Frequently]` — a **3-way roll**. You get proselytizing; you do not get
to specify *frequent*.

**4. 🔴 Recommendation** — **(a)+(c): swap `Loyalist` out, `Proselytizer` in.** The
player would notice Imperial visitors actually preaching at Jawa colonists, which is
the entry's whole ⭐ claim and does not happen today; nothing is lost, because
`Loyalist` was contributing a building slot two other memes already fill.

**5. Diff-ready** — line 105: `**memes** | VME_GodEmperor · Loyalist · Supremacist · HumanPrimacy`
→ `**memes** | VME_GodEmperor · Proselytizer · Supremacist · HumanPrimacy`; line 127 append
"⚠️ the tier is a 3-way roll; *occasional* or *sometimes* is equally likely".

---

## 2 · Hutt Cartel — the Reckoning of Debts

**1. Validator findings, verbatim**

```
🔴 ERROR precept/conflicting-meme     Slavery_Honorable lists ['Guilty', 'Individualist'] in conflictingMemes — hard exclusion
🔴 ERROR precept/required-meme        DrugUse_Essential requires one of ['HighLife']; none is in the meme set
🔴 ERROR precept/npc-disabled         DrugUse_Essential has enabledForNPCFactions:false — it cannot appear on a faction ideo
```

**2. Root cause** — the Cartel's two social memes each independently bar its slavery
precept, and its ⭐ spice precept is both gated and NPC-forbidden.

**3. Legal repair options — Slavery**

| # | option | dump check | cost |
|---|---|---|---|
| a | `Slavery_Honorable` → `Slavery_Acceptable` | `conflictingMemes: []`, `defaultSelectionWeight: 1`, **`ncomps: 0`** | keeps both memes; the doctrine becomes a tooltip |
| b | Drop **both** `Guilty` and `Individualist` | the only way to keep `Slavery_Honorable` — dropping either one alone still trips the other | ✗ **strike.** `Guilty` is the entry's only raid-visible asset: `apparelRequirements → Apparel_TortureCrown` on every Hutt pawn generated. `Individualist` supplies `styleItemTags: Wild`. Both are the top NPC surface per `design.md` §5. |
| c | `GarryFlowers_Slavery_StatusSymbol` / `_Terror` | identical `conflictingMemes: ['Guilty','Individualist']` | ✗ strike — same error, different defName |

**Legal repair options — DrugUse**

| # | option | dump check | cost |
|---|---|---|---|
| d | Drop the `DrugUse` line | the issue has only four precepts and **none carries `defaultSelectionWeight > 0`** — an empty `DrugUse` issue means no drug rules at all, which is mechanically what "spice is our sacrament" wants | none |
| e | Add `HighLife` | ✗ **strike, twice.** It would be a 5th normal meme (over the 1–4 cap), *and* it does not clear the second error — `DrugUse_Essential` stays `enabledForNPCFactions: false`. Note the trap: **`HighLife`'s only `requireOne` group is `[DrugUse_Essential]`, a precept no NPC faction can hold.** |
| f | `DrugUse_MedicalOrSocial` | legal (`conflictingMemes: ['HighLife']`, not held) but it *restricts* drugs | ✗ strike, inverts the doctrine |

**4. 🔴 Recommendation** — **(a) + (d).** The player would notice nothing: the Hutts
still arrive in torture crowns and wild hair, still trade while hostile, and a
recruited Hutt loses only a mood bonus for owning slaves.

**5. Diff-ready** — line 168 `Slavery_Honorable` → `Slavery_Acceptable` (and strike
"⚠️ inert — 0 comps" into the *why* column); delete the `DrugUse | DrugUse_Essential`
row (line 170) and move the ⭐ spice note into the prose.

---

## 3 · Homestead Defense League — the Covenant of Free Wells

**1. Validator findings, verbatim**

```
🔴 ERROR precept/required-meme        RoughLiving_Welcomed requires one of ['TreeConnection', 'PainIsVirtue', 'AM_Monastic', 'Nomadism', 'VME_Nomad', 'VVE_Travelers']; none is in the meme set
🔴 ERROR precept/required-meme        Comfort_Ignored requires one of ['PainIsVirtue']; none is in the meme set
⚠️  WARN  interest/inert               2 precept(s) with NO comps: ['RoughLiving_Welcomed', 'Comfort_Ignored']
```

**2. Root cause** — both austerity precepts are gated behind the same ascetic-meme
family, and the Homestead is a rancher/water faith that holds none of it.

**3. Legal repair options**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop both lines | `RoughLiving_Welcomed` `ncomps: 0`; `Comfort_Ignored` `ncomps: 0`. Neither issue has any precept with `defaultSelectionWeight > 0`, so **nothing punitive fills the vacated slot** | **none** |
| b | Add `PainIsVirtue` (satisfies both gates at once) | ✗ **strike — trades two errors for one worse.** `Charity_Essential`, the entry's ⭐ precept, carries `conflictingMemes: ['Supremacist', 'PainIsVirtue', 'Trader']`. It would also be a 5th normal meme. |
| c | `Comfort_Ignored` → `Comfort_Wanted` | legal (`conflictingMemes: ['PainIsVirtue']`, not held; 1 `MemoryThought`) | ✗ strike on doctrine: "the margin is where they live" becomes "we want soft beds" |
| d | `RoughLiving_Welcomed` → `AM_RoughLiving_Disliked` | the *only* other precept on the issue; `requiredMemes: ['AM_Deforestation']`, not held, and it means the opposite | ✗ strike |

**4. 🔴 Recommendation** — **(a), drop both.** The player would notice nothing whatever:
both precepts have zero comps and no mechanical field, so they were never going to do
anything even if they had been legal.

**5. Diff-ready** — delete the two rows `RoughLiving | RoughLiving_Welcomed` and
`Comfort | Comfort_Ignored` (spec lines 230–231). The table drops to 6 precepts.

---

## 4 · Deep Desert Tribes — the Sun-Debt

**1. Validator findings, verbatim**

```
🔴 ERROR precept/required-meme        Scarification_Heavy requires one of ['PainIsVirtue', 'VME_Fleshcrafters']; none is in the meme set
🔴 ERROR precept/required-meme        Pain_Idealized requires one of ['PainIsVirtue', 'Guilty', 'VME_HolyDiseases']; none is in the meme set
```

**2. Root cause** — the entry writes an ordeal doctrine ("the debt written on the
body") without the one meme that unlocks ordeal precepts.

**3. Legal repair options**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop `VME_Nomad`, add `PainIsVirtue` | `PainIsVirtue` palette line 100, impact 3, `exclusionTags: ['AltruismPain']` — **no overlap** with `NaturePrimacy [Primacy, …]`, `Raider [PacifismRaider, …]`, `VQE_Technophobia [VQE_Technophobia_*]`. Satisfies **both** gates. Count stays 4. **What dropping `VME_Nomad` actually costs is smaller than it looks:** of its four forced groups, `VME_PermanentBases_Despised` is **`enabledForNPCFactions: false`** and could never appear; `RoughLiving_Welcomed` is re-forced by `PainIsVirtue`; only `VME_Travel_Desired` and `VME_Ranching_Nomadic` are genuinely lost. `Nomadic_Preferred` has `requiredMemes: []` so it is unaffected — though under `requiredPreceptsOnly ✅` nothing forces it either way. | **real.** `PainIsVirtue` drags six `requireOne` groups, a `ScarificationCeremony` ritual, four slab-bed designators, the `Morbid` style and `Apparel_TortureCrown`. The tribe becomes an ordeal cult that is also nomadic-in-fiction only. |
| b | Drop both precept lines | cheap, but `Scarification_Heavy` has 3 comps and is one of the few precepts that plausibly changes how an NPC pawn is *generated* (scars on arriving raiders) — **UNVERIFIED in this install; flag for the live check** | loses the ⭐ body-debt doctrine |
| c | Add `VME_Fleshcrafters` for the scarification gate | legal on tags (`FleshAugmentation` unheld here) but **fixes only one of the two errors** — it is not a `Pain_Idealized` gatekeeper — and installs organ-harvest / corpse doctrine on a desert tribe | ✗ strike |
| d | Add `Guilty` for the pain gate | legal on tags, impact 1 — but **fixes only one error**, and it forces `[Charity_Essential, Charity_Important, Charity_Worthwhile]`, i.e. mandatory charity on a faction whose doctrine 2 is "raiding is accounting" | ✗ strike |

⚠️ Whichever way this goes, two prediction errors the validator does **not** flag:
`PainIsVirtue`'s scarification group is `[Scarification_Minor, Scarification_Heavy,
Scarification_Extreme]` — a **3-way roll**, so *Heavy* is not guaranteed; and
`VQE_Technophobia` forces `Research_None` (a real `UnwillingToDo` refusal), which
takes the Research slot, so the spec's `Research_ExtremelySlow` (`ncomps: 0`) will
never appear. `Research_None` is the better precept — update the row rather than
fighting it. (Same meme also forces `AutonomousWeapons_Prohibited`, which is
`enabledForNPCFactions: false` and will silently not appear.)

**4. 🔴 Recommendation** — **(a).** This is the most expensive repair on the sheet and
it is worth it: the player would meet Tusken raiders who arrive scarred and crowned
instead of raiders indistinguishable from any other tribal. If the seat will not
accept the ordeal-cult re-characterisation, take (b) and accept that the body-debt is
fiction.

**5. Diff-ready** — line 252: `**memes** | NaturePrimacy · Raider · VQE_Technophobia · VME_Nomad`
→ `**memes** | NaturePrimacy · Raider · VQE_Technophobia · PainIsVirtue`; line 279
`Research_ExtremelySlow` → `Research_None`.

---

## 5 · Free Droid Enclaves — the Continuity Protocol

**1. Validator findings, verbatim**

```
🔴 ERROR def/unknown-meme             OuterRim_DroidPrimacy is not an installed MemeDef
🔴 ERROR precept/required-meme        Corpses_DontCare requires one of ['PainIsVirtue', 'Cannibal', 'Supremacist', 'Raider', 'Inhuman', 'Necrolatry', 'VME_BloodCourt', 'VME_Fleshcrafters']; none is in the meme set
```

**2. Root cause** — one meme that does not exist in this load order, and one precept
gated behind eight memes of which seven are illegal here.

**3a. `OuterRim_DroidPrimacy`** — confirmed absent from `MemeDef.json` and from
`ideology_palette.md`. No installed def contains `OuterRim` or `Droid`. The spec's own
`MayRequire` table (line 86) maps the prefix to `neronix17.outerrim.droiddepot`, which
is **not in the 585 active mods**. Naming it is the silent no-op the skill warns about.

| # | replacement | dump check | cost |
|---|---|---|---|
| a | **`VME_Emancipation`** | palette line 127, impact 1, `exclusionTags: [GroupRelation, VME_EmancipationVsRaiders, VME_EmancipationVsViolentConversion, VME_EmancipationVsBushido]` — **no overlap** with `Transhumanist`, `Collectivist`, `VME_MechanoidSupremacy`. Forces two **single-option** (deterministic) groups: `VME_Slavery_Forbidden` (High impact, `PreceptComp_UnwillingToDo`) and `VME_SlaveTrading_OnlyBuying` (`PreceptComp_UnwillingToDo`), both `enabledForNPCFactions: true` | **negative cost — this is a gain.** See below. |
| b | Leave the slot empty (3 normal memes) | legal — 1–4 is the cap, not a target | loses nothing that exists today, gains nothing |
| c | Any other primacy meme | `HumanPrimacy` and `NaturePrimacy` both carry `exclusionTags: [Primacy]`, and so does `VME_MechanoidSupremacy` | ✗ strike, collision |

🔴 **Why (a) matters more than filling a slot.** Faction 5 sets `requiredPreceptsOnly ✅`.
`Slavery_Abhorrent` — the ⭐ restraint-bolt doctrine, called "the best single dramatic
collision in the roster" — is forced by **none** of the entry's memes, so **as written
it will not exist in the game at all.** `VME_Emancipation` is the only palette-legal
meme that forces a slavery refusal, and it forces two.

**3b. `Corpses_DontCare`** — the eight-gatekeeper check, re-verified today and
unchanged from `design.md` §6: `Necrolatry` ✗ (`NecrolatryTranshumanist` clashes with
`Transhumanist`) · `VME_Fleshcrafters` ✗ (`FleshAugmentation`, same clash) · `Inhuman`
✗ (`factionWhitelist: ['HoraxCult']`) · `Raider` ✗ (`Slavery_Abhorrent.conflictingMemes`)
· `Supremacist` ✗ and `Cannibal` ✗ (both force an `Execution_*` group that destroys
`Execution_Abhorrent`) · `PainIsVirtue` ✗ (`conflictingMemes` on both `Execution_Abhorrent`
and `Charity_Worthwhile`) · **`VME_BloodCourt` is the only legal one** — impact 3, no tag
clash — and it installs a duelling blood-cult with a leadership-challenge ritual on a
droid enclave. Thematically absurd; and with `VME_Emancipation` taking the fourth slot
it is no longer even available.

**4. 🔴 Recommendation** — **replace the meme with `VME_Emancipation`; drop
`Corpses_DontCare`.** The player would notice the one thing the entry exists for: Free
Droid pawns that flatly refuse to enslave or sell a person, guaranteed by a meme rather
than hoped for from a precept the engine was never going to grant. The lost line — "the
body is a chassis" — was a `ncomps: 0` precept that would have shown nothing anyway.

**5. Diff-ready** — line 297: `OuterRim_DroidPrimacy` → `VME_Emancipation`
(`MayRequire="vanillaexpanded.vmemese"`); delete the `Corpses | Corpses_DontCare` row
(line 319); change the `Slavery | Slavery_Abhorrent` row (line 314) to
`Slavery | VME_Slavery_Forbidden` — the precept the new meme actually forces.

---

## 8 · Geonosian Foundry Hive — Meckgin

**1. Validator findings, verbatim**

```
🔴 ERROR precept/required-meme        Comfort_Ignored requires one of ['PainIsVirtue']; none is in the meme set
🔴 ERROR precept/required-meme        RoughLiving_Welcomed requires one of ['TreeConnection', 'PainIsVirtue', 'AM_Monastic', 'Nomadism', 'VME_Nomad', 'VVE_Travelers']; none is in the meme set
🔴 ERROR precept/required-meme        Corpses_DontCare requires one of ['PainIsVirtue', 'Cannibal', 'Supremacist', 'Raider', 'Inhuman', 'Necrolatry', 'VME_BloodCourt', 'VME_Fleshcrafters']; none is in the meme set
     INFO  interest/live-precepts       2/8 precepts carry comps; 1 High impact
⚠️  WARN  interest/inert               6 precept(s) with NO comps: ['Comfort_Ignored', 'RoughLiving_Welcomed', 'Research_Fast', 'OrganUse_Acceptable', 'Corpses_DontCare', 'Execution_DontCare']
```

**2. Root cause** — one missing gatekeeper meme, `PainIsVirtue`, sits behind all three
errors at once.

**3. Legal repair options**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop all three lines | all three have `ncomps: 0`. Comfort and RoughLiving have **no** `defaultSelectionWeight > 0` precept, so those slots stay empty. Corpses does: `Corpses_Ugly` (`classic: true`, `dsw: 1`) fills it | **none in play.** The only difference is a *recruited* Geonosian inheriting the default corpse-disgust. |
| b | Drop `Collectivist`, add `PainIsVirtue` | legal: `PainIsVirtue [AltruismPain]` vs `Tunneler []`, `VME_HardcoreIndustrialism [VME_Work, …]`, `VME_InsectoidSupremacy [VME_InsectoidVsDefilers]` — no overlap; and it is a gatekeeper for **all three** failed precepts. `Collectivist` is the cheapest drop: impact 1, one forced group (`WorkDrive_Tripled`, `ncomps: 0`, and a player-only moral-guide ability) | **real, and mostly unwanted.** It converts a work-cult into a pain-cult and adds six forced groups, a scarification ritual and torture crowns. Meckgin's doctrine is "idleness is the collapse", not ordeal. |
| c | Drop `Tunneler` or `VME_InsectoidSupremacy` instead to make room | both are the faction's identity (`Tunneler` → `FungalGravel`, `Stonecutting`, `TattooBodyInsect`; `VME_InsectoidSupremacy` → the hymn ritual) | ✗ strike |

🔴 **Blunt: this entry is not worth repairing beyond the delete.** Two of its eight
precepts carry any comps at all; after the fix it is a five-precept religion of which
three are still inert. It passes the validator and fails `design.md` §7 check 1 — no
tier-A/tier-B precept, no tier-1 refusal. Fixing the errors makes it *legal*, not
*interesting*. **File a separate design pass; do not let a green gate imply the entry
is done.**

**4. 🔴 Recommendation** — **(a), drop all three.** The player would notice nothing.

**5. Diff-ready** — delete rows `Comfort | Comfort_Ignored`, `RoughLiving | RoughLiving_Welcomed`
and `Corpses | Corpses_DontCare` (spec lines 445, 446, 449); add a line under the table:
"⚠️ this entry has no tier-1 refusal and needs a design pass, not a validation patch."

---

## 9 · Ascendant Helix — the Ascendant Genome

**1. Validator findings, verbatim**

```
🔴 ERROR meme/exclusion               Transhumanist + VME_Fleshcrafters all carry exclusionTag 'FleshAugmentation' — they cannot coexist
🔴 ERROR precept/conflicting-meme     Charity_Worthwhile lists ['Supremacist'] in conflictingMemes — hard exclusion
```

**2. Root cause** — two body-modification memes that the engine treats as the same
slot, plus a politeness precept that `Supremacist` bars outright.

**3. Legal repair options — the meme collision**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop `VME_Fleshcrafters`, keep `Transhumanist` | `Transhumanist` forces seven groups, and **three of them are the spec's own precept rows**: `BodyMod_Approved`, `Biosculpting_Accelerated`, plus the free `NutrientPasteEating_DontMind`. It also brings `Techist` styles, Ultratech weapon preference and four architect entries | **none.** The engine was already going to drop one of the pair silently — this only makes the outcome deterministic and picks the one the design was written around. |
| b | Drop `Transhumanist`, keep `VME_Fleshcrafters` | `VME_Fleshcrafters` forces `VME_BodyMod_OnlyBiological`, which **contradicts** the spec's `BodyMod_Approved` row, plus `VME_OrganUse_PostMortem`, `VME_Death_DontCare`, `Corpses_DontCare` and a scarification ritual | ✗ strike — trades the error for a doctrinal contradiction inside the same table |

**Legal repair options — Charity**

| # | option | dump check | cost |
|---|---|---|---|
| c | Drop the `Charity` row | **all three** Charity precepts carry `conflictingMemes: ['Supremacist', 'PainIsVirtue', 'Trader']` — there is no non-conflicting Charity position while `Supremacist` is held | politeness stays in the prose, which is where the spec already says it lives ("deliberately mild") |
| d | Drop `Supremacist` to keep `Charity_Worthwhile` | ✗ **strike.** `Supremacist` forces the `Slavery_*` and `Execution_*` groups that produce the entry's `Slavery_Acceptable` and `Execution_DontCare` rows, and it is doctrine 2 ("the unmodified are earlier versions"). Trading it for a 22-comp precept whose comps are `DevelopmentPoints` + `CharityFulfilled_*` memories — tier C, and invisible on an NPC faction — is a bad trade. |

**4. 🔴 Recommendation** — **(a) + (c).** The player would notice nothing change; they
would simply get the transhumanist Helix the spec describes rather than a coin-flip
between two half-applied body doctrines.

**5. Diff-ready** — line 465: delete `· VME_Fleshcrafters` from the meme list (three
normal memes remain, legal); delete the `Charity | Charity_Worthwhile` row (line 494).

---

## 10 · Blackstar Company — the Contract

**1. Validator findings, verbatim**

```
🔴 ERROR precept/conflicting-meme     Apostasy_Horrible lists ['Guilty'] in conflictingMemes — hard exclusion
```

**2. Root cause** — the spec already caught this once and mis-diagnosed the scope: it
switched `Apostasy_Abhorrent` → `Apostasy_Horrible` believing only the first conflicts.

🔴 **Verified in the dump today: every negative Apostasy position conflicts with
`Guilty`.** `Apostasy_Abhorrent`, `Apostasy_Horrible`, `Apostasy_Disapproved` and
`Apostasy_Despicable` all carry `conflictingMemes: ['Guilty']`. The only clean precept
on the issue is `VME_Apostasy_Accepted`, which has `ncomps: 0` and means the opposite.
**The spec's line 541–545 note is wrong and should be rewritten, not just re-pointed.**

**3. Legal repair options**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop the `Apostasy` row entirely | no `defaultSelectionWeight > 0` precept exists on the issue, so nothing fills the slot | the broken-contract doctrine becomes fiction |
| b | Drop `Guilty`, take `Apostasy_Abhorrent` | legal once `Guilty` is gone. But `Guilty` is the Company's **only raid-visible asset** (`apparelRequirements → Apparel_TortureCrown`) and doctrine 3 is literally "that is what `Guilty` is for". Apostasy precepts hook `ChangedIdeo` — `design.md` §3.4 tier D, a handful of fires per campaign, and effectively never for a faction the player does not convert | ✗ strike — trades a costume that fires on every raid for a precept that fires almost never |
| c | `VME_Apostasy_Accepted` | legal, `ncomps: 0` | ✗ strike — it asserts the reverse of the entry's central taboo |

**4. 🔴 Recommendation** — **(a), drop the row and keep `Guilty`.** The player would
notice nothing: the "broken contract is unclean" doctrine reaches them through the
Company's quest behaviour and its helmets, not through a precept that fires on ideo
conversion.

**5. Diff-ready** — delete the `Apostasy | Apostasy_Horrible` row (line 532) and
replace the ⚠️ note at lines 541–545 with: "**All four negative `Apostasy` precepts
list `Guilty` in `conflictingMemes`.** There is no legal apostasy position for this
faction; the doctrine stays in the description."

---

## 11 · the Junkers — no doctrine, only the ladder

**1. Validator findings, verbatim**

```
🔴 ERROR precept/required-meme        RoughLiving_Welcomed requires one of ['TreeConnection', 'PainIsVirtue', 'AM_Monastic', 'Nomadism', 'VME_Nomad', 'VVE_Travelers']; none is in the meme set
🔴 ERROR precept/required-meme        Comfort_Ignored requires one of ['PainIsVirtue']; none is in the meme set
⚠️  WARN  interest/inert               7 precept(s) with NO comps
```

**2. Root cause** — the same ascetic gate as factions 3 and 8; the Junkers hold three
normal memes and none of them is a gatekeeper.

**3. Legal repair options**

| # | option | dump check | cost |
|---|---|---|---|
| a | Drop both lines | both `ncomps: 0`; neither issue has a `defaultSelectionWeight > 0` precept | **none — and it serves the design.** Two precepts that assert nothing, deleted from a religion whose point is asserting nothing. |
| b | Add `PainIsVirtue` (there *is* a free slot — only 3 normal memes) | legal on tags: `[AltruismPain]` vs `Raider [PacifismRaider, AltruismRaider, TraderRaider, …]`, `Cannibal [VME_NoCannibalsAndNonviolenceVow, Pacifism, AltruismCannibal]`, `VME_Scrapper []`. Clears both errors. Would add torture crowns and slab beds | ✗ **strike — it trades a validator error for a design error.** The entry says `requiredPreceptsOnly ✅ 🔴 **essential here** — it is what makes the religion empty`. `PainIsVirtue` forces **six** groups. It would make the Junkers the most doctrinally loaded faction in the roster, which is the exact opposite of the brief. |

⚠️ One prediction error the validator does not flag: `Cannibal`'s group is
`[Cannibalism_Preferred, Cannibalism_RequiredStrong, Cannibalism_RequiredRavenous]`.
Under `requiredPreceptsOnly ✅` the spec's `Cannibalism_Acceptable` (`ncomps: 0`) never
appears — the slot is taken by one of those three, all of which carry comps. That is a
**gain** the spec does not claim, and it means the "not ritual, just food" line
understates what the player meets.

**4. 🔴 Recommendation** — **(a), drop both.** The player would notice nothing, which
is the entry's stated goal.

**5. Diff-ready** — delete the rows `RoughLiving | RoughLiving_Welcomed` and
`Comfort | Comfort_Ignored` (spec lines 586–587); change `Cannibalism_Acceptable`
(line 581) to "`Cannibalism_Preferred` / `_RequiredStrong` / `_RequiredRavenous` — a
3-way roll forced by `Cannibal`; `_Acceptable` is not reachable here".

---

## Footnote — an invisibility defect on a VALID entry

**7 · Deepwater Compact — the Balance** passes the gate. It should not be shipped as
it stands.

```
StyleCategoryDef VME_SecularSpirituality  (Vanilla Ideology Expanded - Memes and Structures)
  thingDefStyles: 0 · addDesignators: 0 · addDesignatorGroups: 0 · iconPath: present
```

`VME_SecularSpirituality` is the Compact's **only** `styles` entry, and it supplies no
art at all — one UI icon and nothing else. For comparison, `Techist` ships 78
`thingDefStyles`, `Totemic` 92, `Rustic` 77, `AM_Scavenger` 60. Per `design.md` §5 the
raid silhouette is the highest-value NPC design surface, and the Compact currently has
none of it. **This is not a validator error and never will be** — it is a real defect
and it costs the entry its entire visual identity. Recommend adding a second style
category with actual `thingDefStyles` (the ceiling is 3). Not repaired here; it is a
design call.

---

## Summary — zero-cost repairs first

| # | faction | errors | recommended action | design cost |
|---|---|---|---|---|
| 3 | Homestead Defense League | 2 | drop `RoughLiving_Welcomed` + `Comfort_Ignored` | **none** — both 0-comp, no default fills either slot |
| 11 | the Junkers | 2 | drop `RoughLiving_Welcomed` + `Comfort_Ignored` | **none** — and it serves the "empty religion" brief |
| 1 | Galactic Empire | 2 | swap `Loyalist` → `Proselytizer` | **none** — Loyalist has no forced precept; the swap makes the ⭐ doctrine real |
| 9 | Ascendant Helix | 2 | drop `VME_Fleshcrafters`; drop `Charity_Worthwhile` | **none** — the engine was dropping one meme anyway; this picks which |
| 8 | Geonosian Foundry Hive | 3 | drop `Comfort_Ignored`, `RoughLiving_Welcomed`, `Corpses_DontCare` | **none*** — *only a recruited drone inherits `Corpses_Ugly`.* 🔴 Needs a design pass regardless: 2/8 precepts have comps. |
| 2 | Hutt Cartel | 3 | `Slavery_Honorable` → `Slavery_Acceptable`; drop `DrugUse_Essential` | **cosmetic** — the slavery doctrine becomes a tooltip |
| 10 | Blackstar Company | 1 | drop the `Apostasy` row; keep `Guilty` | **cosmetic** — no legal apostasy position exists while `Guilty` is held |
| 5 | Free Droid Enclaves | 2 | `OuterRim_DroidPrimacy` → `VME_Emancipation`; drop `Corpses_DontCare` | **real, and positive** — turns the ⭐ restraint-bolt collision from a precept that could not exist into two guaranteed refusals |
| 4 | Deep Desert Tribes | 2 | drop `VME_Nomad`, add `PainIsVirtue` | 🔴 **real — the most expensive repair on this sheet.** Six new forced groups, a ritual, torture crowns; nomadism survives only as fiction. |

**5 of 9 repair at zero design cost** (3, 11, 1, 9, 8). Two are cosmetic (2, 10). One
is a net gain (5). One is expensive (4).

🔴 **A green gate on all eleven would still not mean the roster is buildable.** §0 fact
1 stands: no `FactionDef` field sets precepts, so the 88 precept rows in the spec are
predictions about what the memes force. The repairs above make the predictions honest;
they do not make them authorable.
