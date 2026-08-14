# Expected-failure signatures — the load launched 2026-08-13/14 evening

## ✅ RESULTS — startup harvest, 2026-08-14 ~01:23, 5,837 lines

_Snapshot frozen **before any bridge mutation** at
`observed/2026-08-13/logs/Player.startup.585.2026-08-14.log` (gitignored —
transient, so the findings live here instead). **No map had been generated when
this was taken**, which bounds what it can answer._

| row | verdict | evidence |
|---|---|---|
| 3 `missingartfixes` removed | ✅ **PASS** | `Failed to find any textures at` = **0**. The 7 successors cover it. |
| 5 gravship quest patch | ✅ **PASS (no loud failure)** | 0 errors naming `BTD_DownedGravship`. The 2 `PatchOperationReplace` failures in the log are **Biomes! Caverns** (`2969748433`), not ours. Guard matched, Replace applied. ⚠️ Description rendering still needs the Quests tab. |
| 6 GravTech | ✅ **PASS** | 0 cross-reference failures on `VGE_GravshipBuildingBase`/`ArtilleryBase` — the four turrets resolved their parents. Independently corroborated by the dump: **ThingDef +243**. |
| 8 `rimdefdump` last | ✅ **PASS** | Fresh dump `modCount: 585`, matching `ModsConfig` exactly. rev591, captured 01:20:26. |
| baseline | ✅ **HELD** | **25** `Could not resolve cross-reference`, **0** `Could not load reference to` — unchanged from the previous load despite +5 mods. |
| 1–2 art baseline | ⏸ **not answerable from a log**, by design | Needs the screenshots. |
| 4 ground hulk | ⏸ **untestable** | Map generation only, and no map was generated. |
| 7 `[JawaSea]` | ⏸ **untestable** | Worldgen only, and worldgen is HELD this session. |
| O12 pawn-gen NRE | ⏸ **NOT SETTLED** | 0 hits — **but every map-generation marker is also 0.** A zero for something with no opportunity to occur is not evidence. |

### 🔴 THE FINDING THAT OVERTURNS A SHARED BELIEF: the log DOES confirm Cherry Picker

Two seats recorded that Cherry Picker's result *cannot* be read from the log,
because it is silent for an unresolvable key and silent for an out-of-scope def.
**That is true of FAILURES only. This build logs every SUCCESS, by name:**

```
[Cherry Picker] The database was processed in 01.09090 seconds and the
following defs were removed:
 - IncidentDef/ShamblerAssault, … - ThingDef/GravForge,
 - RecipeDef/Make_GravcoreGF, - ThingDef/AdvShip_GravReactor
```

**22 requested · 22 removed · 0 requested-but-missing · 0 unexpected · 0 `FAILED:`.**

⇒ 🔴 **The gravcore scarcity gate is CLOSED, and proven rather than assumed.**
`ThingDef/GravForge` and `RecipeDef/Make_GravcoreGF` are both gone. **No
architect-menu check is needed.** Parse the block by anchoring on the header line
and reading `- ` entries until they stop — **the last entry has no trailing
comma**, which produced three false negatives before I stopped hand-grepping.



_OPS. **Written BEFORE the launch, deliberately** — that is the whole point. A
signature written after reading the log is not a prediction, it is a
rationalisation, and it cannot tell you the difference between "this worked" and
"I did not look properly". Closes queue item **O5**._

🔴 **REVISED 00:0x after three owner rulings landed post-draft. Mod set is 583,
not 581, and rows 1–2 are INVERTED.** Superseded numbers left visible on purpose;
a sheet that quietly rewrites itself teaches nobody.

**Mod set: 583 active** (`grep -c "<li>"` minus 5 `<knownExpansions>`).
Previous load ran **580**. Net: **+GravTech ×3, +`jawaseashaper`,
−`missingartfixes`**, and the two new art fixes were **added then deliberately
pulled** (rows 1–2).

🔴 **Read `vendor/wisdom/benign_log_errors.md` §0 before triaging anything.**
Baseline from the previous load: **25** `Could not resolve cross-reference`,
**0** `Could not load reference to`. A change in those two is the first check.

---

## The trap that governs half this sheet

**Loose-texture overrides CANNOT FAIL IN THE LOG.** When one loses load order
RimWorld simply draws the other file — no error, no warning, no line. For these,
*"the log is clean"* is not evidence of anything, and the only evidence is a
screenshot of the right pawn facing the right way.

---

## 🔴 Rows 1–2 — INVERTED. This load is the UNFIXED BASELINE.

**Owner's ruling: the evidence that an art fix is needed is a screenshot of the
defect as it currently renders, UNFIXED.** Both overrides were therefore **pulled
from `ModsConfig.xml`** before launch. **We now WANT to see the defect.** Seeing
it is a PASS for this session; *not* seeing it means the defect was never real and
the fix should be dropped rather than shipped.

| # | pulled mod | **what SHOULD be visible now** | if it is ABSENT |
|---|---|---|---|
| 1 | `mandrake.phytokinbarkheadfix` | A female Phytokin with `VRE_BarkSkin` + `Jaw_Heavy`, walking **east or west**, shows a **front-facing head on a side-facing body** — filled from the north view at −90°. | The donor shipped the file, or the head never rolls. **Drop the fix**, do not ship it. |
| 2 | `mandrake.kotorbandoliernorthfix` | A pawn wearing `bandolier_chewbacca` or `bandolier_traveler`, **from behind**, shows **chest pouches on its back** at draw layer 65. | Same — the premise is wrong and the 20 authored files are not needed. |

