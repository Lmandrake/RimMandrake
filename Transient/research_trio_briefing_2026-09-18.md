# RESEARCH_TRIO_RETIRE_1 — Evidence Briefing (2026-09-18)

Read-only evidence prep. Not a ruling. Prepared because the owner said "I need much more information here."

## 1. The 17 projects

Located on disk (Steam workshop root, packageId confirmed by grepping every `About/About.xml` under
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/`):

| packageId | folder | display name |
|---|---|---|
| `petetimessix.researchreinvented.steppingstones` | `2868389782` | Research Reinvented: Stepping Stones |
| `als.gravtech` | `3545374124` | GravTech |
| `als.gravtech.bc` | `3628174105` | GravTech - Big cannons |
| (4th, dependent, NOT in the retire list) `HalituisAmaricanous.gravtechbigcannons` | `3738856637` | GravTech - Big cannons Retextured (hard `modDependencies` on `als.gravtech.bc`) |

Own `ResearchProjectDef`s read straight from each mod's Defs XML on disk (`als.gravtech`'s
`1.6/Defs/Research_GT.xml`, `als.gravtech.bc`'s `1.6/Defs/Research_GTbc.xml`, steppingstones'
`v1.6/Defs/ResearchProjectDefs_Basic.xml` + `ResearchProjectDefs_Electricity.xml`), cross-checked
against `infrastructure/output/research_manifest_draft.csv` (2026-09-04 capture, fingerprint
`3174253fcd55f69c`, 595 mods) for tab/tier/cost/prereq and against a live `grep -rn` of `src/` and
`design/` for OUR references:

| defName | label | mod | tab / tier (manifest) | unlocks (buildings/recipes, read from the mods' own XML) | OUR content references it? |
|---|---|---|---|---|---|
| `GravForge` | grav forge | als.gravtech | The Utinni / T4 | `ThingDef GravForge_GT` (the Grav Forge building) + `RecipeDef Make_GravcoreGF` (Gravcore crafting) — both restored on Cherry Picker by 2026-09-01 owner ruling | YES — `cherrypick_build.py` keeps its building/recipe explicitly OFF the cut list; `load_session.py`, `JawaBenchTerrainTools.cs`, `research_manifest_validate.py` all name it; `RUT_ResearchRetag.xml`/`RUT_ResearchTabAssign.xml` patch its tab/tier |
| `GravWeapon` | grav weapon | als.gravtech | The Strange Schools / T4 | Personal weapons: `GravRifle`/`GravBlaster`/`GravHammer`/`Apparel_GravPack` (named in the 2026-09-01 owner ruling, Armory-side) | YES — `RUT_ResearchRetag.xml` + `RUT_ResearchTabAssign.xml` retag it; carries the Rust Cathedral boon-gate ruling |
| `GravTuning` | precise grav tuning | als.gravtech | The Utinni / T4 | Empty AI cores + special prosthetics from Gravcores (per its own description); prereq'd by `GravBionics`, `AdvShipParts`, `BlackHole_GT` | YES — retag patches only |
| `GravBionics` | grav bionics | als.gravtech | The Reach / T4 | Personal bionic implants `GravArmor`/`GravHands`/`GravSpine`/`GravStomach` | YES — retag patches; carries the 2026-09-04 Rust Cathedral boon-gate ruling |
| `AdvShipParts` | advanced ship parts | als.gravtech | The Utinni / T4 | `ThingDef Apparel_CerebrexNode` requiredAnalyzed; unlocks the Cerebrex computer core (ship tree) | YES — retag patches only |
| `BlackHole_GT` | taming a Black Hole | als.gravtech | The Utinni / T4 | Ship-tree "big cannons" family node; prereq for `GTbc_BigCannons` | YES — retag patches only |
| `GTbc_BigCannons` | big cannons | als.gravtech.bc | The Utinni / T4 | `GravBlasterArtillery_GTbc`, `GravliteDefenseTurret_GTbc`, `GravRailArtillery_GTbc`, `TheSingularityCannon_GTbc` (heavy gravship cannons) | YES — retag patches only |
| `RR_LateralThinking` | lateral thinking | steppingstones | Jawa Scavenging / T0 | Universal orphan-tech prereq ("prerequisite to any orphan research tech, including modded ones") | YES, heavily — depended on by **33 other live research rows** (see §3), incl. `design/Jawa/research_review/*` frozen decks |
| `RR_Organization` | organization | steppingstones | Jawa Scavenging / T0 | Root tribal-start node | YES — retag patches; depended on by 3 other rows incl. our own `VFET_Fire` |
| `RR_BasicApparel` | simple apparel | steppingstones | Jawa Scavenging / T0 | Gate for simple-apparel crafting | YES — depended on by 16 rows, mostly the KOTOR apparel chain (`guy762_ResearchKotOR_*`) |
| `RR_BasicCraftingFacilities` | crafting facilities | steppingstones | Jawa Scavenging / T0 | Gate for basic crafting benches | YES — depended on by `CarpetMaking`/`Smithing`/`Stonecutting` |
| `RR_BasicFoodPrep` | food preparation | steppingstones | Jawa Scavenging / T0 | Gate for food-prep recipes | YES — depended on by `Pemmican`/VCE condiments/stew rows |
| `RR_ElectricityBasics` | electricity | steppingstones | The Workshop / T0 | **Replaces vanilla `Electricity` as the gate for the Power tab** (own `discoveredLetterText` unlocks generators/conduits); vanilla's own `Electricity` row is itself re-pointed to prereq THIS def | YES, load-bearing — depended on by **15 other live rows**, including our own **`RM_WM_AutomatedSmelterRestoration`** (WreckedMachines, a VALIDATED north-star mod) and vanilla `Electricity` itself; also the target of TWO of our own defensive fixes (see below) |
| `RR_HeatingElements` | heating elements | steppingstones | Jawa Scavenging / T0 | Gate for heaters | YES — depended on by `AirConditioning`/`AtmosphericHeater`/`BiofuelRefining` |
| `RR_PowerGenerators` | dynamos | steppingstones | The Workshop / T0 | Gate for power generators | YES — depended on by `BioferriteGenerator`/`BiofuelRefining`/`ToxifierGenerator`/`WatermillGenerator` |
| `RR_IncendiaryWeapons` | incendiary weapons | steppingstones | Jawa Scavenging / T0 | Gate for incendiary weapons | YES — depended on by `BioferriteIgnition` + 3 KOTOR blaster rows |
| `RR_EMP` | EMP weapons | steppingstones | The Strange Schools / T1 | Gate for EMP weaponry (anti-mechanoid) | YES — depended on by `guy762_ResearchKotOR_vibroweapons` |

**Total: 17.** (`als.gravtech` ships an 18th research row, `GravEngineBuild`, that is NOT in this list —
it does not appear anywhere in the 521/515-row manifest census and is explicitly flagged in
`cherrypick_build.py` line 235 as "deliberately NOT here". Not chased further; flagged as an open
loose end, not one of the 17 at risk.)

**`RR_ElectricityBasics` is unusually deep in our own code**, beyond XML retagging: it is the subject
of a real engine crash bug (`QUICKTEST_POSTSETUP_CRASH_1`) — steppingstones' own patch mechanism
injects it as its OWN prerequisite (a self-loop), which silently `StackOverflowException`s
`ResearchManager.FinishProject` on any fresh-graph auto-research walk (quicktest colonies, not the
live save). Two of our own defensive fixes exist because of it:
- `src/RimMandrake/MandrakePatches/Patches/RRElectricityBasicsSelfPrereq_Fix.xml` (XML patch,
  `MayRequire`-gated on the steppingstones packageId, so it becomes a harmless no-op if the mod is
  removed)
- `src/RimMandrake/Ninefold/Source/Patch_ResearchManager_NoSelfPrereq.cs` (a generic Harmony prefix
  on `ResearchManager.FinishProject` that strips any self-referencing prerequisite from any def —
  harmless on every other def, so it also survives the mod's removal as a no-op)
Both fixes are safe under any of the three routes below; neither depends on the mod staying
installed. But their existence is proof that this specific defName has already cost a real crash
investigation.

## 2. Which carry owner rulings

Found in `infrastructure/state/ledger/events.jsonl` and `infrastructure/state/items/RESEARCH_TRIO_RETIRE_1.md`
/ `RESEARCH_TREE_NORMALIZATION_1.md`. Four of the 17 defNames carry dated, specific owner rulings;
the rest inherit only the general "manifest reviewed and approved" ruling.

**Directly named, dated rulings (4 defNames):**

- **`GravWeapon`** — owner ruling, question card, **2026-09-01** (ledger `RESEARCH_MANIFEST_DRAFT_1`,
  `2026-09-01T15:17:43Z`): *"associate this ultra-powerful GravTech as something only the Rust
  Cathedral can grant as a boon. The weapon tech of the Rataka."* — personal weapon unlocks
  (GravRifle/GravBlaster/GravHammer/Apparel_GravPack) stay in Armory but faction-held by Rust
  Cathedral; ship-hardpoint unlocks need a new, not-yet-authored Ship-tree node.
- **`GravForge`** — same ledger event, same timestamp, owner verbatim: *"leave it in for now and
  we'll handle the anti-exponential another way later / back in, but only in key places."* This
  reversed an earlier (false-positive) manifest fate of "cut" for its building/recipe and restored
  `ThingDef GravForge_GT` + `RecipeDef Make_GravcoreGF` + `ThingDef AdvShip_GravReactor` on Cherry
  Picker.
- **`GravBionics`** — owner ruling by card, **2026-09-04** (`RESEARCH_TREE_NORMALIZATION_1` §"Rulings
  2026-09-04", item 3): *"GravBionics: Rust Cathedral boon-gate, same as GravWeapon — all personal
  gravtech is Rataka boon-tech."*
- **`GravTuning`** — no direct card, but its manifest row notes the `GravForge` false-positive
  correction propagates to it (prereq chain), so it inherits the 2026-09-01 restoration indirectly.

**Inherited, general ruling (all 17):** `RESEARCH_TREE_NORMALIZATION_1` §"criteria" item 3 —
**DISCHARGED 2026-09-04**, owner reviewed the full manifest delta sheet and said *"Otherwise the
list is approved and done"* — i.e. every one of the 17 rows' tab/tier/prereq placement (not their
mod-retirement fate) is itself an owner-approved position in the research tree, not a FOUNDRY guess.

**The retirement item itself:** `RESEARCH_TRIO_RETIRE_1` was **filed by BENCH, 2026-09-11T06:33:37Z**,
citing an owner ruling from the same sitting (Wave 3, `STAT_NORMALIZATION_AUDIT_1`,
`2026-09-11T06:33:16Z`): *"research trio (steppingstones + gravtech x2) is NOT here — it folds into
`RESEARCH_TREE_NORMALIZATION_1`"* — i.e. the owner ruled the mods should eventually go, but ruled it
as a fold-in to the (already-closing) research pass, not as a direct "delete now" instruction, and
**never ruled on the 17 at-risk rows' fate specifically**. FOUNDRY's own block
(`2026-09-11T07:10:24Z`) is explicit: *"Owner AFK, not FOUNDRY's to pick."* — no owner sign-off
exists on any of the three routes below. That absence is the entire reason this briefing exists.

**`STAT_NORMALIZATION_AUDIT_1`'s own census** (`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`
§2B, lines 145-146) already classified both `als.gravtech`(+`.bc`) and the steppingstones mod as
*"the same class as the donor-retirement items: a cut here is a port"* — i.e. the census itself
pre-ruled the METHOD (port-or-explicit-loss, never a bare uninstall), even though it did not rule
which of the three routes to take.

## 3. Route consequences

First, the blast radius beyond the 17 themselves. Grepping `infrastructure/output/research_manifest_draft.csv`
for every OTHER live research row that lists one of the 17 as a *prerequisite* (i.e. what dangles if
the 17 vanish, independent of which route is chosen for the 17 rows' own content):

| defName | rows that prereq on it | who owns those rows |
|---|---|---|
| `RR_LateralThinking` | **33** | mostly `VFE_Res_*` (decor techs), `DP_RGive*` (raid-give techs), 3 KOTOR rows, our own `RR_Rugs`/`RR_Storage`/`RR_lighting` |
| `RR_ElectricityBasics` | **15** | vanilla `Electricity` itself, `AdvancedShowers`/`AdvancedToilets`/`HotTubs`/`Saunas`/`ColoredLights`/`ModernFixtures`/`TubeTelevision`, 3 `ProjectHeron_*` door rows, KOTOR HoloRec, and **our own `RM_WM_AutomatedSmelterRestoration`** (WreckedMachines) |
| `RR_BasicApparel` | **16** | almost entirely the `guy762_ResearchKotOR_*` apparel/companion chain |
| `RR_IncendiaryWeapons` | 5 | `BioferriteIgnition`, `OuterRim_LightInstallations`, 3 KOTOR blaster rows |
| `RR_PowerGenerators` | 4 | `BioferriteGenerator`/`BiofuelRefining`/`ToxifierGenerator`/`WatermillGenerator` |
| `RR_HeatingElements` | 3 | `AirConditioning`/`AtmosphericHeater`/`BiofuelRefining` |
| `RR_BasicCraftingFacilities` | 3 | `CarpetMaking`/`Smithing`/`Stonecutting` |
| `RR_Organization` | 3 | `BasicPsychicRituals`/`BioferriteExtraction`/our own `VFET_Fire` |
| `RR_BasicFoodPrep` | 3 | `Pemmican`/2 VCE cooking rows |
| `GravForge` | 3 | `GravBionics`/`GravTuning`/`GravWeapon` (i.e. its own siblings — internal to the trio) |
| `GravWeapon`, `GravTuning` | 2 each | siblings only |
| `GTbc_BigCannons`, `RR_EMP` | 1 each | `BlackHole_GT` (sibling); `guy762_ResearchKotOR_vibroweapons` |
| `AdvShipParts`, `BlackHole_GT`, `GravBionics` | 0 | leaf nodes |

So the 17 rows are not an isolated island: **~90 dependent-row edges** exist across the wider
research graph (many belonging to third-party mods we'd have no standing to "fix," a few belonging
to us). Every route below has to account for this, not just the 17 rows' own content.

### PORT — re-author all 17 as native `RimUtinni` defs first

- We would come to own **17 new `ResearchProjectDef`s** plus, to keep their unlocks meaningful, the
  buildings/recipes/apparel they gate that don't already exist as vanilla-adjacent content: at
  minimum `GravForge_GT` (building) + `Make_GravcoreGF` (recipe) + `AdvShip_GravReactor`,
  `Apparel_CerebrexNode`, `GravRifle`/`GravBlaster`/`GravHammer`/`Apparel_GravPack`,
  `GravArmor`/`GravHands`/`GravSpine`/`GravStomach`, `GravBlasterArtillery_GTbc`/
  `GravliteDefenseTurret_GTbc`/`GravRailArtillery_GTbc`/`TheSingularityCannon_GTbc` — this is the
  same shape of work as `WEAPONS_DONOR_RETIREMENT_1`/`BMT_FAUNA_ABSORPTION_1`, not a small patch.
  The 10 `RR_*` rows are cheaper (they gate vanilla-adjacent recipes already ported elsewhere, e.g.
  `RR_ElectricityBasics` just needs to keep gating the Power tab the way vanilla's own `Electricity`
  did before steppingstones rewired it).
- **What breaks if our costs/prereqs drift from the donor's**: every one of the ~90 dependent rows
  above (both third-party and our own `RM_WM_AutomatedSmelterRestoration`) references these defNames
  by name, not by tab/tier — a port that keeps the same defNames is transparent to them. But if a
  port *renames* anything (which the "no defName is ever renamed" rule in
  `RESEARCH_TREE_NORMALIZATION_1` §"Watch out" already forbids for the manifest's own resolved
  rows), every dependent row's prereq silently breaks with no error (patch-that-matches-nothing logs
  nothing). So a port MUST keep the 17 defNames byte-identical, which in turn means it inherits every
  quirk of the donor's authoring — including the very self-prereq bug our two defensive fixes
  already guard against.
- Also inherits the "cost 1400/1800/2000/2800/3500/4000/6000 doesn't fit T4's 5200 band" note already
  flagged on 6 of the 7 gravtech rows in the manifest — a port would need to either keep the
  non-conforming donor pricing (drift from the rest of the tier) or re-cost them (a second owner
  decision, band conformance vs. donor fidelity).

### ACCEPT-LOSS — rule the 17 cut, no replacement

- **What a player loses in play**: the entire Rust Cathedral personal-gravtech boon branch
  (`GravWeapon`/`GravBionics`, both carrying dated 2026-09-01/09-04 faction-gate rulings), the whole
  Ship-tree T4 gravtech industrial cluster (`GravForge`/`GravTuning`/`AdvShipParts`/`BlackHole_GT`/
  `GTbc_BigCannons`), and the Jawa Scavenging clan's own T0 tribal-start scaffold (10 `RR_*` rows,
  including the literal gate on the Power tab and on vanilla `Electricity` itself).
- **Which of our defs dangle** (grepped `prerequisites` referencing the 17 across the manifest and
  the repo): **`RM_WM_AutomatedSmelterRestoration`** (WreckedMachines, a north-star VALIDATED mod)
  directly prereqs `RR_ElectricityBasics` — losing that def without re-anchoring breaks a validated
  mod's own research chain. `VFET_Fire` prereqs `RR_Organization`. Beyond our own defs, ~85 more
  third-party rows (the KOTOR chain especially — 16+5+3+1 = 25 rows keyed off `RR_BasicApparel`/
  `RR_IncendiaryWeapons`/`RR_EMP`) would need the same "explicit cut + prereq re-anchor" treatment
  `RESEARCH_RECOST_PREREQ_JOIN_1` already used for 106 tier-inverted edges elsewhere in the manifest
  — this is not a clean edge, it's a second, comparably-sized reconciliation pass.
- **What re-fills the gap**: nothing does, unless explicitly authored. `check_coverage`/`check_prereqs`
  will report the hole precisely (already proven working per the item file's baseline run) but won't
  propose a replacement — that's still a design decision, not a mechanical one.

### COUNTER-PATCH — keep the mods, neutralize only the collision

- The precedent (`STAT_NORM_WAVE3_RETIRE_1`, same-day sibling item) counter-patched
  `iforgotmysocks.CaravanAdventures` by resetting only its 9 colliding stat fields
  (`ArmorRating`/`baseBodySize`/`combatPower` on 5 hand-triggered boss defs) to their vanilla
  analogues, wrapped every operation in `PatchOperationConditional` so the file no-ops if the donor
  is later retired, and left the mod's quest layer (FactionDefs, QuestScriptDefs, the Sacrileg
  Hunters faction) fully resident and untouched. `validate_patch.py` confirmed 0 errors, 9/9 targets
  resolved.
- Applied here: steppingstones' cost/prereq rewrites (656 total `ResearchProjectDef` operations, 112
  of which collide with our own patches per the audit doc) and gravtech's stat edits (9 `baseCost`
  replaces + `damageAmountBase` + `statBases`, per the item file) would get a same-shaped
  `PatchOperationConditional`-wrapped counter-patch neutralizing just those numeric collisions —
  **not** touching the 17 rows' own existence, tab, prereqs, or the two Rust Cathedral/Ship-tree
  owner rulings, which is exactly what "counter-patch" is for: the content and the prior rulings both
  survive untouched, same as CaravanAdventures' quest layer did.
- **What stays resident**: all three mods stay in `ModsConfig.xml` (plus the 4th, the Big Cannons
  retexture, which otherwise hard-fails to load without `als.gravtech.bc`). This is the only route of
  the three that requires zero re-authoring of the 17 rows and zero prereq re-anchoring across the
  ~90 dependent edges — the entire graph is untouched, only the numeric collisions this item was
  originally filed to resolve (the "112 collision rows") are addressed.
- **Cost of this route**: the mods stay a permanent third-party dependency (steppingstones already
  has zero external packageId references from any other mod, so it is not "load-bearing" for anyone
  but us and our own patches — but "us and our own patches" is exactly the point). It does not
  reduce mod-count, which was the audit's original motivating goal for touching this trio at all.

## 4. VERDICT (sweep opinion, not a ruling)

**Counter-patch is what the evidence favors, and it isn't close.** The other two routes both require
redoing work that is already finished elsewhere in this project: PORT means re-authoring 17 defs plus
a dozen-plus dependent buildings/recipes/apparel from scratch while being forbidden from renaming any
of them (so it inherits the donor's own bugs, including the self-prereq crash our code already has to
guard against); ACCEPT-LOSS means reversing four dated, specific owner rulings (the Rust Cathedral
boon-gates on `GravWeapon`/`GravBionics`, the 2026-09-01 restoration of `GravForge`) with no owner
sign-off on record, and then re-anchoring ~90 dependent research-graph edges by hand — including
our own validated `WreckedMachines` mod's `RM_WM_AutomatedSmelterRestoration`, which would dangle
outright. Counter-patch, by contrast, is a same-day sibling item's already-proven pattern
(`STAT_NORM_WAVE3_RETIRE_1`'s CaravanAdventures/MVT neutralizations, 0 validator errors) applied to a
smaller, already-quantified set of numeric collisions (9 gravtech fields + steppingstones' colliding
subset of 112 `ResearchProjectDef` operations), and it is the only route that touches neither the 17
rows' content nor any owner ruling nor any of the ~90 dependent edges. Its only real cost is that the
mod count doesn't go down — which was the audit's original motivation, but that motivation was about
reducing *silent stat collisions*, and counter-patching resolves exactly that, directly, without
inventing a research-tree placement decision the owner hasn't made.