⭐ **This is why the pull was right:** an art fix that is never seen failing cannot
be verified. Both are the silent-failure class, so without the baseline shot there
is no way to separate *"the fix worked"* from *"nothing was ever wrong"*.
Re-adding is one line each; both declare their own `loadAfter`.

## Row 3 — `mandrake.missingartfixes` REMOVED (was @555)

- **Expected: NOTHING.** All 7 textures are md5-identical to the per-donor successors.
- **FAIL, loud:** `Failed to find any textures at <path>` — fires only when *every*
  direction of a `Graphic_Multi` is absent, so this one is real, not silent.
- **Also FAIL:** any startup complaint naming `mandrake.missingartfixes`.
- List entry dropped **first**, folder left on disk — deliberately, so the game
  never boots pointing at a folder that might later vanish.

## Row 4 — the ground hulk (`JawaGroundHulk` GenStep + PrefabDef + register patch)

- **FAIL, def half:** `Could not resolve cross-reference` naming `Jawa_GroundHulk`
  or its prefab → **def loader**, a live mod-set problem.
- **FAIL, runtime half:** 🔴 surfaces as a silent *"GenStep failed"* with nothing
  naming the hulk.
- **PASS:** a hulk present on a **newly generated** map. Map generation only — an
  existing map shows nothing, and that is not a failure. **State which map.**

## Row 5 — `BTDGravshipQuest_GrammarFix.xml`

- **FAIL, loud:** a red error naming `PatchOperationReplace` on
  `BTD_DownedGravship` → the `FindMod` guard missed, i.e. the mod-name string is
  wrong. Guard reads `[BTD] Gravship Blueprints`, taken from its About.xml root.
- **FAIL, quiet:** `Grammar unresolvable. Root 'questDescription'` appears again
  (exactly 1 occurrence last load).
- **PASS: 🔴 POSITIVE OBSERVATION ONLY** — open the Quests tab and read the Downed
  Gravship description. The error's *absence* proves nothing; the quest may not
  have fired.

## Row 6 — 🆕 GravTech trio (`als.gravtech` @555 → `.bc` @556 → retexture @557)

🔴 **The parent is `forbidden_mods.md`-FORBIDDEN and is in by owner override**,
on condition the economy is cherry-picked out **in-game this session**.

- **FAIL, loud:** `Could not resolve cross-reference` on `VGE_GravshipBuildingBase`
  / `VGE_GravshipArtilleryBase` → a turret's `ParentName` missed its parent.
  Ordering verified: 555–557 all sit after `vanillaexpanded.gravship` @375.
- 🔴 **THE REAL RISK IS NOT A LOG LINE — IT IS THAT THE CHERRY-PICK NEVER HAPPENS.**
  Cherry Picker has **no config file**; its list is written from the in-game
  settings UI. **If nobody does that pass, we have shipped craftable gravcores and
  the quest-only scarcity gate the campaign leans on is gone**, silently and with
  a clean log. Must remove: **Grav Forge, Singularity Reactor, grav-engine
  recipes.** Keep the cannons.
- **Player-zero note:** the Singularity Cannon is **1000 damage / AP 100 with
  explosion falloff disabled**, and its own author warns it can destroy the firing
  gravship — in a campaign where the gravship is the one thing shipping DEEP.
  Flagged to VISION for the ladder, not mine to rule.

## Row 7 — 🆕 `mandrake.jawaseashaper` @581 (ships a DLL)

- **PASS: grep `[JawaSea]`.** It self-reports every acceptance test — water
  fraction against the 22–28% band, per-body tile count, perimeter, compactness,
  mean latitude, orphan tiles released. **Judged by reading that line across a few
  seeds**, not by looping to hit a number.
- **FAIL, caught:** `Error in WorldGenStep:` — `WorldGenerator` try/catches each
  step, so worldgen continues with an **unshaped planet** rather than dying.
- 🔴 **FAIL, silent — check this FIRST if `[JawaSea]` never appears:** defining a
  `WorldGenStepDef` does **not** make it run. `PlanetLayerDef.GenStepsInOrder`
  iterates the layer def's own private `worldGenSteps` list, **not** the
  DefDatabase — so a step absent from `PlanetLayers.xml`'s list loads, validates
  and is never called, **with no log line at all**. The mod ships a
  `PatchOperationAdd` for it. **Suspect that patch before suspecting the C#.**
  *(CREATE's finding, and the most useful thing handed to me tonight.)*

## Row 8 — `mandrake.rimdefdump` must still be LAST

Verified @582 of 583. **FAIL: the dump's own mod count is not 583** — which
invalidates every derived artefact, silently. The previous dump described **573**
while **580** were loaded. **Check a dump's own count before trusting it, every
time.**

---

## Two counts to record on arrival, with derivation

1. `grep -c "Could not resolve cross-reference"` — **baseline 25.** Higher: the new
   mods are first suspects. Lower: something that used to load did not, which is
   not automatically good news.
2. `grep -c "Could not load reference to"` — **baseline 0.** Non-zero means a
   **saved file** holds a dead name. Different system, different fix. **Never
   conflate the two phrasings.**

## One open question this load settles for free

`Error while generating pawn. Rethrowing … NullReferenceException` from
`AlienRace.GenerationChanceGenderless` — **9 last load, not waived** (queue
**O12**). 8 were on a droid **I debug-spawned myself**, so they may be an
artefact. **If it fires this session on pawns nobody spawned by hand, it is live** —
relation generation runs for faction leaders at worldgen and fails silently there.

⚠️ **Method note, my own error, recorded because it is the reusable part:** I first
censused exceptions with a `^`-anchored grep and **missed every inline one**,
under-reporting 44 as a handful. Correcting it is what surfaced the gravship quest
bug and O12. **Do not anchor an exception census at line-start.**
